import warnings

import cvxpy

from pepflow import constraint as ctr
from pepflow import expression_manager as exm
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils


def evaled_scalar_to_cvx_express(
    eval_scalar: sc.EvaluatedScalar, vec_var: cvxpy.Variable, matrix_var: cvxpy.Variable
) -> cvxpy.Expression:
    return (
        vec_var @ eval_scalar.vector
        + cvxpy.trace(matrix_var @ eval_scalar.matrix)
        + eval_scalar.constant
    )


class DualVariableManager:
    def __init__(self, named_constraints: list[tuple[str, cvxpy.Constraint]]):
        self.named_constraints = {}
        for name, c in named_constraints:
            self.add_constraint(name, c)

    def cvx_constraints(self) -> list[cvxpy.Constraint]:
        return list(self.named_constraints.values())

    def clear(self) -> None:
        self.named_constraints.clear()

    def add_constraint(self, name: str, constraint: cvxpy.Constraint) -> None:
        if name in self.named_constraints:
            raise KeyError(f"There is already a constraint named {name}")
        self.named_constraints[name] = constraint

    def dual_value(self, name: str) -> float | None:
        if name not in self.named_constraints:
            raise KeyError(f"Cannot find the constraint named {name}")
        dual_value = self.named_constraints[name].dual_value
        if dual_value is None:
            warnings.warn("Did you forget to solve the problem first?")
            return None
        return dual_value


class CVXSolver:
    def __init__(
        self,
        perf_metric: sc.Scalar,
        constraints: list[ctr.Constraint],
        context: pc.PEPContext,
    ):
        self.perf_metric = perf_metric
        self.constraints = constraints
        self.dual_var_manager = DualVariableManager([])
        self.context = context

    def build_problem(self) -> cvxpy.Problem:
        em = exm.ExpressionManager(self.context)
        f_var = cvxpy.Variable(em._num_basis_scalars)
        g_var = cvxpy.Variable(
            (em._num_basis_points, em._num_basis_points), symmetric=True
        )

        # Evaluate all poiints and scalars in advance to store it in cache.
        for point in self.context.points:
            em.eval_point(point)
        for scalar in self.context.scalars:
            em.eval_scalar(scalar)

        self.dual_var_manager.clear()
        self.dual_var_manager.add_constraint("PSD of Grammian Matrix", g_var >> 0)
        for c in self.constraints:
            exp = evaled_scalar_to_cvx_express(em.eval_scalar(c.scalar), f_var, g_var)
            if c.comparator == utils.Comparator.GT:
                self.dual_var_manager.add_constraint(c.name, exp >= 0)
            elif c.comparator == utils.Comparator.LT:
                self.dual_var_manager.add_constraint(c.name, exp <= 0)
            elif c.comparator == utils.Comparator.EQ:
                self.dual_var_manager.add_constraint(c.name, exp == 0)
            else:
                raise ValueError(f"Unknown comparator {c.comparator}")

        obj = evaled_scalar_to_cvx_express(
            em.eval_scalar(self.perf_metric), f_var, g_var
        )

        return cvxpy.Problem(
            cvxpy.Maximize(obj), self.dual_var_manager.cvx_constraints()
        )

    def solve(self, **kwargs):
        problem = self.build_problem()
        result = problem.solve(**kwargs)
        return result
