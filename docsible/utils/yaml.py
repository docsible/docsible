"""Module providing yaml parsing functions"""
import os
import yaml


def load_yaml_generic(filepath):
    """Function to load YAML in a standard way"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    except (FileNotFoundError, yaml.constructor.ConstructorError) as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_yaml_file_custom(filepath):
    """Function to load YAML, evalate comments and avoid to report vault values"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        collected_data = {}
        current_title = None
        current_required = None
        current_list_var = None
        current_list_items = []
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
                if not stripped_line.startswith("#"):
                    if current_list_var:
                        collected_data[current_list_var] = {
                            'value': current_list_items,
                            'title': current_title,
                            'required': current_required
                        }
                        current_list_var = None
                        current_list_items = []

                    # Added dis to avoid inline comments to be part of the value
                    stripped_line = stripped_line.split("#")[0].rstrip()
                    # If the inline comment is on an array variable:
                    if stripped_line.endswith(":"):
                        current_list_var = stripped_line[:-1].strip()
                        current_list_items = []
                        continue

                    parts = stripped_line.split(":", 1)
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
                    current_title = None
                    current_required = None

            elif stripped_line.endswith(":"):
                current_list_var = stripped_line[:-1].strip()
                current_list_items = []

            elif current_list_var:
                current_list_items.append(stripped_line.split("#")[0])

            else:
                current_title = None
                current_required = None

        if current_list_var:
            collected_data[current_list_var] = {
                'value': current_list_items,
                'title': current_title,
                'required': current_required
            }

        return collected_data

    except (FileNotFoundError, yaml.constructor.ConstructorError) as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_yaml_files_from_dir_custom(dir_path):
    """Function to load all YAML files from a given directory and include file names"""
    collected_data = []
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for yaml_file in os.listdir(dir_path):
            if yaml_file.endswith(".yml") or yaml_file.endswith(".yaml"):
                file_data = load_yaml_file_custom(os.path.join(dir_path, yaml_file))
                if file_data:
                    collected_data.append({'file': yaml_file, 'data': file_data})
    return collected_data

def get_task_commensts(filepath):
    # read task file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    task_comments = []
    task_comment = {}
    comment_line = ""
    for line in lines:
        stripped_line = line.strip()
        # the line is a comment, ad it to buffer comment_line
        if stripped_line.startswith("#"):
            comment_line =  comment_line+ stripped_line.split("#", 1)[1].strip()
        #if the line start with "- name:" assign to it the previous comment
        elif stripped_line.startswith("- name:"):
            if comment_line:
                task_name =  stripped_line.replace("- name:", "").split("#")[0].strip()
                task_comment = { "task_name": task_name, "task_comments": comment_line }
                task_comments.append(task_comment)
                comment_line = ""
        else:
            comment_line = ""
    return task_comments