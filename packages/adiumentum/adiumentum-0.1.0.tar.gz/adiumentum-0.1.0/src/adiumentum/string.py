import json
import re
from collections.abc import Callable, Iterable
from typing import Literal, TypeAlias, cast

from datethyme import Date, Time

from .functional import lmap

MixedValidated: TypeAlias = (
    str
    | bool
    | int
    | float
    | Time
    | Date
    | tuple[str, ...]
    | tuple[str, str]
    | tuple[float, float]
    | None
)
PromptTypeName = Literal[
    "string",
    "boolean",
    "integer",
    "float",
    "minutes",
    "time",
    "positiveScore",
    "negativeScore",
    "date",
    "stringtuple",
]


def indent_lines(lines: Iterable[object], indent_size: int = 4) -> str:
    joiner = "\n" + indent_size * " "
    return joiner + joiner.join(map(str, lines))


def flexsplit(s: str) -> list[str]:
    return re.split(r", ?| ", s)


def split_sequence_string(seq: str) -> tuple[str, str, int]:
    _start: str | None
    _end: str | None
    _step: str | None
    match seq.count(":"):
        case 2:
            _start, _end, _step = seq.split(":")
        case 1:
            _start, _end = seq.split(":")
            _step = None
        case 0:
            _start, _end, _step = None, seq, None
        case _:
            raise ValueError
    return (_start or "").upper(), (_end or "").upper(), int(_step or 1)


def parse_sequence(s: str) -> list[str]:
    def interpolate(_s: str) -> list[str]:
        start, end, step = split_sequence_string(_s)
        if end.isnumeric():
            return lmap(str, range(int(start or 1), int(end) + 1, step))
        elif end.isalpha():
            start = start or "A"
            assert len(start) == len(end) == 1
            return lmap(chr, range(ord(start), ord(end) + 1, step))
        else:
            pattern = re.compile(r"[A-Z]\d+$")
            letter = start[0]
            assert re.match(pattern, start) and re.match(pattern, end) and (letter == end[0])
            start, end = start[1:], end[1:]
            return [f"{letter}{i}" for i in range(int(start), int(end) + 1, step)]

    segments = []
    for subseq in s.strip().split(","):
        segments.extend(interpolate(subseq))
    return segments


def cast_to_bool(s: str | bool) -> bool:
    if isinstance(s, bool):
        return s
    s = s.lower()
    if s.startswith(("y", "t")):
        return True
    if s.startswith(("f", "n")):
        return False
    raise ValueError(f"Ambiguous input for 'cast_to_bool': '{s}'")


def cast_to_int(s: str | bool) -> int:
    if isinstance(s, bool):
        return int(s)
    return int(s.strip())


def cast_to_float(s: str | bool) -> float:
    if isinstance(s, bool):
        return float(s)
    return float(s.strip())


def cast_to_minutes(s: str | bool) -> int:
    if isinstance(s, bool):
        raise TypeError
    s = s.strip()
    if ":" in s:
        if s.count(":") > 1:
            raise ValueError
        hours, minutes = s.split(":")
        return 60 * int(hours) + int(minutes)
    return int(s)


def cast_to_positive_score(s: str | bool) -> float:
    if isinstance(s, bool):
        raise TypeError
    score = float(s.strip())
    if not 0.0 <= score <= 5.0:
        raise ValueError
    return score


def cast_to_negative_score(s: str | bool) -> float:
    if isinstance(s, bool):
        raise TypeError
    score = float(s.strip())
    if not -5.0 <= score <= 0.0:
        raise ValueError
    return score


def cast_to_Date(s: str | bool) -> Date:
    if isinstance(s, bool):
        raise TypeError
    return Date.model_validate(s)


def cast_to_stringtuple(s: str | bool) -> tuple[str, ...]:
    if isinstance(s, bool):
        raise TypeError
    if not s:
        return tuple()
    return cast(tuple[str, ...], tuple(re.split(r"[ ,;]+", s)))


def cast_as(
    input_type: PromptTypeName,
) -> Callable[[str | bool], MixedValidated]:
    dispatch: dict[
        PromptTypeName,
        Callable[[str | bool], MixedValidated],
    ] = {
        "boolean": cast_to_bool,
        "integer": cast_to_int,
        "float": cast_to_float,
        "minutes": cast_to_minutes,
        "time": Time.model_validate,
        "positiveScore": cast_to_positive_score,
        "negativeScore": cast_to_negative_score,
        "date": cast_to_Date,
        "stringtuple": cast_to_stringtuple,
    }
    caster = dispatch[input_type]

    def type_specific_caster(s: str | bool) -> MixedValidated:
        if str(s).lower() in {"none", "null", "skip", "pass"}:
            return None
        return caster(s)

    return type_specific_caster


def as_json(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, indent=4)
