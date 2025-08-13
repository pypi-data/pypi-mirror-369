"""
@Author = 'Michael Stanley'

============ Change Log ============
01/24/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

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
from dataclasses import dataclass
from wmul_test_utils import FieldToReplace, replace_with_fake_data, make_namedtuple


@dataclass
class DummyObject:
    name: str
    address: str
    age: int
    tricorder: object


@pytest.fixture
def default_objects():
    obj1 = DummyObject(
        name="Kyle Alexander",
        address="3986 Guerra Ports Suite 164\nWest Kimfurt, KY 22894",
        age=4,
        tricorder=object()
    )

    obj2 = DummyObject(
        name="Samuel Shepard",
        address="183 Miguel Forge Apt. 475\nHelenborough, NH 09613",
        age=50,
        tricorder=object()
    )
    
    obj3 = DummyObject(
        name="Joshua Rogers",
        address="8302 Brian Stravenue Apt. 371\nAlexanderport, MD 40748",
        age=95,
        tricorder=object()
    )

    return make_namedtuple(
        "default_objects",
        obj1=obj1,
        obj2=obj2,
        obj3=obj3
    )


def test_empty_fields_list(default_objects):
    obj1 = default_objects.obj1
    modified_object = replace_with_fake_data(obj1, [])
    assert modified_object == obj1

def test_replace_name(default_objects, faker):
    obj1 = default_objects.obj1
    fields_to_replace = [FieldToReplace(field_name="name", replacement_function=faker.name)]
    modified_object = replace_with_fake_data(input_object=obj1, fields_to_replace=fields_to_replace)
    assert not modified_object == obj1
    faker.seed_instance(0)
    name = faker.name()
    assert modified_object.name == name
    assert not obj1.name == name
    assert obj1.address == modified_object.address
    assert obj1.age == modified_object.age
    assert obj1.tricorder == modified_object.tricorder


def test_replace_multiple_fields(default_objects, faker):
    obj1 = default_objects.obj1
    fields_to_replace = [
        FieldToReplace(field_name="name", replacement_function=faker.name),
        FieldToReplace(field_name="age", replacement_function=lambda: faker.random_int(1, 99)),
        FieldToReplace(field_name="tricorder", replacement_function=object),
    ]
    modified_object = replace_with_fake_data(input_object=obj1, fields_to_replace=fields_to_replace)
    assert not modified_object == obj1
    assert not obj1.name == modified_object.name
    assert obj1.address == modified_object.address
    assert not obj1.age == modified_object.age
    assert not obj1.tricorder == modified_object.tricorder


def test_modify_multiple_objects(default_objects, faker):
    obj1 = default_objects.obj1
    obj2 = default_objects.obj2
    obj3 = default_objects.obj3
    fields_to_replace = [
        FieldToReplace(field_name="name", replacement_function=faker.name),
        FieldToReplace(field_name="age", replacement_function=lambda: faker.random_int(1, 99)),
        FieldToReplace(field_name="tricorder", replacement_function=object),
    ]
    modified_object1 = replace_with_fake_data(input_object=obj1, fields_to_replace=fields_to_replace)
    assert not modified_object1 == obj1
    assert not obj1.name == modified_object1.name
    assert obj1.address == modified_object1.address
    assert not obj1.age == modified_object1.age
    assert not obj1.tricorder == modified_object1.tricorder

    modified_object2 = replace_with_fake_data(input_object=obj2, fields_to_replace=fields_to_replace)
    assert not modified_object2 == obj2
    assert not obj2.name == modified_object2.name
    assert not modified_object2.name == modified_object1.name
    assert obj2.address == modified_object2.address
    assert not obj2.age == modified_object2.age
    assert not obj2.tricorder == modified_object2.tricorder
    assert not modified_object2.tricorder == modified_object1.tricorder

    modified_object3 = replace_with_fake_data(input_object=obj3, fields_to_replace=fields_to_replace)
    assert not modified_object3 == obj3
    assert not obj3.name == modified_object3.name
    assert not modified_object3.name == modified_object2.name
    assert obj3.address == modified_object3.address
    assert not obj3.age == modified_object3.age
    assert not obj3.tricorder == modified_object3.tricorder
    assert not modified_object3.tricorder == modified_object2.tricorder


def test_trying_to_modify_nonexistant_no_error(default_objects, faker):
    obj1 = default_objects.obj1
    assert not hasattr(obj1, "foo")
    fields_to_replace = [FieldToReplace(field_name="foo", replacement_function=faker.name)]
    modified_object = replace_with_fake_data(
        input_object=obj1, 
        fields_to_replace=fields_to_replace, 
        error_if_non_existant=False
    )
    assert hasattr(modified_object, "foo")

def test_trying_to_modify_nonexistant_with_error(default_objects, faker):
    obj1 = default_objects.obj1
    assert not hasattr(obj1, "foo")
    fields_to_replace = [FieldToReplace(field_name="foo", replacement_function=faker.name)]
    with pytest.raises(AttributeError):
        modified_object = replace_with_fake_data(
            input_object=obj1, 
            fields_to_replace=fields_to_replace, 
            error_if_non_existant=True
        )

def test_pass_existing_value_positional(default_objects, mocker):
    obj1 = default_objects.obj1
    mock_replacement_value = "mock_replacement_value"

    replacement_function = mocker.Mock(
        return_value=mock_replacement_value
    )
    
    fields_to_replace = [
        FieldToReplace(field_name="name", replacement_function=replacement_function, pass_existing_value=True)
    ]
    
    modified_object = replace_with_fake_data(
        input_object=obj1,
        fields_to_replace=fields_to_replace
    )

    assert modified_object.name == mock_replacement_value
    replacement_function.assert_called_once_with(obj1.name)


def test_pass_existing_value_key_word(default_objects, mocker):
    obj1 = default_objects.obj1
    mock_replacement_value = "mock_replacement_value"

    replacement_function = mocker.Mock(
        return_value=mock_replacement_value
    )
    
    fields_to_replace = [
        FieldToReplace(
            field_name="name", 
            replacement_function=replacement_function, 
            pass_existing_value=True,
            existing_value_kwarg="foobar"
        )
    ]
    
    modified_object = replace_with_fake_data(
        input_object=obj1,
        fields_to_replace=fields_to_replace
    )

    assert modified_object.name == mock_replacement_value
    replacement_function.assert_called_once_with(foobar=obj1.name)
