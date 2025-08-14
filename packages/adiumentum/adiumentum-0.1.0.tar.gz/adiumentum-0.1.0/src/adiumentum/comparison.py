def nearly_equal(a: int | float, b: int | float) -> bool:
    return abs(a - b) < 0.00001


def equal_within(a: int | float, b: int | float, epsilon: float | int) -> bool:
    return abs(a - b) < epsilon
