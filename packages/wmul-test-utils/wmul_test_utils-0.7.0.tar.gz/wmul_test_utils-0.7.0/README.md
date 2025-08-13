# WMUL-FM Test Untilities

These are utilities that help with testing WMUL-FM's other python modules.

1. `make_namedtuple` creates one-off named tuples for concisely passing data from the fixture method to the test
    methods.

2. `generate_true_false_matrix_from_named_tuple` creates a list of true and false values, and a list of corresponding
    ids, to be passed into a pytest test fixture.

3. `generate_true_false_matrix_from_list_of_strings` is a convenience function. If you give it a string name, and a
    list of strings, it will create a named tuple from those and then call
    `generate_true_false_matrix_from_named_tuple`.

4. `generate_combination_matrix_from_dataclass` When given a dataclass (the class, not an instance), whose fields are
    all either boolean or enums, it will return two lists. The first list will contain instances of the dataclass
    covering all possible values of the fields. The second list will be the test_ids of those instances. These are
    indended to be passed to a pytest fixture.

5. `assert_has_only_these_calls` receives a `unittest.mock` object and asserts that it has been called with the
    specified calls and only the specified calls. The counts are compared and then the `mock_calls` list is checked for
    the calls.

6. `assert_lists_contain_same_items` asserts that every item in list one is also in list2 and vice-versa, in any order.

7. `random_case_string` will take an input string and generate a new string from it with the case randomized.

8. `multiple_random_case_strings` will take an input string, and an optional number of iterations, and return a list of
    strings with the case randomized. (By calling `random_case_string` multiple times.)

9. `sequential_dates` Generates a series of sequential dates in blocks of 10.

## make_namedtuple(class_name, **fields)

`class_name`: The name of the tuple class. Same as `namedtuple(class_name=)`.

`fields`: A keyword dictionary of field names and values. The names are the same as `namedtuple(field_names=)`.

`returns` A namedtuple of type `class_name`, with `field_names` corresponding to the keys of the fields dictionary and
    field values corresponding to the values of the fields dictionary.

```python
enterprise = make_namedtuple("Starship", name="U.S.S. Enterprise", registry_number="NCC-1701")
```

is the same as

```python
starship_tuple = namedtuple("Starship", ["name", "registry_number"])
enterprise = starship_tuple("U.S.S. Enterprise", "NCC-1701")
```

This is useful when you want to make a one-off namedtuple. It can be used to pass data concisely from a testing
    fixture to the test methods.

## generate_true_false_matrix_from_namedtuple(input_namedtuple)

`input_namedtuple` A named tuple whose fields will be used to generate the True False matrix.

`returns` Two lists: true_false_matrix and test_ids. The True-False matrix is a list of the namedtuples that is of
    size len(input_tuple) and with the fields set to every combination of True and False. The list of ids is a list of
    strings that describe the corresponding tuples.

Given: `input_tuple = namedtuple("burger_toppings", ["with_cheese", "with_ketchup", "with_mustard"])`

`true_false_matrix` will be:  

```python
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
```

and `test_ids` will be:

```python
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
```

Note that true_false_matrix is a list of namedtuples and test_ids is a list of the string representations of those same
 namedtuples.

## generate_true_false_matrix_from_list_of_strings(name, input_strings)

A convenience function. It takes a string name and a list of strings, and returns the true-false matrix built from
    those values.

```python
generate_true_false_matrix_from_list_of_strings(
    "burger_toppings",
    ["with_cheese", "with_ketchup", "with_mustard"]
)
```

is the equivalent of

```python
burger_toppings = namedtuple(
    "burger_toppings", 
    ["with_cheese", "with_ketchup", "with_mustard"]
)
generate_true_false_matrix_from_namedtuple(burger_toppings)
```

## generate_combination_matrix_from_dataclass(input_dataclass: dataclasses.dataclass) -> list

When given a dataclass (the class, not an instance), whose fields are all either boolean or enums, it will return
    two lists. The first list will contain instances of the dataclass covering all possible values of the fields.
    The second list will be the test_ids of those instances. If the dataclass provides a .test_id(self) function,
    that function will be used to generate the test_ids. Otherwise, the dataclass's \_\_str__(self) function will be
    used.

