"""Tests for Ansible YAML tag handling (!unsafe, !vault, and unknown tags)."""

from docsible.utils.yaml import load_yaml_file_custom


FIXTURE_PATH = "fixtures/unsafe_tag_fixture.yml"


def load_test_fixture():
    """Load the test fixture file once for all tests."""
    return load_yaml_file_custom(FIXTURE_PATH)


def test_vault_tag_uses_placeholder():
    """!vault tag should show a placeholder since encrypted content cannot be displayed."""
    result = load_test_fixture()

    assert result['vault_encrypted']['value'] == "ENCRYPTED_WITH_ANSIBLE_VAULT"


def test_basic_unsafe_tag_preservation():
    """!unsafe tag should be preserved in output to document non-templated values."""
    result = load_test_fixture()

    assert result['basic_unsafe']['value'] == '!unsafe "{{ not_a_template }}"'
    assert result['complex_unsafe']['value'] == '!unsafe "{{ timestamp }} - [{{ log_level }}] {{ message }}"'


def test_smart_quoting_with_double_quotes():
    """Values with embedded double quotes should use single quote wrapper (no escaping)."""
    result = load_test_fixture()

    # Smart quoting: wraps in single quotes to avoid backslash escaping
    assert result['double_quotes']['value'] == "!unsafe 'He said \"hello\" to everyone'"


def test_smart_quoting_with_single_quotes():
    """Values with embedded single quotes should use double quote wrapper (no escaping)."""
    result = load_test_fixture()

    # Smart quoting: wraps in double quotes to avoid backslash escaping
    assert result['single_quotes']['value'] == '!unsafe "It\'s working perfectly"'


def test_smart_quoting_with_mixed_quotes():
    """Values with both quote types must escape double quotes with backslash."""
    result = load_test_fixture()

    # When both quote types present, use double quotes and escape only the doubles
    # Use regular string: apostrophe needs no escaping, only double quotes do
    assert result['mixed_quotes']['value'] == '!unsafe "She said \\"it\'s fine\\" confidently"'


def test_backslashes_preserved_without_escaping():
    """Backslashes in values should be preserved as-is, not double-escaped."""
    result = load_test_fixture()

    # Backslashes are preserved literally (not escaped)
    assert result['backslashes']['value'] == r'!unsafe "C:\path\to\file"'


def test_simple_values_wrapped_in_quotes():
    """Simple unquoted values should be wrapped in double quotes."""
    result = load_test_fixture()

    assert result['simple_value']['value'] == '!unsafe "somevalue"'
