import re
from enum import StrEnum
from pathlib import Path
from typing import Callable, Iterable

from pandas import DataFrame, read_csv

from pyholos.core_constants import CoreConstants


class AutoNameEnum(StrEnum):
    """Allows automatically setting the member value identical to the member name."""

    def _generate_next_value_(self, start, count, last_values):
        return self


def read_holos_resource_table(
        path_file: Path | str,
        **kwargs
) -> DataFrame:
    return read_csv(path_file, sep=',', decimal='.', comment='#', **kwargs
                    ).replace({
        'NotApplicable': CoreConstants.NotApplicable,
        float('nan'): None})


def get_local_args(kwargs: dict) -> dict:
    return {k: v for k, v in kwargs.items() if not any([k.startswith('_'), k == 'self'])}


def convert_camel_case_to_space_delimited(s: str) -> str:
    return re.sub("([a-z])([A-Z])", r"\g<1> \g<2>", s)


def concat_lists(*args) -> list:
    return [v for ls in args for v in ls]


def keep_alphabetical_characters(name: str) -> str:
    return ''.join(s for s in name if s.isalpha()).lower()


def calc_average(values: Iterable[int | float]) -> float:
    values = list(values)
    return sum(values) / len(list(values))


def clean_string(
        input_string: str,
        characters_to_remove: str | list[str] = (',', ' ', ';'),
        is_remove_text_between_parentheses: bool = True,
        is_remove_text_between_brackets: bool = True
) -> str:
    if not isinstance(characters_to_remove, (str, tuple)):
        characters_to_remove = [characters_to_remove]

    for s in characters_to_remove:
        input_string = input_string.replace(s, '')

    if is_remove_text_between_parentheses:
        input_string = re.sub("[(].*?[)]", "", input_string)

    if is_remove_text_between_brackets:
        input_string = re.sub("[[].*?[]]", "", input_string)

    return input_string


def calc_vector_percentage(vector: int | float | Iterable) -> list:
    if not isinstance(vector, Iterable):
        vector = [vector]
    assert all([v >= 0 for v in vector]), "Negative values are not allowed when calculating a vector's percentage"
    assert sum(vector) > 0, "At least on item must be greater than 0 when calculating a vector's percentage"

    return [v / sum(vector) * 100 for v in vector]


def print_holos_msg(
        is_print_message: bool,
        holos_message: str
) -> Callable | None:
    return print(holos_message) if is_print_message else None