Function will generate up to a maximum of 1,000,000 instances. That limit was chosen arbitrarily and may be
    changed with testing.

`input_dataclass` A dataclass (not an instance), whose fields are all either boolean or enums.  
`returns` Two lists: dataclass_matrix and test_ids. dataclass_matrix is the list of instances of input_dataclass
    covering all possible values of the fields. test_ids is the list of strings that describe those instances.  
`raises TypeError` If input_dataclass is not a dataclass or is an instance of a dataclass.  
`raises TypeError` If any of the fields of the dataclass are not a subclass of either bool or Enum.  
`raises ValueError` If the total number of possible values excees 1,000,000.

Given:

```python
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

```

`dataclass_matrix` will be:

```python
[
    Car(runs=True, color=Colors.BLACK),
    Car(runs=True, color=Colors.BROWN),
    Car(runs=True, color=Colors.RED),
    Car(runs=False, color=Colors.BLACK),
    Car(runs=False, color=Colors.BROWN),
    Car(runs=False, color=Colors.RED)
]
```

`test_ids` will be:

```python
[
    "Car(runs=True, color=Colors.BLACK)",
    "Car(runs=True, color=Colors.BROWN)",
    "Car(runs=True, color=Colors.RED)",
    "Car(runs=False, color=Colors.BLACK)",
    "Car(runs=False, color=Colors.BROWN)",
    "Car(runs=False, color=Colors.RED)"
]
```

## assert_has_only_these_calls(mock, calls, any_order=False)

`mock` a `unittest.mock` object.

`calls` a list of calls.

If `any_order` is False (the default) then the calls must be sequential.

If `any_order` is True then the calls can be in any order, but they must all appear in `mock_calls`.

assert the mock has been called with the specified calls and only the specified calls. The counts are compared and
    then `assert_has_calls` is called.

This is the natural continuation of `assert_called_once_with` and is based on that method.

## assert_lists_contain_same_items(list1, list2)

Asserts that every item in list one is also in list2 and vice-versa, in any order. If they have to be in the same
    order, then you should use list1 == list2.

`list1` The first list to compare.  
`list2` The second list to compare.  
`raises AssertionError` If any item in one list is not also in the other list.  

## FieldToReplace

This class is used by the `replace_with_fake_data` method. A list of these objects is passed to
    `replace_with_fake_data` to describe which fields on the input_object need to be replaced and how.

`field_name` (str): The name of the field on the object that is to be replaced.  

`replacement_function` (callable): The return value of this function will be set as the new value of the field.
    The function must take either no arguments (if pass_existing_value is False), or one positional argument
    (if pass_existing_value is True and existing_value_kwarg is falsy), or one key-work argument (if
    pass_existing_value is True and existing_value_kwarg is a string).  

`pass_existing_value` (bool): If this is set to true, then the existing value of the field will be passed to the
    replacement_function. Defaults to False.  

`existing_value_kwarg` (str): If this is set to a truthy value and pass_existing_value is True, then the existing
    value will be passed to replacement_function with this string as the keyword. If pass_existing_value is
    False, then this value will be ignored. Defaults to empty string, a falsy value.

Examples:  
    See `replace_with_fake_data`

## replace_with_fake_data(input_object: object, fields_to_replace: List[FieldToReplace], error_if_non_existant = True) -> object

Makes a shallow copy of input_object, then replaces fields of input_object with fake data generated by a
    passed-in function.

Args:  
`input_object` (object): The object whose fields are to be replaced.  

`fields_to_replace` (List[FieldToReplace]): A list of `FieldToReplace`s. All of the fields on input_object will
    be replaced using the function provided in FieldToReplace.  

`error_if_non_existant` (bool, optional): If True, raise AttributeError (from getattr) if a provided field does
    not already exist. If False, any non-existant fields will be added and set to the value provided by the
    function. Defaults to True.  

Returns:  
`object`: A shallow copy of input_object, with the fields replaced by the values of the provided functions.

Examples:  
Using faker <https://github.com/joke2k/faker> to generate new text.

```python

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
```

`modified_object1` will be a shallow copy of `obj1` with the `.name` field replaced by the value of the `fake.text`
function.

