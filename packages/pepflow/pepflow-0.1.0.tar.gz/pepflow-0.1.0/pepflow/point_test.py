import time

import numpy as np

from pepflow import expression_manager as exm
from pepflow import function as fc
from pepflow import pep as pep
from pepflow import point, scalar, utils


def test_point_hash_different():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = point.Point(is_basis=True, eval_expression=None)
        p2 = point.Point(is_basis=True, eval_expression=None)
    assert p1.uid != p2.uid


def test_scalar_hash_different():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s2 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1.uid != s2.uid


def test_point_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = point.Point(is_basis=True, eval_expression=None)
        p1.add_tag(tag="my_tag")
    assert p1.tags == ["my_tag"]


def test_scalar_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s1.add_tag(tag="my_tag")
    assert s1.tags == ["my_tag"]


def test_point_in_a_list():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = point.Point(is_basis=True, eval_expression=None)
        p2 = point.Point(is_basis=True, eval_expression=None)
        p3 = point.Point(is_basis=True, eval_expression=None)
    assert p1 in [p1, p2]
    assert p3 not in [p1, p2]


def test_scalar_in_a_list():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s2 = scalar.Scalar(is_basis=True, eval_expression=None)
        s3 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1 in [s1, s2]
    assert s3 not in [s1, s2]


def test_expression_manager_on_basis_point():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        p1 = point.Point(is_basis=True, eval_expression=None, tags=["p1"])
        p2 = point.Point(is_basis=True, eval_expression=None, tags=["p2"])
        pm = exm.ExpressionManager(ctx)

        np.testing.assert_allclose(pm.eval_point(p1).vector, np.array([1, 0]))
        np.testing.assert_allclose(pm.eval_point(p2).vector, np.array([0, 1]))

        p3 = point.Point(is_basis=True, eval_expression=None, tags=["p3"])  # noqa: F841
        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_point(p1).vector, np.array([1, 0, 0]))
    np.testing.assert_allclose(pm.eval_point(p2).vector, np.array([0, 1, 0]))


def test_expression_manager_on_basis_scalar():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])
        pm = exm.ExpressionManager(ctx)

        np.testing.assert_allclose(pm.eval_scalar(s1).vector, np.array([1, 0]))
        np.testing.assert_allclose(pm.eval_scalar(s2).vector, np.array([0, 1]))

        s3 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s3"])  # noqa: F841
        pm = exm.ExpressionManager(ctx)

        np.testing.assert_allclose(pm.eval_scalar(s1).vector, np.array([1, 0, 0]))
        np.testing.assert_allclose(pm.eval_scalar(s2).vector, np.array([0, 1, 0]))


def test_expression_manager_eval_point():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        p1 = point.Point(is_basis=True)
        p2 = point.Point(is_basis=True)
        p3 = 2 * p1 + p2 / 4
        p4 = p3 + p1

        pm = exm.ExpressionManager(ctx)
    np.testing.assert_allclose(pm.eval_point(p3).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_point(p4).vector, np.array([3, 0.25]))


def test_expression_manager_eval_scalar():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True)
        s2 = scalar.Scalar(is_basis=True)
        s3 = 2 * s1 + s2 / 4 + 5
        s4 = s3 + s1
        s5 = s4 + 5

        p1 = point.Point(is_basis=True)
        p2 = point.Point(is_basis=True)
        s6 = p1 * p2

        p3 = point.Point(is_basis=True)
        p4 = point.Point(is_basis=True)
        s7 = 5 * p3 * p4

        s8 = s6 + s7

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_scalar(s3).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s3).constant, 5)
    np.testing.assert_allclose(pm.eval_scalar(s4).vector, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).vector, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).constant, 10)

    np.testing.assert_allclose(pm.eval_point(p1).vector, np.array([1, 0, 0, 0]))
    np.testing.assert_allclose(pm.eval_point(p2).vector, np.array([0, 1, 0, 0]))
    np.testing.assert_allclose(pm.eval_point(p3).vector, np.array([0, 0, 1, 0]))
    np.testing.assert_allclose(pm.eval_point(p4).vector, np.array([0, 0, 0, 1]))

    np.testing.assert_allclose(
        pm.eval_scalar(s6).matrix,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        ),
    )
    np.testing.assert_allclose(
        pm.eval_scalar(s7).matrix,
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )

    np.testing.assert_allclose(
        pm.eval_scalar(s8).matrix,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )


