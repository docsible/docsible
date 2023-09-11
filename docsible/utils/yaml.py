import yaml
import os

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
                if current_list_var:
                    collected_data[current_list_var] = {
                        'value': current_list_items,
                        'title': current_title,
                        'required': current_required
                    }
                    current_list_var = None
                    current_list_items = []

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
                current_title = None
                current_required = None

            elif stripped_line.endswith(":"):
                current_list_var = stripped_line[:-1].strip()
                current_list_items = []

            elif current_list_var:
                current_list_items.append(stripped_line)

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