import pytest
from docsible.utils.yaml import load_yaml_file_custom

def test_type_detection():
    result = load_yaml_file_custom("fixtures/type_fixture.yml")
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
