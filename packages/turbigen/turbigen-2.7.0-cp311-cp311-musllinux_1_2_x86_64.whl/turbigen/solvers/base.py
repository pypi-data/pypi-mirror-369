"""Base class to define solver interface."""

from abc import ABC, abstractmethod
import dataclasses
import numpy as np


class ConvergenceHistory:
    def __init__(self, istep, istep_avg, resid, mdot, state):
        """Store simulation convergence history.

        Parameters
        ----------
        istep: (nlog,) array
            Indices of the logged time steps.
        resid: (nlog,), array
            Iteration residuals for logged time steps.
        mdot: (2, nlog) array
            Inlet and outlet mass flow rates for all time steps.
        state: Fluid size (nlog,)
            Working fluid object to logg thermodynamic properties.

        """
        self.istep = istep
        self.istep_avg = istep_avg
        self.nlog = len(istep)
        self.mdot = mdot
        self.resid = resid
        self.state = state

    def raw_data(self):
        return np.column_stack(
            (self.istep, *self.mdot, self.resid, self.state.rho, self.state.u)
        )

    @property
    def err_mdot(self):
        return self.mdot[1] / self.mdot[0] - 1.0

    def to_dict(self):
        return {
            "istep": self.istep.tolist(),
            "istep_avg": self.istep_avg,
            "mdot": self.mdot.tolist(),
            "resid": self.resid.tolist(),
            "rho": self.state.rho.tolist(),
            "u": self.state.u.tolist(),
        }

    def save(self, fname):
        """Save the convergence history to a file.

        Parameters
        ----------
        fname: str
            Filename to save the data to.

        """
        np.savez_compressed(fname, **self.to_dict())

    @classmethod
    def load(cls, fname, state):
        """Load the convergence history from a file.

        Parameters
        ----------
        fname: str
            Filename to load the data from.

        Returns
        -------
        ConvergenceHistory
            The loaded convergence history object.

        """
        data = np.load(fname)
        nstep = len(data["istep"])
        state = state.empty(shape=(2, nstep)).set_rho_u(data["rho"], data["u"])
        return cls(
            istep=data["istep"],
            istep_avg=data["istep_avg"],
            resid=data["resid"],
            mdot=data["mdot"],
            state=state,
        )


@dataclasses.dataclass
class BaseSolver(ABC):
    """
    Flow solvers
    ============

    Once the machine geometry is generated, and the fluid domain discretised
    using a suitable mesh, the next step is to predict the flow field and hence
    aerodynamic performance using a computational fluid dynamics (CFD) solver.

    :program:`turbigen` is solver-agnostic: either the built in CFD solver or
    an interface to an external code can be used for flow field prediction;
    pre- and post-processing is done in common, native Python code. Adding a new
    external solver only requires implementing functions to save input files,
    execute the solver, and then read back the output file into
    :program:`turbigen`'s internal data structures. See the
    :ref:`solver-custom` section for more details.

    Select which solver to use by setting the `type` key under the `solver` section
    of the configuration file. Valid choices are:

    - `ember`: :ref:`Enhanced Multi-Block solvER<solver-ember>`
    - `ts3`: :ref:`solver-ts3`
    - `ts4`: :ref:`solver-ts4`

    Each CFD solver accepts different configuration options. Solver options and
    their default values are listed below; override the defaults using the
    `solver` section of the configuration file. For example, to use the
    built-in :program:`ember` solver, with a reduced damping factor:

    .. code-block:: yaml

        solver:
          type: ember
          n_step: 1000  # Case-dependent
          n_step_avg: 250  # Typically ~1/4 of n_step
          damping_factor: 10.  # Override default value of 25.0


    Every solver accepts a `soft_start` flag, which runs a precursor simulation
    with more robust settings before running the actual simulation. Enabling
    this option should be the first step when a simulation fails to converge.
    If a design does not run with `soft_start` enabled, this suggests the mesh
    is poor quality, or the aerodynamic design itself is not feasible.

    xxx

    .. _solver-custom:

    Custom solvers
    --------------

    To add a new solver, create a new Python module in the user-defined plugin
    directory, say `./plug/my_solver.py` and set `plugdir: ./plug` in the
    configuration file. Write a new class that inherits from
    :class:`turbigen.solvers.base.BaseSolver`  and implement the following
    methods:

    - :meth:`run`: Run the solver on the given grid and machine geometry.
    - :meth:`robust`: Create a copy of the config with more robust settings.
    - :meth:`restart`: Create a copy of the config with settings to restart from converged solution.

    :class:`turbigen.solvers.base.BaseSolver` is a dataclass, so has an automatic constructor and
    useful built-in methods. The configuration file `solver` section
    is fed into the constructor as keyword arguments and becomes attributes of
    the instance.

    """

    soft_start: bool = False
    """Run a robust initial guess solution first, then restart."""

    convergence: ConvergenceHistory = None
    """Storage for convergence history."""

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    @abstractmethod
    def robust(self):
        """Create a copy of the config with more robust settings."""
        raise NotImplementedError()

    @abstractmethod
    def restart(self):
        """Create a copy of the config with settings to restart from converged soln."""
        raise NotImplementedError()

    @abstractmethod
    def run(self, grid, machine, workdir):
        """Run the solver on the given grid and machine geometry.

        Parameters
        ----------
        grid:
            Grid object.
        machine:
            Machine geometry object.

        Returns
        -------
        conv: ConvergenceHistory
            The time-marching convergence history of the flow solution.

        """
        raise NotImplementedError

    def to_dict(self):
        # Built in dataclasses.asdict() gets us most of way
        d = dataclasses.asdict(self)

        # Convert the convergence history to a dictionary
        if self.convergence is not None:
            d["convergence"] = self.convergence.to_dict()

        return d
