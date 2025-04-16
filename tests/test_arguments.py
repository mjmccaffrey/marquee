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