def test_constraint():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True)
        s2 = scalar.Scalar(is_basis=True)
        s3 = 2 * s1 + s2 / 4 + 5

        c1 = s3.le(5, name="c1")
        c2 = s3.lt(5, name="c2")
        c3 = s3.ge(5, name="c3")
        c4 = s3.gt(5, name="c4")
        c5 = s3.eq(5, name="c5")

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_scalar(c1.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c1.scalar).constant, 0)
    assert c1.comparator == utils.Comparator.LT

    np.testing.assert_allclose(pm.eval_scalar(c2.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c2.scalar).constant, 0)
    assert c2.comparator == utils.Comparator.LT

    np.testing.assert_allclose(pm.eval_scalar(c3.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c3.scalar).constant, 0)
    assert c3.comparator == utils.Comparator.GT

    np.testing.assert_allclose(pm.eval_scalar(c4.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c4.scalar).constant, 0)
    assert c4.comparator == utils.Comparator.GT

    np.testing.assert_allclose(pm.eval_scalar(c5.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c5.scalar).constant, 0)
    assert c5.comparator == utils.Comparator.EQ


def test_expression_manager_eval_point_large_scale():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        all_basis = [point.Point(is_basis=True) for _ in range(100)]
        p = all_basis[0]
        for i in range(len(all_basis)):
            for j in range(i + 1, len(all_basis)):
                p += all_basis[i] * 2 + all_basis[j]
        pm = exm.ExpressionManager(ctx)
        t = time.time()
        for pp in ctx.points:
            pm.eval_point(pp)

        assert (time.time() - t) < 0.1


def test_function_generate_triplet():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=True)
        g = fc.Function(is_basis=True, reuse_gradient=True)
        h = 5 * f + 5 * g

        f1 = fc.Function(is_basis=True, reuse_gradient=False)
        g1 = fc.Function(is_basis=True, reuse_gradient=False)
        h1 = 5 * f1 + 5 * g1

        p1 = point.Point(is_basis=True)
        _, func_value, grad = h.generate_triplet(p1)
        _, func_value_1, grad_1 = h.generate_triplet(p1)

        _, func_value_2, grad_2 = h1.generate_triplet(p1)
        _, func_value_3, grad_3 = h1.generate_triplet(p1)

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(
        pm.eval_point(p1).vector, np.array([1, 0, 0, 0, 0, 0, 0])
    )

    np.testing.assert_allclose(
        pm.eval_point(grad).vector, np.array([0, 5, 5, 0, 0, 0, 0])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(func_value).vector, np.array([5, 5, 0, 0])
    )

    np.testing.assert_allclose(
        pm.eval_point(grad_1).vector, np.array([0, 5, 5, 0, 0, 0, 0])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(func_value_1).vector, np.array([5, 5, 0, 0])
    )

    np.testing.assert_allclose(
        pm.eval_point(grad_2).vector, np.array([0, 0, 0, 5, 5, 0, 0])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(func_value_2).vector, np.array([0, 0, 5, 5])
    )

    np.testing.assert_allclose(
        pm.eval_point(grad_3).vector, np.array([0, 0, 0, 0, 0, 5, 5])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(func_value_3).vector, np.array([0, 0, 5, 5])
    )


def test_function_add_stationary_point():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.Function(is_basis=True, reuse_gradient=True)
        x_opt = f.add_stationary_point()

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_point(x_opt).vector, np.array([1, 0]))

    np.testing.assert_allclose(
        pm.eval_scalar(f.constraints[0].scalar).matrix, [[0, 0], [0, 1]]
    )
    np.testing.assert_allclose(pm.eval_scalar(f.constraints[0].scalar).vector, [0])
    np.testing.assert_allclose(pm.eval_scalar(f.constraints[0].scalar).constant, 0)
    assert f.constraints[0].comparator == utils.Comparator.EQ


def test_smooth_interpolability_constraints():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        f = fc.SmoothConvexFunction(L=1)
        _ = f.add_stationary_point()

        x_0 = point.Point(is_basis=True)
        _, _, _ = f.generate_triplet(x_0)

        all_interpolation_constraints = f.get_interpolation_constraints()

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(
        pm.eval_scalar(all_interpolation_constraints[1].scalar).vector, [1, -1]
    )
    np.testing.assert_allclose(
        pm.eval_scalar(all_interpolation_constraints[1].scalar).matrix,
        [
            [0.0, -0.5, 0.0, 0.0],
            [-0.5, 0.5, 0.5, -0.5],
            [0.0, 0.5, 0.0, 0.0],
            [0.0, -0.5, 0.0, 0.5],
        ],
    )

    np.testing.assert_allclose(
        pm.eval_scalar(all_interpolation_constraints[1].scalar).constant, 0
    )
