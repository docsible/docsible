static_template = """{{- role.existing_readme -}}

# Generated Documentation

## {{ role.name }}

{% if role.meta and role.meta.galaxy_info -%}
Description: {{ role.meta.galaxy_info.description or 'Not available.' }}
{% else %}
Description: Not available.
{%- endif %}

{% if role.docsible -%}
| Field                | Value           |
|--------------------- |-----------------|
| Functional description | {{ role.docsible.description or 'Not available.' }} |
| Requester            | {{ role.docsible.requester or 'Not available.' }} |
| Users                | {{ role.docsible.users or 'Not available.' }} |
| Date dev             | {{ role.docsible.dt_dev or 'Not available.' }} |
| Date prod            | {{ role.docsible.dt_prod or 'Not available.' }} |
| Readme update            | {{ role.docsible.dt_update or 'Not available.' }} |
| Version              | {{ role.docsible.version or 'Not available.' }} |
| Time Saving              | {{ role.docsible.time_saving or 'Not available.' }} |
| Category              | {{ role.docsible.category or 'Not available.' }} |
| Sub category              | {{ role.docsible.subCategory or 'Not available.' }} |
{%- endif %}

### Defaults

{% if role.defaults|length > 0 -%}
**These are static variables with lower priority**
{%- for defaultfile in role.defaults %}

#### File: {{ defaultfile.file }}
{# Cicle used for decide to set Title and Required Column #}
{% set ns = namespace (details_required = false) %}{% set ns = namespace (details_title = false) %}
{% for key, details in defaultfile.data.items() %}{% if details.required is not none %}{% set ns.details_required = true %}{% endif %}{% if details.title is not none %}{% set ns.details_title = true %}{% endif %}{% endfor %}
| Var          | Type         | Value       |{% if ns.details_required %}Required    |{% endif %}{% if ns.details_title %} Title       |{% endif %}
|--------------|--------------|-------------|{% if ns.details_required %}-------------|{% endif %}{% if ns.details_title %}-------------|{% endif %}
{%- for key, details in defaultfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| {{ key }}    | {{ var_type }}   | {{ details.value }}  | {% if ns.details_required %} {{ details.required }}  |{% endif %} {% if ns.details_title %} {{ details.title }} |{% endif %}
{%- endfor %}
{%- endfor %}
{%- else %}
No defaults available.
{%- endif %}

### Vars

{% if role.vars|length > 0 -%}
**These are variables with higher priority**
{%- for varsfile in role.vars %}
#### File: {{ varsfile.file }}
{# Cicle used for decide to set Title and Required Column #}
{% set ns = namespace (details_required = false) %}{% set ns = namespace (details_title = false) %}{% for key, details in varsfile.data.items() %}{% if details.required is not none %}{% set ns.details_required = true %}{% endif %}{% if details.title is not none %}{% set ns.details_title = true %}{% endif %}{% endfor %}
| Var          | Type         | Value       |{% if ns.details_required %} Required    |{% endif %}{% if ns.details_title %} Title       |{% endif %}
|--------------|--------------|-------------|{% if ns.details_required %}-------------|{% endif %}{% if ns.details_title %}-------------|{% endif %}
{%- for key, details in varsfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| {{ key }}    | {{ var_type }}   | {{ details.value }}  |{% if ns.details_required %} {{ details.required }} |{% endif %}{% if ns.details_title %} {{ details.title }} |{% endif %}
{%- endfor %}
{%- endfor %}
{%- else %}
No vars available.
{%- endif %}


### Tasks

{% for taskfile in role.tasks %}
#### File: {{ taskfile.file }}
{% set ns = namespace (comments_required = false) %}{% for comment in taskfile['comments'] %}{% if comment != "" %}{% set ns.comments_required = true %}{% endif %}{% endfor %}
{{ ns.comments_required }}
| Name | Module | Has Conditions |{% if ns.comments_required %} Comments |{% endif %}
| ---- | ------ | --------- |{% if ns.comments_required %}  -------- |{% endif %}
{%- for task in taskfile.tasks %}
| {{ task.name }} | {{ task.module }} | {{ 'True' if task.when else 'False' }} |{% if ns.comments_required %} {{ taskfile['comments'] | selectattr('task_name', 'equalto', task.name) | map(attribute='task_comments') | join }} |{% endif %}
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