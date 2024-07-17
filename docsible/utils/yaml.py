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
              title, required, description, line number, and type of each key.
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
                    comment_dict = {'title': "n/a", 'required': "n/a", 'description': "n/a"}
                    for comment in comments:
                        comment_lower = comment.lower()
                        if 'title:' in comment_lower:
                            title_index = comment_lower.find('title:') + 6  # Start after 'title:'
                            if title_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['title'] = comment[title_index:].lstrip()
                        if 'required:' in comment_lower:
                            required_index = comment_lower.find('required:') + 9  # Start after 'required:'
                            if required_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['required'] = comment[required_index:].lstrip()
                        if 'description:' in comment_lower:
                            description_index = comment_lower.find('description:') + 12  # Start after 'description:'
                            if description_index > -1:
                                # Trim any whitespace after the colon before capturing the value
                                comment_dict['description'] = comment[description_index:].lstrip()

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