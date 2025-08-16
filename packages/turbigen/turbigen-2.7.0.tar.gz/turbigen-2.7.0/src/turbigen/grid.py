"""A general multiblock structured grid class."""

import numpy as np
from copy import copy
from turbigen.base import dependent_property, concatenate
from turbigen import util
import turbigen.yaml
import turbigen.fluid
import turbigen.base
import turbigen.flowfield
from scipy.interpolate import LinearNDInterpolator
import turbigen.marching_cubes
import importlib
from scipy.spatial import KDTree
from scipy.interpolate import interpn
from enum import IntEnum


logger = util.make_logger()


class MatchDir(IntEnum):
    IPLUS = 0
    JPLUS = 1
    KPLUS = 2
    IMINUS = 3
    JMINUS = 4
    KMINUS = 5
    CONST = 6


class BaseBlock(turbigen.flowfield.BaseFlowField):
    """Base block with coordinates only, flow-field and connectivity data."""

    _data_rows = (
        "x",
        "r",
        "t",
        "w",
        "mu_turb",
        "Omega",
    )  # , "Vx", "Vr", "Vt", "P", "T", "w")

    grid = None
    _conserved_store = None

    def __str__(self):
        return (
            f"Block({self.label}, xav={self.x.mean()}, rav={self.r.mean()},"
            f" tav={self.t.mean()}"
        )

    def area_average(self, prop):
        """Take area average of property over the cut surface.

        prop_avg = integral (prop  dA) / integral (dA)

        Parameters
        ----------
        prop : array
            Nodal property to average over the cut surface, same shape as self.

        Returns
        -------
            prop_avg : float
            Area average of the property over the cut surface.

        """
        return np.sum(prop * self.dA_node) / np.sum(self.dA_node)

    @dependent_property
    def mass_flow(self):
        """Integrate the mass flow through a cut surface."""
        if not self.ndim == 2:
            raise Exception("Mass flow is only defined for 2D cuts")
        return np.sum(util.dot(self.flux_mass, self.dA_node))

    def mass_average(self, prop):
        """Take mass average of property through the cut surface.

        prop_avg = integral (prop  rho V dot dA) / integral (rho V dot dA)

        Parameters
        ----------
        prop : array
            Nodal property to average over the cut surface, same shape as self.

        Returns
        -------
            prop_avg : float
            Area average of the property over the cut surface.

        """
        if not self.ndim == 2:
            raise Exception("Mass average is only defined for 2D cuts")
        return np.sum(prop * util.dot(self.flux_mass, self.dA_node)) / self.mass_flow

    @dependent_property
    def i_stag(self):
        """i-index of stagnation point."""

        if not self.ndim == 2:
            raise Exception(
                "Can only find stagnation point on 2D cuts; "
                f"this cut has shape {self.shape}"
            )

        # Use rotary static pressure to take out centrifugal pressure gradient
        P = self.P_rot

        # Extract surface distance, normalise to [-1,1] on each j-line
        z = self.zeta / np.ptp(self.zeta, axis=0) * 2.0 - 1.0

        # Find pressure maxima
        # This must be a loop over j because there can be a different number of
        # turning points at each spanwise lnocation
        _, nj = self.shape
        istag = np.full((nj,), 0, dtype=int)
        for j in range(nj):
            # Calculate gradient and curvature
            dP = np.diff(P[:, j])

            # Indices of downward zero crossings of pressure derivative
            izj = np.where(np.diff(np.sign(dP[:-2])) < 0.0)[0] + 1

            # Only keep maxima close to LE
            izj = izj[np.abs(z[izj, j]) < 0.2]

            # Now take the candiate point with maximum pressure
            try:
                istag[j] = izj[np.argsort(P[izj, j])][-1]
            except Exception:
                istag[j] = 0

        return istag

    @dependent_property
    def zeta_stag(self):
        """Surface distance along i-line with origin at stagnation point."""

        _, nj = self.shape
        zstag = np.full(
            (
                1,
                nj,
            ),
            np.nan,
        )
        istag = self.i_stag
        for j in range(nj):
            zstag[0, j] = self.zeta[istag[j], j]

        return self.zeta - zstag

    @dependent_property
    def xrt_stag(self):
        """Coordinates of the stagnation point at all j indices."""
        _, nj = self.shape
        xrt_stag = np.full(
            (
                3,
                nj,
            ),
            np.nan,
        )
        for j in range(nj):
            xrt_stag[:, j] = self.xrt[:, self.i_stag[j], j]
        return xrt_stag

    def meridional_slice(self, xrc):
        """Slice a block cut using a meridional curve."""

        # Get signed distance
        dist = util.signed_distance_piecewise(xrc, self.xr)

        # Preallocate
        data = self._data
        nv, ni, nj, nk = data.shape
        data_cut = np.zeros(
            (
                nv,
                ni,
                nk,
            )
        )

        # Get j indices above slice
        jcut = np.argmax(dist > 0, axis=1, keepdims=True) - 1
        if (dist > 0).all():
            return

        for i in range(ni):
            jnow = jcut[i]
            dist_now = dist[i, (jnow, jnow + 1), :]
            frac = -dist_now[0] / (dist_now[1] - dist_now[0])
            data_cut[:, i, :] = (
                data[:, i, jnow, :]
                + (data[:, i, jnow + 1, :] - data[:, i, jnow, :]) * frac
            )[:, 0, 0, :]

        out = self.empty(shape=(ni, nk))
        out._data = data_cut
        out._metadata = self._metadata
        return out

    def pitchwise_integrate(self, y):
        """Integrate something."""
        # Check if we have a 3D cut and i is singleton
        assert len(self.shape) == 3
        assert self.shape[0] == 1

        # The pitchwise grid lines should be at constant radius
        rtol = 1e-5 * np.ptp(self.r)
        assert (np.abs(np.diff(self.r, axis=2)) < rtol).all()

        # Trapezoidal integral
        return np.trapz(y, self.t, axis=2)

    @dependent_property
    def vol(self):
        # Volume
        if not self.ndim == 3:
            raise Exception("Face area is only defined for 3D grids")

        # Get face-centered coordinates
        xi, xj, xk = self.x_face
        ri, rj, rk = self.r_face
        rti, rtj, rtk = self.rt_face
        Fi = np.stack((xi, ri / 2.0, rti))
        Fj = np.stack((xj, rj / 2.0, rtj))
        Fk = np.stack((xk, rk / 2.0, rtk))
        dAi = self.dAi
        dAj = self.dAj
        dAk = self.dAk

        # Volume by Gauss' theorem
        Fisum = np.diff(np.sum(Fi * dAi, axis=0), axis=0)
        Fjsum = np.diff(np.sum(Fj * dAj, axis=0), axis=1)
        Fksum = np.diff(np.sum(Fk * dAk, axis=0), axis=2)
        vol = Fisum + Fjsum + Fksum

        return vol / 3.0

    @property
    def vol_approx(self):
        if not self.ndim == 3:
            raise Exception("Cell volume is only defined for 3D grids")

        # Vectors for cell sides
        xyz = self.xrrt
        qi = np.diff(xyz[:, :, :-1, :-1], axis=1)
        qj = np.diff(xyz[:, :-1, :, :-1], axis=2)
        qk = np.diff(xyz[:, :-1, :-1, :], axis=3)

        return np.sum(qk * np.cross(qi, qj, axis=0), axis=0)

    @dependent_property
    def spf(self):
        if self.ndim == 1:
            span = util.cum_arc_length(self.xr, axis=1)
            spf = span / np.max(span, axis=0, keepdims=True)
        else:
            span = util.cum_arc_length(self.xr, axis=2)
            spf = span / np.max(span, axis=1, keepdims=True)
        return spf

    @dependent_property
    def zeta(self):
        """Arc length along each i gridline."""
        return util.cum_arc_length(self.xyz, axis=1)

    @dependent_property
    def tri_area(self):
        if not self.shape[1] == 3:
            raise Exception("This is not a triangulated cut.")

        # Vectors for each side
        qAB = self.xrrt[..., 1] - self.xrrt[..., 0]
        qAC = self.xrrt[..., 2] - self.xrrt[..., 0]

        return 0.5 * np.cross(qAC, qAB, axis=0)

    def get_mpl_triangulation(self):
        """Generate a matplotlib-compatible triangulation for an unstructured cut."""

        # Check we have a triangulated shape (ntri, 3)
        try:
            ntri, ndim = self.shape
            assert ndim == 3
        except Exception:
            raise Exception("This is not a triangulated cut.")

        # Reshape to a 1D array
        C = self.flatten()

        # Because we store all three vertices for every triangle, many vertices are repeated
        # Matplotlib prefers without repeats
        # So find the 1D indices of unique coordiates only
        _, iunique, triangles = np.unique(
            C.xrt,
            axis=1,
            return_index=True,
            return_inverse=True,
        )

        # Only keep unique points
        C = C[(iunique,)]

        # The triangles are indices into the 1D unique data that
        # reconstruct the original (ntri, 3) data
        triangles = triangles.reshape(-1, 3)

        return C, triangles

    def interpolate_to_structured(self, npitch=99, nspan=101):
        """Given an unstructured cut interpolate to a regular grid.

        Note must be a straight line in x-r plane."""

        # TODO - at the moment we just use a brute force interpolation
        # but the *correct* way to do this is to:
        # Define a set of xr points along the cut line
        # Examine each triangle to see if it encloses the xr point
        # Interpolate within each triangle appropriately

        # unstructured shape (ntri, 3, nvar)

        # Repeat and centre on theta=0
        C = self.repeat_pitchwise(3)
        tmid = 0.5 * (C.t.max() + C.t.min())
        C.t -= tmid

        # Set up new coordinates
        xr0 = np.reshape((np.min(self.x), np.min(self.r)), (2, 1, 1))
        xr1 = np.reshape((np.max(self.x), np.max(self.r)), (2, 1, 1))
        eps = 1e-5
        clu = (
            (turbigen.util.cluster_cosine(nspan).reshape(1, -1, 1) + eps)
            / (1.0 + eps)
            * (1.0 - eps)
        )
        xr = clu * xr1 + (1.0 - clu) * xr0
        pitch = self.pitch
        t = -np.linspace(-pitch / 2.0, pitch / 2.0, npitch).reshape(1, -1)
        xrt = np.stack(np.broadcast_arrays(*xr, t), axis=0)

        # Initialise a new cut
        Cs = C.empty(shape=(1,) + xrt.shape[1:])
        xrt1 = np.expand_dims(xrt, 1)
        Cs.xrt = xrt1

        # Interpolate the data
        Cf = C.flatten()

        if np.ptp(Cf.x) > np.ptp(Cf.r):
            xi = np.stack((Cf.x, Cf.t), axis=-1)
            xo = np.stack((Cs.x, Cs.t), axis=-1)
        else:
            xi = np.stack((Cf.r, Cf.t), axis=-1)
            xo = np.stack((Cs.r, Cs.t), axis=-1)

        yi = Cf._data.T

        # ind_t = np.abs(xi[:, 1]) <= pitch * 0.6
        # xi = xi[ind_t]
        # yi = yi[ind_t]

        # fig, ax = plt.subplots()
        # ax.plot(xi[:, 0], xi[:, 1], "rx")
        # ax.plot(xo[0, :, :, 0], xo[0, :, :, 1], "b-")
        # ax.plot(xo[0, :, :, 0].T, xo[0, :, :, 1].T, "b-")
        # ax.axis("equal")
        # plt.show()
        # quit()
        #
        interp = LinearNDInterpolator(xi, yi)
        yo = np.moveaxis(interp(xo), -1, 0)
        ind_nan = np.isnan(yo)
        if ind_nan.any():
            raise Exception()
        Cs._data[:] = yo

        assert np.allclose(Cs.xrt, xrt1)

        # Ensure that Omega is exactly constant
        # (removing numerical error due to interpolation)
        Cs.Omega[:] = Cs.Omega.mean()

        return Cs

    def repeat_pitchwise(self, N, axis=0):
        """Replicate the data in pitchwise direction."""

        # Make a list of copies of this cut with different theta
        C_all = []
        for i in range(N):
            Ci = self.copy()
            Ci.t += self.pitch * i
            C_all.append(Ci)

        # Join the copies together
        C_all = concatenate(C_all, axis=axis)

        return C_all

    @property
    def dli(self):
        return np.diff(self.xyz, axis=1)

    @property
    def dlj(self):
        return np.diff(self.xyz, axis=2)

    @property
    def dlk(self):
        return np.diff(self.xyz, axis=3)

    @property
    def dlmin(self):
        # Get face area magnitudes
        dAi = util.vecnorm(self.dAi)
        dAj = util.vecnorm(self.dAj)
        dAk = util.vecnorm(self.dAk)

        # For each volume, take the minimum of the bounding length
        # scales for every coordinate direction
        vol = self.vol
        dli = np.minimum(vol / dAi[1:, :, :], vol / dAi[:-1, :, :])
        dlj = np.minimum(vol / dAj[:, 1:, :], vol / dAj[:, :-1, :])
        dlk = np.minimum(vol / dAk[:, :, 1:], vol / dAk[:, :, :-1])

        # Now take minimum of all directions
        dlmin = np.minimum(dli, dlj)
        dlmin = np.minimum(dlmin, dlk)

        return dlmin

    @property
    def cell_ARi(self):
        """Cell aspect ratio at constant i."""
        assert self.ndim == 3, "Cell aspect ratio is only defined for 3D grids"
        dlj = util.average(util.vecnorm(self.dlj), axis=2)
        dlk = util.average(util.vecnorm(self.dlk), axis=1)
        AR = dlj / dlk
        AR[AR < 1] = 1.0 / AR[AR < 1]  # Ensure AR >= 1
        return AR

    @property
    def cell_ARj(self):
        """Cell aspect ratio at constant j."""
        assert self.ndim == 3, "Cell aspect ratio is only defined for 3D grids"
        dli = util.average(util.vecnorm(self.dli), axis=2)
        dlk = util.average(util.vecnorm(self.dlk), axis=0)
        AR = dli / dlk
        AR[AR < 1] = 1.0 / AR[AR < 1]  # Ensure AR >= 1
        return AR

    @property
    def cell_ARk(self):
        """Cell aspect ratio at constant k."""
        assert self.ndim == 3, "Cell aspect ratio is only defined for 3D grids"
        dli = util.average(util.vecnorm(self.dli), axis=1)
        dlj = util.average(util.vecnorm(self.dlj), axis=0)
        AR = dli / dlj
        AR[AR < 1] = 1.0 / AR[AR < 1]  # Ensure AR >= 1
        return AR

    @dependent_property
    def dAi(self):
        # Vector area for i=const faces, Gauss' theorem method
        if self.ndim < 3:
            raise Exception("i-face area is only defined for 3D grids")

        # Define four vertices ABCD
        #    B      C
        #     *----*
        #  ^  |    |
        #  k  *----*
        #    A      D
        #      j>
        #
        if self.ndim > 3:
            v = self.xrrt[:, :, :, :, 0]  # Discard any time dimension
        else:
            v = self.xrrt
        A = v[:, :, :-1, :-1]
        B = v[:, :, :-1, 1:]
        C = v[:, :, 1:, 1:]
        D = v[:, :, 1:, :-1]

        return util.dA_Gauss(A, B, C, D)

    @dependent_property
    def dAj(self):
        # Vector area for j=const faces, Gauss' theorem method
        if not self.ndim == 3:
            raise Exception("j-face area is only defined for 3D grids")

        # Define four vertices ABCD
        #    B      C
        #     *----*
        #  ^  |    |
        #  k  *----*
        #    A      D
        #      i>
        #
        v = self.xrrt
        A = v[:, :-1, :, :-1]
        B = v[:, :-1, :, 1:]
        C = v[:, 1:, :, 1:]
        D = v[:, 1:, :, :-1]

        return -util.dA_Gauss(A, B, C, D)

    @dependent_property
    def dAk(self):
        # Vector area for k=const faces, Gauss' theorem method
        if not self.ndim == 3:
            raise Exception("k-face area is only defined for 3D grids")

        # Define four vertices ABCD
        #    B      C
        #     *----*
        #  ^  |    |
        #  k  *----*
        #    A      D
        #      i>
        #
        v = self.xrrt
        A = v[:, :-1, :-1, :]
        B = v[:, :-1, 1:, :]
        C = v[:, 1:, 1:, :]
        D = v[:, 1:, :-1, :]

        return util.dA_Gauss(A, B, C, D)

    @property
    def r_face(self):
        return util.node_to_face3(self.r)

    @property
    def r_cell(self):
        return util.node_to_cell(self.r)

    @property
    def t_face(self):
        return util.node_to_face3(self.t)

    @property
    def rt_face(self):
        return util.node_to_face3(self.rt)

    @property
    def x_face(self):
        return util.node_to_face3(self.x)

    def to_perfect(self):
        bnew = PerfectBlock(shape=self.shape)
        bnew.xrt = self.xrt
        bnew.w = self.w
        bnew.Omega = self.Omega
        bnew._metadata.update(self._metadata)
        for patch in bnew.patches:
            patch.block = bnew
        bnew.mu_turb = np.full_like(bnew.w, np.nan)
        return bnew

    def to_real(self):
        bnew = RealBlock(shape=self.shape)
        bnew.xrt = self.xrt
        bnew.w = self.w
        bnew.Omega = self.Omega
        bnew._metadata.update(self._metadata)
        for patch in bnew.patches:
            patch.block = bnew
        bnew.mu_turb = np.full_like(bnew.w, np.nan)
        return bnew

    def copy(self):
        b = super().copy()
        b.patches = []
        for p in self.patches:
            b.add_patch(copy(p))
            b.patches[-1].ijk_limits = b.patches[-1].ijk_limits + 0
        return b

    def write_npz(self, fname):
        """Save this object to an npz file."""
        d = self.to_dict()
        d["metadata"].pop("patches")
        d.update(d.pop("metadata"))
        np.savez_compressed(fname, **d)

    def check_negative_volumes(self):
        ni, nj, nk = self.shape
        vol = self.vol
        for i in range(ni - 1):
            for j in range(nj - 1):
                for k in range(nk - 1):
                    if vol[i, j, k] < 0.0:
                        print(
                            f"Negative volume at i={i}, j={j}, k={k} "
                            f"({vol[i, j, k]:.3e}) in block {self.label}"
                        )
        print(f"Summary: {np.sum(vol < 0.0)} negative volumes in block {self.label}")

    @classmethod
    def from_coordinates(cls, xrt, Nb, patches=(), label=None, Omega=0.0):
        # Make empty object of correct shape
        block = cls(shape=xrt.shape[1:])
        block.xrt = xrt
        block._metadata = {"Nb": Nb, "patches": list(patches)}
        block.Omega = Omega
        for p in patches:
            p.block = block
            # Check the limit indices are valid
            nijk = np.reshape(block.shape, (3, 1))
            if not (p.ijk_limits < nijk).all():
                raise Exception(
                    f"Patch indices {p.ijk_limits} exceed block size {nijk}"
                )

        block.label = label
        return block

    def transpose(self, order):
        # Rearrange the data
        order1 = [
            0,
        ] + [o + 1 for o in order]
        self._data = self._data.transpose(order1)
        self._dependent_property_cache.clear()

        # Rearrange the patches
        for patch in self.patches:
            patch.ijk_limits = patch.ijk_limits[order, :]

        return self

    @property
    def w(self):
        return self._get_data_by_key("w")

    @w.setter
    def w(self, val):
        return self._set_data_by_key("w", val)

    @property
    def mu_turb(self):
        return self._get_data_by_key("mu_turb")

    @mu_turb.setter
    def mu_turb(self, val):
        return self._set_data_by_key("mu_turb", val)

    @property
    def Nb(self):
        return self._get_metadata_by_key("Nb")

    @Nb.setter
    def Nb(self, val):
        return self._set_metadata_by_key("Nb", val)

    @property
    def label(self):
        return self._get_metadata_by_key("label")

    @label.setter
    def label(self, val):
        return self._set_metadata_by_key("label", val)

    @property
    def patches(self):
        return self._get_metadata_by_key("patches")

    @patches.setter
    def patches(self, val):
        return self._set_metadata_by_key("patches", val)

    @property
    def npts(self):
        return self.size

    @property
    def pitch(self):
        return 2.0 * np.pi / self.Nb

    @property
    def ni(self):
        return self.shape[0]

    @property
    def nj(self):
        return self.shape[1]

    @property
    def nk(self):
        return self.shape[2]

    def apply_guess_uniform(self, Vxrt, P, T, Omega=0.0):
        self.Vx = Vxrt[0]
        self.Vr = Vxrt[1]
        self.Vt = Vxrt[2]
        self.Omega = Omega
        self.set_P_T(P, T)

    def delete(self):
        """Delete this block from the parent grid"""
        logger.debug(f"Deleting block {self.label}")
        # Remove this block from the grid
        if self.grid is not None:
            self.grid._blocks.remove(self)
        else:
            logger.warning("Block is not part of a grid, cannot remove from grid.")

    def trim(self, i=None, j=None, k=None, update_matches=True):
        """Extract a subset of this block in-place, correct patch indices."""

        logger.debug(f"Trimming block {self}")
        if i:
            ni_old = self.shape[0]
            logger.debug(f"i limits={i}")
            if i[1] < 0:
                i = (i[0], ni_old + i[1])
            logger.debug(f"corrected i limits={i}")
            self._data = self._data[:, i[0] : (i[1] + 1), :, :]
            ni_new = self.shape[0]
            logger.debug(f"old ni={ni_old}")
            logger.debug(f"new ni={ni_new}")
            for p in self.patches:
                logger.debug(f"Fixing patch {p}")
                isten = p.ijk_limits[0, :]
                isten_old = isten.copy()
                isten[isten == ni_old - 1] = -1
                isten[isten > 0] = isten[isten > 0] - i[0]
                logger.debug(f"{isten_old}->{isten}")

            # Now adjust the patches that reference this block
            if update_matches:
                logger.debug("Now updating the matching patches")
                for p2 in self.grid.periodic_patches:
                    if p2.match is None:
                        raise Exception("Must match patches before trimming the block")
                    if (p2.block is self) or (p2.match.block is not self):
                        continue
                    logger.debug(f"{p2}")
                    if p2.idir == 0:
                        logger.debug("next patch i matches trim block i")
                        isten = p2.ijk_limits[0, :]
                        isten[isten == ni_old - 1] = -1
                        isten[isten > 0] = isten[isten > 0] - i[0]
                        logger.debug(f"{isten_old}->{isten}")
                    elif p2.jdir == 0:
                        logger.debug("next patch j matches trim block i")
                    elif p2.kdir == 0:
                        logger.debug("next patch k matches trim block i")
                    elif p2.idir == 3:
                        logger.debug("next patch i matches trim block -i")
                    elif p2.jdir == 3:
                        logger.debug("next patch j matches trim block -i")
                    elif p2.kdir == 3:
                        logger.debug("next patch k matches trim block -i")

        if j:
            raise NotImplementedError
        if k:
            raise NotImplementedError

        logger.debug("Sucessfully trimmed block.")

    def get_wall(self, ignore_slip=False):
        ni, nj, nk = self.shape

        # Zero means is a wall
        # Positive values are not-wallness
        iwall = np.zeros((ni, nj - 1, nk - 1), dtype=int)
        iwall[1:-1, :, :] = 1

        jwall = np.zeros((ni - 1, nj, nk - 1), dtype=int)
        jwall[:, 1:-1, :] = 1

        kwall = np.zeros((ni - 1, nj - 1, nk), dtype=int)
        kwall[:, :, 1:-1] = 1

        # The plan is to loop over all patches, and increment a
        # wall indicator for all nodes on each not-wall patch
        for patch in self.patches:
            # Skip if this patch *is* a wall
            if ignore_slip:
                if not type(patch) in NOT_WALL_FRICTION:
                    continue
            else:
                if not type(patch) in NOT_WALL_WDIST:
                    continue

            # Make block number of points in each direction
            # same size as ijk_limits (3, 2)
            nijk = np.tile(np.reshape(self.shape, (3, 1)), (1, 2))

            # Get ijk limits of this patch, accounting for -ve ends
            ijk_lim = patch.ijk_limits.copy()
            ijk_lim[ijk_lim < 0] = (nijk + ijk_lim)[ijk_lim < 0]

            # Make the end values exclusive for Python range convention
            ijk_lim[:, 1] += 1
            ist, ien = ijk_lim[0]
            jst, jen = ijk_lim[1]
            kst, ken = ijk_lim[2]

            # # Increment the not wall indicator on the const-dirn
            # iwall[ist:ien, jst : jen, kst : ken] += 1
            # jwall[ist:ien, jst : jen, kst : ken] += 1
            # kwall[ist:ien, jst : jen, kst : ken] += 1

            if patch.cdir == 0:
                # iwall[ist:ien, jst:jen, kst:ken] += 1
                iwall[ist:ien, jst : (jen - 1), kst : (ken - 1)] += 1
                # print(f'Setting iwall for {patch}')
                # print(patch.block.shape)
                # print(ijk_lim)
                # kwall[ist:ien, jst:jen, kst:ken] += 1
            elif patch.cdir == 1:
                # jwall[ist:ien, jst:jen, kst:ken] += 1
                jwall[ist : (ien - 1), jst:jen, kst : (ken - 1)] += 1
            elif patch.cdir == 2:
                # print(f'Setting kwall for {patch}')
                # print(patch.block.shape)
                # print(ijk_lim)
                # kwall[ist:ien, jst:jen, kst:ken] += 1
                kwall[ist : (ien - 1), jst : (jen - 1), kst:ken] += 1

        # Now distribute the face not-wallness to the nodes
        wall = np.zeros((ni, nj, nk), dtype=int)

        # i-faces
        wall[:, :-1, :-1] += iwall  # Bottom-left
        wall[:, 1:, :-1] += iwall  # Bottom-right
        wall[:, :-1, 1:] += iwall  # Top-left
        wall[:, 1:, 1:] += iwall  # Top-right

        # j-faces
        wall[:-1, :, :-1] += jwall  # Bottom-left
        wall[1:, :, :-1] += jwall  # Bottom-right
        wall[:-1, :, 1:] += jwall  # Top-left
        wall[1:, :, 1:] += jwall  # Top-right

        # j-faces
        wall[:-1, :-1, :] += kwall  # Bottom-left
        wall[1:, :-1, :] += kwall  # Bottom-right
        wall[:-1, 1:, :] += kwall  # Top-left
        wall[1:, 1:, :] += kwall  # Top-right

        # A node is *not* on a wall if *all* of the faces touching it are *not*
        # walls. So the thresholds are:
        #   corner: 3
        #   edge: 4
        #   face: 8
        #   interior: 0
        thresh = np.zeros_like(wall, dtype=int)

        thresh[0, :, :] = 8
        thresh[-1, :, :] = 8
        thresh[:, 0, :] = 8
        thresh[:, -1, :] = 8
        thresh[:, :, 0] = 8
        thresh[:, :, -1] = 8

        thresh[:, 0, 0] = 4
        thresh[:, 0, -1] = 4
        thresh[:, -1, 0] = 4
        thresh[:, -1, -1] = 4
        thresh[0, :, 0] = 4
        thresh[0, :, -1] = 4
        thresh[-1, :, 0] = 4
        thresh[-1, :, -1] = 4
        thresh[0, 0, :] = 4
        thresh[0, -1, :] = 4
        thresh[-1, 0, :] = 4
        thresh[-1, -1, :] = 4

        thresh[0, 0, 0] = 3
        thresh[-1, 0, 0] = 3
        thresh[0, -1, 0] = 3
        thresh[-1, -1, 0] = 3
        thresh[0, 0, -1] = 3
        thresh[-1, 0, -1] = 3
        thresh[0, -1, -1] = 3
        thresh[-1, -1, -1] = 3

        wall = (wall < thresh).astype(np.int8)

        iwall = (iwall == 0).astype(np.int8)
        jwall = (jwall == 0).astype(np.int8)
        kwall = (kwall == 0).astype(np.int8)

        return iwall, jwall, kwall, wall

    def get_dwall(self):
        # Get wall length scales at nodes
        dli = turbigen.util.vecnorm(self.dli)
        dlj = turbigen.util.vecnorm(self.dlj)
        dlk = turbigen.util.vecnorm(self.dlk)

        # Distribute length scales to faces
        dlif = np.stack(
            (
                dli[:, :-1, :-1],
                dli[:, 1:, :-1],
                dli[:, :-1, 1:],
                dli[:, 1:, 1:],
            )
        ).mean(axis=0)
        dljf = np.stack(
            (
                dlj[:-1, :, :-1],
                dlj[1:, :, :-1],
                dlj[:-1, :, 1:],
                dlj[1:, :, 1:],
            )
        ).mean(axis=0)
        dlkf = np.stack(
            (
                dlk[:-1, :-1, :],
                dlk[1:, :-1, :],
                dlk[:-1, 1:, :],
                dlk[1:, 1:, :],
            )
        ).mean(axis=0)

        return dlif, dljf, dlkf

    def check_coordinates(self):
        """Raise an error if coordinates are invalid."""

        # No negative radii
        assert (self.r >= 0.0).all()

        # Finite coordinates
        try:
            assert np.isfinite(self.xrt).all()
        except AssertionError:
            logger.iter(
                np.nanmean(self.xrt[0]),
                np.nanmin(self.xrt[0]),
                np.nanmax(self.xrt[0].max),
                np.sum(np.isnan(self.xrt[0])),
            )
            logger.iter(
                np.nanmean(self.xrt[1]),
                np.nanmin(self.xrt[1]),
                np.nanmax(self.xrt[1].max),
                np.sum(np.isnan(self.xrt[1])),
            )
            logger.iter(
                np.nanmean(self.xrt[2]),
                np.nanmin(self.xrt[2]),
                np.nanmax(self.xrt[2].max),
                np.sum(np.isnan(self.xrt[2])),
            )
            raise Exception("Coordinates not finite")

        # No negative cells
        assert (self.vol_approx > 0.0).all()

    def check_wall_distance(self):
        """Raise an error if wall distance is invalid."""

        # No zeros or nans
        assert np.isfinite(self.w).all()

        # No negative distances
        assert (self.w >= 0.0).all()

        # No huge distances
        Lmax = np.max(np.ptp(self.xrrt, axis=(1, 2, 3)))
        assert (self.w < Lmax).all()

    def get_connected(self, npass=10):
        g = self.grid
        bid_start = g.index(self)
        bid_conn = [bid_start]
        for _ in range(npass):
            bid_conn_new = []
            for bid in bid_conn:
                for p in g[bid].patches:
                    if not isinstance(
                        p, (turbigen.grid.PeriodicPatch, turbigen.grid.NonMatchPatch)
                    ):
                        continue
                    bid_match = g.index(p.match.block)
                    if bid_match not in bid_conn + bid_conn_new:
                        bid_conn_new.append(bid_match)
            bid_conn.extend(bid_conn_new)

        assert len(bid_conn) == len(set(bid_conn)), "Connected blocks not unique"
        return [g[bid] for bid in bid_conn]

    def add_patch(self, patch):
        patch.block = self
        self.patches.append(patch)

    def find_patches(self, cls):
        patches = []
        for patch in self.patches:
            if isinstance(patch, cls):
                patches.append(patch)
        return patches

    @property
    def rotating_patches(self):
        return self.find_patches(RotatingPatch)

    @property
    def mixing_patches(self):
        return self.find_patches(MixingPatch)

    @property
    def inlet_patches(self):
        return self.find_patches(InletPatch)

    @property
    def outlet_patches(self):
        return self.find_patches(OutletPatch)

    @property
    def periodic_patches(self):
        return self.find_patches(PeriodicPatch)

    @property
    def cooling_patches(self):
        return self.find_patches(CoolingPatch)

    def interp_from(self, other):
        """Interpolate solution from another block."""

        # TODO - logic to transfer fluid properties should be a method of the
        # RealState or PerfectState, can then remove branch here
        if not isinstance(self, RealBlock):
            self.cp = other.cp
            self.gamma = other.gamma
            self.mu = other.mu
        else:
            self.fluid_name = other.fluid_name

        if self.shape == other.shape:
            # When shapes match exactly, just take a copy
            self.Vxrt = other.Vxrt.copy()
            self.set_rho_u(other.rho, other.u)
            self.mu_turb = other.mu_turb.copy()
        else:
            # Otherwise, interpolate by index

            # Other block relative indexes
            ijkv_other = [np.linspace(0.0, 1.0, n) for n in other.shape]

            # Target block relative indexes
            ijkv = [np.linspace(0.0, 1.0, n) for n in self.shape]
            ijk = np.stack(np.meshgrid(*ijkv, indexing="ij"), axis=-1)

            self.Vx = interpn(ijkv_other, other.Vx, ijk)
            self.Vr = interpn(ijkv_other, other.Vr, ijk)
            self.Vt = interpn(ijkv_other, other.Vt, ijk)
            self.mu_turb = interpn(ijkv_other, other.mu_turb, ijk)
            rho = interpn(ijkv_other, other.rho, ijk)
            u = interpn(ijkv_other, other.u, ijk)
            self.set_rho_u(rho, u)

    def subsample(self, factor):
        """Scale the number of grid points along each edge, keeping connectivity.

        In general, without whole-face to whole-face connectivity, we cannot just
        downsample each block seperately because the periodic patches will not line
        up. So we find the critical points at patch start and ends and keep these
        the same, and apply the same coarsening between those critical points."""

        # Assemble critical values of i, j, k
        ic = [0, self.ni - 1]
        jc = [0, self.nj - 1]
        kc = [0, self.nk - 1]
        ijkc = [ic, jc, kc]
        nijk = np.tile(np.reshape(self.shape, (3, 1)), (1, 2))
        for p in self.patches:
            ijk_lim = p.ijk_limits
            ijk_lim[ijk_lim < 0] = (nijk + ijk_lim)[ijk_lim < 0]
            for m in range(3):
                ijkc[m] += ijk_lim[m].tolist()
        ijkc = [np.unique(c) for c in ijkc]

        # Allow different factors for each direction
        if not isinstance(factor, (list, tuple)):
            factors = (factor,) * 3
        else:
            factors = factor

        # Now resample keeping the critical indices
        ijk_new = [
            util.resample_critical_indices(nii, ijkci, f)
            for nii, ijkci, f in zip(self.shape, ijkc, factors)
        ]
        nijk_new = tuple([len(xx) for xx in ijk_new])

        # Convert old patch start/end for indices into new block
        for p in self.patches:
            for m in range(3):
                p.ijk_limits[m, :] = np.argwhere(
                    np.isin(ijk_new[m], p.ijk_limits[m, :])
                ).squeeze()

        # Extract these points from the block
        mask = np.zeros((3,) + self.shape, dtype=bool)
        mask[0, ijk_new[0], :, :] = True
        mask[1, :, ijk_new[1], :] = True
        mask[2, :, :, ijk_new[2]] = True
        mask = np.repeat(mask.all(axis=0)[None, :], self.nprop, axis=0)
        self._data = self._data[mask].reshape((self.nprop,) + nijk_new)
        self._dependent_property_cache.clear()

    def refine(self, k):
        """Make a finer mesh by halving each edge k times."""

        # Store angular velocity and reset later to make sure Omega.ptp() remains 0
        Omega = self.Omega.mean()

        # Input data
        ni, nj, nk = self.shape
        ijk = range(ni), range(nj), range(nk)
        d = np.moveaxis(self._data, 0, -1)

        # Query data
        iqv = np.linspace(0, ni - 1, (ni - 1) * (2**k) + 1)
        jqv = np.linspace(0, nj - 1, (nj - 1) * (2**k) + 1)
        kqv = np.linspace(0, nk - 1, (nk - 1) * (2**k) + 1)
        ijkq = np.moveaxis(np.stack(np.meshgrid(iqv, jqv, kqv, indexing="ij")), 0, -1)

        # Peform interpolation
        dq = interpn(ijk, d, ijkq)
        self._data = np.moveaxis(dq, -1, 0)

        # Adjust patches
        for patch in self.patches:
            pos = patch.ijk_limits >= 0
            patch.ijk_limits[pos] *= 2**k
            patch.ijk_limits[~pos] = ((patch.ijk_limits[~pos] + 1) * 2**k) - 1

        self.Omega = Omega

    def nearest_index(self, xrt):
        """Get the indices of closest point in a block to a query point."""
        xrrt = np.copy(xrt)
        xrrt[2] *= xrrt[1]
        dist = np.sum((self.xrrt - np.reshape(xrrt, (3, 1, 1, 1))) ** 2, axis=0)
        return np.unravel_index(np.argmin(dist), self.shape)

    def __eq__(self, other):
        """Two blocks are equal if they have the same coordinates."""
        return self is other


