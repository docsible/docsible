import re
import hashlib

def sanitize_for_mermaid_id(text):
    text = text.replace("|", "_")
    # Allowing a-zA-Z0-9 as well as French accents
    return re.sub(r'[^a-zA-Z0-9À-ÿ]', '_', text)

def sanitize_for_title(text):
    # Allowing a-z0-9 as well as French accents, and converting to lower case
    return re.sub(r'[^a-z0-9À-ÿ]', ' ', text.lower())

def sanitize_for_condition(text):
    txt = text.replace("|", " or ")
    return re.sub(r'[^a-z0-9À-ÿ]', ' ', txt.lower()) 

def md5_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def sanitize_for_mermaid_when_id(text):
    text = text.replace("|", "_")
    hashed_text = md5_hash(text)
    return hashed_text

def process_tasks(tasks, last_node, mermaid_data, parent_node=None, level=0):
    # print(f"Processing tasks: {tasks}")
    for i, task in enumerate(tasks):
        task_name = task.get("name", f"Unnamed_task_{i}")
        when_condition = task.get("when", False)
        block = task.get("block", False)
        rescue = task.get("rescue", False)

        task_name = re.sub(r"{{\s*(\w+)\s*}}", r"\1", task_name)
        sanitized_task_name = sanitize_for_mermaid_id(task_name)
        sanitized_task_title = sanitize_for_title(task_name)

        if when_condition:
            when_condition = sanitize_for_mermaid_id(str(when_condition))
            sanitized_when_condition = sanitize_for_condition(when_condition)
            sanitized_task_name += f"_when_{when_condition}"

        if block:
            block_start_node = sanitized_task_name + f'_block_start_{level}'
            mermaid_data += f'\n  {last_node}-->|Block Start| {block_start_node}[{sanitized_task_title}]'
            last_node, mermaid_data = process_tasks(block, block_start_node, mermaid_data, block_start_node, level + 1)
        elif rescue:
            rescue_start_node = sanitized_task_name + f'_rescue_start_{level}'
            mermaid_data += f'\n  {last_node}-->|Rescue Start| {rescue_start_node}[{sanitized_task_title}]'
            last_node, mermaid_data = process_tasks(rescue, rescue_start_node, mermaid_data, parent_node, level + 1)
        else:
            mermaid_data += f'\n  {last_node}-->|Task| {sanitized_task_name}[{sanitized_task_title}]'
            if when_condition:
                mermaid_data += f'\n  {sanitized_task_name}---|When: {sanitized_when_condition}| {sanitized_task_name}'

            last_node = sanitized_task_name

        if parent_node:
            mermaid_data += f'\n  {last_node}-.->|End of Block/Rescue| {parent_node}'

    return last_node, mermaid_data


def generate_mermaid_playbook(playbook):
    mermaid_data = "flowchart TD"
    for play in playbook:
        hosts = play.get("hosts", "UndefinedHost")
        tasks = play.get("tasks", [])
        roles = play.get("roles", [])

        hosts = re.sub(r"{{\s*(\w+)\s*}}", r"\1", hosts)
        sanitized_hosts = sanitize_for_mermaid_id(hosts)

        last_node = sanitized_hosts

        # Process roles first
        if roles:
            for i, role in enumerate(roles):
                role_name = role["role"] if isinstance(role, dict) else role
                role_name = role_name if role_name else f"Unnamed_role_{i}"
                role_name = re.sub(r"{{\s*(\w+)\s*}}", r"\1", role_name)

                sanitized_role_name = sanitize_for_mermaid_id(role_name)
                sanitized_role_title = sanitize_for_title(role_name)

                mermaid_data += f'\n  {last_node}-->|Role| {sanitized_role_name}[{sanitized_role_title}]'
                last_node = sanitized_role_name

        # Then process tasks
        last_node, mermaid_data = process_tasks(tasks, last_node, mermaid_data)
    return mermaid_data



def generate_mermaid_role_tasks_per_file(tasks_per_file):
    mermaid_codes = {}
    # print(tasks_per_file)
    for task_info in tasks_per_file:
        # print("info", task_info)
        task_file = task_info['file']
        # print('file', task_file)
        tasks = task_info['tasks']
        # print("tasks", tasks)
        mermaid_data = "flowchart TD\n  Start"
        last_node = "Start"
        last_node, mermaid_data = process_tasks(tasks, last_node, mermaid_data)

        mermaid_codes[task_file] = mermaid_data
    return mermaid_codes
