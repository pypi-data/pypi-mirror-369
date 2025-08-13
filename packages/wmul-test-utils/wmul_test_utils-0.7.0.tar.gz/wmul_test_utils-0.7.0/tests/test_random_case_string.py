"""
@Author = 'Michael Stanley'

============ Change Log ============
2025-May-23 = Created.

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
import random
from wmul_test_utils import random_case_string, multiple_random_case_strings

def test_five_strings():
    seed = 1000
    random.seed(seed)

    input_string = "foobarbaz"

    expected_strings = [
        'fOobArBaZ',
        'FOobArBaZ',
        'FoObaRBaZ',
        'FOoBaRBaZ',
        'foOBarbAZ'
    ]

    for expected in expected_strings:
        result = random_case_string(input_string=input_string)
        assert result == expected


def test_five_more_strings():
    seed = 5999
    random.seed(seed)

    input_string = "homersimpson"
    
    expected_strings = [    
        'hoMERSImpSoN',
        'HOmeRsiMPSoN',
        'hOmERSImpSon',
        'homErSiMpSOn',
        'HOMERsIMpsOn'
    ]

    for expected in expected_strings:
        result = random_case_string(input_string=input_string)
        assert result == expected

def test_setting_seed():
    first_seed = 1000
    second_seed = 5999

    random.seed(first_seed)
    # Set it here, to test that the function resets it.

    input_string = "homersimpson"
    expected_string = 'hoMERSImpSoN'
    result = random_case_string(input_string=input_string, seed=second_seed)

    assert result == expected_string

def test_generating_multiple_strings_1():
    seed = 1000
    random.seed(seed)

    input_string = "foobarbaz"

    expected_strings = [
        'fOobArBaZ',
        'FOobArBaZ',
        'FoObaRBaZ',
        'FOoBaRBaZ',
        'foOBarbAZ'
    ]

    result_strings = multiple_random_case_strings(input_string=input_string, iterations=5)

    assert expected_strings == result_strings


def test_generating_multiple_strings_2():
    seed = 5999
    random.seed(seed)

    input_string = "homersimpson"
    
    expected_strings = [    
        'hoMERSImpSoN',
        'HOmeRsiMPSoN',
        'hOmERSImpSon',
        'homErSiMpSOn',
        'HOMERsIMpsOn'
    ]

    result_strings = multiple_random_case_strings(input_string=input_string, iterations=5)

    assert expected_strings == result_strings


def test_generating_multiple_strings_setting_seed():
    first_seed = 1000
    second_seed = 5999

    random.seed(first_seed)
    # Set it here, to test that the function resets it.

    input_string = "homersimpson"
    
    expected_strings = [    
        'hoMERSImpSoN',
        'HOmeRsiMPSoN',
        'hOmERSImpSon',
        'homErSiMpSOn',
        'HOMERsIMpsOn'
    ]

    result_strings = multiple_random_case_strings(input_string=input_string, iterations=5, seed=second_seed)

    assert expected_strings == result_strings


def test_generating_multiple_strings_setting_iterations():
    seed = 5999

    random.seed(seed)
    # Set it here, to test that the function resets it.

    input_string = "homersimpson"
    
    expected_strings = [    
        'hoMERSImpSoN',
        'HOmeRsiMPSoN',
        'hOmERSImpSon'
    ]

    result_strings = multiple_random_case_strings(input_string=input_string, iterations=3)

    assert expected_strings == result_strings
