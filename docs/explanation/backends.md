# Backends

Backends execute compiled [`AtomicCircuit`][oqd_core.interface.atomic.AtomicCircuit] programs.

## Supported backends

- [QuTiP](https://qutip.org/) — [`QutipBackend`][oqd_trical.backend.qutip.QutipBackend]
- [Dynamiqs](https://www.dynamiqs.org/) (JAX + Diffrax) — [`DynamiqsBackend`][oqd_trical.backend.dynamiqs.DynamiqsBackend]

## Compile and run

Both backends share the same compile path (atomic IR → emulator Hamiltonian → backend experiment) and return a result dict with `states`, `tspan`, and `final_state`.

```python
from oqd_trical.backend import DynamiqsBackend, QutipBackend

backend = DynamiqsBackend(approx_pass=approx_pass)
experiment, hilbert_space = backend.compile(circuit, fock_cutoff=3)
result = backend.run(experiment, hilbert_space, timestep=1e-8)
```

### Task API

For parity with the analog emulator’s [`QutipBackend.run`][oqd_analog_emulator.qutip_backend.QutipBackend], Dynamiqs also supports a task entry point:

```python
from oqd_core.backend.task import Task
from oqd_trical.backend import DynamiqsBackend, TaskArgsAtomicEmulator

args = TaskArgsAtomicEmulator(fock_trunc=3, dt=1e-8)
task = Task(program=circuit, args=args)
result = DynamiqsBackend(approx_pass=approx_pass).run_task(task)
```

## Dynamiqs: units and Diffrax settings

Atomic inputs use **angular frequencies in rad/s** (often written with factors of \(2\pi\)) and **pulse durations in seconds**. The lowered Hamiltonian and `dq.sesolve` use the same convention (\(\hbar = 1\), \(d|\psi\rangle/dt = -i H |\psi\rangle\)).

Because \(|H|\) can be \(\sim 2\pi \times 10^6\,\mathrm{rad/s}\) or larger, the VM optionally rescales to dimensionless time \(\tau = \omega t\) with \(H' = H/\omega\) before calling Diffrax. Physical times in `result["tspan"]` are unchanged.

Configure the integrator via [`DynamiqsSolverOptions`][oqd_trical.backend.dynamiqs.solver.DynamiqsSolverOptions] (default: **Tsit5** with PID step control, `rtol=atol=1e-3`, `progress_meter=False` to avoid Jupyter ZMQ issues):

```python
from oqd_trical.backend import DynamiqsBackend, DynamiqsSolverOptions

backend = DynamiqsBackend(
    solver_options=DynamiqsSolverOptions(rtol=1e-4, atol=1e-4, rescale_time=True),
)
```

See [`solver.py`][oqd_trical.backend.dynamiqs.solver] for full documentation of defaults.
