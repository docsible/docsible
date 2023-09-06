# Import libraries
import os
import yaml
import click
from jinja2 import Environment, BaseLoader

static_template = """{{- role.existing_readme -}}

# Generated Documentation
## {{ role.name }}
{% if role.meta and role.meta.galaxy_info -%}
Description: {{ role.meta.galaxy_info.description or 'Not available.' }}
{% else %}
Description: Not available.
{%- endif %}

### Defaults
{% if role.defaults|length > 0 -%}
{% for defaultfile in role.defaults %}
#### File: {{ defaultfile.file }}
| Var | Value | Required | Title |
| --- | --- | --- | --- |
{% for key, details in defaultfile.data.items() -%}
| {{ key }} | {{ details.value }} | {{ details.required }} | {{ details.title }} |
{% endfor -%}
{% endfor %}
{%- else -%}
No defaults available.
{%- endif %}

### Vars
{% if role.vars|length > 0 -%}
{% for varsfile in role.vars %}
#### File: {{ varsfile.file }}
| Var | Value | Required | Title |
| --- | --- | --- | --- |
{% for key, details in varsfile.data.items() -%}
| {{ key }} | {{ details.value }} | {{ details.required }} | {{ details.title }} |
{% endfor -%}
{% endfor %}
{%- else -%}
No vars available.
{%- endif %}

### Tasks
{%- if role.tasks|length == 1 and role.tasks[0]['file'] == 'main.yml' %}
| Name | Module |
| ---- | ------ |
{%- for task in role.tasks[0]['tasks'] %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{%- else %}
{% for taskfile in role.tasks %}
#### File: {{ taskfile.file }}
| Name | Module |
| ---- | ------ |
{%- for task in taskfile.tasks %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{% endfor %}
{%- endif %}

{% if role.playbook -%}
## Playbook
```yml
{{ role.playbook }}
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
- **{{ platform.name }}**: {{ ", ".join(platform.versions) }}
{% endfor -%}
{%- else -%}
No platforms specified.
{%- endif %}
{%- endif %}
"""

# Initialize the Jinja2 Environment
env = Environment(loader=BaseLoader)
env.from_string(static_template)


def load_yaml_generic(filepath):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return data
    except (FileNotFoundError, yaml.constructor.ConstructorError) as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_yaml_file_custom(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:  # Specify encoding for UTF-8
            lines = f.readlines()

        collected_data = {}
        current_title = None
        current_required = None
        skip = False
        for line in lines:
            stripped_line = line.strip()
            
            if skip:
                if stripped_line == "":
                    skip = False
                continue

            if "# title:" in stripped_line:
                current_title = stripped_line.split(":", 1)[1].strip()
            elif "# required:" in stripped_line:
                current_required = stripped_line.split(":", 1)[1].strip().lower() == 'true'
            elif ": " in stripped_line:
                parts = stripped_line.split(":")
                var_name = parts[0].strip()
                value = parts[1].strip()
                if "!vault |" in value:
                    value = 'ENCRYPTED_WITH_ANSIBLE_VAULT'
                    skip = True
                collected_data[var_name] = {
                    'value': value,
                    'title': current_title,
                    'required': current_required
                }
                # Reset current_title and current_required for the next variable
                current_title = None
                current_required = None
            else:
                # Reset current_title and current_required if there's a new section or other unhandled lines
                current_title = None
                current_required = None

        return collected_data
    except (FileNotFoundError, yaml.constructor.ConstructorError) as e:
        print(f"Error loading {filepath}: {e}")
        return None


# Function to load all YAML files from a given directory and include file names
def load_yaml_files_from_dir_custom(dir_path):
    collected_data = []
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for yaml_file in os.listdir(dir_path):
            if yaml_file.endswith(".yml"):
                file_data = load_yaml_file_custom(os.path.join(dir_path, yaml_file))
                if file_data:
                    collected_data.append({'file': yaml_file, 'data': file_data})
    return collected_data

# Function to process tasks for special keys like 'block'
def process_special_task_keys(task):
    tasks = []
    if 'block' in task:
        for sub_task in task['block']:
            processed_tasks = process_special_task_keys(sub_task)
            tasks.extend(processed_tasks)
    elif 'rescue' in task:
        for sub_task in task['rescue']:
            processed_tasks = process_special_task_keys(sub_task)
            tasks.extend(processed_tasks)
    else:
        task_name = task.get('name', 'Unnamed')
        task_module = list(task.keys())[1] if 'name' in task else list(task.keys())[0]
        tasks.append({
            'name': task_name,
            'module': task_module
        })
    return tasks


@click.command()
@click.option('--role', default='./role', help='Path to the Ansible role directory.')
@click.option('--playbook', default=None, help='Path to the playbook file.')
def doc_the_role(role, playbook):
    role_path = os.path.abspath(role)
    if not os.path.exists(role_path) or not os.path.isdir(role_path):
        print(f"Folder {role_path} does not exist.")
        return

    playbook_content = None
    if playbook:
        try:
            with open(playbook, 'r') as f:
                playbook_content = f.read()
        except FileNotFoundError:
            print('playbook not found:', playbook)
        except Exception as e:
            print('playbook import error:', e)

    document_role(role_path, playbook_content)
    
def document_role(role_path, playbook_content):
    role_name = os.path.basename(role_path)
    readme_path = os.path.join(role_path, "README.md")
    meta_path = os.path.join(role_path, "meta", "main.yml")

    defaults_data = load_yaml_files_from_dir_custom(os.path.join(role_path, "defaults")) or []
    vars_data = load_yaml_files_from_dir_custom(os.path.join(role_path, "vars")) or []

    role_info = {
        "name": role_name,
        "defaults": defaults_data,
        "vars": vars_data,
        "tasks": [],
        "meta": load_yaml_generic(meta_path) or {},
        "playbook": playbook_content
    }

    tasks_dir = os.path.join(role_path, "tasks")
    role_info["tasks"] = []

    if os.path.exists(tasks_dir) and os.path.isdir(tasks_dir):
        for task_file in os.listdir(tasks_dir):
            if task_file.endswith(".yml"):
                tasks_data = load_yaml_generic(os.path.join(tasks_dir, task_file))
                if tasks_data:
                    task_info = {'file': task_file, 'tasks': []}
                    if not isinstance(tasks_data, list):
                        print(f"Unexpected data type for tasks in {task_file}. Skipping.")
                        continue
                    for task in tasks_data:
                        if not isinstance(task, dict):
                            print(f"Skipping unexpected data in {task_file}: {task}")
                            continue
                        if task and len(task.keys()) > 0:
                            processed_tasks = process_special_task_keys(task)
                            task_info['tasks'].extend(processed_tasks)
                    role_info["tasks"].append(task_info)

    if os.path.exists(readme_path):
        os.remove(readme_path)

    role_info["existing_readme"] = ""

    # Render the static template
    template = env.from_string(static_template)
    output = template.render(role=role_info)

    with open(readme_path, "w") as f:
        f.write(output)

    print('Documentation generated at:', readme_path)

if __name__ == '__main__':
    doc_the_role()
