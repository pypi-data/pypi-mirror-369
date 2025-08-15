# GTPyhop as an MCP Tool (V3, merged)

This merged report consolidates the prior analysis in `GTPyhopAsMCPTool.md` and the updated assessment in `GTPyhopAsMCPTool-V2.md`, based strictly on the code in `src/gtpyhop/` (notably `src/gtpyhop/main.py` and the public exports in `src/gtpyhop/__init__.py`).

## Scope and Sources
- Reviewed: `src/gtpyhop/main.py` (v1.2.1 markers) and `src/gtpyhop/__init__.py`.
- Public API (re-exported by `__init__.py`): `Domain`, `State`, `Multigoal`, `declare_actions`/`declare_operators`, `declare_commands`, `declare_task_methods`, `declare_unigoal_methods`, `declare_multigoal_methods`, `find_plan`, `pyhop`, `run_lazy_lookahead`, domain-print helpers, domain-finder helpers, verbosity and planning strategy controls, current-domain utilities.

## Core Architecture
- __Domain container__: `Domain` stores mappings for actions (`_action_dict`), commands (`_command_dict`), task methods (`_task_method_dict`), unigoal methods (`_unigoal_method_dict`), multigoal methods (`_multigoal_method_list`). Creating a `Domain` sets global `current_domain` and appends to global `_domains`.
- __State/Multigoal__: Lightweight dynamic objects; attributes become state variables. Provide `copy()`, `display()`, `state_vars()`.
- __Planning strategies__:
  - Iterative: `seek_plan_iterative()`; default is iterative via `set_recursive_planning(False)` at the end of `main.py`.
  - Recursive: `seek_plan_recursive()`.
  - Strategy controls: `set_recursive_planning(True|False)`, `get_recursive_planning()`, `reset_planning_strategy()`. Internal `_current_seek_plan` governs `find_plan()`.
- __Planning entry__: `find_plan(state, todo_list)` returns a plan (list of action tuples) or `False`. Items may be tasks, actions, unigoals, or multigoals; refinement functions decompose tasks/goals and verify achievements.
- __Acting__: `run_lazy_lookahead(state, todo_list, max_tries=10)` loops plan→act by invoking `c_<action>` from `_command_dict`, falling back to action if no command exists.
- __Verification hooks__: `_m_verify_g`, `_m_verify_mg` insert checks (and may raise) to ensure goal/multigoal achievement when verification is enabled in the flow.
- __I/O and side effects__: Global `verbose` controls prints; module import prints informational lines and sets iterative planning.

## Strengths (MCP perspective)
- __Clear entry points__: `find_plan()` and `run_lazy_lookahead()` map directly to planning and plan-and-act tool operations.
- __Separation of plan vs act__: Distinct action vs command functions enables planning-only simulation and optional execution modes.
- __Iterative planner available__: Avoids recursion limits; more suitable for long-lived tool invocations.
- __Goal constructs and verification__: Unigoals and multigoals with verification steps provide consistent semantics for MCP wrappers.
- __Domain utilities__: Helpers like `find_domain_by_name`, `set_current_domain`, `get_current_domain`, prints, and declarations simplify organizing domains (see caveats below).
- __Zero external dependencies__: Only standard library (`copy`, `re`). Easy to integrate and vendor.

## Weaknesses and Current Limits
- __Global mutable state__:
  - `current_domain`, `_domains`, `_current_seek_plan`, and `verbose` are module-level.
  - Domain creation mutates globals; many APIs implicitly depend on `current_domain`.
  - Not thread-safe; concurrent sessions require isolation.
- __Import-time side effects__:
  - On import, prints info lines and calls `set_recursive_planning(False)`. This introduces stdout noise and implicit configuration.
- __Verbose printing to stdout__:
  - Many functions print at `verbose ≥ 1` (including `find_plan` and `run_lazy_lookahead`). Tool responses risk being polluted unless captured.
- __Dynamic, untyped data model__:
  - `State`/`Multigoal` rely on dynamic attributes and nested dicts without schema or type hints. Adapters are needed to serialize/validate MCP inputs and outputs robustly.
- __Error signaling via exceptions__:
  - Verification helpers may raise on unmet goals. Adapters must translate exceptions into structured tool outcomes.
