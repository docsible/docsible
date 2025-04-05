static_template = """
# 📃 Role overview

## {{ role.name }}

{% if role.belongs_to_collection -%}
```
Role belongs to {{ role.belongs_to_collection.namespace }}/{{ role.belongs_to_collection.name }}
Namespace - {{ role.belongs_to_collection.namespace }}
Collection - {{ role.belongs_to_collection.name }}
Version - {{ role.belongs_to_collection.version }}
Repository - {{ role.belongs_to_collection.repository }}
```
{%- endif %}

{% if role.meta and role.meta.galaxy_info -%}
Description: {{ role.meta.galaxy_info.description or 'Not available.' }}
{% else %}
Description: Not available.
{%- endif %}

{% if role.docsible -%}
| Field                | Value           |
|--------------------- |-----------------|
{%- if role.docsible.description %}
| Functional description | {{ role.docsible.description }} |
{%- endif %}
{%- if role.docsible.requester %}
| Requester            | {{ role.docsible.requester }} |
{%- endif %}
{%- if role.docsible.users %}
| Users                | {{ role.docsible.users }} |
{%- endif %}
{%- if role.docsible.dt_dev %}
| Date dev             | {{ role.docsible.dt_dev }} |
{%- endif %}
{%- if role.docsible.dt_prod %}
| Date prod            | {{ role.docsible.dt_prod }} |
{%- endif %}
{%- if role.docsible.dt_update %}
| Readme update        | {{ role.docsible.dt_update }} |
{%- endif %}
{%- if role.docsible.version %}
| Version              | {{ role.docsible.version }} |
{%- endif %}
{%- if role.docsible.time_saving %}
| Time Saving          | {{ role.docsible.time_saving }} |
{%- endif %}
{%- if role.docsible.category %}
| Category             | {{ role.docsible.category }} |
{%- endif %}
{%- if role.docsible.subCategory %}
| Sub category         | {{ role.docsible.subCategory }} |
{%- endif %}
{%- if role.docsible.aap_hub %}
| AAP Hub              | {{ role.docsible.aap_hub }} |
{%- endif %}
{%- if role.docsible.automation_kind %}
| Automation Kind      | {{ role.docsible.automation_kind }} |
{%- endif %}
{%- if role.docsible.critical %}
| Critical ⚠️          | {{ role.docsible.critical }} |
{%- endif %}
{%- endif %}

{% macro render_arguments_list(arguments, level=0) %}
{% for arg, details in arguments.items() %}
  {%- set indent = '  ' * level %}
  {{ indent }}- **{{ arg }}**
  {{ indent }}  - **Required**: {{ details.required | default('false') }}
  {{ indent }}  - **Type**: {{ details.type }}
  {{ indent }}  - **Default**: {{ details.default | default('none') }}
  {{ indent }}  - **Description**: {{ details.description | default('No description provided') }}
  {% if details.choices is defined %}
    {{ indent }}  - **Choices**:
    {% for choice in details.choices %}
      {{ indent }}    - {{ choice }}
    {% endfor %}
  {% endif %}
  {% if details.aliases is defined %}
    {{ indent }}  - **Aliases**:
    {% for alias in details.aliases %}
      {{ indent }}    - {{ alias }}
    {% endfor %}
  {% endif %}
  {% if details.type == 'dict' and details.options %}
    {{ render_arguments_list(details.options, level + 1) }}
  {% elif details.type == 'list' and details.elements == 'dict' %}
    {% for elem in details.default %}
      {% if elem is mapping %}
        {{ render_arguments_list(elem, level + 1) }}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endfor %}
{% endmacro %}

{% if role.argument_specs %}
<details>
<summary><b>🧩 Argument Specifications in meta/argument_specs</b></summary>
{% for section, specs in role.argument_specs.argument_specs.items() %}
#### Key: {{ section }}
**Description**: {{ specs.description or specs.short_description or 'No description provided' }}
{{ render_arguments_list(specs.options) }}
{% endfor %}
</details>
{% else %}
{% endif %}

{% macro render_repo_link(repo, role_name, file_path, line, repo_type, branch) -%}
  {%- if repo and file_path and line is not none -%}
    {%- if role.belongs_to_collection -%}
      {%- set full_path = 'roles/' ~ role_name ~ '/' ~ file_path -%}
    {%- else -%}
      {%- set full_path = file_path -%}
    {%- endif %}
    {%- set encoded_path = full_path | replace(' ', '%20') -%}

    {%- if repo_type == 'github' -%}
      {{ repo }}/blob/{{ branch }}/{{ encoded_path }}#L{{ line }}
    {%- elif repo_type == 'gitlab' -%}
      {{ repo }}/-/blob/{{ branch }}/{{ encoded_path }}#L{{ line }}
    {%- elif repo_type == 'gitea' -%}
      {{ repo }}/src/branch/{{ branch }}/{{ encoded_path }}#L{{ line }}
    {%- else -%}
      {{ repo }}/{{ encoded_path }}#L{{ line }}
    {%- endif %}
  {%- else -%}
    {{ file_path }}#L{{ line }}
  {%- endif %}
{%- endmacro %}

{% if role.defaults|length > 0 -%}
### Defaults

**These are static variables with lower priority**
{%- for defaultfile in role.defaults %}

#### File: defaults/{{ defaultfile.file }}
{# Cycle used for deciding to set Title and Required Column #}
{% set ns = namespace(details_required = false, details_title = false, details_choices = false) %}
{%- for key, details in defaultfile.data.items() -%}
    {%- if details.required is not none -%}{%- set ns.details_required = true -%}{%- endif -%}
    {%- if details.title is not none -%}{%- set ns.details_title = true -%}{%- endif -%}
    {%- if details.choices != "n/a" -%}{%- set ns.details_choices = true -%}{%- endif -%}
{%- endfor -%}
| Var          | Type         | Value       |{% if ns.details_choices %}Choices    |{% endif %}{% if ns.details_required %}Required    |{% endif %}{% if ns.details_title %} Title       |{% endif %}
|--------------|--------------|-------------|{% if ns.details_choices %}-------------|{% endif %}{% if ns.details_required %}-------------|{% endif %}{% if ns.details_title %}-------------|{% endif %}
{%- for key, details in defaultfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| [{{ key }}]({{ render_repo_link(role.repository, role.name, 'defaults/' ~ defaultfile.file, details.line, role.repository_type, role.repository_branch) }})   | {{ var_type }}   | `{{ details.value | replace('|', '¦') }}` | {% if ns.details_choices %} {{ details.choices | replace('|', '¦') }}  |{% endif %}  {% if ns.details_required %} {{ details.required }}  |{% endif %} {% if ns.details_title %} {{ details.title | replace('|', '¦') }} |{% endif %}
{%- endfor %}
{%- endfor %}

{%- for defaultfile in role.defaults -%}
{%- set ns = namespace(has_descriptions = false) -%}
{%- for key, details in defaultfile.data.items() -%}
    {%- if details.description != "n/a" -%}{%- set ns.has_descriptions = true -%}{% endif -%}
{%- endfor -%}
{%- if ns.has_descriptions %}
<details>
<summary><b>🖇️ Full descriptions for vars in defaults/{{ defaultfile.file }}</b></summary>
<br>
{%- for key, details in defaultfile.data.items() %}
    {%- if details.description != "n/a" %}
<b>{{ key }}:</b> {{ details.description }}
<br>
    {%- endif %}
{%- endfor %}
<br>
</details>
{%- endif %}
{%- endfor %}
{%- else %}
{%- endif %}


{% if role.vars|length > 0 -%}
### Vars

**These are variables with higher priority**
{%- for varsfile in role.vars %}
#### File: vars/{{ varsfile.file }}
{# Cycle used for deciding to set Title and Required Column #}
{% set ns = namespace(details_required = false, details_title = false, details_choices = false) %}
{%- for key, details in varsfile.data.items() -%}
    {%- if details.required is not none -%}{%- set ns.details_required = true -%}{%- endif -%}
    {%- if details.title is not none -%}{%- set ns.details_title = true -%}{%- endif -%}
    {%- if details.choices != "n/a" -%}{%- set ns.details_choices = true -%}{%- endif -%}
{%- endfor -%}
| Var          | Type         | Value       |{% if ns.details_choices %}Choices    |{% endif %}{% if ns.details_required %}Required    |{% endif %}{% if ns.details_title %} Title       |{% endif %}
|--------------|--------------|-------------|{% if ns.details_choices %}-------------|{% endif %}{% if ns.details_required %}-------------|{% endif %}{% if ns.details_title %}-------------|{% endif %}
{%- for key, details in varsfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| [{{ key }}]({{ render_repo_link(role.repository, role.name, 'vars/' ~ varsfile.file, details.line, role.repository_type, role.repository_branch) }})   | {{ var_type }}   | `{{ details.value | replace('|', '¦') }}` | {% if ns.details_choices %} {{ details.choices | replace('|', '¦') }}  |{% endif %}  {% if ns.details_required %} {{ details.required }}  |{% endif %} {% if ns.details_title %} {{ details.title | replace('|', '¦') }} |{% endif %}
{%- endfor %}
{%- endfor %}

{%- for varsfile in role.vars -%}
{% set ns = namespace(has_descriptions = false) -%}
{%- for key, details in varsfile.data.items() -%}
    {%- if details.description != "n/a" -%}{%- set ns.has_descriptions = true -%}{%- endif %}
{%- endfor %}
{%- if ns.has_descriptions %}
<details>
<summary><b>🖇️ Full Descriptions for vars in vars/{{ varsfile.file }}</b></summary>
<br>
{%- for key, details in varsfile.data.items() %}
    {%- if details.description != "n/a" %}
<b>{{ key }}:</b> {{ details.description }}
<br>
    {%- endif %}
{%- endfor %}
<br>
</details>
{%- endif %}
{%- endfor %}
{%- else %}
{%- endif %}


### Tasks

{% for taskfile in role.tasks %}
#### File: tasks/{{ taskfile.file }}
{% set ns = namespace (comments_required = false) %}{% for comment in taskfile['comments'] %}{% if comment != "" %}{% set ns.comments_required = true %}{% endif %}{% endfor %}
| Name | Module | Has Conditions |{% if ns.comments_required %} Comments |{% endif %}
| ---- | ------ | --------- |{% if ns.comments_required %}  -------- |{% endif %}
{%- for task in taskfile.tasks %}
| {{ task.name.replace("|", "¦") }} | {{ task.module }} | {{ 'True' if task.when else 'False' }} |{% if ns.comments_required %} {{ taskfile['comments'] | selectattr('task_name', 'equalto', task.name) | map(attribute='task_comments') | join }} |{% endif %}
{%- endfor %}
{% endfor %}

{% if mermaid_code_per_file -%}
## Task Flow Graphs

{% for task_file, mermaid_code in mermaid_code_per_file.items() %}

### Graph for {{ task_file }}

```mermaid
{{ mermaid_code }}
```
{% endfor %}
{%- endif %}

{% if role.playbook.content -%}
## Playbook

```yml
{{ role.playbook.content }}
```
{%- endif %}
{% if role.playbook.graph -%}
## Playbook graph
```mermaid
{{ role.playbook.graph }}
```
{%- endif %}

{% if role.meta.galaxy_info -%}
## Author Information
{{ role.meta.galaxy_info.author or 'Unknown Author' }}

#### License

{{ role.meta.galaxy_info.license or 'No license specified.' }}

#### Minimum Ansible Version

{{ role.meta.galaxy_info.min_ansible_version or 'No minimum version specified.' }}

#### Platforms

{% if role.meta.galaxy_info.platforms -%}
{% for platform in role.meta.galaxy_info.platforms -%}
- **{{ platform.name }}**: {{ platform.versions }}
{% endfor -%}
{%- else -%}
No platforms specified.
{%- endif %}
{%- endif %}
"""

