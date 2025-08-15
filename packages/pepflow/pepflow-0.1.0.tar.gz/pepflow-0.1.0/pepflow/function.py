import uuid

import attrs

from pepflow import point as pt
from pepflow import scalar as sc
from pepflow import utils


class Function:
    def __init__(
        self,
        is_basis: bool,
        reuse_gradient: bool,
        composition: dict | None = None,
        tag: str | None = None,
    ):
        self.is_basis = is_basis
        self.reuse_gradient = reuse_gradient
        self.tag = tag
        self.uid = attrs.field(factory=uuid.uuid4, init=False)
        self.triplets = []  #: list[("point", "scalar", "point")] = []
        self.constraints = []  #: list["constraint"] = []

        if is_basis:
            assert composition is None
            self.composition = {self: 1}
        else:
            assert isinstance(composition, dict)
            self.composition = composition  #: dict[{"function": float})] = []

    def add_tag(self, tag: str) -> None:
        self.tag = tag
        return None

    def get_interpolation_constraints(self):
        raise NotImplementedError(
            "This method should be implemented in the children class."
        )

    def add_triplet(self, triplet: tuple) -> None:
        return NotImplemented

    def add_stationary_point(self) -> pt.Point:
        point = pt.Point(is_basis=True)
        _, _, grad = self.generate_triplet(point)
        self.constraints.append(
            (grad**2).eq(0, name=str(self.__hash__) + " stationary point")
        )
        return point

    def generate_triplet(self, point: pt.Point) -> tuple:
        func_value = 0
        grad = 0

        if self.is_basis:
            generate_new_basis = True
            for triplet in self.triplets:
                if triplet[0].uid == point.uid and self.reuse_gradient:
                    func_value = triplet[1]
                    grad = triplet[2]
                    generate_new_basis = False
                    break
                elif triplet[0].uid == point.uid and not self.reuse_gradient:
                    func_value = triplet[1]
                    grad = pt.Point(is_basis=True)
                    generate_new_basis = False
                    self.triplets.append((point, func_value, grad))
                    break
            if generate_new_basis:
                func_value = sc.Scalar(is_basis=True)
                grad = pt.Point(is_basis=True)
                self.triplets.append((point, func_value, grad))
        else:
            for function, weights in self.composition.items():
                _, func_value_slice, grad_slice = function.generate_triplet(point)
                func_value += weights * func_value_slice
                grad += weights * grad_slice

        return (point, func_value, grad)

    def gradient(self, point: pt.Point) -> pt.Point:
        _, _, grad = self.generate_triplet(point)
        return grad

    def subgradient(self, point: pt.Point) -> pt.Point:
        _, _, subgrad = self.generate_triplet(point)
        return subgrad

    def function_value(self, point: pt.Point) -> sc.Scalar:
        _, func_value, _ = self.generate_triplet(point)
        return func_value

    def __add__(self, other):
        assert isinstance(other, Function)
        merged_composition = utils.merge_dict(self.composition, other.composition)
        pruned_composition = utils.prune_dict(merged_composition)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient and other.reuse_gradient,
            composition=pruned_composition,
            tag=None,
        )

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        return self.__rmul__(other=other)

    def __rmul__(self, other):
        assert utils.is_numerical(other)
        scaled_composition = dict()
        for key, value in self.composition.items():
            scaled_composition[key] = value * other
        pruned_composition = utils.prune_dict(scaled_composition)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=pruned_composition,
            tag=None,
        )

    def __neg__(self):
        return self.__mul__(other=-1)

    def __truediv__(self, other):
        assert utils.is_numerical(other)
        scaled_composition = dict()
        for key, value in self.composition.items():
            scaled_composition[key] = value / other
        pruned_composition = utils.prune_dict(scaled_composition)
        return Function(
            is_basis=False,
            reuse_gradient=self.reuse_gradient,
            composition=pruned_composition,
            tag=None,
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return self.uid == other.uid


class SmoothConvexFunction(Function):
    def __init__(self, L, is_basis=True, composition=None, reuse_gradient=True):
        super().__init__(
            is_basis=is_basis, composition=composition, reuse_gradient=reuse_gradient
        )
        self.L = L

    def smooth_convex_interpolability_constraints(self, triplet_i, triplet_j):
        point_i, func_value_i, grad_i = triplet_i
        point_j, func_value_j, grad_j = triplet_j
        func_diff = func_value_j - func_value_i
        cross_term = grad_j * (point_i - point_j)
        quad_term = 1 / (2 * self.L) * (grad_i - grad_j) ** 2

        return (func_diff + cross_term + quad_term).le(
            0,
            name=str(self.__hash__())
            + ":"
            + str(point_i.__hash__())
            + ","
            + str(point_j.__hash__()),
        )

    def get_interpolation_constraints(self):
        interpolation_constraints = []
        for i in range(len(self.triplets)):
            for j in range(len(self.triplets)):
                if i == j:
                    continue
                interpolation_constraints.append(
                    self.smooth_convex_interpolability_constraints(
                        self.triplets[i], self.triplets[j]
                    )
                )
        return interpolation_constraints