- __Limited search controls__:
  - No built-in depth/width bounds, heuristic hooks, or timeouts in `find_plan` (only `max_tries` at `run_lazy_lookahead`). Risk of long/blocking searches.
- __No async/cancellation hooks__:
  - Planner is synchronous; cooperative cancellation must be provided externally (threads/processes) if needed.
- __Diagnostics not structured__:
  - Rich trace info is printed rather than returned as data; limited programmatic visibility without instrumentation.
- __Global domain registry__:
  - `_domains` is global; domains identified by name with no explicit teardown/namespacing. Lookup is simple and global.

## Integration Considerations (MCP)
- __Process/session model__: Prefer per-session worker processes or a per-session mutex around planner calls. Snapshot/restore `current_domain`, `verbose`, and `_current_seek_plan` if multiplexing within one process.
- __State and task/goal serialization__: Define a canonical JSON mapping and adapters, e.g.:
  - State: `{ "__name__": str, "vars": { varName: dict|value } }` ↔ set attributes on `State`.
  - Multigoal: same shape as `State` for goal variables.
  - Tasks/Goals: tuples like `(name, arg1, ...)` mapped to `{ "name": str, "args": [...] }` and vice versa.
- __Verbosity/logging__: Default to `verbose=0` in tool context; capture logs and attach as a structured field rather than emitting to stdout.
- __Timeouts/limits__: Enforce wall-clock and node-expansion/depth limits around `find_plan` via wrappers to keep calls bounded.
- __Error mapping__: Normalize returns to clear statuses (e.g., `{status: "ok"|"fail", plan, message, logs}`); treat `[]` (empty plan) as success and `False/None` as failure with explanation.

## Recommendations (code-level changes to ease MCP integration)
- __Introduce a non-global Planner/Session object__:
  - Encapsulate domain, verbosity, and strategy; expose `find_plan`/`run_lazy_lookahead` as instance methods.
  - Keep module-level wrappers delegating to a default session for backward compatibility.
- __Remove import-time prints and implicit strategy set__:
  - Avoid printing at import; don’t set strategy implicitly. Default to iterative lazily on first use if unset, or require explicit `set_recursive_planning`.
- __Return diagnostics as data__:
  - Add optional structured trace: sequence of applied methods/actions, depth, expansions, elapsed time, success/failure reasons.
  - Gate all printing behind `verbose`; set library default to `0`.
- __Add resource bounds and cancellation__:
  - Support `max_depth`, `max_expansions`, `max_time_ms` parameters; allow an optional `should_cancel()` callback checked cooperatively.
- __Thread-safety and isolation__:
  - Remove reliance on module globals in core algorithms; allow multiple independent planner instances.
- __Typing and validation__:
  - Add `typing` annotations and define JSON schema-like representations for `State`/`Multigoal` for MCP I/O.
- __Error model harmonization__:
  - Offer a toggle to convert verification failures into structured results instead of exceptions.

## Suggested MCP Tool Surface
- __gtpyhop.load_domain__({ modulePath, domainName? }) → { domainName }
- __gtpyhop.set_domain__({ domainName }) → { ok: true }
- __gtpyhop.plan__({ state, todo, options }) → { status, plan, logs?, stats? }
  - options: `{ recursive?: bool, verbose?: 0|1|2|3, limits?: { timeMs?, depth?, expansions? } }`
- __gtpyhop.run_lazy_lookahead__({ state, todo, options }) → { status, newState, logs?, tries, lastPlan? }
- __gtpyhop.list_domains__() → { domains: [...] }

These map to `find_plan(...)`, `run_lazy_lookahead(...)`, domain helpers, and strategy/verbosity setters in `main.py` and the public exports in `__init__.py`.

## Mitigations without code changes (adapter layer)
- __Global state isolation__:
  - Run each request in a fresh process or assign a dedicated worker per session.
  - If sharing a process, protect with a lock and snapshot/restore `current_domain`, `verbose`, `_current_seek_plan` around each call.
- __Import-time side effects__:
  - Import once at startup; immediately set `verbose=0` and explicitly set desired strategy.
  - Optionally redirect stdout during import to suppress banner lines.
- __Serialization adapters__:
  - Implement `state_to_json`, `state_from_json`, `multigoal_to_json`, `multigoal_from_json`, and task/goal tuple mappers.