class PerfectBlock(BaseBlock, turbigen.flowfield.PerfectFlowField):
    _data_rows = ("x", "r", "t", "Vx", "Vr", "Vt", "rho", "u", "w", "mu_turb", "Omega")

    def __str__(self):
        return f"Block({self.label})"


class RealBlock(BaseBlock, turbigen.flowfield.RealFlowField):
    _data_rows = ("x", "r", "t", "Vx", "Vr", "Vt", "rho", "u", "w", "mu_turb", "Omega")

    def __str__(self):
        return f"Block({self.label}"


class Grid:
    """A collection of blocks."""

    def __init__(self, blocks):
        self._blocks = blocks
        self._iter_ind = 0

        for block in self._blocks:
            block.grid = self

    def __iter__(self):
        # Use an iterator class so we can do nested iteration
        class GridIter:
            def __init__(self, g):
                self.g = g
                self.i = -1

            def __next__(self):
                self.i += 1
                if self.i >= len(self.g):
                    raise StopIteration
                return self.g[self.i]

            def __iter__(self):
                return self

        return GridIter(self)

    def __len__(self):
        return len(self._blocks)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.block_by_label(key)
        else:
            return self._blocks[key]

    def extend(self, g):
        self._blocks += g._blocks
        self._iter_ind = 0
        for block in self._blocks:
            block.grid = self

    def append(self, b):
        self._blocks.append(b)
        b.grid = self

    def index(self, block):
        return [block is bi for bi in self._blocks].index(True)

    def block_by_label(self, label):
        for b in self:
            if b.label == label:
                return b
        raise KeyError(f'label "{label}" not found in grid')

    def find_patches(self, cls):
        patches = []
        for block in self:
            for patch in block.patches:
                if isinstance(patch, cls):
                    patches.append(patch)
        return patches

    def block_by_point(self, xrt):
        """Get the block containing a point."""

        # Loop over blocks
        for b in self:
            # Skip blocks where this point is outside the box
            xrt_max = b.xrt.max(axis=(1, 2, 3))
            xrt_min = b.xrt.min(axis=(1, 2, 3))

            if np.logical_and(xrt >= xrt_min, xrt <= xrt_max).all():
                return b

    def blocks_by_box(self, xrt_box):
        """Get blocks inside a bouding box."""
        xrt_box = np.reshape(xrt_box, (3, 2))

        # Loop over blocks
        blocks = []
        for b in self:
            xmin = (b.x >= xrt_box[0, 0]).all()
            xmax = (b.x <= xrt_box[0, -1]).all()
            ymin = (b.r >= xrt_box[1, 0]).all()
            ymax = (b.r <= xrt_box[1, -1]).all()
            zmin = (b.t >= xrt_box[2, 0]).all()
            zmax = (b.t <= xrt_box[2, -1]).all()

            if all((xmin, xmax, ymin, ymax, zmin, zmax)):
                blocks.append(b)

        return blocks

    @property
    def inlet_patches(self):
        return self.find_patches(InletPatch)

    @property
    def outlet_patches(self):
        return self.find_patches(OutletPatch)

    @property
    def mixing_patches(self):
        return self.find_patches(MixingPatch)

    @property
    def porous_patches(self):
        return self.find_patches(PorousPatch)

    @property
    def probe_patches(self):
        return self.find_patches(ProbePatch)

    @property
    def periodic_patches(self):
        return self.find_patches(PeriodicPatch)

    @property
    def cooling_patches(self):
        return self.find_patches(CoolingPatch)

    @property
    def rotating_patches(self):
        return self.find_patches(RotatingPatch)

    @property
    def nonmatch_patches(self):
        return self.find_patches(NonMatchPatch)

    @property
    def cusp_patches(self):
        return self.find_patches(CuspPatch)

    @property
    def inviscid_patches(self):
        return self.find_patches(CuspPatch)

    def match_patches(self, raise_fail=True):
        """Connect all pairs of patches that should match together."""

        # Periodics first, then mixing
        for patches in [
            self.periodic_patches,
            self.mixing_patches,
            self.nonmatch_patches,
            self.cusp_patches,
        ]:
            # Remove existing matches
            for P in patches:
                P.match = None

            if raise_fail and not np.mod(len(patches), 2) == 0:
                raise Exception(f"Wrong number of {type(patches[0])} to match")

            for P1 in patches:
                for P2 in patches:
                    try:
                        if P1 is P2:  # or p1.match or p2.match:
                            continue
                        elif P1.check_match(P2):
                            break
                    except Exception as e:
                        logger.info("Error checking match:")
                        logger.info(P1)
                        logger.info(P2)
                        raise e
            for P in patches:
                if P.match is None and raise_fail:
                    raise Exception(
                        "Could not match patch "
                        f"bid={self._blocks.index(P.block)} "
                        f"pid={P.block.patches.index(P)} {P} {P.block}"
                    )

    @property
    def nrow(self):
        if len(self.mixing_patches) == 0:
            return 1
        else:
            return len(self.mixing_patches) // 2 + 1

    @property
    def ncell(self):
        return sum([b.size for b in self])

    @property
    def row_blocks(self):
        """Split blocks into rows."""

        if self.nrow == 1:
            return [list(self)]
        elif self.nrow == 2:
            blkin = self.inlet_patches[0].block.get_connected()
            blkout = [b for b in self._blocks if b not in blkin]
            return [blkin, blkout]
        else:
            blk = []
            # Start at inlet
            blk.append(self.inlet_patches[0].block.get_connected())
            mix_visited = []
            for _ in range(1, self.nrow - 1):
                # Look for a mixing patch in the previous row
                for p in self.mixing_patches:
                    if p.block in blk[-1] and p not in mix_visited:
                        # Add the patches on the other side of mixing patch
                        blk.append(p.match.block.get_connected())
                        mix_visited.append(p)
                        break
            blk.append(self.outlet_patches[0].block.get_connected())
            # Check for any orphan blocks and arbitrarily put on last row
            blk_flat = sum(blk, [])
            for b in self._blocks:
                if b not in blk_flat:
                    blk[-1].append(b)

            assert sum([len(b) for b in blk]) == len(self._blocks)

            return blk

    def row_index(self, block):
        for irow, row_block in enumerate(self.row_blocks):
            if block in row_block:
                return irow
        raise Exception(f"Could not locate {block} in the row lists")

    def check_coordinates(self):
        passed = True
        for ib, b in enumerate(self):
            try:
                b.check_coordinates()
            except Exception as e:
                logger.iter(f"Block {ib}")
                logger.iter(e)
                passed = False
        if not passed:
            raise Exception("Coordinate check failed.")

    def apply_periodic(self):
        """For each pair of periodic patches, set average of conserved quantities."""
        done = []
        for patch in self.periodic_patches:
            if patch in done:
                continue

            perm, flip = patch.get_match_perm_flip()

            i1 = (slice(3, 8, None),) + patch.get_slice()
            i2 = (slice(3, 8, None),) + patch.match.get_slice()

            data1 = patch.block._data[i1].copy()
            data2 = np.flip(patch.match.block._data[i2].transpose(perm), axis=flip)

            avg = 0.5 * (data1 + data2)
            patch.block._data[i1] = avg
            nxavg = np.flip(avg, axis=flip).transpose(np.argsort(perm))
            patch.match.block._data[i2] = nxavg
            done.append(patch)
            done.append(patch.match)

    def apply_rotation(self, row_types, Omega):
        """Set wall rotations."""

        assert len(row_types) == len(Omega)
        assert self.nrow == len(row_types)

        for row_block, row_type, Omegai in zip(self.row_blocks, row_types, Omega):
            for block in row_block:
                block.Omega = Omegai

                if row_type == "stationary":
                    patches = []

                elif row_type == "tip_gap":
                    patches = [
                        RotatingPatch(i=0),
                        RotatingPatch(i=-1),
                        RotatingPatch(j=0),
                        RotatingPatch(k=0),
                        RotatingPatch(k=-1),
                    ]

                elif row_type == "shroud":
                    patches = [
                        RotatingPatch(i=0),
                        RotatingPatch(i=-1),
                        RotatingPatch(j=0),
                        RotatingPatch(j=-1),
                        RotatingPatch(k=0),
                        RotatingPatch(k=-1),
                    ]

                else:
                    raise Exception("Unknown row type %s", row_type)

                for patch in patches:
                    patch.Omega = Omegai
                    block.add_patch(patch)

    def apply_inlet(self, state, Alpha, Beta):
        for patch in self.inlet_patches:
            patch.state = state
            patch.Alpha = Alpha
            patch.Beta = Beta

    def apply_outlet(self, Pout):
        for patch in self.outlet_patches:
            patch.Pout = Pout

    def apply_throttle(self, mdot, Kpid):
        for patch in self.outlet_patches:
            patch.mdot_target = mdot
            patch.Kpid = Kpid

    def update_outlet(self, rf=0.5):
        for patch in self.outlet_patches:
            if patch.mdot_target:
                P_old = patch.Pout + 0.0
                P_new = patch.get_cut().P.mean()
                patch.Pout = rf * P_new + (1.0 - rf) * P_old

    def check_outlet_choke(self):
        for patch in self.outlet_patches:
            if patch.mdot_target:
                C = patch.get_cut()
                Cm = C.mix_out()[0]
                if Cm.Mam > 1.0:
                    logger.iter(
                        f"Warning: outlet Mam={Cm.Mam:.3f} is choked; this can affect"
                        " mass flow continuity."
                    )

    def get_wall_nodes(self):
        """Unstructured coordinates of all points on walls."""

        # Loop over blocks
        xrrt_wall_block = []
        for block in self:
            # Assemble unstructured wall coordinates for this block
            _, _, _, is_wall = block.get_wall()
            xrtbw = block.xrt[:, is_wall.astype(bool)].reshape(3, -1)

            # Replicate by +/- a pitch
            pitch = 2.0 * np.pi / float(block.Nb)
            dxrt = np.zeros_like(xrtbw)
            dxrt[2] = pitch
            xrtbw_rep = np.concatenate((xrtbw - dxrt, xrtbw, xrtbw + dxrt), axis=1)

            # Convert to rt
            xrrtbw = xrtbw_rep + 0.0
            xrrtbw[2] *= xrrtbw[1]

            xrrt_wall_block.append(xrrtbw)

        # Join all blocks together
        xrrt_wall = np.concatenate(xrrt_wall_block, axis=1)

        return xrrt_wall

    def calculate_wall_distance(self):
        """Get distance to nearest wall node for all grid points."""

        # Initialise a kdtree of wall points
        kdtree = KDTree(self.get_wall_nodes().T)

        # Loop over blocks
        for block in self:
            # wmax = 2.0 * np.pi * block.r.max() / block.Nb * 0.1

            block.w = kdtree.query(
                block.flatten().xrrt.T,
                workers=-1,
            )[0].reshape(block.shape)

    def apply_guess_uniform(self, F):
        for b in self:
            b.apply_guess_uniform(F)

    def apply_guess_meridional(self, Fg):
        """Apply meridional guess from a mean-line object."""

        # Ensure the guess flow field is sane
        Fg.check_flow()

        # Initialise a kdtree of guess points
        xrgT = Fg.xr.T
        kdtree = KDTree(xrgT)

        # Loop over all blocks
        for block in self:
            # Copy fluid props etc.
            block._metadata.update(Fg._metadata)

            # Find indices of nearest guess point to all block points
            xri = block.flatten().xr.T
            ind_nearest = kdtree.query(
                xri,
                workers=-1,
            )[1]

            # Set thermodynamic properties
            rob = Fg.rho[ind_nearest].reshape(block.shape)
            ub = Fg.u[ind_nearest].reshape(block.shape)
            block.set_rho_u(rob, ub)

            # Set velocities
            block.Vxrt = Fg.Vxrt[:, ind_nearest].reshape(block.Vxrt.shape)

            block.mu_turb = np.full_like(block.mu_turb, np.mean(Fg.mu))

    def apply_guess_3d(self, g):
        for block, block_other in zip(self, g):
            block.interp_from(block_other)

    def run(self, settings, machine):
        """Run a solver on the grid, prescribing some settings."""

        # Obtain a solver configuration object of the correct type
        settings_copy = settings.copy()
        solver_type = settings_copy.pop("type")
        solver = importlib.import_module(f".{solver_type}", package="turbigen.solvers")
        solver_conf = solver.Config(**settings_copy)

        # If soft start then run the robust config first
        if solver_conf.soft_start:
            logger.info("Soft start...")
            solver_conf_robust = solver_conf._robust()
            solver.run(self, solver_conf_robust, machine)
            self.update_outlet()
            logger.info("Accurate solution...")

        return solver.run(self, solver_conf, machine)

    def unstructured_cut_marching(self, xr_cut):
        """Take an unstructured cut using marching cubes."""

        # Loop over blocks
        triangles = []
        last_block = None
        for block in self:
            # Evaluate signed distance for all points in the block
            dist = turbigen.util.signed_distance(xr_cut, block.xr)

            # Get triangles for this block
            triangles_block = turbigen.marching_cubes.marching_cubes(block._data, dist)

            # Add triangles to the list
            if triangles_block is not None:
                triangles.append(triangles_block)
                last_block = block

        # Join all blocks into one array
        if triangles:
            triangles = np.concatenate(triangles).transpose(2, 0, 1)

            out = last_block.empty(shape=triangles.shape[1:])
            out._data[:] = triangles
            # Ensure Omega is exactly uniform
            out.Omega[:] = np.mean(out.Omega)

            return out

    def cut_blade_sides(self, offset=0):
        """Nested list of pressure/suction side cuts in each row."""

        # Assuming a H-mesh
        cuts = []

        for i in range(self.nrow):
            # Check periodics first
            ile = None
            ite = None
            for patch in self.periodic_patches:
                this_row = patch.block in self.row_blocks[i]
                same_block = patch.match.block == patch.block
                spans_j = np.allclose(patch.ijk_limits[1], [0, -1])
                spans_i = np.allclose(patch.ijk_limits[0], [0, -1])
                k0 = np.allclose(patch.ijk_limits[2], [0, 0])
                if same_block and spans_j and k0 and not spans_i and this_row:
                    if patch.ijk_limits[0, 0] == 0:
                        ile = patch.ijk_limits[0, 1]
                    elif patch.ijk_limits[0, 1] == -1:
                        ite = patch.ijk_limits[0, 0]

            # Now check cusps
            for patch in self.cusp_patches + self.inviscid_patches:
                this_row = patch.block in self.row_blocks[i]
                if this_row:
                    ite = patch.ijk_limits[0, 0]

            if not ile or not ite:
                cuts.append(None)
                continue

            # Get both sides
            Ck0 = self[i][ile : (ite + 1), :, None, 0 + offset].copy()
            Cnk = self[i][ile : (ite + 1), :, None, -1 - offset].copy()
            C = [Ck0, Cnk]

            # Find the side at highest theta
            iu = np.argmax([Ci.t.max() for Ci in C])
            C[iu].t -= self[i].pitch

            cuts.append(C)

        return cuts

    @property
    def is_hmesh(self):
        return len(self) == len(self.row_blocks)

    def cut_blade_surfs(self, offset=0):
        """O-mesh style cuts for the blades in each row."""

        surfs = []

        if self.is_hmesh:
            row_sides = self.cut_blade_sides(offset)
            for sides in row_sides:
                if sides is None:
                    surfs.append(None)
                else:
                    cut_now = turbigen.base.concatenate(
                        (sides[0].flip(axis=0), sides[1][1:, ...]), axis=0
                    )
                    surfs.append([cut_now])
        else:
            for row_block in self.row_blocks:
                # Preallocate list for this row
                surfs.append([])

                # Determine full span nj as the modal nj in this row
                nj_vals, nj_counts = np.unique(
                    [b.shape[1] for b in row_block], return_counts=True
                )
                nj = nj_vals[np.argmax(nj_counts)]

                # Loop over blocks and find o-meshes
                for b in row_block:
                    if (
                        np.allclose(b[0, :, 0].xrt, b[-1, :, 0].xrt)
                        and b.shape[1] == nj
                    ):
                        surfs[-1].append(b[:, :, None, offset])

        return surfs

    def cut_mid_pitch(self):
        # Assumes H-mesh
        k = self[0].shape[2] // 2
        return [b[:, :, k].squeeze() for b in self]

    def spf_index(self, spf):
        return np.argmin(np.abs(self[0].spf[1, :, 1] - spf))

    def cut_span_unstructured(self, xr):
        """Take an unstructured meridional cut, e.g. at constant span."""
        bcut = []
        for row in self.row_blocks:
            brow = []
            for block in row:
                if bnow := block.meridional_slice(xr):
                    brow.append(bnow.squeeze().triangulate())
            bcut.append(turbigen.base.concatenate(brow))
        return bcut

    def cut_span(self, spf):
        # Find j index nearest to requested span fraction
        jspf = self.spf_index(spf)
        nj = self[0].shape[1]
        logger.debug(f"Cutting at spf={spf}: jspf={jspf}, nj={nj}")

        bcut = []
        for block in self:
            njb = block.shape[1]
            if njb < nj:
                # This is a tip block
                jtip = jspf - (nj - njb)
                if jtip >= 0:
                    logger.debug(f"Tip block jcut={jtip}")
                    bcut.append(block[:, jtip, :])
                else:
                    logger.debug("Skipping tip block")
            else:
                # This is a normal block
                bcut.append(block[:, jspf, :])
                logger.debug(f"Main block jcut={jspf}")
        return bcut

    def partition(self, N):
        nb = len(self)

        if N == 1:
            procids = [0 for _ in self]
        elif N == nb:
            procids = list(range(0, nb))
        elif N > nb:
            raise Exception(f"Cannot load balance {nb} blocks into {N} partitions!")
        else:
            # Lazy import
            import metis

            # Assemble block sizes and adjacencyectivity
            vertex_weights = (
                np.round(np.array([b.size for b in self]) / self.ncell * 100)
                .astype(int)
                .tolist()
            )
            adjacency = []
            logger.debug("Weights and adjacency for each block:")
            for ib, block in enumerate(self):
                adjacency_now = []
                for patch in block.patches:
                    if isinstance(patch, PeriodicPatch) or isinstance(
                        patch, PorousPatch
                    ):
                        if patch.match:
                            nxblock = patch.match.block
                            nxblockid = self._blocks.index(nxblock)
                            if nxblockid not in adjacency_now:
                                adjacency_now.append(nxblockid)
                adjacency.append(tuple(adjacency_now))
                logger.debug(f"    {vertex_weights[ib]} {adjacency[-1]}")
            G = metis.adjlist_to_metis(adjacency, vertex_weights)
            _, procids = metis.part_graph(G, N)
            procids = np.array(procids)

            # Metis may produce fewer partitions than requested, which results
            # in skipped procids. Shift the procids first so there are no gaps.
            procids_unique = np.unique(procids)
            procids_missing = np.setdiff1d(range(N), procids_unique)
            for pmiss in procids_missing:
                procids[procids >= pmiss] -= 1
            npart = procids.max() + 1

            if not npart == N:
                logger.debug(
                    f"Metis produced {npart} partitions, fewer than target {N}"
                )
                logger.debug(f"Original procids {procids}")

                # Find indices of repeated procids, i.e. those that are not
                # required to form the unique array
                ind_repeat = []
                proc_used = []
                for iiproc, iproc in enumerate(procids):
                    if iproc in proc_used:
                        ind_repeat.append(iiproc)
                    else:
                        proc_used.append(iproc)

                # ind_repeat = np.setdiff1d(range(N), ind_unique)
                logger.debug(f"Indexes of repeats {ind_repeat}")
                procids_add = list(range(npart - 1, N))
                logger.debug(f"procids to be added {procids_add}")

                # Loop over the left-over procids and reassign to repeated procids
                for iipart, ipart in enumerate(procids_add):
                    procids[ind_repeat[iipart]] = ipart
                logger.debug(f"Corrected procids {procids}")

            assert len(np.unique(procids)) == N
            assert (procids >= 0).all()
            assert len(procids) == nb
            assert procids.max() == (N - 1)

            # Sum cells per partition
            ncell_part = np.zeros(N)
            for ib, b in enumerate(self):
                ncell_part[procids[ib]] += b.size
            logger.info(
                "Load-balanced cells per GPU/10^6: "
                f"{np.array2string(ncell_part / 1e6, precision=2)}"
            )
            assert (ncell_part > 0.0).all()

        return procids


