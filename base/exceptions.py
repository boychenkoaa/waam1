class IncorrectOffsetDistanceError(ArithmeticError):
    pass


class AmbiguousOffsetDistanceError(IncorrectOffsetDistanceError):
    pass


class TooSmallOffsetDistanceError(IncorrectOffsetDistanceError):
    pass


class BentleyError(ValueError):
    pass


class DcelError(ValueError):
    pass


class PendantVertexError(DcelError):
    pass

class ValidationError(TypeError):
    pass