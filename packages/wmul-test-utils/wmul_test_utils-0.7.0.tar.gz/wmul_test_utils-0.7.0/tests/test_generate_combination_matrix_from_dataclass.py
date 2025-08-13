"""
@Author = 'Michael Stanley'

============ Change Log ============
02/19/2024 = Created.

============ License ============
Copyright (C) 2024 Michael Stanley

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
from dataclasses import dataclass
from enum import Enum
from wmul_test_utils import generate_combination_matrix_from_dataclass, assert_lists_contain_same_items
import pytest

class _Colors(Enum):
    BROWN = 0
    BLACK = 1
    RED = 2
    ORANGE = 3
    YELLOW = 4
    GREEN = 5
    BLUE = 6
    VIOLET = 7
    GREY = 8
    WHITE = 9
    SILVER = 10
    GOLD = 11
    INDIGO = 12
    PURPLE = 13
    HUNTER_GREEN = 14
    CHARCOAL = 15
    SKY_BLUE = 16
    LIME_GREEN = 17
    PINK = 18
    RAW_UMBER = 19
    

def test_not_a_dataclass():
    class Car:
        def __init__(self, runs: bool, color: _Colors) -> None:
            self.runs = runs
            self.color = color

    with pytest.raises(TypeError) as te:
        generate_combination_matrix_from_dataclass(Car)

    assert "input_dataclass must be of type dataclass" in str(te.value)


def test_instance_of_a_dataclass():
    @dataclass
    class Car:
        runs: bool
        color: _Colors

    x = Car(runs=True, color=_Colors.RED)

    with pytest.raises(TypeError) as te:
        generate_combination_matrix_from_dataclass(x)

    assert "input_dataclass must be a dataclass and not an instance of a dataclass" in str(te.value)


def test_dataclass_all_fields_valid_types():
    @dataclass
    class Car:
        runs: bool
        color: _Colors

    generate_combination_matrix_from_dataclass(Car)


def test_dataclass_one_field_type_invalid():
    @dataclass
    class Car:
        runs: bool
        color: _Colors
        name: str

    with pytest.raises(TypeError) as te:
        generate_combination_matrix_from_dataclass(Car)

    assert "All of the fields of the dataclass must be of either" in str(te.value)

def test_too_many_possible_values():
    @dataclass
    class Car:
        hood_color: _Colors
        front_fender_color: _Colors
        door_color: _Colors
        rear_fender_color: _Colors
        trunk_color: _Colors

    with pytest.raises(ValueError) as ve:
        generate_combination_matrix_from_dataclass(Car)

    assert "The total possible combinations of values exceeds safe limits. A total of" in str(ve.value)

class _ShortColors(Enum):
    BROWN = 0
    BLACK = 1
    RED = 2

def test_all_combinations_of_values_no_str_function():
    @dataclass
    class Car:
        runs: bool
        color: _ShortColors

        def test_id(self):
            return f"Car(runs={self.runs}, color={self.color})"

    result_instances, result_strings = generate_combination_matrix_from_dataclass(Car)

    expected_result_instances = [
        Car(runs=True, color=_ShortColors.BLACK),
        Car(runs=True, color=_ShortColors.BROWN),
        Car(runs=True, color=_ShortColors.RED),
        Car(runs=False, color=_ShortColors.BLACK),
        Car(runs=False, color=_ShortColors.BROWN),
        Car(runs=False, color=_ShortColors.RED)
    ]

    expected_result_strings = [
        "Car(runs=True, color=_ShortColors.BLACK)",
        "Car(runs=True, color=_ShortColors.BROWN)",
        "Car(runs=True, color=_ShortColors.RED)",
        "Car(runs=False, color=_ShortColors.BLACK)",
        "Car(runs=False, color=_ShortColors.BROWN)",
        "Car(runs=False, color=_ShortColors.RED)"
    ]

    assert_lists_contain_same_items(result_instances, expected_result_instances)
    assert_lists_contain_same_items(result_strings, expected_result_strings)


def test_all_combinations_of_values_no_test_id_function():
    @dataclass
    class Car:
        runs: bool
        color: _ShortColors

        def __str__(self) -> str:
            return f"Car(runs={self.runs}, color={self.color})"

    result_instances, result_strings = generate_combination_matrix_from_dataclass(Car)

    expected_result_instances = [
        Car(runs=True, color=_ShortColors.BLACK),
        Car(runs=True, color=_ShortColors.BROWN),
        Car(runs=True, color=_ShortColors.RED),
        Car(runs=False, color=_ShortColors.BLACK),
        Car(runs=False, color=_ShortColors.BROWN),
        Car(runs=False, color=_ShortColors.RED)
    ]

    expected_result_strings = [
        "Car(runs=True, color=_ShortColors.BLACK)",
        "Car(runs=True, color=_ShortColors.BROWN)",
        "Car(runs=True, color=_ShortColors.RED)",
        "Car(runs=False, color=_ShortColors.BLACK)",
        "Car(runs=False, color=_ShortColors.BROWN)",
        "Car(runs=False, color=_ShortColors.RED)"
    ]

    assert_lists_contain_same_items(result_instances, expected_result_instances)
    assert_lists_contain_same_items(result_strings, expected_result_strings)

def test_all_combinations_of_values_both_test_id_and_str():
    @dataclass
    class Car:
        runs: bool
        color: _ShortColors

        def test_id(self):
            return f"Car(runs={self.runs}, color={self.color})"

        def __str__(self) -> str:
            return "This is the wrong function."

    result_instances, result_strings = generate_combination_matrix_from_dataclass(Car)

    expected_result_instances = [
        Car(runs=True, color=_ShortColors.BLACK),
        Car(runs=True, color=_ShortColors.BROWN),
        Car(runs=True, color=_ShortColors.RED),
        Car(runs=False, color=_ShortColors.BLACK),
        Car(runs=False, color=_ShortColors.BROWN),
        Car(runs=False, color=_ShortColors.RED)
    ]

    expected_result_strings = [
        "Car(runs=True, color=_ShortColors.BLACK)",
        "Car(runs=True, color=_ShortColors.BROWN)",
        "Car(runs=True, color=_ShortColors.RED)",
        "Car(runs=False, color=_ShortColors.BLACK)",
        "Car(runs=False, color=_ShortColors.BROWN)",
        "Car(runs=False, color=_ShortColors.RED)"
    ]

    assert_lists_contain_same_items(result_instances, expected_result_instances)
    assert_lists_contain_same_items(result_strings, expected_result_strings)
