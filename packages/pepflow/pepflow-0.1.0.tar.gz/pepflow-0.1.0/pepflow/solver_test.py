import numpy as np

from pepflow import pep as pep
from pepflow import point as pp
from pepflow import solver as ps


def test_cvx_solver_case1():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Point(is_basis=True)
        s1 = pp.Scalar(is_basis=True)
        s2 = -(1 + p1 * p1)
        constraints = [(p1 * p1).gt(1, name="x^2 >= 1"), s1.gt(0, name="s1 > 0")]

    solver = ps.CVXSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )

    # It is a simple `min_x 1 + x^2; s.t. x^2 >= 1` problem.
    problem = solver.build_problem()
    result = problem.solve()
    assert abs(-result - 2) < 1e-6

    assert np.isclose(solver.dual_var_manager.dual_value("x^2 >= 1"), 1)
    assert solver.dual_var_manager.dual_value("s1 > 0") == 0


def test_cvx_solver_case2():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Point(is_basis=True)
        s1 = pp.Scalar(is_basis=True)
        s2 = -(p1 - 1) * (p1 - 2)
        constraints = [(p1 * p1).lt(1, name="x^2 <= 1"), s1.gt(0, name="s1 > 0")]

    solver = ps.CVXSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )

    # It is a simple `min_x (x-1)(x-2); s.t. x^2 <= 1` problem.
    problem = solver.build_problem()
    result = problem.solve()
    assert abs(-result) < 1e-6

    assert np.isclose(solver.dual_var_manager.dual_value("x^2 <= 1"), 0)
    assert solver.dual_var_manager.dual_value("s1 > 0") == 0
