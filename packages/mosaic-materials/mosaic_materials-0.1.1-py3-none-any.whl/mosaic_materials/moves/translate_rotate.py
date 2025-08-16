import numpy as np

from mosaic_materials.moves.move import BaseMove
from mosaic_materials.moves.utils import _rotate_cluster_inplace, random_vector


class TranslateRotateMove(BaseMove):
    """
    Rigid-body rotation about the cluster COM followed by a translation.

    The proposal is symmetric if:
      - theta ~ Uniform(-max_angle, +max_angle)
      - disp direction ~ uniform on S^2
      - disp length ~ symmetric about 0 once combined with direction.
    """

    tuning_params = ("max_disp", "max_angle")

    def __init__(
        self,
        engine,
        atom_ids: list[int],
        max_disp: float,
        max_angle: float,
        pivot: str = "com",
        rng: np.random.Generator | None = None,
    ):
        super().__init__(engine, atom_ids, rng)
        self.max_disp = max_disp
        self.max_angle = max_angle
        self.pivot = pivot
        self.weights = (
            self.system.masses_for(self.atom_ids)
            if self.pivot == "com"
            else np.ones(len(self.atom_ids), dtype=np.float64)
        )

        # scratch buffers to avoid reallocations
        self._pos_rot = self.pos_old.copy()
        self._img_rot = self.img_old.copy()

    def propose(self) -> None:
        L = self.system.cell_lengths

        # --- draw rotation: random axis & symmetric angle ---
        axis = random_vector(self.rng.random(), self.rng.random())
        theta = np.deg2rad(self.rng.uniform(-self.max_angle, self.max_angle))

        # --- rotate about COM (in-place into scratch buffers) ---
        _rotate_cluster_inplace(
            self.pos_old,
            self.img_old,
            L,
            axis,
            theta,
            self.weights,
            self.pos_new,
            self.img_new,
        )

        # --- draw translation: random direction & length in [0, max_disp] ---
        direction = random_vector(self.rng.random(), self.rng.random())
        length = self.max_disp * self.rng.random()
        disp = direction * length  # Cartesian displacement

        # --- apply translation in unwrapped space, then re-wrap ---
        cart_rot = self._pos_rot + self._img_rot * L  # unwrapped rotated
        cart_new = cart_rot + disp

        img_new = np.floor_divide(cart_new, L).astype(int)
        pos_new = cart_new - img_new * L

        # --- store → send to LAMMPS ---
        self.pos_new = pos_new
        self.img_new = img_new
        self._apply()
