# Import libraries
import os
import yaml
import click
from jinja2 import Environment, BaseLoader
from docsible.markdown_template import static_template
from docsible.utils.mermaid import generate_mermaid_playbook, generate_mermaid_role_tasks_per_file
from docsible.utils.yaml import load_yaml_generic, load_yaml_files_from_dir_custom

# Initialize the Jinja2 Environment
env = Environment(loader=BaseLoader)
env.from_string(static_template)

def process_special_task_keys(task, task_type='task'):
    tasks = []
    if 'block' in task:
        task_name = task.get('name', 'Unnamed_block')
        task_module = 'block'
        tasks.append({
            'name': task_name,
            'module': task_module,
            'type': 'block'
        })
        for sub_task in task['block']:
            processed_tasks = process_special_task_keys(sub_task, 'block')
            tasks.extend(processed_tasks)
    elif 'rescue' in task:
        task_name = task.get('name', 'Unnamed_rescue')
        task_module = 'rescue'
        tasks.append({
            'name': task_name,
            'module': task_module,
            'type': 'rescue'
        })
        for sub_task in task['rescue']:
            processed_tasks = process_special_task_keys(sub_task, 'rescue')
            tasks.extend(processed_tasks)
    else:
        task_name = task.get('name', 'Unnamed')
        task_module = list(task.keys())[1] if 'name' in task else list(task.keys())[0]
        tasks.append({
            'name': task_name,
            'module': task_module,
            'type': task_type
        })
    return tasks


@click.command()
@click.option('--role', default='./role', help='Path to the Ansible role directory.')
@click.option('--playbook', default=None, help='Path to the playbook file.')
@click.option('--graph', is_flag=True, help='Generate Mermaid graph for tasks.')
def doc_the_role(role, playbook, graph):
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

    document_role(role_path, playbook_content, graph)
    
def document_role(role_path, playbook_content, generate_graph):
    role_name = os.path.basename(role_path)
    readme_path = os.path.join(role_path, "README.md")
    meta_path = os.path.join(role_path, "meta", "main.yml")

    defaults_data = load_yaml_files_from_dir_custom(os.path.join(role_path, "defaults")) or []
    vars_data = load_yaml_files_from_dir_custom(os.path.join(role_path, "vars")) or []
    docsible_path = os.path.join(role_path, ".docsible")

    if os.path.exists(docsible_path):
        docsible_present = True
    else:
        docsible_present = False
        default_data = {
        'description': '',
        'requester': '',
        'users': [],
        'dt_dev': '',
        'dt_prod': '',
        'version': '',
        'time_saving': ''
        }

        if not os.path.exists(docsible_path):
            print(f"{docsible_path} not found. Initializing...")
            try:
                with open(docsible_path, 'w') as f:
                    yaml.dump(default_data, f, default_flow_style=False)
                print(f"Initialized {docsible_path} with default keys.")
            except Exception as e:
                print(f"An error occurred while initializing {docsible_path}: {e}")

    role_info = {
        "name": role_name,
        "defaults": defaults_data,
        "vars": vars_data,
        "tasks": [],
        "meta": load_yaml_generic(meta_path) or {},
        "playbook": {"content": playbook_content, "graph": generate_mermaid_playbook(yaml.safe_load(playbook_content)) if playbook_content else None},
        "docsible": load_yaml_generic(docsible_path) if docsible_present else None
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

    all_tasks = []
    for task_file in role_info["tasks"]:
        all_tasks.extend(task_file['tasks'])

    mermaid_code_per_file = {}
    if generate_graph:
        # print(role_info["tasks"])
        mermaid_code_per_file = generate_mermaid_role_tasks_per_file(role_info["tasks"])

    # Render the static template
    template = env.from_string(static_template)
    output = template.render(role=role_info, mermaid_code_per_file=mermaid_code_per_file)

    with open(readme_path, "w") as f:
        f.write(output)

    print('Documentation generated at:', readme_path)

if __name__ == '__main__':
    doc_the_role()