class Patch:
    """Base class for all patches."""

    @staticmethod
    def _get_indices(ijk):
        if ijk is None:
            st, en = (0, -1)
        else:
            try:
                st, en = ijk
            except TypeError:
                st = ijk
                en = ijk + 1
        return st, en

    def __repr__(self):
        return f"{self.__class__}(i={self.ijk_limits[0]}, j={self.ijk_limits[1]}, k={self.ijk_limits[2]})"

    def __init__(self, i=None, j=None, k=None, label=None):
        """Select a subset of a block by indices."""

        self.label = label

        # ijk limits are INCLUSIVE
        # because we cannot use an integer to range slice including last element
        self.ijk_limits = np.zeros((3, 2), dtype=int)
        for n, ind in enumerate([i, j, k]):
            if ind is None:
                self.ijk_limits[n] = (0, -1)
            else:
                try:
                    self.ijk_limits[n] = ind
                except TypeError:
                    self.ijk_limits[n] = (ind, ind)

        # Disallow volume patches
        assert np.sum(np.diff(self.ijk_limits) == 0) >= 1

        self.block = None

        self.idir = None
        self.jdir = None
        self.kdir = None

    @property
    def ijkdir(self):
        return [self.idir, self.jdir, self.kdir]

    @ijkdir.setter
    def ijkdir(self, value):
        self.idir, self.jdir, self.kdir = value

    @property
    def cdir(self):
        return np.where(np.diff(self.ijk_limits, axis=1) == 0)[0][0]

    def get_slice(self, offset=0, trim=0):
        # Convert inclusive start/end to indices for range slice
        sl = []
        for lim in self.ijk_limits:
            lim_now = lim.copy()

            if np.ptp(lim) == 0:
                if lim[0] == 0:
                    lim_now += offset
                else:
                    lim_now -= offset
            else:
                lim_now[0] += trim
                lim_now[1] -= trim

            if (lim_now == -1).any():
                sl.append(slice(lim_now[0], None))
            else:
                sl.append(slice(lim_now[0], lim_now[1] + 1))
        return tuple(sl)

    def get_npts(self):
        if hasattr(self, "_npts"):
            return self._npts

        nijk = np.tile(np.reshape(self.block.shape, (3, 1)), (1, 2))
        ijk_lim = self.ijk_limits.copy()
        ijk_lim[ijk_lim < 0] = (nijk + ijk_lim)[ijk_lim < 0]
        ijk_lim[:, 1] += 1
        self._npts = np.prod(np.diff(ijk_lim, axis=1))
        return self._npts

    def get_indices(self, perm=None, flip=()):
        # Return ijk indices over the patch
        nijk = np.tile(np.reshape(self.block.shape, (3, 1)), (1, 2))
        ijk_lim = self.ijk_limits.copy()
        ijk_lim[ijk_lim < 0] = (nijk + ijk_lim)[ijk_lim < 0]
        ijk_lim[:, 1] += 1
        ijkv = [list(range(*ijkl)) for ijkl in ijk_lim]
        ijk = np.stack(np.meshgrid(*ijkv, indexing="ij"))
        if perm is not None:
            ijk = np.stack([np.flip(ijkn, axis=flip).transpose(perm) for ijkn in ijk])
        return ijk

    @property
    def shape(self):
        return self.get_indices().shape[1:]

    def get_flat_indices(self, order="C", perm=None, flip=None):
        # Return indices of all points on patch into self.block.ravel
        ijk = self.get_indices()
        shape = self.block.shape
        ind = np.ravel_multi_index(ijk, shape, order=order)
        if perm is not None:
            ind = np.flip(ind, axis=flip).transpose(perm)
        return ind.reshape(-1)

    def get_cut(self, offset=0):
        return self.block[self.get_slice(offset)]

    def __str__(self):
        return (
            f"{self.__class__.__name__}(i={self.ijk_limits[0]}, j={self.ijk_limits[1]},"
            f" k={self.ijk_limits[2]}, label={self.label}, block={self.block})"
        )

    def is_point(self):
        return (np.ptp(self.ijk_limits, axis=1) == 0).all()


