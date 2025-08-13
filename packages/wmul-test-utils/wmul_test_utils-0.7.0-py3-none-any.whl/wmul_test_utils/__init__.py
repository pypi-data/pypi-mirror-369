"""
@Author = 'Michael Stanley'

These are utilities that help with testing.

make_namedtuple creates one-off named tuples for concisely passing data from the fixture method to the test methods.

generate_true_false_matrix_from_named_tuple creates a list of true and false values, and a list of corresponding ids,
to be passed into a test fixture.

generate_true_false_matrix_from_list_of_strings is a convenience function. It takes a string name and a list of 
strings, and returns the true-false matrix built from those values. 

generate_combination_matrix_from_dataclass creates a list of instances of a dataclass containing all the possible 
values of the fields of that dataclass. Provided all the fields are either bool or enum and that the total number of
possible values is less than 1,000,000.

assert_has_only_these_calls asserts that the mock has been called with the specified calls and only the specified 
calls. 

assert_lists_contain_same_items checks that two lists contain all of the same items, in any order.

FieldsToReplace and replace_with_fake_data will replace the fields of an object with fake data. 

random_case_string will take an input string and generate a new string from it with the case randomized.

multiple_random_case_strings will take an input string, and an optional number of iterations, and return a list of 
strings with the case randomized. (By calling random_case_string multiple times.)

sequential_dates Generates a series of sequential dates in blocks of 10.

============ Change Log ============
08/12/2025 = Add sequential_dates

05/23/2025 = Add random_case_string and multiple_random_case_strings

01/27/2025 = Add FieldsToReplace and replace_with_fake_data.

02/20/2024 = Add generate_combination_matrix_from_dataclass and assert_lists_contain_same_items.
             Add comments to generate_true_false_matrix_from_namedtuple.

01/17/2023 = Added generate_true_false_matrix_from_list_of_strings

01/11/2023 = Added assert_has_only_these_calls

10/01/2020 = Created.

============ License ============
Copyright (C) 2020, 2023-2025 Michael Stanley

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
__version__ = "0.7.0"

import dataclasses
import random
from collections import namedtuple
from collections.abc import Callable
from copy import copy
from datetime import datetime, timedelta
from enum import Enum
from faker import Faker
from itertools import product
from typing import List, Union
from unittest.mock import Mock


def make_namedtuple(class_name: str, **fields):
    """Generates a named tuple from a class name and a dictionary of fields and values.

    enterprise = make_namedtuple("Starship", name="U.S.S. Enterprise", registry_number="NCC-1701")

    is the same as

    starship_tuple = namedtuple("Starship", ["name", "registry_number"])
    enterprise = starship_tuple("U.S.S. Enterprise", "NCC-1701")

    This is useful when you want to make a one-off namedtuple. It can be used to pass data concisely from a testing
    fixture to the test methods.

    Args:
        class_name (str): The name of the tuple class. Same as namedtuple(class_name=).
        fields: A keyword dictionary of field names and values. The names are the same as namedtuple(field_names=)

    Returns:
        A namedtuple of type class_name, with field_names corresponding to the keys of the fields dictionary and
        field values corresponding to the values of the fields dictionary.
    """


    return namedtuple(class_name, fields)(*fields.values())


def generate_true_false_matrix_from_namedtuple(input_namedtuple) -> tuple[List, List[str]]:
    """Genereates a true/false matrix from a named tuple. 

    Given a named tuple, it generates two lists. The first list is a list of named tuples with the fields set to every
    combination of true and false. The second list is a list of strings that describe the corresponding tuples.

    Given: input_tuple = namedtuple("burger_toppings", ["with_cheese", "with_ketchup", "with_mustard"])

    true_false_matrix will be:
    [
        burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=False),
        burger_toppings(with_cheese=True,  with_ketchup=False, with_mustard=False),
        burger_toppings(with_cheese=False, with_ketchup=True,  with_mustard=False),
        burger_toppings(with_cheese=True,  with_ketchup=True,  with_mustard=False),
        burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=True),
        burger_toppings(with_cheese=True,  with_ketchup=False, with_mustard=True),
        burger_toppings(with_cheese=False, with_ketchup=True,  with_mustard=True),
        burger_toppings(with_cheese=True,  with_ketchup=True,  with_mustard=True)
    ]

    and test_ids will be:
    [
        'burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=False)',
        'burger_toppings(with_cheese=True,  with_ketchup=False, with_mustard=False)',
        'burger_toppings(with_cheese=False, with_ketchup=True,  with_mustard=False)',
        'burger_toppings(with_cheese=True,  with_ketchup=True,  with_mustard=False)',
        'burger_toppings(with_cheese=False, with_ketchup=False, with_mustard=True)',
        'burger_toppings(with_cheese=True,  with_ketchup=False, with_mustard=True)',
        'burger_toppings(with_cheese=False, with_ketchup=True,  with_mustard=True)',
        'burger_toppings(with_cheese=True,  with_ketchup=True,  with_mustard=True)'
    ]

    Note that true_false_matrix is a list of namedtuples and test_ids is the list of the string representations of
    those same namedtuples.

    Args:
        input_namedtuple (Named Tuple): A named tuple whose fields will be used to generate the True False matrix.

    Returns:
        tuple[List, List[str]]: Two lists: true_false_matrix and test_ids. The True-False matrix is a list of the 
        namedtuples that is of size len(input_tuple) and with the fields set to every combination of True and False.
        The list of ids is a list of strings that describe the corresponding tuples.
    
    Raises:
        ValueError: If input_namedtuple does not have at least one field.
    """    
    number_of_fields = len(input_namedtuple._fields)
    
    if number_of_fields < 1:
        raise ValueError("The named tuple passed in must have at least one field.")

    powers_of_two = {2**i: i for i in range(number_of_fields)}
    '''
    Creates a dictionary where the powers of two are mapped to their exponents for the exponents from
    0 to <number_of_fields
    E.G. given number_of_fields = 3, then powers_of_two = {1: 0, 2: 1, 4: 2}
    '''

    these_field_values = [False for i in range(number_of_fields)]
    '''
    Creates a list of False values for each field in the namedtuple.
    This list will be used and manipulated to create instances of the namedtuple .
    '''

    true_false_matrix = []
    test_ids = []

    for i in range(1, 2**number_of_fields + 1):
        this_combination = input_namedtuple._make(these_field_values)
        '''
        Make an instance of the namedtuple using the current value of these_field_values. 
        '''

        true_false_matrix.append(this_combination)
        test_ids.append(str(this_combination))

        for this_power_of_two, corresponding_index in powers_of_two.items():
            if i % this_power_of_two == 0:
                these_field_values[corresponding_index] = not these_field_values[corresponding_index]
        '''
        This for loop goes through the powers_of_two generated above. When it finds one that divided evenly 
        into the current value of i, it flips the value in the corresponding index in these_field_values.
        This means that the first value in these_field_values will be flipped every iteration, 
        the second value will be flipped every other iteration, the third value will be flipped every 
        fourth iteration, etc.
        '''

    return true_false_matrix, test_ids


def generate_true_false_matrix_from_list_of_strings(name: str, input_strings: List[str]) -> tuple[List, List[str]]:
    """A convenience function to convert a name and a list of strings into a true/false matrix.
    
    It takes a name and a list of strings, calls namedtuple with those values and then calls 
    generate_true_false_matrix_from_namedtuple with that named tuple. 

    generate_true_false_matrix_from_list_of_strings(
        "burger_toppings", 
        ["with_cheese", "with_ketchup", "with_mustard"]
    )

    is the equivalent of

    burger_toppings = namedtuple(
        "burger_toppings", 
        ["with_cheese", "with_ketchup", "with_mustard"]
    )
    generate_true_false_matrix_from_namedtuple(burger_toppings)

    Args:
        name (str): The name of the tuple class. Will be passed to namedtuple as the class name.
        input_strings (List[str]): A list of strings that will be used to generate the fields of the named tuple.

    Returns:
        Two lists: true_false_matrix and test_ids. The True-False matrix is a list of the namedtuples
        that is of size len(input_strings) and with the fields set to every combination of True and False.
        The list of ids is a list of strings that describe the corresponding tuples.
    """
    named_tuple_for_generating = namedtuple(name, input_strings)
    return generate_true_false_matrix_from_namedtuple(named_tuple_for_generating)


def generate_combination_matrix_from_dataclass(input_dataclass) -> tuple[list, list]:
    """Generates a list of input_dataclass using all possible values.

    When given a dataclass (the class, not an instance), whose fields are all either boolean or enums, it will return 
    two lists: dataclass_matrix and test_ids. 
    
    dataclass_matrix will contain instances of the dataclass covering all possible values of the fields. 
    
    test_ids will be the test ids of those instances. If the dataclass provides a .test_id(self) function, that 
    function will be used to generate the test_ids. Otherwise, the dataclass's __str__(self) function will be used.

    Function will generate up to a maximum of 1,000,000 instances. That limit was chosen arbitrarily and may be 
    changed with testing.

    Given:

    class Colors(Enum):
        BROWN = 0
        BLACK = 1
        RED = 2

    @dataclass
    class Car:
        runs: bool
        color: Colors

        def test_id(self):
            return f"Car(runs={self.runs}, color={self.color})"

    The first list will be:
    [
        Car(runs=True, color=Colors.BLACK),
        Car(runs=True, color=Colors.BROWN),
        Car(runs=True, color=Colors.RED),
        Car(runs=False, color=Colors.BLACK),
        Car(runs=False, color=Colors.BROWN),
        Car(runs=False, color=Colors.RED)
    ]

    The second list will be:
    [
        "Car(runs=True, color=Colors.BLACK)",
        "Car(runs=True, color=Colors.BROWN)",
        "Car(runs=True, color=Colors.RED)",
        "Car(runs=False, color=Colors.BLACK)",
        "Car(runs=False, color=Colors.BROWN)",
        "Car(runs=False, color=Colors.RED)"
    ]

    Args:
        input_dataclass (dataclass): A dataclass (not an instance), whose fields are all either boolean or enums.

    Raises:
        TypeError: If input_dataclass is not a dataclass  
        TypeError: If input_dataclass is an instance of a dataclass.
        TypeError: If any of the fields of the dataclass are not a subclass of either bool or Enum.
        ValueError: If the total number of possible values excees 1,000,000.

    Returns:
        tuple[list, list]: dataclass_matrix and test_ids. dataclass_matrix is the list of instances of input_dataclass 
        covering all possible values of the fields. test_ids is the list of strings that describe those instances.
    """    
    if not dataclasses.is_dataclass(input_dataclass):
        raise TypeError("input_dataclass must be of type dataclass")
    if not isinstance(input_dataclass, type):
        raise TypeError("input_dataclass must be a dataclass and not an instance of a dataclass")

    if hasattr(input_dataclass, "test_id"):
        string_function = input_dataclass.test_id
    else:
        string_function = input_dataclass.__str__

    all_field_values = []
    total_number_of_values = 1
    for field in dataclasses.fields(input_dataclass):   
        if issubclass(field.type, bool):
            this_field_values = [
                {
                    field.name: True
                },
                {
                    field.name: False
                }
            ]
        elif issubclass(field.type, Enum):
            this_field_values = [
                { field.name: value } for value in field.type
            ]
        else:
            raise TypeError(
                f"All of the fields of the dataclass must be of either {bool} or {Enum}," 
                f"field {field} is of {field.type}."
            )
        total_number_of_values *= len(this_field_values)
        all_field_values.append(this_field_values)
    
    if total_number_of_values > 1_000_000:
        # Sanity check. Chosen limit is arbitrary and may be changed with testing.
        raise ValueError(f"The total possible combinations of values exceeds safe limits. A total of {total_number_of_values} combinations is possible given the inputs. The safe limit is set at 1,000,000.")
    
    all_combinations_of_values = product(*all_field_values)
    
    dataclass_matrix = []
    test_ids = []

    for combination in all_combinations_of_values:
        unified_dict_for_item = {}
        for sub_dict in combination:
            unified_dict_for_item.update(sub_dict)
        combination_as_a_dataclass_instance = input_dataclass(**unified_dict_for_item)
        dataclass_matrix.append(combination_as_a_dataclass_instance)
        test_ids.append(string_function(combination_as_a_dataclass_instance))

    return dataclass_matrix, test_ids


def assert_has_only_these_calls(mock: Mock, calls: list, any_order: bool=False) -> None:
    """assert the mock has been called with the specified calls and only
    the specified calls.

    The counts are compared and then the `mock_calls` list is checked for the calls.

    This is the natural continuation of `assert_called_once_with` and is based on that method.

    Args:
        mock (Mock): A unittest.mock.Mock or other object that supports .call_count and .assert_has_calls
        calls (list of unittest.mock.call): A list of unittest.mock.call's that must all be present.
        any_order (bool, optional): If False, then the calls must be sequential. If True, then the calls can be in any 
        order, but they must all appear in `mock_calls`. Defaults to False.

    Raises:
        AssertionError: If any of the calls are not present in the mock or if any additional calls are present.
    """    
    provided_call_count = len(calls)

    if not mock.call_count == provided_call_count:
        msg = f"Expected {mock._mock_name or 'mock'} to be called " \
              f" {provided_call_count} times. Called {mock.call_count} " \
              f"times.{mock._calls_repr()}"
        raise AssertionError(msg)
    mock.assert_has_calls(calls, any_order)


def assert_lists_contain_same_items(list1: list, list2: list) -> None:
    """Asserts that every item in list one is also in list2 and vice-versa, in any order. If they have to be in the 
    same order, use list1 == list2.
    """
    for item in list1:
        assert item in list2
    for item in list2:
        assert item in list1


@dataclasses.dataclass
class FieldToReplace:
    """This class is used by the `replace_with_fake_data` method. A list of these objects is passed to 
    `replace_with_fake_data` to describe which fields on the input_object need to be replaced and how.

    Examples:
        See `replace_with_fake_data`

    Args:
        field_name (str): The name of the field on the object that is to be replaced.
        replacement_function (Callable): The return value of this function will be set as the new value of the field. 
            The function must take either no arguments (if pass_existing_value is False), or one positional argument 
            (if pass_existing_value is True and existing_value_kwarg is falsy), or one key-word argument (if 
            pass_existing_value is True and existing_value_kwarg is a string).
        pass_existing_value (bool): If this is set to true, then the existing value of the field will be passed to 
            the replacement_function. Defaults to False.
        existing_value_kwarg (str): If this is set to a truthy value and pass_existing_value is True, then the existing
            value will be passed to replacement_function with this string as the keyword. If pass_existing_value is 
            False, then this value will be ignored. Defaults to empty string, a falsy value.
    """
    field_name: str
    replacement_function: Callable
    pass_existing_value: bool = False
    existing_value_kwarg: str = ""


def replace_with_fake_data(input_object: object, fields_to_replace: List[FieldToReplace], error_if_non_existant = True) -> object:
    """Makes a shallow copy of input_object, then replaces fields of input_object with fake data generated by a 
    passed-in function.
    
    Args:
        input_object (object): The object whose fields are to be replaced.
        fields_to_replace (List[FieldToReplace]): A list of `FieldToReplace`s. All of the fields on input_object will 
            be replaced using the function provided in FieldToReplace.  
        error_if_non_existant (bool, optional): If True, raise AttributeError (from getattr) if a provided field does 
            not already exist. If False, any non-existant fields will be added and set to the value provided by the 
            function. Defaults to True.
    Returns:
        A shallow copy of input_object, with the fields replaced by the values of the provided functions.

    Raises:
        AttributeError if error_if_non_existant is True (Default) and field.field_name does not exist.

    Examples:
        Using faker to generate new text.

            from faker import Faker
            fake = Faker()

            @dataclass
            class DummyObject:
                name: str
                address: str
                age: int
                tricorder: object
            
            obj1 = DummyObject(
                name="Kyle Alexander",
                address="3986 Guerra Ports Suite 164\nWest Kimfurt, KY 22894",
                age=4,
                tricorder=object()
            )

            fields_to_replace1 = [
                FieldToReplace(
                    field_name="name"
                    replacement_function=fake.text
                )
            ]

            modified_object1 = replace_with_fake_data(obj1, fields_to_replace1)

        `modified_object1` will be a shallow copy of obj1 with the .name field replaced by the value of the fake.text 
        function.

            fields_to_replace2 = [
                FieldToReplace(field_name="name", replacement_function=fake.name),
                FieldToReplace(field_name="age", replacement_function=lambda: fake.random_int(1, 99)),
                FieldToReplace(field_name="tricorder", replacement_function=object),
            ]
            modified_object2 = replace_with_fake_data(obj1, fields_to_replace2)

        `modified_object2` will be a shallow copy of obj1 with the .name field replaced by the value of the fake.name
        function, .age replaced by a random int between 1 and 99, and .tricorder replaced by a new object.

            fields_to_replace3 = [FieldToReplace(field_name="foo", replacement_function=fake.name)]
            modified_object3 = replace_with_fake_data(
                input_object=obj1, 
                fields_to_replace=fields_to_replace3, 
                error_if_non_existant=False
            )
            
        `modified_object3` will be a shallow copy of obj1 with the .foo field added and set to the value of the 
        fake.name function.

            fields_to_replace4 = [FieldToReplace(field_name="foo", replacement_function=faker.name)]
            modified_object4 = replace_with_fake_data(
                input_object=obj1, 
                fields_to_replace=fields_to_replace4, 
                error_if_non_existant=True
            )
        
        In this case, an AttributeError will be raised because obj1.foo does not exist.

            def backwards1(input_str):
                return "".join(reversed(input_str))
            
            fields_to_replace5 = [
                FieldToReplace(field_name="name", replacement_function=backwards1, pass_existing_value=True)
            ]
            
            modified_object5 = replace_with_fake_data(
                input_object=obj1,
                fields_to_replace=fields_to_replace5
            )

        `modified_object5` will be a shallow copy of obj1 with the .name field set to `rednaxelA elyK`.

            def backwards2(*, input_str, titlecase=True):
                reversed_string = "".join(reversed(input_str))
                if titlecase:
                    return reversed_string.title()
                else:
                    return reversed_string
            
            fields_to_replace6 = [
                FieldToReplace(field_name="name", replacement_function=backwards2, pass_existing_value=True)
            ]
            
            modified_object6 = replace_with_fake_data(
                input_object=obj1,
                fields_to_replace=fields_to_replace6
            )

        `modified_object6` will be a shallow copy of obj1 with the .name field set to `Rednaxela Elyk`.
    """
    copy_object = copy(input_object)
    for field in fields_to_replace:
        if error_if_non_existant:
            existing_value = getattr(copy_object, field.field_name) 
            # Will raise AttributeError if field.field_name doesn't exist.
        else:
            existing_value = getattr(copy_object, field.field_name, None)
            # Will return None if field.field_name doesn't exist.
        func_arg = []
        func_kwarg = dict()
        if field.pass_existing_value:
            if field.existing_value_kwarg:
                func_kwarg = { field.existing_value_kwarg: existing_value }
            else:
                func_arg = [getattr(copy_object, field.field_name)]
        new_value = field.replacement_function(*func_arg, **func_kwarg)
        setattr(copy_object, field.field_name, new_value)
    return copy_object


def random_case_string(input_string: str, seed: Union[int, None] = None) -> str:
    """Mangles input_string by randomly changing the case of every letter."""
    if seed:
        random.seed(seed)
    return ''.join(random.choice((str.upper, str.lower))(char) for char in input_string)


def multiple_random_case_strings(input_string: str, iterations: int = 5, seed: Union[int, None] = None) -> list[str]:
    """Generates multiple versions of input_string with the case mangled by random_case_string."""
    if seed:
        random.seed(seed)
        # Set the seed here. If the seed is passed to random_case_string, it will regenerate the same string for each 
        # iteration.
    return [random_case_string(input_string=input_string) for _ in range(iterations)]


def sequential_dates(
        start_date: Union[datetime, None] = None, 
        span: Union[timedelta, None] = None, 
        step: Union[timedelta, None] = None
    ):
    """Generates a series of sequential dates in blocks of 10.
    
    Generates a block of 10 random dates between start_date and start_date + span. 
    
    Sorts those dates. 

    Yields them individually.

    After the first 10 dates are exhausted, resets start_date to end_date + step and repeats.

    Args:
        start_date (Union[datetime, None], optional): The initial starting date. Defaults to January 1, 2000.
        span (Union[timedelta, None], optional): The span is added to the starting date to create the end date. 
            Each block of 10 dates will be between the start_date and the end_date. Defaults to 365 days.
        step (Union[timedelta, None], optional): After the first block of 10 dates is exhausted, this value is added to
            the end_date to create a new start_date. Defaults to 1 day.

    Yields:
        datetime: A ordered sequence of datetimes.
    """    
    if not start_date:
        start_date = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
    if not span:
        span = timedelta(days=365)
    if not step:
        step = timedelta(days=1)
    faker = Faker()
    
    while True:
        end_date = start_date + span
        generated_dates = []
        for _ in range(10):
            this_date = faker.date_time_between_dates(
                datetime_start = start_date,
                datetime_end = end_date
            )
            generated_dates.append(this_date)

        generated_dates.sort()

        yield from generated_dates

        start_date = end_date + step
