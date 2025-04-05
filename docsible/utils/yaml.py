"""Module providing yaml parsing functions"""
import os
import yaml


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
    Function to load YAML, evaluate comments and avoid reporting vault values.

    Args:
        filepath (str): The path to the YAML file.

    Returns:
        dict: A dictionary with keys representing YAML keys and values containing the value,
              title, required, choices, description, line number, and type of each key.
              Returns None if the file is empty or an error occurs.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(filepath, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        result = {}
        if not data:
            return None

        def is_multiline_value(line):
            return line.strip().endswith('|')

        for key in data:
            for idx, line in enumerate(lines):
                if line.strip().startswith(f"{key}:"):
                    # Fetch comments from previous lines
                    comments = []
                    for comment_index in range(idx - 1, -1, -1):
                        comment_line = lines[comment_index].strip()
                        if comment_line.startswith("#"):
                            comments.append(comment_line[1:].strip())
                        else:
                            break
                    comments.reverse()

                    # Initialize with default None values
                    comment_dict = {'title': "n/a", 'required': "n/a",
                                    'choices': "n/a", 'description': "n/a"}
                    for comment in comments:
                        comment_lower = comment.lower()
                        if 'title:' in comment_lower:
                            title_index = comment_lower.find(
                                'title:') + 6  # Start after 'title:'
                            if title_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['title'] = comment[title_index:].lstrip(
                                )
                        if 'required:' in comment_lower:
                            required_index = comment_lower.find(
                                'required:') + 9  # Start after 'required:'
                            if required_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['required'] = comment[required_index:].lstrip(
                                )
                        if 'choices:' in comment_lower:
                            choices_index = comment_lower.find(
                                'choices:') + 8  # Start after 'choices:'
                            if choices_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['choices'] = comment[choices_index:].lstrip(
                                )
                        if 'description:' in comment_lower:
                            description_index = comment_lower.find(
                                'description:') + 12  # Start after 'description:'
                            if description_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['description'] = comment[description_index:].lstrip(
                                )
                        if 'description-lines:' in comment_lower:
                            description_lines = []
                            start_collecting = False  # Flag to start collecting lines

                            # Process all subsequent lines to collect description content
                            for subsequent_line in lines[comment_index:]:
                                line_content = subsequent_line.strip()

                                # Start collecting after `description-lines:`
                                if line_content.startswith("# description-lines:"):
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
                                comment_dict['description'] = "\n".join(
                                    description_lines)

                    # Handle multiline values
                    if is_multiline_value(line):
                        value = "<multiline value>"
                    else:
                        value = data[key]

                    # Handle long lists
                    if isinstance(data[key], list) and len(data[key]) > 10:
                        value = "<list too long>"

                    value_type = type(data[key]).__name__
                    result[key] = {
                        'value': value,
                        'title': comment_dict['title'],
                        'required': comment_dict['required'],
                        'choices': comment_dict['choices'],
                        'description': comment_dict['description'],
                        'line': idx + 1,
                        'type': value_type
                    }
                    break
        return result

    except (FileNotFoundError, yaml.constructor.ConstructorError, yaml.YAMLError) as e:
        print(f"Error loading {filepath}: {e}")
        return None


def load_yaml_files_from_dir_custom(dir_path):
    """Function to load all YAML files from a given directory and include file names"""
    collected_data = []
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for yaml_file in os.listdir(dir_path):
            if yaml_file.endswith(".yml") or yaml_file.endswith(".yaml"):
                file_data = load_yaml_file_custom(
                    os.path.join(dir_path, yaml_file))
                if file_data:
                    collected_data.append(
                        {'file': yaml_file, 'data': file_data})
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
                task_comments[-1]["task_comments"] += " " + comment_line
            comment_line = ""

    return task_comments