class PeriodicPatch(Patch):
    """Node-to-node matching periodicity."""

    match = None
    cartesian = False

    def check_match(self, other, rtol=1e-4):
        is_match = _get_patch_connectivity(self, other, corners_only=False, rtol=rtol)
        if is_match:
            Omega = [P.block.Omega.mean() for P in [self, other]]
            if not np.isnan(Omega).any() and not np.isclose(*Omega):
                raise Exception(
                    f"Reference frame angular velocites {Omega} does not match across {self} and {other}"
                )
            return True
        else:
            return False

    def get_match_perm_flip(self):
        # We need to establise a permutation order and set of flips that will
        # transform the other coordinates to our indexing
        perm = np.zeros(3, dtype=int)
        flip = np.zeros(3, dtype=int)

        ijkdir_match = self.match.ijkdir
        ijkdir = self.ijkdir

        for n in range(3):
            if ijkdir[n] == MatchDir.IPLUS:
                perm[n] = 0
                flip[n] = 0
            elif ijkdir[n] == MatchDir.JPLUS:
                perm[n] = 1
                flip[n] = 0
            elif ijkdir[n] == MatchDir.KPLUS:
                perm[n] = 2
                flip[n] = 0
            elif ijkdir[n] == MatchDir.IMINUS:
                perm[n] = 0
                flip[n] = 1
            elif ijkdir[n] == MatchDir.JMINUS:
                perm[n] = 1
                flip[n] = 1
            elif ijkdir[n] == MatchDir.KMINUS:
                perm[n] = 2
                flip[n] = 1
            elif ijkdir[n] == MatchDir.CONST:
                # We must put the const dirn of the next patch here
                for m in range(3):
                    if ijkdir_match[m] == MatchDir.CONST:
                        perm[n] = m
                flip[n] = 0

        flip = np.where(flip)[0]

        return perm, flip

    def get_match_cut(self, offset=0):
        Cnx = self.match.get_cut(offset)
        perm, flip = self.get_match_perm_flip()
        Cnx._data = np.flip(Cnx._data.transpose(perm), axis=flip).copy()

        return Cnx