- __Deterministic resource control__:
  - Enforce wall-clock limits via watchdogs; apply expansion/depth limits in adapters (by instrumenting iterative loop if necessary).
- __Return conventions__:
  - Map `False/None` to `{status: "fail", message}`; map `[]` to `{status: "ok", plan: []}`.

## Notable Code Facts (citations)
- __Globals and strategy__: `_current_seek_plan` is declared in the planning system section; strategy set via `set_recursive_planning`, defaulted to iterative at the end of `main.py`.
- __Current domain and registry__: `current_domain`, `_domains`, and `Domain` are defined in `main.py` with `current_domain` documented as the domain used by `find_plan`/`run_lazy_lookahead`.
- __Planning workers__: `seek_plan_iterative()` (stack-based) and `seek_plan_recursive()`; helper functions `_apply_*` and `_refine_*` variants for tasks, goals, and multigoals.
- __Acting integration__: `run_lazy_lookahead()` selects `c_<action>` in `_command_dict` or falls back to the action function.
- __Verification__: `_m_verify_g`, `_m_verify_mg` add checks and may raise when goals aren’t achieved.

## Conclusion
GTPyhop’s compact HTN planner with a clean API is well-suited for MCP exposure. The principal work is engineering isolation from module-level global state, suppressing/std-structuring output, and adding resource/cancellation controls. With a thin adapter (or modest internal refactors toward a sessionized planner), robust multi-tenant MCP integration is practical while preserving backward compatibility.

---

## Appendix A — Minimal Planner/Session Sketch (remove globals, keep API)

The goal is to encapsulate `current_domain`, `verbose`, and planning strategy in a session while preserving module-level wrappers for backward compatibility.

```python
# planner_session.py (sketch)
from typing import List, Tuple, Any, Optional, Dict
from gtpyhop.main import (
    Domain, State, Multigoal,
    seek_plan_iterative, seek_plan_recursive,
)

Plan = List[Tuple[str, Any]]

class PlannerSession:
    def __init__(self, domain: Domain, *, recursive: bool = False, verbose: int = 0):
        self.domain = domain
        self.verbose = verbose
        self._seek = seek_plan_recursive if recursive else seek_plan_iterative

    def set_recursive(self, use_recursive: bool) -> None:
        self._seek = seek_plan_recursive if use_recursive else seek_plan_iterative

    def get_recursive(self) -> bool:
        return self._seek is seek_plan_recursive

    def find_plan(self, state: State, todo_list: list) -> Plan | bool:
        # Localize the global accesses by temporarily swapping current_domain if needed.
        # Prefer refactoring helpers to accept domain explicitly; shown conceptually here.
        return self._seek(state, todo_list, [], 0)

    def run_lazy_lookahead(self, state: State, todo_list: list, max_tries: int = 10) -> State:
        # Reuse existing algorithm but bind to this session's domain/verbosity.
        # In a full refactor, pass self.domain explicitly to helpers instead of using globals.
        from gtpyhop.main import run_lazy_lookahead as rll  # reuse implementation
        return rll(state, todo_list, max_tries=max_tries)


# Backward-compatibility: keep module-level wrappers delegating to a default session
_default_session: Optional[PlannerSession] = None

def _ensure_default_session(domain: Domain) -> PlannerSession:
    global _default_session
    if _default_session is None:
        _default_session = PlannerSession(domain)
    return _default_session

def find_plan(state: State, todo_list: list) -> Plan | bool:
    from gtpyhop.main import current_domain
    return _ensure_default_session(current_domain).find_plan(state, todo_list)

def run_lazy_lookahead(state: State, todo_list: list, max_tries: int = 10) -> State:
    from gtpyhop.main import current_domain
    return _ensure_default_session(current_domain).run_lazy_lookahead(state, todo_list, max_tries)
```

Notes:
- This sketch shows the direction. A proper refactor would thread `domain` through helpers to eliminate reliance on module-level globals entirely.
- Module-level wrappers maintain the public API, gradually migrating users to sessions.

---

## Appendix B — JSON Adapter Stubs (State, Multigoal, Tasks/Goals)

Define canonical JSON shapes and adapters for robust I/O in MCP.

