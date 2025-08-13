"""
@Author = 'Michael Stanley'

============ Change Log ============
01/12/2023 = Created.

============ License ============
Copyright (C) 2023 Michael Stanley

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
import pytest
import wmul_test_utils
from collections import namedtuple


def test_zero_fields():
    test_object = namedtuple("burger_toppings", [])
    with pytest.raises(ValueError):
        result = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)


def test_object_no_fields_field():
    test_object = object()
    with pytest.raises(AttributeError):
        result = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)


def test_object_fields_no_len():
    class test_object_definition:
        def __init__(self, x):
            self._fields = x

    test_object = test_object_definition(5)
    with pytest.raises(TypeError):
        result = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)


def test_one_field():
    test_object = namedtuple("burger_toppings", ["with_cheese"])
    
    expected_matrix = [
        test_object(with_cheese=False),
        test_object(with_cheese=True)
    ]
    
    expected_ids = [
        'burger_toppings(with_cheese=False)',
        'burger_toppings(with_cheese=True)'
    ]
    
    result_matrix, result_ids = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)

    assert result_matrix == expected_matrix
    assert result_ids == expected_ids


def test_two_fields():
    test_object = namedtuple("burger_toppings", ["with_cheese", "with_ketchup"])
    
    expected_matrix = [
        test_object(with_cheese=False, with_ketchup=False),
        test_object(with_cheese=False, with_ketchup=True),
        test_object(with_cheese=True, with_ketchup=False),
        test_object(with_cheese=True, with_ketchup=True),
    ]
    
    expected_ids = [
        'burger_toppings(with_cheese=False, with_ketchup=False)',
        'burger_toppings(with_cheese=False, with_ketchup=True)',
        'burger_toppings(with_cheese=True, with_ketchup=False)',
        'burger_toppings(with_cheese=True, with_ketchup=True)',
    ]
    
    result_matrix, result_ids = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)

    assert sorted(result_matrix) == sorted(expected_matrix)
    assert sorted(result_ids) == sorted(expected_ids)


def test_three_fields():
    test_object = namedtuple("burger_toppings", ["with_cheese", "with_ketchup", "with_mustard"])
    
    expected_matrix = [
        test_object(with_cheese=False, with_ketchup=False, with_mustard=False),
        test_object(with_cheese=False, with_ketchup=False, with_mustard=True),
        test_object(with_cheese=False, with_ketchup=True, with_mustard=False),
        test_object(with_cheese=False, with_ketchup=True, with_mustard=True),
        test_object(with_cheese=True, with_ketchup=False, with_mustard=False),
        test_object(with_cheese=True, with_ketchup=False, with_mustard=True),
        test_object(with_cheese=True, with_ketchup=True, with_mustard=False),
        test_object(with_cheese=True, with_ketchup=True, with_mustard=True),
    ]
    
    expected_ids = [
        'burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=False)',
        'burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=True)',
        'burger_toppings(with_cheese=False, with_ketchup=True, with_mustard=False)',
        'burger_toppings(with_cheese=False, with_ketchup=True, with_mustard=True)',
        'burger_toppings(with_cheese=True, with_ketchup=False, with_mustard=False)',
        'burger_toppings(with_cheese=True, with_ketchup=False, with_mustard=True)',
        'burger_toppings(with_cheese=True, with_ketchup=True, with_mustard=False)',
        'burger_toppings(with_cheese=True, with_ketchup=True, with_mustard=True)',
    ]
    
    result_matrix, result_ids = wmul_test_utils.generate_true_false_matrix_from_namedtuple(test_object)

    assert sorted(result_matrix) == sorted(expected_matrix)
    assert sorted(result_ids) == sorted(expected_ids)


def test_generate_from_list_of_strings(mocker):
    mock_namedtuple = "mock_namedtuple"
    mock_make_namedtuple = mocker.Mock(return_value=mock_namedtuple)
    mocker.patch("wmul_test_utils.namedtuple", mock_make_namedtuple)

    mock_true_false_matrix = "mock_true_false_matrix"
    mock_generate_true_false_matrix = mocker.Mock(
        return_value=mock_true_false_matrix
        )
    mocker.patch(
        "wmul_test_utils.generate_true_false_matrix_from_namedtuple",
        mock_generate_true_false_matrix
    )

    mock_name = "mock_name"
    mock_input_strings = "mock_input_strings"

    result = wmul_test_utils.generate_true_false_matrix_from_list_of_strings(
        mock_name,
        mock_input_strings
    )

    mock_make_namedtuple.assert_called_once_with(mock_name, mock_input_strings)
    mock_generate_true_false_matrix.assert_called_once_with(mock_namedtuple)
    assert result == mock_true_false_matrix