class PorousPatch(PeriodicPatch):
    """Node-to-node matching periodicity with pressure loss."""

    porous_fac_loss = None

    def check_match(self, other):
        match_coords = super().check_match(other)
        try:
            match_porous = np.isclose(self.porous_fac_loss, other.porous_fac_loss)
        except (AttributeError, TypeError):
            match_porous = False
        return match_coords and match_porous


class MixingPatch(Patch):
    """Connect two reference frames with a mixing plane."""

    match = None
    slide = False

    def check_match(self, other, rtol=1e-5):
        # Slice both the patches
        C = [self.get_cut(), other.get_cut()]

        # Reference length to set meridional tolerance
        Lref = np.max((np.ptp(C[0].x), np.ptp(C[0].r)))

        # Check these cuts satisfy the conditions
        try:
            assert np.diff(self.ijk_limits[0]) == 0
            assert np.diff(other.ijk_limits[0]) == 0
            for Ci in C:
                assert (np.ptp(Ci.xr, axis=-1) < Lref * rtol).all()
        except AssertionError:
            # raise Exception(f"Invalid mixing patch indices {self} {other}")
            return False

        # Get coordinates of hub and casing on each patch
        # xr has dimensions: [which patch, x or r, hub/casing]
        xr = np.stack([Ci.xr[:, :, (0, -1), :].mean(axis=-1).squeeze() for Ci in C])

        nj = np.array([Ci.shape[1] for Ci in C], dtype=int)

        err = np.abs(np.diff(xr, axis=0).squeeze())
        err_rel = err / Lref

        if err_rel.max() < rtol:
            self.match = other
            other.match = self

            if np.ptp(nj) == 0:
                dt = np.stack(
                    [np.diff(Ci.t[:, :, (0, -1)], axis=-1).squeeze() for Ci in C]
                )
                if np.allclose(dt[0], dt[1]):
                    self.slide = True
                    other.slide = True

        else:
            return False


