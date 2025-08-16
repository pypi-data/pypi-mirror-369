from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from mosaic_materials.moves.move import MoveStrategy
from mosaic_materials.state.system import System


@dataclass
class MoveSpec:
    """
    Generate a MC move and (optionally) tune one or more proposal parameters
    to reach a target acceptance rate.
    """

    name: str
    move_class: type[MoveStrategy]
    selector: Callable[[System, np.random.Generator], Sequence[int]]
    kwargs: dict[str, Any]

    # --- tuning config ---
    tuning_param: str | None = None                  # single param
    tuning_params: Sequence[str] | None = None       # multiple params
    target_acceptance: float = 0.5
    adjustment_factor: float = 1.1                   # >1.0
    interval: int = 100
    adjust_mode: str = "all"                         # "all" or "alternate"

    # optional bounds (applied if provided)
    min_values: dict[str, float] = field(default_factory=dict)
    max_values: dict[str, float] = field(default_factory=dict)

    # internal counters/state
    _trial_count: int = field(default=0, init=False)
    _accept_count: int = field(default=0, init=False)
    _alt_index: int = field(default=0, init=False)   # for alternate mode

    def __post_init__(self):
        if self.tuning_param is None and self.tuning_params is None:
            # try single
            tp = getattr(self.move_class, "tuning_param", None)
            # or plural
            tps = getattr(self.move_class, "tuning_params", None)
            if tps is not None:
                self.tuning_params = tuple(tps)
            elif tp is not None:
                self.tuning_param = tp

        # Normalise into a list of names to update
        if self.tuning_params is None:
            self._param_names: list[str] = (
                [self.tuning_param] if self.tuning_param else []
            )
        else:
            self._param_names = list(self.tuning_params)

        # Sanity checks
        if not self._param_names:
            pass
        else:
            # ensure kwargs contain all parameters
            missing = [p for p in self._param_names if p not in self.kwargs]
            if missing:
                raise ValueError(f"Missing parameter(s) in kwargs: {missing}")
            if self.adjustment_factor <= 1.0:
                raise ValueError("adjustment_factor must be > 1.0")

        if self.adjust_mode not in ("all", "alternate"):
            raise ValueError("adjust_mode must be 'all' or 'alternate'")

    def instantiate(self, engine, rng: np.random.Generator) -> MoveStrategy:
        atom_ids = self.selector(engine.system, rng)
        return self.move_class(
            engine, atom_ids=atom_ids, rng=rng, **self.kwargs # type: ignore[call-arg]
        )

    def record(self, accepted: bool) -> None:
        """
        Record one attempt outcome, and every `interval` trials adjust
        the tuning parameters toward the target acceptance rate.

        - If observed > target: multiply chosen params by `adjustment_factor`.
        - Else: divide them by `adjustment_factor`.
        - Applies optional min/max clamps if provided.
        """
        self._trial_count += 1
        if accepted:
            self._accept_count += 1

        if self._trial_count < self.interval:
            return

        observed = self._accept_count / self._trial_count

        to_update: Iterable[str]
        if not self._param_names:
            to_update = ()
        elif self.adjust_mode == "all" or len(self._param_names) == 1:
            to_update = self._param_names
        else:  # "alternate"
            name = self._param_names[self._alt_index % len(self._param_names)]
            to_update = (name,)
            self._alt_index += 1

        if observed > self.target_acceptance:
            scale = self.adjustment_factor
        else:
            scale = 1.0 / self.adjustment_factor

        for name in to_update:
            old = float(self.kwargs[name])
            new = old * scale
            if name in self.min_values:
                new = max(new, float(self.min_values[name]))
            if name in self.max_values:
                new = min(new, float(self.max_values[name]))
            self.kwargs[name] = new

        # reset counters
        self._trial_count = 0
        self._accept_count = 0
