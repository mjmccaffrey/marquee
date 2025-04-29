import pytest

import arguments

def test_arguments_brightness_pattern_empty():
    with pytest.raises(ValueError, match="brightness pattern"):
        arguments.validate_brightness_pattern("")

def test_arguments_brightness_pattern_too_short():
    with pytest.raises(ValueError, match="brightness pattern"):
        arguments.validate_brightness_pattern("A")

def test_arguments_brightness_pattern_too_long():
    with pytest.raises(ValueError, match="brightness pattern"):
        arguments.validate_brightness_pattern("AAAAAAAAAAAAA")

def test_arguments_brightness_pattern_invalid_char():
    with pytest.raises(ValueError, match="brightness pattern"):
        arguments.validate_brightness_pattern("BBBBBBBBBB")

def test_arguments_light_pattern_empty():
    with pytest.raises(ValueError, match="light pattern"):
        arguments.validate_light_pattern("")

def test_arguments_light_pattern_too_short():
    with pytest.raises(ValueError, match="light pattern"):
        arguments.validate_light_pattern("1")

def test_arguments_light_pattern_too_long():
    with pytest.raises(ValueError, match="light pattern"):
        arguments.validate_light_pattern("1111111111111")

def test_arguments_light_pattern_invalid_char():
    with pytest.raises(ValueError, match="light pattern"):
        arguments.validate_light_pattern("2222222222")

def test_validate_brightness_factor_invalid():
    with pytest.raises(ValueError, match="brightness factor"):
        arguments.validate_brightness_factor('q')

def test_validate_brightness_factor_negative():
    with pytest.raises(ValueError, match="brightness factor"):
        arguments.validate_brightness_factor('-1')

def test_validate_brightness_factor_too_large():
    with pytest.raises(ValueError, match="brightness factor"):
        arguments.validate_brightness_factor('1.0001')

def test_validate_speed_factor_invalid():
    with pytest.raises(ValueError, match="speed factor"):
        arguments.validate_speed_factor('q')

def test_validate_speed_factor_zero():
    with pytest.raises(ValueError, match="speed factor"):
        arguments.validate_speed_factor('0')

def test_validate_speed_factor_negative():
    with pytest.raises(ValueError, match="speed factor"):
        arguments.validate_speed_factor('-1')

def test_validate_speed_factor_too_large():
    with pytest.raises(ValueError, match="speed factor"):
        arguments.validate_speed_factor('5.0001')
