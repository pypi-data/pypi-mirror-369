from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from mosaic_materials.constraints.total_scattering import (
    StructureFactorConstraint,
    TotalRDFConstraint,
)

if TYPE_CHECKING:
    from mosaic_materials.engine import MCEngine

# === Neutron scattering lengths in femtometers (fm) ===

_fm_to_m = 1e-15
""" Conversion factor from femtometers to angstroms. """

_neutron_scattering_lengths: dict[str, float] = {
    "H1": -3.7406,  # fm
    "H2": 6.6710,   # fm
    "Zn": 5.6800,   # fm
    "C": 6.6460,    # fm
    "N": 9.3600,    # fm
}


# === Neutron scattering constraint ===

class NeutronStructureFactorConstraint(StructureFactorConstraint):
    """
    Total neutron scattering structure factor constraint.

    Uses:
      S_ij(Q) = 4πρ₀ b_i b_j ∫ [g_ij(r)-1] (r sin(Qr)/Q) dr
    """

    default_minimise_differences: bool = False

    def __init__(
        self,
        name: str,
        q_exp: npt.NDArray[np.floating],
        fq_exp: npt.NDArray[np.floating],
        rdf_constraint_name: str = "c_rdf",
        sigma: npt.NDArray[np.floating] | float = 1.0,
        weight: float = 1.0,
        scattering_lengths: dict[str, float] | None = None,
        deuteration_ratio: float = 1.0,
        multiply_by_q: bool = False,
        minimise_differences: bool = False,
    ):
        super().__init__(
            name,
            q_exp,
            fq_exp,
            rdf_constraint_name,
            sigma,
            weight,
            multiply_by_q,
            minimise_differences,
        )
        self._b_map = dict(scattering_lengths or _neutron_scattering_lengths)
        self.deuteration_ratio = deuteration_ratio

    def install(self, engine: MCEngine) -> None:
        """
        Nothing to install in LAMMPS itself. We compute required constants.
        """

        assert engine.system is not None, (
            "System must be set before installing "
            "NeutronStructureFactorConstraint."
        )

        super().install(engine)

        self._b_map["H"] = (
            self._b_map["H1"] * (1 - self.deuteration_ratio)
            + self._b_map["H2"] * self.deuteration_ratio
        )

        prefac = 4 * np.pi * 1e28

        self._constants = np.array(
            [
                prefac
                * (2 - int(i == j))
                * self._b_map[i]
                * self._b_map[j]
                * _fm_to_m
                * _fm_to_m
                * engine.system.composition.atomic_fraction(i)
                * engine.system.composition.atomic_fraction(j)
                for i, j in engine.system.element_pairs
            ]
        )

class NeutronTotalRDFConstraint(TotalRDFConstraint):
    """ Total radial distribution constraint for neutron scattering data. """

    def __init__(
        self,
        name: str,
        r_exp: npt.NDArray[np.floating],
        gr_exp: npt.NDArray[np.floating],
        rdf_constraint_name: str = "c_rdf",
        sigma: np.ndarray | float = 1.0,
        weight: float = 1.0,
        scattering_lengths: dict[str, float] | None = None,
        deuteration_ratio: float = 0.0,
        minimise_differences: bool = False,
    ):
        super().__init__(
            name=name,
            r_exp=r_exp,
            gr_exp=gr_exp,
            rdf_constraint_name=rdf_constraint_name,
            sigma=sigma,
            weight=weight,
            minimise_differences=minimise_differences,
        )
        self._b_map = dict(scattering_lengths or _neutron_scattering_lengths)
        self.deuteration_ratio = deuteration_ratio
    
    def install(self, engine: MCEngine) -> None:
        """ Install the neutron scattering constraint. """

        assert engine.system is not None, (
            "System must be set before installing "
            "NeutronTotalRadialDistributionConstraint."
        )

        super().install(engine)

        self._b_map["H"] = (
            self._b_map["H1"] * (1 - self.deuteration_ratio)
            + self._b_map["H2"] * self.deuteration_ratio
        )

        self._constants = np.array(
            [
                (2 - int(i == j))
                * self._b_map[i]
                * self._b_map[j]
                * _fm_to_m
                * _fm_to_m
                * 1e28
                * engine.system.composition.atomic_fraction(i)
                * engine.system.composition.atomic_fraction(j)
                for i, j in engine.system.element_pairs
            ]
        )