```python
fields_to_replace2 = [
    FieldToReplace(field_name="name", replacement_function=fake.name),
    FieldToReplace(field_name="age", replacement_function=lambda: fake.random_int(1, 99)),
    FieldToReplace(field_name="tricorder", replacement_function=object),
]
modified_object2 = replace_with_fake_data(obj1, fields_to_replace2)
```

`modified_object2` will be a shallow copy of `obj1` with the `.name` field replaced by the value of the `fake.name`
function, `.age` replaced by a random `int` between 1 and 99, and `.tricorder` replaced by a new `object`.

```python
fields_to_replace3 = [FieldToReplace(field_name="foo", replacement_function=fake.name)]
modified_object3 = replace_with_fake_data(
    input_object=obj1, 
    fields_to_replace=fields_to_replace3, 
    error_if_non_existant=False
)
```

`modified_object3` will be a shallow copy of `obj1` with the `.foo` field added and set to the value of the
`fake.name` function.

```python
fields_to_replace4 = [FieldToReplace(field_name="foo", replacement_function=faker.name)]
modified_object4 = replace_with_fake_data(
    input_object=obj1, 
    fields_to_replace=fields_to_replace4, 
    error_if_non_existant=True
)
```

In this case, an `AttributeError` will be raised because `obj1.foo` does not exist.

```python
def backwards1(input_str):
    return "".join(reversed(input_str))

fields_to_replace5 = [
    FieldToReplace(field_name="name", replacement_function=backwards1, pass_existing_value=True)
]

modified_object5 = replace_with_fake_data(
    input_object=obj1,
    fields_to_replace=fields_to_replace5
)
```

`modified_object5` will be a shallow copy of `obj1` with the `.name` field set to `rednaxelA elyK`.

```python
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
```

`modified_object6` will be a shallow copy of `obj1` with the `.name` field set to `Rednaxela Elyk`.

## random_case_string(input_string: str, seed: Union[int, None] = None) -> str

`random_case_string` will take an input string and generate a new string from it with the case randomized.

Args:  
`input_string` The string from which to generate the randomly cased string.  
`seed` The seed for Python's `random` module.  
`returns` A version of `input_string` with the case of each letter randomized.

Given:

```python
input_string = "foobarbaz"

result = random_case_string(input_string=input_string)
```

`result` will be something like:

```python
'fOobArBaZ'
```

## multiple_random_case_strings(input_string: str, iterations: int = 5, seed: Union[int, None] = None) -> list[str]

`multiple_random_case_strings` will take an input string, and an optional number of iterations, and return a list of
    strings with the case randomized. (By calling `random_case_string` multiple times.)

Args:  
`input_string` The string from which to generate the randomly cased strings.  
`iterations` How many strings to return.  
`seed` The seed for Python's `random` module. The seed will be set inside this function and no seed will be passed to
    `random_case_string`. (Otherwise, `random_case_string` would return the same string every time it is called.)  
`returns` A version of `input_string` with the case of each letter randomized.

Given:

```python
input_string = "foobarbaz"

result_strings = multiple_random_case_strings(input_string=input_string, iterations=3)
```

`result_strings` will be something like:

```python
expected_strings = [
    'fOobArBaZ',
    'FOobArBaZ',
    'FoObaRBaZ'
]
```

## sequential_dates(start_date: Union[datetime, None] = None, span: Union[timedelta, None] = None, step: Union [timedelta, None] = None)

Generates a series of sequential dates in blocks of 10.

Generates a block of 10 random dates between start_date and start_date + span.

Sorts those dates.

Yields them individually.

After the first 10 dates are exhausted, resets start_date to end_date + step and repeats.

Args:  
`start_date (Union[datetime, None], optional)` The initial starting date. Defaults to January 1, 2000.  
`span (Union[timedelta, None], optional)` The span is added to the starting date to create the end date.
    Each block of 10 dates will be between the start_date and the end_date. Defaults to 365 days.  
`step (Union[timedelta, None], optional)` After the first block of 10 dates is exhausted, this value is added to
    the end_date to create a new start_date. Defaults to 1 day.

Yields:  
`datetime` A ordered sequence of datetimes.
