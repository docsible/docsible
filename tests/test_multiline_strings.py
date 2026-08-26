from pathlib import Path
import pytest
from jinja2 import Environment, BaseLoader
from docsible.utils.yaml import load_yaml_file_custom, get_multiline_indicator
from docsible.markdown_template import static_template, collection_template

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "multiline_fixture.yml"


def test_load_multiline_yaml():
    result = load_yaml_file_custom(str(FIXTURE_PATH))
    assert result is not None

    # Check content_block indicator
    assert result['content_block']['multiline_indicator'] == 'literal'
    assert '\n' not in result['content_block']['value']

    # Check quoted_multiline has no newlines in value
    assert '\n' not in result['quoted_multiline']['value']
    assert result['quoted_multiline']['value'] == 'line 1 line 2 line 3'

    # Check escaped_newline has no newlines in value
    assert '\n' not in result['escaped_newline']['value']
    assert result['escaped_newline']['value'] == 'line 1 line 2'

    # Check list item multiline values
    assert '\n' not in result['multiline_list.0']['value']
    assert '\n' not in result['multiline_list.1']['value']

    # Check nested dict multiline value
    assert '\n' not in result['multiline_dict.nested_key']['value']


def test_get_multiline_indicator():
    assert get_multiline_indicator("var: |") == "literal"
    assert get_multiline_indicator("var: |-") == "literal_strip"
    assert get_multiline_indicator("var: |+") == "literal_keep"
    assert get_multiline_indicator("var: >") == "folded"
    assert get_multiline_indicator("var: >-") == "folded_strip"
    assert get_multiline_indicator("var: >+") == "folded_keep"
    assert get_multiline_indicator("var: |2") == "literal_indent_2"
    assert get_multiline_indicator("  nested_var: |") == "literal"
    assert get_multiline_indicator("- item: |") == "literal"
    assert get_multiline_indicator("- |") == "literal"
    assert get_multiline_indicator('"quoted_var": |') == "literal"
    assert get_multiline_indicator("not_multiline: value") is None


def test_render_static_template_with_multiline_values():
    env = Environment(loader=BaseLoader)
    template = env.from_string(static_template)

    raw_data = load_yaml_file_custom(str(FIXTURE_PATH))

    # Also simulate raw multiline strings directly in data to test template escaping
    raw_data['raw_multiline'] = {
        'value': "line1\nline2\nline3",
        'line': 1,
        'title': "title line 1\ntitle line 2",
        'required': "false",
        'choices': "choice 1\nchoice 2",
        'description': "description",
        'type': 'str'
    }

    role_info = {
        "name": "test_role",
        "defaults": [{
            "file": "main.yml",
            "data": raw_data
        }],
        "vars": [{
            "file": "main.yml",
            "data": raw_data
        }],
        "tasks": [],
        "meta": {},
        "playbook": {"content": None, "graph": None},
        "docsible": None,
        "belongs_to_collection": False,
        "repository": None,
        "repository_type": None,
        "repository_branch": "main",
        "argument_specs": None
    }

    rendered = template.render(role=role_info, mermaid_code_per_file={})

    # Verify that in all Markdown table rows (| ... |), there are no embedded newlines
    lines = rendered.splitlines()
    table_lines = [line for line in lines if line.strip().startswith('|')]
    for line in table_lines:
        assert '\n' not in line
        assert '\r' not in line
        # Every table line must end with |
        assert line.strip().endswith('|')


def test_render_collection_template_with_multiline_values():
    env = Environment(loader=BaseLoader)
    template = env.from_string(collection_template)

    raw_data = load_yaml_file_custom(str(FIXTURE_PATH))
    raw_data['raw_multiline'] = {
        'value': "val1\nval2",
        'line': 1,
        'title': "title",
        'required': None,
        'choices': None,
        'description': None,
        'type': 'str'
    }

    collection_metadata = {
        "namespace": "my_namespace",
        "name": "my_collection",
        "version": "1.0.0",
        "authors": ["Author"],
        "description": "Collection desc",
        "repository": None,
        "repository_type": None,
        "repository_branch": "main"
    }

    role_info = {
        "name": "test_role",
        "defaults": [{
            "file": "main.yml",
            "data": raw_data
        }],
        "vars": [{
            "file": "main.yml",
            "data": raw_data
        }],
        "tasks": [],
        "meta": {},
        "playbook": {"content": None, "graph": None},
        "docsible": None,
        "belongs_to_collection": collection_metadata,
        "repository": None,
        "repository_type": None,
        "repository_branch": "main",
        "argument_specs": None
    }

    rendered = template.render(collection=collection_metadata, roles=[role_info])

    lines = rendered.splitlines()
    table_lines = [line for line in lines if line.strip().startswith('|')]
    for line in table_lines:
        assert '\n' not in line
        assert '\r' not in line
        assert line.strip().endswith('|')
