# Copyright 2024-2025 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Task-level arguments for atomic-layer simulation with TrICal backends.

[`TaskArgsAtomic`][oqd_core.backend.task.TaskArgsAtomic] in oqd-core defines the
cross-layer fields ``fock_trunc`` and ``dt``. Dynamiqs-specific Diffrax controls
live here until they are promoted into oqd-core (see the todo on ``TaskArgsAtomic``).
"""

from __future__ import annotations

from typing import Literal, Optional, Union

from oqd_core.backend.task import TaskArgsAtomic
from pydantic import BaseModel, ConfigDict, Field

from oqd_trical.backend.dynamiqs.solver import DynamiqsSolverOptions

########################################################################################


class TaskArgsAtomicEmulator(BaseModel):
    """Atomic-layer task arguments for TrICal emulators (QuTiP and Dynamiqs).

    Aligns with [`TaskArgsAtomic`][oqd_core.backend.task.TaskArgsAtomic] and
    [`TaskArgsAnalog`][oqd_core.backend.task.TaskArgsAnalog] (``fock_trunc`` ↔
    ``fock_cutoff``, ``dt``). Adds optional Diffrax settings for
    [`DynamiqsBackend`][oqd_trical.backend.dynamiqs.DynamiqsBackend].
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    layer: Literal["atomic"] = "atomic"
    n_shots: int = 10
    fock_trunc: int = Field(default=4, description="Fock space truncation per phonon mode.")
    dt: float = Field(
        default=1e-8,
        description="Output timestep between saved states (seconds).",
    )
    dynamiqs_solver_options: Optional[DynamiqsSolverOptions] = Field(
        default=None,
        description="Diffrax integrator settings (Tsit5 + PID, rtol/atol, time rescaling).",
    )


def task_args_from_atomic(
    args: Union[TaskArgsAtomic, TaskArgsAtomicEmulator, DynamiqsSolverOptions, None],
    *,
    default_dt: float = 1e-8,
) -> tuple[int, float, Optional[DynamiqsSolverOptions]]:
    """Normalize Task args into (fock_trunc, dt, dynamiqs_solver_options)."""
    if isinstance(args, DynamiqsSolverOptions):
        return 4, default_dt, args
    if args is None:
        return 4, default_dt, None
    fock = getattr(args, "fock_trunc", 4)
    dt = getattr(args, "dt", default_dt)
    solver = (
        args.dynamiqs_solver_options
        if isinstance(args, TaskArgsAtomicEmulator)
        else None
    )
    return fock, dt, solver
