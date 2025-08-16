import numpy as np
import turbigen.autogrid
import os
import turbigen.util
import turbigen.mesh
import dataclasses

logger = turbigen.util.make_logger()


@dataclasses.dataclass
class OH(turbigen.mesh.Mesher):
    """Contains all configuration options with default values."""

    _name = "OH mesh"

    spf_ref: float = 0.5
    """Set blade-to-blade mesh parameters based on geometry at this span fraction."""

    nj: tuple = ()
    """Number of spanwise grid points."""

    remote_host: str = ""
    """Remote host on which AutoGrid server is running."""

    span_interpolation: float = 2.0
    """Spanwise % spacing between optimisations of the mesh, interpolate between."""

    via_host: str = ""
    """Jump host for SSH connection to the AutoGrid server."""

    remote_workdir: str = ""
    """File on remote host to append our queued meshing jobs."""

    workdir = ""

    gbcs_path: str = ""
    """Location of pre-made mesh, or 'reuse' to take from `workdir/mesh.{g,bcs}`."""

    ni_inlet: int = 65
    """Number of streamwise points in inlet."""

    ni_outlet: int = 65
    """Number of streamwise points in outlet."""

    resolution_factor: float = 1.0

    fix_h_inlet: bool = False
    fix_h_outlet: bool = False

    wake_control: bool = False
    wake_deviation: float = 0.0

    match_mixing: bool = False

    skewness_control: int = 0
    orthogonality_control: float = 0.5
    nsmooth: int = 100
    nsmooth_multigrid: int = 100
    blade_streamwise_weight: float = 2.0

    untwist_outlet: bool = False
    untwist_inlet: bool = False
    untwist_inlet_extent: float = 0.5

    round_TE: bool = True

    const_cells_frac: float = 0.45

    nj_tip: int = 25
    nk_gap: int = 9
    const_cells_frac: float = 0.45

    frac_inlet: float = 0.9
    frac_outlet: float = 0.15
    relax_outlet: int = 1
    relax_inlet: int = 1

    R_fillet_hub: float = 0.0
    R_fillet_shd: float = 0.0
    nj_fillet_hub: float = 17
    nj_fillet_shd: float = 17
    is_butterfly: bool = False
    nk_fillet: int = 9

    ncell_target: float = 0.0

    inlet_bulb: str = ""

    def __init__(self, **kwargs):
        """Initialise a configuration, overriding defaults with keyword arguments."""

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_autogrid_dict(self, chi_ref, dhub, dcas, dsurf, splitter):
        stagger_topo = _get_stagger_topology(chi_ref)
        nrow = len(stagger_topo)

        if not self.nj:
            nj = [81 for _ in range(nrow)]
        else:
            nj = self.nj

        if self.via_host == "":
            via = None
        else:
            via = self.via_host

        # Default configs
        return {
            "verbose": True,
            "is_cascade": False,
            "match_mixing": self.match_mixing,
            "fix_h_inlet": self.fix_h_inlet,
            "fix_h_outlet": self.fix_h_outlet,
            "nrow": nrow,
            "inlet_bulb": self.inlet_bulb,
            "nx_up": self.ni_inlet,
            "nx_dn": self.ni_outlet,
            "ncell_target": self.ncell_target,
            "nx_mix": 9,
            "dr_hub": dhub,
            "dr_cas": dcas,
            "nr": nj,
            "round_TE": self.round_TE,
            "drt_row": dsurf.tolist(),
            "stagger": stagger_topo,
            "const_cells_pc": self.const_cells_frac * 100.0,
            "nr_tip_gap": self.nj_tip,
            "relax_inlet": self.relax_inlet,
            "relax_outlet": self.relax_outlet,
            "ER_boundary_layer": 1.1,
            "ER_blade_surf": 1.2,
            "n_te": 17,
            "frac_up": self.frac_inlet,
            "frac_dn": self.frac_outlet,
            "prefix": "mesh",
            "spf_ref": self.spf_ref,
            "remote": self.remote_host,
            "via": via,
            "remote_workdir": self.remote_workdir,
            "nsmooth": self.nsmooth,
            "nsmooth_multigrid": self.nsmooth_multigrid,
            "orthogonality_control": self.orthogonality_control,
            "skewness_control": self.skewness_control,
            "wake_control": self.wake_control,
            "wake_deviation": self.wake_deviation,
            "untwist_outlet": self.untwist_outlet,
            "untwist_inlet": self.untwist_inlet,
            "untwist_inlet_extent": int(self.untwist_inlet_extent * 100),
            "splitter": splitter,
            "span_interp": self.span_interpolation,
            "blade_streamwise_weight": self.blade_streamwise_weight,
            "R_fillet_hub": self.R_fillet_hub,
            "R_fillet_shd": self.R_fillet_shd,
            "nk_fillet": self.nk_fillet,
            "nk_gap": self.nk_gap,
            "nj_fillet_hub": self.nj_fillet_hub,
            "nj_fillet_shd": self.nj_fillet_shd,
            "is_butterfly": self.is_butterfly,
        }

    def make_grid(self, workdir, machine, dhub, dcas, dsurf, Omega):
        logger.info("Generating OH-mesh...")

        # dsurf = np.mean(dsurf, axis=0)
        mesh_config = self

        # File paths
        if workdir == "":
            raise Exception("workdir for OH meshing not set")
        output_stem = os.path.join(os.path.abspath(workdir), "mesh")

        if (mesh_config.gbcs_path == "reuse") or (
            os.path.exists(os.path.join(output_stem + ".g"))
        ):
            logger.info(f"Reusing existing {output_stem}." + r"{g,bcs}")

        elif mesh_config.gbcs_path == "":
            chi_ref = []
            is_unbladed = []
            for bld in machine.bld:
                chi_ref.append(bld[0].get_chi(mesh_config.spf_ref))
                is_unbladed.append(0)
                # else:
                #     chi_ref.append(np.zeros((2,)))
                #     is_unbladed.append(1)
            chi_ref = np.concatenate(chi_ref)

            logger.info("Making a new mesh.")
            splitter = []
            if machine.split:
                for irow, splt in enumerate(machine.split):
                    if splt:
                        splitter.append(irow)
            else:
                splitter = []
            ag_config = mesh_config.to_autogrid_dict(
                chi_ref, dhub, dcas, dsurf, splitter
            )
            ag_config["Nb"] = machine.Nb.tolist()
            ag_config["tip"] = machine.tip.tolist()
            success = turbigen.autogrid.autogrid.make_mesh(
                output_stem, *machine.get_coords(), Omega, ag_config
            )

            if not success:
                raise Exception("Meshing failed.")

        else:
            output_stem = os.path.abspath(mesh_config.gbcs_path)
            logger.info(f"Loading {output_stem}." + r"{g,bcs}")

        bcs_path = output_stem + ".bcs"
        g_path = output_stem + ".g"

        g = turbigen.autogrid.reader.read(g_path, bcs_path)

        if rf := mesh_config.resolution_factor:
            for b in g:
                b.subsample(rf)
            g.match_patches()

        return g


def _get_stagger_topology(Al):
    nAl = len(Al)
    assert np.mod(nAl, 2) == 0
    Nrow = nAl // 2

    # Threshold for 'normal' angles
    Al[np.abs(Al) < 45.0] = 0.0

    return [
        np.sign(Al[(irow * 2, irow * 2 + 1),]).astype(int).tolist()
        for irow in range(Nrow)
    ]
