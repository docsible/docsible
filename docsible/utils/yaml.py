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


def get_multiline_indicator(line):
    """
    Detect and map YAML multiline scalar indicators to a descriptive name.
    Handles all combinations of |, >, +, -, and 1-9 indent levels.
    Returns: e.g., 'literal', 'folded_keep_indent_2', or 'invalid_...'
    """
    match = re.match(r'^\s*\w[\w\-\.]*\s*:\s*([>|][^\s#]*)', line)
    if not match:
        return None

    raw = match.group(1)

    # Invalid if multiple digits or unknown characters
    if re.search(r'\d{2,}', raw) or re.search(r'[^>|0-9+-]', raw):
        return f'invalid_{raw}'

    style = 'literal' if raw.startswith('|') else 'folded'
    chomping = None
    indent = None

    # Extract components
    chomp_match = re.search(r'[+-]', raw)
    indent_match = re.search(r'[1-9]', raw)

    if chomp_match:
        chomping = chomp_match.group(0)
    if indent_match:
        indent = indent_match.group(0)

    # Build result
    name = style
    if chomping == '+':
        name += '_keep'
    elif chomping == '-':
        name += '_strip'
    if indent:
        name += f'_indent_{indent}'

    return name


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
            indicator_name = get_multiline_indicator(lines[current_line])
            result[k] = {
                'value': f"<multiline value: {indicator_name}>" if indicator_name
                        else [] if isinstance(v, list)
                        else {} if isinstance(v, dict)
                        else v.strip() if isinstance(v, str)
                        else v,
                'multiline_indicator': indicator_name,
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


def get_task_comments(filepath: str) -> list[dict[str, str]]:
    """
    Extracts comments for Ansible tasks.
    - For any named task (block or regular), uses any immediately preceding comments.
    - A blank line between a comment and the next task (or its direct comments)
      will prevent the earlier comment from being associated with that task.
    - Ignores comments not immediately preceding a named task due to other
      intervening non-comment lines.
    - Handles task names containing '#' if they are quoted, while still removing
      actual inline comments.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found {filepath}")
        return []
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    output_task_comments = []
    # This list will hold comment lines gathered immediately before a potential task.
    candidate_comments = []

    for i, line_content in enumerate(lines):
        stripped_line = line_content.strip()

        if stripped_line.startswith("#"):
            # Collect comments that might belong to the next task
            candidate_comments.append(stripped_line[1:].strip())
        elif stripped_line.startswith("- name:"):
            # This line defines a task. Process it and its collected candidate_comments.
            try:
                # Get the entire string part after "- name:"
                task_name_value_and_inline_comment = stripped_line.split(":", 1)[1]

                # Robustly find the first '#' that is NOT within quotes
                # to separate the actual task name value from a true inline comment.
                in_single_quote = False
                in_double_quote = False
                name_part_end_index = len(task_name_value_and_inline_comment)

                for k, char_code in enumerate(task_name_value_and_inline_comment):
                    # Basic quote state machine (doesn't handle escaped quotes within quotes)
                    if char_code == "'" and (k == 0 or task_name_value_and_inline_comment[k-1] != '\\'):
                        in_single_quote = not in_single_quote
                    elif char_code == '"' and (k == 0 or task_name_value_and_inline_comment[k-1] != '\\'):
                        in_double_quote = not in_double_quote
                    elif char_code == '#' and not in_single_quote and not in_double_quote:
                        name_part_end_index = k  # Found start of a true inline comment
                        break

                task_name_raw = task_name_value_and_inline_comment[:name_part_end_index].strip(
                )

            except IndexError:
                # Malformed - name: line, skip
                candidate_comments = []  # Reset comments
                continue

            # Clean task name (remove surrounding quotes if they match)
            if (task_name_raw.startswith("'") and task_name_raw.endswith("'")) or \
               (task_name_raw.startswith('"') and task_name_raw.endswith('"')):
                task_name = task_name_raw[1:-1]
            else:
                task_name = task_name_raw

            # For markdown compatibility
            task_name = task_name.replace("|", "¦")

            comment_to_assign = ""
            if candidate_comments:
                # Assign all collected candidate_comments, joined by newline
                comment_to_assign = "\n".join(candidate_comments)

            if comment_to_assign:  # Only add if there's a comment
                output_task_comments.append({
                    "task_name": task_name,
                    "task_comments": comment_to_assign
                })

            candidate_comments = []  # Reset for the next task

        elif not stripped_line:  # An empty line
            # An empty line always breaks the contiguity of comments for the next task.
            candidate_comments = []

        else:  # Any other type of line (e.g., module call, different list item)
            # These lines break the contiguity of comments leading to a task name.
            candidate_comments = []

    return output_task_comments

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