class InletPatch(Patch):
    state = None
    rfin = 0.5
    force = False
    amplitude = 0.0
    phase = 0.0
    rho_store = None
    harmonics = (1,)
    force_factor = None

    def get_unsteady_multipliers(self, freq, nstep_cycle, ncycle):
        """Given time discretisation, generate unsteady bcond factors.

        Parameters
        ----------
        freq : float
            Fundamental frequency of the unsteady forcing.
        nstep_cycle : int
            Number of time steps per fundamental period.
        ncycle : int
            Number of fundamental periods to simulate.

        Returns
        -------
        fac_ho: (nt,) array
            Factor multiplying mean inlet stagnation enthalpy at each time step.
        fac_Po: (nt,) array
            Factor multiplying mean inlet stagnation pressure at each time step.

        """

        # Lay out a time vector
        nt = nstep_cycle * ncycle
        it = np.arange(nt)
        dt = 1.0 / freq / nstep_cycle
        t = it * dt

        if self.force_factor is not None:
            fac = self.force_factor
            assert np.shape(fac) == (nt,), (
                f"Force factor shape {np.shape(fac)} does not match (nt,)=({nt},)"
            )
            print("Using pre-defined force factor for inlet patch")
        else:
            # Start with a steady unity factor
            fac = np.ones((nt,))

            # Phase offsets for each harmonic
            try:
                len(self.phase)
                phase = self.phase
            except TypeError:
                phase = np.pi * self.harmonics**2 / 2.5338  # For minimum crest factor
                phase += self.phase

            # Add on perturbations for each harmonic
            for n in self.harmonics:
                fac += self.amplitude * np.sin(2.0 * np.pi * freq * n * t + phase)

        # Choose the forcing type
        if self.force == "isentropic":
            ga = self.state.gamma
            fac_Po = fac
            fac_ho = fac_Po ** ((ga - 1.0) / ga)
        elif self.force == "entropic":
            fac_Po = np.ones_like(fac)
            fac_ho = fac
        else:
            raise Exception(f"Unknown inlet forcing type {self.force}")

        return fac_ho, fac_Po

    def set_profile(self, spf, profiles):
        """Apply a radial variation to the inlet profile.

        Parameters
        ----------
        spf : (n,) array
            Span fraction of some radial stations running 0 to 1.
        profiles : (4, n,) array
            Perturbation profiles for each of the four variables:
            [Po/Po_avg, To/To_avg, Alpha, Beta] at each station.

        """

        # Get span fractions for all patch points
        C = self.get_cut()
        rmin = C.r.min()
        rmax = C.r.max()
        spfq = (C.r - rmin) / (rmax - rmin)

        # Interpolate inlet stagnation quantities
        Poq = (np.interp(spfq, spf, profiles[0]) + 1.0) * self.state.P
        Toq = (np.interp(spfq, spf, profiles[1]) + 1.0) * self.state.T
        self.state = self.state.empty(shape=C.shape)
        self.state.set_P_T(Poq, Toq)

        # Flow angles
        self.Alpha = np.interp(spfq, spf, profiles[2]) + self.Alpha
        self.Beta = np.interp(spfq, spf, profiles[3]) + self.Beta


