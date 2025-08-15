from __future__ import annotations

# A global variable for storing the current context that is used for points or scalars.
CURRENT_CONTEXT: PEPContext | None = None


def get_current_context() -> PEPContext | None:
    return CURRENT_CONTEXT


def set_current_context(ctx: PEPContext | None):
    global CURRENT_CONTEXT
    assert ctx is None or isinstance(ctx, PEPContext)
    CURRENT_CONTEXT = ctx


class PEPContext:
    def __init__(self):
        self.points = []
        self.scalars = []

    def add_point(self, point):
        self.points.append(point)

    def add_scalar(self, scalar):
        self.scalars.append(scalar)

    def clear(self):
        self.points = []
        self.scalars = []
