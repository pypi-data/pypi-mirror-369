def round5(num: int | float, min_val: int | float = 15) -> int:
    """For numbers greater than min_val, round to the nearest multiple of 5."""
    if num < min_val:
        return round(num)
    q, r = divmod(num, 5)
    return int(5 * (q + int(r > 2)))


def evenly_spaced(
    start: float,
    end: float,
    steps: int,
    reversed: bool = False,
) -> list[float]:
    if start > end:
        start, end = end, start
        reversed = True
    start += 1e-7
    end -= 1e-7
    step_size = (end - start) / steps
    numbers = [start + step_size * i for i in range(steps)]
    if reversed:
        numbers.reverse()
    return numbers


def ihash(i: int) -> str:
    return str(hash(str(i)))[-4:]