class InviscidPatch(Patch):
    pass


class OutletPatch(Patch):
    Pout = None
    mdot_target = None
    Kpid = None
    force = False
    amplitude = 0.0
    phase = 0.0


class RotatingPatch(Patch):
    Omega = None


class ProbePatch(Patch):
    label = ""
    pass


class CuspPatch(Patch):
    def check_match(self, other, rtol=1e-4):
        # Should be on same block
        if self.block is not other.block:
            return False

        # Should have same shape
        xyz = self.get_cut().xyz
        xyz_other = other.get_cut().xyz
        if not xyz.shape == xyz_other.shape:
            return False

        # Check that the patches are touching
        dxyz = np.abs(xyz - xyz_other)
        Lref = np.max([np.ptp(c) for c in xyz])

        if matched := np.any(dxyz < Lref * rtol):
            self.match = other
            other.match = self

        return matched


class CoolingPatch(Patch):
    cool_mass = 0.0
    cool_pstag = 0.0
    cool_tstag = 0.0
    cool_sangle = 0.0
    cool_xangle = 0.0
    cool_angle_def = 0.0
    cool_type = 0
    cool_mach = np.nan

    def check(self):
        # Complain about negative values
        if self.cool_mass <= 0.0:
            raise Exception(f"{self} has negative cool_mass={self.cool_mass}")
        if self.cool_pstag <= 0.0:
            raise Exception(f"{self} has negative cool_pstag={self.cool_pstag}")
        if self.cool_tstag <= 0.0:
            raise Exception(f"{self} has negative cool_tstag={self.cool_tstag}")
        if self.cool_mach <= 0.0:
            raise Exception(f"{self} has negative cool_mach={self.cool_mach}")

        # Complain about large values
        val_max = 1e8
        if self.cool_mass > val_max:
            raise Exception(f"{self} has suspiciously large cool_mass={self.cool_mass}")
        if self.cool_pstag > val_max:
            raise Exception(
                f"{self} has suspiciously large cool_pstag={self.cool_pstag}"
            )
        if self.cool_tstag > val_max:
            raise Exception(
                f"{self} has suspiciously large cool_tstag={self.cool_tstag}"
            )
        if self.cool_mach > val_max:
            raise Exception(f"{self} has suspiciously large cool_mach={self.cool_mach}")


