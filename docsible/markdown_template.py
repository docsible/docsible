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

{% if role.defaults|length > 0 -%}
### Defaults

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
| [{{ key }}](defaults/{{ defaultfile.file }}#L{{details.line}})   | {{ var_type }}   | `{{ details.value | replace('|', '\|') }}`  | {% if ns.details_required %} {{ details.required }}  |{% endif %} {% if ns.details_title %} {{ details.title | replace('|', '\|') }} |{% endif %}
{%- endfor %}
{%- endfor %}
{%- else %}
{%- endif %}


{% if role.vars|length > 0 -%}
### Vars

**These are variables with higher priority**
{%- for varsfile in role.vars %}
#### File: {{ varsfile.file }}
{# Cicle used for decide to set Title and Required Column #}
{% set ns = namespace (details_required = false) %}{% set ns = namespace (details_title = false) %}{% for key, details in varsfile.data.items() %}{% if details.required is not none %}{% set ns.details_required = true %}{% endif %}{% if details.title is not none %}{% set ns.details_title = true %}{% endif %}{% endfor %}
| Var          | Type         | Value       |{% if ns.details_required %} Required    |{% endif %}{% if ns.details_title %} Title       |{% endif %}
|--------------|--------------|-------------|{% if ns.details_required %}-------------|{% endif %}{% if ns.details_title %}-------------|{% endif %}
{%- for key, details in varsfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| [{{ key }}](vars/{{ varsfile.file }}#L{{details.line}})    | {{ var_type }}   | `{{ details.value | replace('|', '\|') }}`  |{% if ns.details_required %} {{ details.required }} |{% endif %}{% if ns.details_title %} {{ details.title | replace('|', '\|') }} |{% endif %}
{%- endfor %}
{%- endfor %}
{%- else %}
{%- endif %}


### Tasks

{% for taskfile in role.tasks %}
#### File: {{ taskfile.file }}
{% set ns = namespace (comments_required = false) %}{% for comment in taskfile['comments'] %}{% if comment != "" %}{% set ns.comments_required = true %}{% endif %}{% endfor %}
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

collection_template = """
# 📃 Collection overview

**Namespace**: {{ collection.namespace }}

**Name**: {{ collection.name }}

**Version**: {{ collection.version }}

**Authors**: 
{% for author in collection.authors %}{{ author }}{% if not loop.last %}\n {% endif %}{% endfor %}

{% if collection.description %}
## Description
{{ collection.description }}
{% endif %}

## Roles
{% for role in roles %}
### [{{ role.name }}](roles/{{ role.name }}/README.md)
- Description: {{ role.meta.galaxy_info.description }}
{% endfor %}

## Metadata
{% if collection.repository %}
- **Repository**: [Repository]({{ collection.repository }})
{% endif %}
{% if collection.documentation %}
- **Documentation**: [Documentation]({{ collection.documentation }})
{% endif %}
{% if collection.homepage %}
- **Homepage**: [Homepage]({{ collection.homepage }})
{% endif %}
{% if collection.issues %}
- **Issues**: [Issues]({{ collection.issues }})
{% endif %}
"""
