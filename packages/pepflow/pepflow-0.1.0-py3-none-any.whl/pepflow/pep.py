from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import attrs

from pepflow import pep_context as pc
from pepflow import point as pt
from pepflow import scalar as sc
from pepflow import solver as ps

if TYPE_CHECKING:
    from pepflow.solver import DualVariableManager


@attrs.frozen
class PEPResult:
    primal_opt_value: float
    dual_var_manager: DualVariableManager
    solver_status: Any


class PEPBuilder:
    """The main class for PEP primal formulation."""

    def __init__(self):
        self.pep_context_dict: dict[str, pc.PEPContext] = {}

        self.init_conditions = []  #: list["constraint"] =[]
        self.functions = []  #: list["function"] = []
        self.interpolation_constraints = []  #: list["constraint"] = []
        self.performance_metric = None  # scalar

        # Contain the name for the constraints that should be removed.
        # We should think about a better choice like manager.
        self.relaxed_constraints = []

    @contextlib.contextmanager
    def make_context(self, name: str, override: bool = False) -> pc.PEPContext:
        if not override and name in self.pep_context_dict:
            raise KeyError(f"There is already a context {name} in the builder")
        try:
            ctx = pc.PEPContext()
            self.pep_context_dict[name] = ctx
            pc.set_current_context(ctx)
            yield ctx
        finally:
            pc.set_current_context(None)

    def get_context(self, name: str) -> pc.PEPContext:
        if name not in self.pep_context_dict:
            raise KeyError(f"Cannot find a context named {name} in the builder.")
        ctx = self.pep_context_dict[name]
        pc.set_current_context(ctx)
        return ctx

    def clear_context(self, name: str) -> None:
        if name not in self.pep_context_dict:
            raise KeyError(f"Cannot find a context named {name} in the builder.")
        del self.pep_context_dict[name]

    def clear_all_context(self) -> None:
        self.pep_context_dict.clear()

    def set_init_point(self, tag: str | None = None) -> pt.Point:
        point = pt.Point(is_basis=True)
        point.add_tag(tag)
        return point

    def set_initial_constraint(self, constraint):
        self.init_conditions.append(constraint)

    def set_performance_metric(self, metric: sc.Scalar):
        self.performance_metric = metric

    def declare_func(self, function_class, **kwargs):
        func = function_class(is_basis=True, composition=None, **kwargs)
        self.functions.append(func)
        return func

    def solve(self, context: pc.PEPContext | None = None, **kwargs):
        if context is None:
            context = pc.get_current_context()
        if context is None:
            raise RuntimeError("Did you forget to create a context?")

        all_constraints = [*self.init_conditions]
        for f in self.functions:
            if f.is_basis:
                all_constraints.extend(f.get_interpolation_constraints())
            all_constraints.extend(f.constraints)

        # for now, we heavily rely on the CVX. We can make a wrapper class to avoid
        # direct dependency in the future.
        solver = ps.CVXSolver(
            perf_metric=self.performance_metric,
            constraints=[
                c for c in all_constraints if c.name not in self.relaxed_constraints
            ],
            context=context,
        )
        problem = solver.build_problem()
        result = problem.solve(**kwargs)
        return PEPResult(
            primal_opt_value=result,
            dual_var_manager=solver.dual_var_manager,
            solver_status=problem.status,
        )