class NonMatchPatch(Patch):
    match = None

    def check_match(self, other, rtol=1e-4):
        return _get_patch_connectivity(self, other, corners_only=True, rtol=rtol)


# Default is that block edges are walls
# So we want to identify patches that are NOT walls
# But there are two seperate lists:
# 1) For the purpose of wall distance calculation and setting boundary
#    conditions in CFD. This list does not include InviscidWalls, because
#    their wdist=0 and they are impermeable
# 2) For the purpose of wall functions in viscous CFD. This list also
#    includes Inviscid and Cooling patches, which should be treated as
#    impermeable but frictionless
NOT_WALL_WDIST = [
    InletPatch,
    OutletPatch,
    MixingPatch,
    PeriodicPatch,
    PorousPatch,
    ProbePatch,
    NonMatchPatch,
    CuspPatch,
]
NOT_WALL_FRICTION = NOT_WALL_WDIST + [
    InviscidPatch,
    CoolingPatch,
]


def _get_patch_connectivity(patch, other, corners_only=False, rtol=1e-4):
    """Patch attributes describing periodic or mixing connectivity."""

    # Get patches
    p = [patch, other]

    # The patches cannot match if their pitches are different
    pitch = [2.0 * np.pi / pi.block.Nb for pi in p]
    if not np.ptp(pitch) == 0.0:
        return False

    if p[0].get_npts() != p[1].get_npts() and not corners_only:
        # If the number of points is different, they cannot match
        return False

    # and their coordinates and shapes
    xrt = [pi.get_cut().xrt.copy() for pi in p]
    dijk = [xrti.shape[1:] for xrti in xrt]

    # Cope with circumferential offset by taking mod wrt pitch
    for xrti in xrt:
        xrti[2, ...] = np.mod(xrti[2, ...], pitch[0])
        # We need to be careful at the pitch boundaries. For example, if one point
        # is pitch - tol/2 and its matching point is pitch + tol/2 then they
        # *should* match, but will be in error by whole pitch after modulus.
        # So move any points very close to upper pitch boundary back to zero
        xrti[2, ...][xrti[2, ...] / pitch[0] > (1.0 - rtol)] = 0.0

    # We are going to loop over all possible choices for i/j/kdir
    # and return from this function if the coordinates match.
    # Skip iterations if dir=-1 does not match shape or a direction is repeated.
    # TS3 notations for dirs:
    # -1: current patch is on this face
    # 0: matches i on next patch
    # 1: matches j
    # 2: matches k
    # 3: matches -i
    # 4: matches -j
    # 5: matches -k

    # Begin looping
    for idir in range(-1, 6):
        idirm = np.mod(idir, 3)
        # If we have one i point, patch on i face, idir must be -1
        if dijk[0][0] == 1 and not idir == -1:
            continue
        for jdir in range(-1, 6):
            jdirm = np.mod(jdir, 3)
            # If we have one j point, patch on j face, jdir must be -1
            if dijk[0][1] == 1 and not jdir == -1:
                continue
            for kdir in range(-1, 6):
                kdirm = np.mod(kdir, 3)
                # If we have one k point, patch on k face, kdir must be -1
                if dijk[0][2] == 1 and not kdir == -1:
                    continue

                # Make a permutation order that will convert next patch
                # coordinates to same shape as current patch
                order = np.array(
                    [
                        idirm if idir >= 0 else -1,
                        jdirm if jdir >= 0 else -1,
                        kdirm if kdir >= 0 else -1,
                    ]
                )

                # Skip repeated directions - two dirs cannot match to same dir
                # on the next patch
                if not len(np.unique(order)) == 3:
                    continue

                # Choose location for next patch const face
                assert np.sum(order == -1) == 1
                order[order == -1] = np.setdiff1d([0, 1, 2], order)

                # Which axes of next patch need flipping
                dirs = np.array([idir, jdir, kdir])
                flip = np.where(dirs > 2)[0]

                # Add one to dirs array because xrt contains 3 coordinates on
                # first dim, and apply transpose or flips
                xrt_next = np.flip(
                    xrt[1].copy().transpose(np.insert(order + 1, 0, 0)),
                    axis=tuple(flip + 1),
                )

                if corners_only:
                    # For non-matching patches, we only care about corners
                    xrtc1 = xrt_next.squeeze()[:, (0, 0, -1, -1), (0, -1, 0, -1)]
                    xrtc2 = xrt[0].squeeze()[:, (0, 0, -1, -1), (0, -1, 0, -1)]
                    err = np.abs(xrtc1 - xrtc2)
                else:
                    # For fully matching patches, we expect the shapes to be
                    # compatible, and coordinates to be coincident
                    if not xrt_next.shape == xrt[0].shape:
                        continue
                    err = np.abs(xrt_next - xrt[0])

                # Test for coordinate equality
                dxref = np.ptp(xrt_next[0])
                drref = np.ptp(xrt_next[1])
                Lref = np.max((dxref, drref))
                err_rel = np.zeros_like(err)
                err_rel[0] = err[0, :] / Lref
                err_rel[1] = err[1, :] / Lref
                err_rel[2] = err[2, :] / pitch[0]

                # Although the TS User Manual says that -1 implies the constant
                # direction, it seems that 6 is the real convention
                dirs[dirs == -1] = 6
                idir6, jdir6, kdir6 = dirs

                # Only error if more than 1 in 1000 points do not match
                if err_rel.max() < rtol:
                    patch.idir = MatchDir(idir6)
                    patch.jdir = MatchDir(jdir6)
                    patch.kdir = MatchDir(kdir6)

                    patch.match = other

                    return True

    return False


def from_jmesh(blocks, conn_face, state):
    """Extrude a set of 2D blocks and patch them toghether."""

    from jmesh.primitives import EdgeKind

    # Use the reference state to choose fluid model
    if isinstance(state, turbigen.fluid.PerfectState):
        Block = PerfectBlock
    elif isinstance(state, turbigen.fluid.RealState):
        Block = RealBlock

    blocks_out = []
    for b, cf in zip(blocks, conn_face):
        patches = []
        for c in cf:
            if c.e == EdgeKind.i0:
                p = PeriodicPatch(i=0, j=(c.st, c.en))
            elif c.e == EdgeKind.ni:
                p = PeriodicPatch(i=-1, j=(c.st, c.en))
            elif c.e == EdgeKind.j0:
                p = PeriodicPatch(i=(c.st, c.en), j=0)
            elif c.e == EdgeKind.nj:
                p = PeriodicPatch(i=(c.st, c.en), j=-1)
            patches.append(p)

        Nb = np.round(2.0 * np.pi / np.ptp(b[0, 0, :].t)).astype(int)

        bnow = Block.from_coordinates(b.xrt, Nb, patches, label=b.label)
        bnow._metadata.update(state._metadata)
        blocks_out.append(bnow)

    g = Grid(blocks_out)
    g.check_coordinates()
    g.match_patches()

    return g


def from_xyz(xyz, state, Nb, roffset, labels, sector=True, patches=None):
    """Generate a grid object from Cartesian coordinates with face-to-face patching.

    To greatly simplify block connectivity, all periodic boundaries occupy
    entire face and matching subsets of faces is disallowed. This means we can
    start by adding periodic patches on all six faces of every block, match
    them automatically, and then delete mismatched ones.

    Parameters
    ----------
    xyz: list of array (3, ni, nj, nk)
        Cartesian coordinates for each block.
    state: State
        Reference thermodynamic state to set fluid model.
    Nb: int
        Number of blades, setting the circumferential period.
    roffset: float
        Raidus at y=0. If negative, then do not offset but use -roffset as
        reference radius for z->t conversion.
    labels: list of str
    sector: bool
        If True, the mesh is distorted such that a rectangle in the y-z plane
        becomes a sector in the final grid, i.e. rectangle in the r-rt plane.
        Constant z lines correspond to constant theta lines in the final grid.
        If False, the angular coordinates are set to give the true geometry.
        To retain periodic boundaries in the z direction, the sector method must
        be used, but this will distort the geometry. If there is no periodicity
        in the z-direction, then the sector method is not required.


    """

    # Use the reference state to choose fluid model
    if isinstance(state, turbigen.fluid.PerfectState):
        Block = PerfectBlock
    elif isinstance(state, turbigen.fluid.RealState):
        Block = RealBlock

    # Initialise the blocks
    blocks = []
    for i in range(len(xyz)):
        xyzi = xyz[i]
        labi = labels[i]
        if sector:
            xrt = xyzi.copy()
            if roffset > 0.0:
                xrt[1] += roffset
                xrt[2] /= roffset
            else:
                xrt[2] /= -roffset
        else:
            x, y, z = xyzi.copy()
            y += roffset
            r = np.sqrt(y**2 + z**2)
            t = -np.arctan2(y, z) + np.pi / 2
            xrt = np.stack((x, r, t))

        # Periodic patches on all faces
        if patches is None:
            patches_block = (
                PeriodicPatch(i=0),
                PeriodicPatch(i=-1),
                PeriodicPatch(j=0),
                PeriodicPatch(j=-1),
                PeriodicPatch(k=0),
                PeriodicPatch(k=-1),
            )
        elif patches is False:
            patches_block = []
        else:
            patches_block = patches[i]

        # block = Block.from_coordinates(np.flip(xrt, axis=-1), Nb, patches, label=labi)
        block = Block.from_coordinates(xrt, Nb, patches_block, label=labi)
        block._metadata.update(state._metadata)
        blocks.append(block)

    # Initialise the grid
    g = Grid(blocks)

    return g


def write_plot3d(g, fname):
    """Save a multi-block structured grid to plot3d format."""

    with open(fname, "w") as f:
        # Number of blocks
        nb = len(g)
        f.write(f"{nb}\n")

        # Size of all blocks
        for b in g:
            f.write(f"{b.ni} {b.nj} {b.nk}\n")

        # Now write block coords
        for b in g:
            # Flip k so that volumes have correct sign in Pointwise
            xyz = np.flip(b.xyz, axis=-1)
            # Save this array in the correct order
            np.savetxt(
                f, xyz.transpose(0, 3, 2, 1).reshape(-1), newline=" ", fmt="%.12f"
            )
