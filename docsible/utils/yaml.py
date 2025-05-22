"""Module providing yaml parsing functions"""
import os
import yaml
import re


def vault_constructor(loader, node):
    # Handle '!vault' tag to prevent constructor issues
    return "ENCRYPTED_WITH_ANSIBLE_VAULT"


# Register the custom constructor with the '!vault' tag.
yaml.SafeLoader.add_constructor('!vault', vault_constructor)


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
    """
    Load a YAML file and extract both its data and associated metadata from comments, 
    while also tracking the line number for each key and nested item.
    The function parses the YAML file, collects metadata (title, required, choices, description) 
    from preceding comments for each key, and tracks the line number where each key appears. 
    It supports nested dictionaries and lists, and can handle multi-line values and 
    extended descriptions via special comment blocks.
    Args:
        filepath (str): Path to the YAML file.
    Returns:
        dict or None: A dictionary mapping each key path to its value, metadata, and line number,
        or None if the file is empty or an error occurs.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(filepath, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        if not data:
            return None

        result = {}
        parent_line = 0

        def is_multiline_value(line):
            """
            Determine if a line in the YAML file indicates the start of a multi-line value.
            Args:
                line (str): A line from the YAML file.
            Returns:
                bool: True if the line ends with '|', indicating a multi-line value.
            """
            return line.strip().endswith('|')

        def extract_metadata(idx):
            """
            Extract metadata (title, required, choices, description) from comments preceding a given line index.
            Args:
                idx (int or None): The line index in the file for the current key.
            Returns:
                dict: Metadata dictionary with keys 'title', 'required', 'choices', and 'description'.
            """
            if idx is None:
                return {'title': None, 'required': None, 'choices': None, 'description': None}

            comments = []
            for comment_index in range(idx - 1, -1, -1):
                line = lines[comment_index].strip()
                if line.startswith("#"):
                    comments.append(line[1:].strip())
                else:
                    break
            comments.reverse()

            meta = {'title': None, 'required': None, 'choices': None, 'description': None}

            for comment in comments:
                lc = comment.lower()
                if lc.startswith('title:'):
                    meta['title'] = comment[6:].strip()
                elif lc.startswith('required:'):
                    meta['required'] = comment[9:].strip()
                elif lc.startswith('choices:'):
                    meta['choices'] = comment[8:].strip()
                elif lc.startswith('description:'):
                    meta['description'] = comment[12:].strip()
                elif lc.startswith('description-lines:'):
                    description_lines = []
                    start_collecting = False  # Flag to start collecting lines

                    # Process all subsequent lines to collect description content
                    for subsequent_line in lines[comment_index:]:
                        line_content = subsequent_line.strip()

                        # Start collecting after `description-lines:`
                        if line_content.startswith("#") and 'description-lines:' in line_content:
                            start_collecting = True
                            continue

                        # Stop collecting when encountering `# end`
                        if line_content.startswith("# end"):
                            break
                        
                        if start_collecting:
                            if line_content.startswith("#"):
                                # Collect the line content
                                description_lines.append(
                                    f'{line_content[1:].strip()}<br>')
                            else:
                                break  # Stop if a non-comment line is encountered
                    
                    # Join all collected lines into a single description string
                    if description_lines:
                        meta['description'] = "\n".join(
                            description_lines)
            return meta

        def process_line(k, v):
            """
            Process a single key-value pair, determine its line number, extract metadata, 
            and store the result in the output dictionary.
            Args:
                k (str): The full key path (dot-separated for nested keys).
                v (Any): The value associated with the key.
            """
            nonlocal parent_line

            line_idx = None
            dictkey = k.split('.')[-1]
            vtype = type(v)

            for idx in range(parent_line, len(lines)):
                line_stripped = lines[idx].strip()

                if line_stripped.startswith("#"):
                    continue

                if isinstance(v, dict):
                    dictvalue = None
                    if dictkey.isnumeric():
                        prev_path = ".".join(k.split(".")[:-1])
                        if result.get(prev_path, {}).get("type") == "list":
                            dictkey = list(v.keys())[0]
                            dictvalue = str(list(v.values())[0])
                    if dictvalue is None:
                        # dict 
                        if line_stripped.startswith(f"{dictkey}:") or line_stripped.startswith(f"- {dictkey}:"):
                            line_idx = idx
                            break
                    else:
                        # inline dict
                        if f"{dictkey}:" in line_stripped and dictvalue in line_stripped:
                            line_idx = idx
                            break

                elif isinstance(v, list):
                    # list
                    if line_stripped.startswith(f"{dictkey}:") or line_stripped.startswith(f"- {v}"):                        
                        line_idx = idx
                        break

                else:
                    # key match
                    if line_stripped.startswith(f"{dictkey}:") or f"{dictkey}:" in line_stripped:
                        line_idx = idx
                        break
                    # bool in list
                    if vtype is bool and f"- {str(v).lower()}" in line_stripped.lower():
                        line_idx = idx
                        break
                    # none / null in list
                    if v is None and any(null_str in line_stripped.lower() for null_str in ['- none', '- null']):
                        line_idx = idx
                        break
                    # list item part 1
                    if f"- {str(v).lower()}" in line_stripped.lower():
                        line_idx = idx
                        break
                    # list item part 2 
                    if dictkey.isnumeric():
                        prev_path = ".".join(k.split(".")[:-1])
                        if result.get(prev_path, {}).get("type") == "list":
                            if str(v).lower() in line_stripped.lower():
                                line_idx = idx
                                break

            current_line = line_idx if line_idx is not None else parent_line
            parent_line = current_line

            meta = extract_metadata(current_line)

            result[k] = {
                'value': '<multiline value>' if is_multiline_value(lines[current_line]) 
                         else [] if isinstance(v, list)
                         else {} if isinstance(v, dict)
                         else v.strip() if isinstance(v, str)
                         else v,
                'title': meta['title'],
                'required': meta['required'],
                'choices': meta['choices'],
                'description': meta['description'],
                'line': current_line + 1,
                'type': 'dict' if isinstance(v, dict)
                        else 'list' if isinstance(v, list)
                        else type(v).__name__
            }

        def process_dict(base_key, value):
            """
            Recursively process a dictionary, handling each key-value pair and their nested structures.
            Args:
                base_key (str): The base key path for the current dictionary.
                value (dict): The dictionary to process.
            """
            for k, v in value.items():
                full_key = f"{base_key}.{k}"
                process_line(full_key, v)
                if isinstance(v, dict):
                    process_dict(full_key, v)
                elif isinstance(v, list):
                    process_list(full_key, v)

        def process_list(base_key, value):
            """
            Recursively process a list, handling each item and their nested structures.
            Args:
                base_key (str): The base key path for the current list.
                value (list): The list to process.
            """
            for idx, item in enumerate(value):
                full_key = f"{base_key}.{idx}"
                process_line(full_key, item)
                if isinstance(item, dict):
                    process_dict(full_key, item)
                elif isinstance(item, list):
                    process_list(full_key, item)

        for key, value in data.items():
            process_line(key, value)
            if isinstance(value, dict):
                process_dict(key, value)
            elif isinstance(value, list):
                process_list(key, value)

        return result

    except (FileNotFoundError, yaml.constructor.ConstructorError, yaml.YAMLError) as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_yaml_files_from_dir_custom(dir_path):
    """Function to load all YAML files from a given directory and include file names"""
    collected_data = []

    def process_yaml_file(full_path, dir_path):
        if full_path.endswith((".yml", ".yaml")):
            file_data = load_yaml_file_custom(full_path)
            if file_data:
                relative_path = os.path.relpath(full_path, dir_path)
                return ({'file': relative_path, 'data': file_data})
        return None
    
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        # dir-path
        for file in os.listdir(dir_path):
            full_path = os.path.join(dir_path, file)
            if os.path.isfile(full_path):
                item = process_yaml_file(full_path, dir_path)
                if item:
                    collected_data.append(item)
        # main-dir
        main_dir = os.path.join(dir_path, "main")
        if os.path.exists(main_dir) and os.path.isdir(main_dir):
            for root, _, files in os.walk(main_dir):
                for yaml_file in files:
                    full_path = os.path.join(root, yaml_file)
                    item = process_yaml_file(full_path, dir_path)
                    if item:
                        collected_data.append(item)

    return collected_data

def get_task_comments(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    task_comments = []
    comment_line = ""
    for line in lines:
        stripped_line = line.strip()

        # Accumulate comments found directly above each task
        if stripped_line.startswith("#"):
            if comment_line:
                comment_line += " "
            comment_line += stripped_line.split("#", 1)[1].strip()

        # If a new task starts with "- name:", capture the accumulated comments and task name
        elif stripped_line.startswith("- name:"):
            task_name = stripped_line.replace(
                "- name:", "").split("#")[0].strip().replace("|", "¦")
            task_comments.append({
                "task_name": task_name,
                "task_comments": comment_line.strip()  # Trim excess whitespace
            })
            comment_line = ""  # Reset for the next task

        # Reset comments if a new list item or block begins, without a "- name:"
        elif stripped_line.startswith("-") and not stripped_line.startswith("- name:"):
            if comment_line:
                # Append to the last task's comments to avoid losing data
                if task_comments:
                    task_comments[-1]["task_comments"] += " " + comment_line
            comment_line = ""

    return task_comments

def get_task_line_numbers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tasks_lines = {}
    for idx, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line.startswith("- name:"):
            task_name = stripped_line.replace(
                "- name:", "").split("#")[0].strip().replace("|", "¦").replace("'", "").replace('"', "")
            tasks_lines[task_name] = idx + 1

    return tasks_lines