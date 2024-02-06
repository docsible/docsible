# Import libraries
import os
import yaml
import click
from shutil import copyfile
from datetime import datetime
from jinja2 import Environment, BaseLoader
from docsible.markdown_template import static_template
from docsible.utils.mermaid import generate_mermaid_playbook, generate_mermaid_role_tasks_per_file
from docsible.utils.yaml import load_yaml_generic, load_yaml_files_from_dir_custom, get_task_commensts
from docsible.utils.special_tasks_keys import process_special_task_keys

def get_version():
    return "0.5.8"

# Initialize the Jinja2 Environment
env = Environment(loader=BaseLoader)
env.from_string(static_template)


def initialize_docsible(docsible_path, default_data):
    try:
        with open(docsible_path, 'w') as f:
            yaml.dump(default_data, f, default_flow_style=False)
        print(f"Initialized {docsible_path} with default keys.")
    except Exception as e:
        print(f"An error occurred while initializing {docsible_path}: {e}")

@click.command()
@click.option('--role', default='.', help='Path to the Ansible role directory.')
@click.option('--playbook', default='./tests/test.yml', help='Path to the playbook file.')
@click.option('--graph', is_flag=True, help='Generate Mermaid graph for tasks.')
@click.option('--no-backup', is_flag=True, help='Do not backup the readme before remove.')
@click.option('--no-docsible', is_flag=True, help='Do not generate .docsible file and do not include it in README.md.')
@click.option('--comments', is_flag=True, help='Read comments from tasks files')
@click.version_option(version=get_version(), help="Show the module version.")


def doc_the_role(role, playbook, graph, no_backup, no_docsible, comments):
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

    document_role(role_path, playbook_content, graph, no_backup, no_docsible, comments)


def document_role(role_path, playbook_content, generate_graph, no_backup, no_docsible, comments):
    role_name = os.path.basename(role_path)
    readme_path = os.path.join(role_path, "README.md")
    meta_path = os.path.join(role_path, "meta", "main.yml")
    timestamp_readme = datetime.now().strftime('%d/%m/%Y')

    # Check if meta/main.yml exist, otherwise try meta/main.yaml
    if not os.path.exists(meta_path):
        meta_path = os.path.join(role_path, "meta", "main.yaml")

    defaults_data = load_yaml_files_from_dir_custom(
        os.path.join(role_path, "defaults")) or []
    vars_data = load_yaml_files_from_dir_custom(
        os.path.join(role_path, "vars")) or []
    if no_docsible:
        docsible_present = False
    else:
        docsible_path = os.path.join(role_path, ".docsible")

        if os.path.exists(docsible_path):
            docsible_present = True
        else:
            default_data = {
                'description': None,
                'requester': None,
                'users': None,
                'dt_dev': None,
                'dt_prod': None,
                'dt_update': timestamp_readme,
                'version': None,
                'time_saving': None,
                'category': None,
                'subCategory': None,
                'aap_hub': None
            }

            print(f"{docsible_path} not found. Initializing...")
            try:
                initialize_docsible(docsible_path, default_data)
                docsible_present = True
            except Exception as e:
                print(
                    f"An error occurred while initializing {docsible_path}: {e}")

    role_info = {
        "name": role_name,
        "defaults": defaults_data,
        "vars": vars_data,
        "tasks": [],
        "meta": load_yaml_generic(meta_path) or {},
        "playbook": {"content": playbook_content, "graph": 
                        generate_mermaid_playbook(yaml.safe_load(playbook_content)) if playbook_content else None},
        "docsible": load_yaml_generic(docsible_path) if docsible_present else None
    }

    tasks_dir = os.path.join(role_path, "tasks")
    role_info["tasks"] = []

    if os.path.exists(tasks_dir) and os.path.isdir(tasks_dir):
        for dirpath, dirnames, filenames in os.walk(tasks_dir):
            for task_file in filenames:
                if task_file.endswith(".yml") or task_file.endswith(".yaml"):
                    file_path = os.path.join(dirpath, task_file)
                    tasks_data = load_yaml_generic(file_path)
                    if tasks_data:
                        relative_path = os.path.relpath(file_path, tasks_dir)
                        task_info = {'file': relative_path, 'tasks': [], 'mermaid': [], "comments": []}
                        if comments:
                            task_info['comments'] = get_task_commensts(file_path)
                        if not isinstance(tasks_data, list):
                            print(
                                f"Unexpected data type for tasks in {task_file}. Skipping.")
                            continue
                        for task in tasks_data:
                            if not isinstance(task, dict):
                                print(
                                    f"Skipping unexpected data in {task_file}: {task}")
                                continue
                            if task and len(task.keys()) > 0:
                                processed_tasks = process_special_task_keys(task)
                                task_info['tasks'].extend(processed_tasks)
                                task_info['mermaid'].extend([task])

                        role_info["tasks"].append(task_info)

    if os.path.exists(readme_path):
        if not no_backup:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_readme_path = os.path.join(role_path, f"README_backup_{timestamp}.md")
            copyfile(readme_path, backup_readme_path)
            print(f'Readme file backed up as: {backup_readme_path}')
        os.remove(readme_path)

    role_info["existing_readme"] = ""

    mermaid_code_per_file = {}
    if generate_graph:
        mermaid_code_per_file = generate_mermaid_role_tasks_per_file(
            role_info["tasks"])
    
    # Render the static template
    template = env.from_string(static_template)
    output = template.render(
        role=role_info, mermaid_code_per_file=mermaid_code_per_file)

    with open(readme_path, "w") as f:
        f.write(output)

    print('Documentation generated at:', readme_path)


if __name__ == '__main__':
    doc_the_role()