```python
# json_adapters.py (stubs)
from typing import Any, Dict, List, Tuple
from gtpyhop.main import State, Multigoal

def state_to_json(state: State) -> Dict[str, Any]:
    return {
        "__name__": state.__name__,
        "vars": {k: v for k, v in vars(state).items() if k != "__name__"},
    }

def state_from_json(data: Dict[str, Any]) -> State:
    name = data.get("__name__", "state")
    vars_dict = data.get("vars", {})
    return State(name, **vars_dict)

def multigoal_to_json(goal: Multigoal) -> Dict[str, Any]:
    return {
        "__name__": goal.__name__,
        "vars": {k: v for k, v in vars(goal).items() if k != "__name__"},
    }

def multigoal_from_json(data: Dict[str, Any]) -> Multigoal:
    name = data.get("__name__", "goal")
    vars_dict = data.get("vars", {})
    return Multigoal(name, **vars_dict)

# Tasks/Goals encoded as {"name": str, "args": [...]}
def task_to_json(task: Tuple[Any, ...]) -> Dict[str, Any]:
    if not isinstance(task, (list, tuple)) or not task:
        raise ValueError("task must be a non-empty list/tuple")
    name, *args = task
    return {"name": str(name), "args": list(args)}

def task_from_json(obj: Dict[str, Any]) -> Tuple[Any, ...]:
    return (obj["name"], *obj.get("args", []))
```

Notes:
- These stubs assume that state-variable values and arguments are themselves JSON-serializable (dicts, lists, numbers, strings). If not, provide custom encoders.

---

## Appendix C — Normalized Result Wrapper for `find_plan`

Provide a small adapter to normalize return conventions for MCP: `[]` ⇒ success (no-op plan), list ⇒ success, `False/None` ⇒ failure with explanation. Optionally capture logs.

```python
# result_wrapper.py (sketch)
from typing import Any, Dict, List, Tuple
from contextlib import redirect_stdout
import io

Plan = List[Tuple[str, Any]]

def find_plan_normalized(find_plan_fn, state, todo_list, *, capture_logs: bool = True) -> Dict[str, Any]:
    buf = io.StringIO()
    if capture_logs:
        with redirect_stdout(buf):
            result = find_plan_fn(state, todo_list)
    else:
        result = find_plan_fn(state, todo_list)
    logs = buf.getvalue() if capture_logs else ""

    if result is False or result is None:
        return {"status": "fail", "plan": None, "message": "no plan found", "logs": logs}
    if isinstance(result, list):
        # Either [] or a non-empty action list
        return {"status": "ok", "plan": result, "message": None, "logs": logs}
    # Fallback: unexpected type (defensive)
    return {"status": "fail", "plan": None, "message": f"unexpected result type: {type(result)}", "logs": logs}
```

Notes:
- This leaves the core planner untouched and is safe to use from an MCP adapter.
- For production, prefer structured logs over stdout capture.

---

## Appendix D — Integrated Design (A+B+C with Current API)

This appendix evaluates and merges Appendices A (Session), B (JSON adapters), and Appendix C (normalized results) into a cohesive solution that integrates smoothly with the existing GTPyhop API without breaking changes.

### Design Goals
- __Backward compatibility__: Preserve module-level API (`find_plan`, `run_lazy_lookahead`, `declare_*`, etc.).
- __Session isolation__: Allow multiple independent planning contexts to avoid global cross-talk.
- __Structured I/O__: Provide canonical JSON shapes and normalized outcomes suitable for MCP.
- __Minimal intrusion__: Avoid invasive refactors; rely on thin wrappers where necessary.

### Architecture Overview
- __Session layer (A)__: `PlannerSession` encapsulates domain, verbosity, and strategy. It delegates to existing workers (`seek_plan_iterative`/`seek_plan_recursive`) and `run_lazy_lookahead` while preparing for a future refactor that threads `domain` explicitly.
- __Serialization layer (B)__: JSON adapters map `State`/`Multigoal` and task/goal tuples to wire formats and back. They live separately and do not alter core types.
- __Result normalization (Appendix C)__: A wrapper converts raw planner returns to `{status, plan, message, logs}` and optionally captures logs to avoid stdout pollution.
- __Compatibility shim__: Module-level wrappers can create or reuse a default session to maintain current call sites; advanced users adopt sessions explicitly.