collection_template = """
# 📃 Collection overview

**Namespace**: {{ collection.namespace }}

**Name**: {{ collection.name }}

**Version**: {{ collection.version }}

**Authors**:
{% for author in collection.authors %}
- {{ author }}\n
{%- endfor %}

{% if collection.description -%}
## Description

{{ collection.description }}
{%- endif %}

{% macro render_repo_role_readme_link(repo, role_name, repo_type, branch) -%}
  {%- if repo and role_name -%}
    {%- set file_path = 'roles/' ~ role_name -%}
    {%- set encoded_path = file_path | replace(' ', '%20') -%}
    {%- if repo_type == 'github' -%}
      {{ repo }}/tree/{{ branch }}/{{ encoded_path }}
    {%- elif repo_type == 'gitlab' -%}
      {{ repo }}/-/tree/{{ branch }}/{{ encoded_path }}
    {%- elif repo_type == 'gitea' -%}
      {{ repo }}/src/branch/{{ branch }}/{{ encoded_path }}
    {%- else -%}
      {{ repo }}/{{ encoded_path }}
    {%- endif %}
  {%- else -%}
    roles/{{ role_name }}
  {%- endif %}
{%- endmacro %}

## Roles
{% for role in roles|sort(attribute='name') %}
### [{{ role.name }}]({{ render_repo_role_readme_link(collection.repository, role.name, collection.repository_type, collection.repository_branch) }})

{% if role.meta and role.meta.galaxy_info -%}
- Description: {{ role.meta.galaxy_info.description or 'Not available.' }}
{%- else -%}
No description available.
{%- endif %}
{% endfor %}
## Metadata

{% if collection.repository -%}
- **Repository**: [Repository]({{ collection.repository }})
{% endif %}
{% if collection.documentation -%}
- **Documentation**: [Documentation]({{ collection.documentation }})
{% endif %}
{% if collection.homepage -%}
- **Homepage**: [Homepage]({{ collection.homepage }})
{% endif %}
{% if collection.issues -%}
- **Issues**: [Issues]({{ collection.issues }})
{% endif %}
"""
