from pathlib import Path

import pytest
from docsible.utils.yaml import load_yaml_file_custom


# Absolute path to fixture, works from both root and tests directory
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "type_fixture.yml"


def test_type_detection():
    result = load_yaml_file_custom(str(FIXTURE_PATH))
    # Type is overriden in the fixture to str
    assert result['test']['type'] == "str"
    # Type is overriden in the fixture to int
    assert result['test2']['type'] == "int"
    # This is not overriden in the fixture, so it should be int
    # Original behavior is to use the type of the value
    assert result['test3']['type'] == "int"
    # This is not overriden in the fixture
    assert result['test4']['type'] == "list"
    assert result['test4.0']['type'] == "int"
    assert result['test4.1']['type'] == "bool"
    assert result['test4.2']['type'] == "str"
    # This is not overriden in the fixture, so it should be dict
    assert result['test5']['type'] == "dict"
    assert result['test5.example']['type'] == "int"