### Integration with Current API
1) __Module-level wrappers__
   - Keep `gtpyhop.find_plan` and `gtpyhop.run_lazy_lookahead` intact by delegating to a lazily-created default `PlannerSession` bound to `current_domain`.
   - No behavior change for existing users; opt-in to sessions for isolation.

2) __Opt-in Session usage__
   - Power users instantiate `PlannerSession(domain, recursive=?, verbose=?)` for per-request isolation (e.g., per MCP session).
   - Future internal refactor can thread `domain` into helpers to fully eliminate globals; the public surface remains the same.

3) __JSON adapters__
   - Adapters live in an `adapters/json_adapters.py` module (or equivalent). They convert inputs/outputs for MCP without touching core code.
   - Plan items remain tuples internally; adapters expose `{name, args}` externally.

4) __Normalized results__
   - Adapters expose `find_plan_normalized(...)` for tool endpoints. Internally they call either the module-level `find_plan` or a session’s `find_plan`.
   - Treat `[]` as success, `False/None` as failure, and include optional captured logs.

### Threading and Concurrency
- __Recommended__: one worker process per MCP session for strong isolation.
- __If in-process__: guard with a session-specific lock; snapshot/restore `current_domain`, `verbose`, and strategy around calls if any core helpers still consult globals.

### Logging and Verbosity
- Default to `verbose=0` for sessions created by adapters.
- Provide an option to capture stdout (as in Appendix C) for legacy prints; long term, prefer structured trace data returned by the planner (future enhancement).

### Error Handling
- Verification exceptions and other planner errors are caught at the adapter layer and converted into `{status:"fail", message, logs}`.
- Unexpected types are treated as failures with diagnostic messages to avoid ambiguity.

### Resource Limits and Cancellation
- While core `find_plan` lacks time/depth bounds, the adapter should enforce watchdog timeouts and optional step counters.
- Expose limits via adapter options and implement cooperative checks where possible in the iterative loop (future contribution to core).

### Migration Path
- Phase 1 (non-invasive): add Session, JSON adapters, and normalized wrapper externally; keep core unchanged.
- Phase 2 (compat upgrade): thread `domain` explicitly through helpers to remove implicit globals; keep module-level wrappers delegating to a default session.
- Phase 3 (enhancements): provide structured traces/metrics, native bounds/cancellation, and library-default `verbose=0`.

### Example End-to-End Flow (MCP)

```python
# Server bootstrap
from gtpyhop import Domain
from adapters.json_adapters import state_from_json, task_from_json
from adapters.result_wrapper import find_plan_normalized
from adapters.planner_session import PlannerSession

dom = Domain("my_domain")
# declare_actions/commands/methods(...)

# Per-request handler (pseudo-code)
def handle_plan(req_json):
    session = PlannerSession(dom, recursive=req_json.get("options", {}).get("recursive", False), verbose=0)
    state = state_from_json(req_json["state"])
    todo = [task_from_json(t) for t in req_json["todo"]]
    result = find_plan_normalized(session.find_plan, state, todo, capture_logs=True)
    return result  # {status, plan, message, logs}
```

This design combines isolation (A), robust I/O (B), and clear outcomes (Appendix C) while preserving today’s GTPyhop API and behavior. It requires no disruptive changes and positions the project for future internal improvements without breaking existing users.

#### Adapters package file: `adapters/__init__.py` (also usable as a single-file `adapters.py`)

Provide convenient re-exports so callers may use either `from adapters.planner_session import PlannerSession` (package layout) or `from adapters import PlannerSession` (single-file layout).

```python
# adapters/__init__.py  (or a single-file module named adapters.py)

from .planner_session import PlannerSession
from .json_adapters import (
    state_to_json, state_from_json,
    multigoal_to_json, multigoal_from_json,
    task_to_json, task_from_json,
)
from .result_wrapper import find_plan_normalized

__all__ = [
    "PlannerSession",
    "state_to_json", "state_from_json",
    "multigoal_to_json", "multigoal_from_json",
    "task_to_json", "task_from_json",
    "find_plan_normalized",
]
```

Usage options:
- Package-style (as in the example): `from adapters.planner_session import PlannerSession`
- Convenience import: `from adapters import PlannerSession, state_from_json, task_from_json, find_plan_normalized`
