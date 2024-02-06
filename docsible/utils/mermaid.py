import re


def sanitize_for_mermaid_id(text):
    text = text.replace(r"\|", "_")
    # Allowing a-zA-Z0-9 as well as French accents
    return re.sub(r'[^a-zA-Z0-9À-ÿ]', '_', text)


def break_text(text, max_length=50):
    words = text.split(' ')
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + len(current_line) > max_length:
            lines.append(' '.join(current_line))
            current_length = 0
            current_line = []
        current_line.append(word)
        current_length += len(word)
    if current_line:
        lines.append(' '.join(current_line))
    return '<br>'.join(lines)


def sanitize_for_title(text):
    # Allowing a-z0-9 as well as French accents, and converting to lower case
    sanitized_text = re.sub(r'[^a-z0-9À-ÿ]', ' ', text.lower())
    return break_text(sanitized_text)


def sanitize_for_condition(text, max_length=50):
    sanitized_text = re.sub(r'[^a-z0-9À-ÿ]', ' ', text.lower())
    return break_text(sanitized_text, max_length)


def process_tasks(tasks, last_node, mermaid_data, parent_node=None, level=0, in_rescue_block=False):
    for i, task in enumerate(tasks):
        has_rescue = False
        task_name = task.get("name", f"Unnamed_task_{i}")
        task_module = task.get("ansible.builtin.include_tasks", False)
        when_condition = task.get("when", False)
        block = task.get("block", False)
        rescue = task.get("rescue", False)
        task_name = re.sub(r"{{\s*(\w+)\s*}}", r"\1", task_name)
        sanitized_task_name = sanitize_for_mermaid_id(task_name)
        sanitized_task_title = sanitize_for_title(task_name)
        if when_condition:
            if isinstance(when_condition, list):
                when_condition = " AND ".join(when_condition)
            when_condition = sanitize_for_mermaid_id(str(when_condition))
            sanitized_when_condition = sanitize_for_condition(when_condition)
            sanitized_task_name += f"_when_{when_condition}"
        if block:
            block_start_node = sanitized_task_name + f'_block_start_{level}'
            if when_condition:
                mermaid_data += f'\n  {last_node}-->|"Block Start (When: {sanitized_when_condition})"| {block_start_node}[{sanitized_task_title}]'
            else:
                mermaid_data += f'\n  {last_node}-->|Block Start| {block_start_node}[{sanitized_task_title}]'
            last_node, mermaid_data = process_tasks(
                block, block_start_node, mermaid_data, block_start_node, level + 1, in_rescue_block=False)
            if rescue:
                has_rescue = True
                rescue_start_node = sanitized_task_name + \
                    f'_rescue_start_{level}'
                mermaid_data += f'\n  {last_node}-->|Rescue Start| {rescue_start_node}[{sanitized_task_title}]'
                last_node, mermaid_data = process_tasks(
                    rescue, rescue_start_node, mermaid_data, block_start_node, level + 1, in_rescue_block=True)
                end_label = "End of Rescue Block"
                mermaid_data += f'\n  {last_node}-.->|{end_label}| {block_start_node}'
        elif rescue:
            rescue_start_node = sanitized_task_name + f'_rescue_start_{level}'
            mermaid_data += f'\n  {last_node}-->|Rescue Start| {rescue_start_node}[{sanitized_task_title}]'
            last_node, mermaid_data = process_tasks(
                rescue, rescue_start_node, mermaid_data, parent_node, level + 1, in_rescue_block=True)
            end_label = "End of Rescue Block"
            mermaid_data += f'\n  {last_node}-.->|{end_label}| {parent_node}'
        else:
            if task_module:
                mermaid_data += f'\n  {last_node}-->|Task| {sanitized_task_name}[{sanitized_task_title}] -->|Include| {task_module}'
            else:
                mermaid_data += f'\n  {last_node}-->|Task| {sanitized_task_name}[{sanitized_task_title}]'
            if when_condition:
                mermaid_data += f'\n  {sanitized_task_name}---|When: {sanitized_when_condition}| {sanitized_task_name}'
                    
            last_node = sanitized_task_name
            
            # # Add 'End of Task' line only for standalone tasks
            # if parent_node is None and not in_rescue_block:
            #     end_label = "End of Task"
            #     mermaid_data += f'\n  {last_node}-.->|{end_label}| {last_node}'

    if parent_node and not in_rescue_block and not has_rescue:
        end_label = "End of Block"
        mermaid_data += f'\n  {last_node}-.->|{end_label}| {parent_node}'
            
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
        if roles:
            for i, role in enumerate(roles):
                role_name = role["role"] if isinstance(role, dict) else role
                role_name = role_name if role_name else f"Unnamed_role_{i}"
                role_name = re.sub(r"{{\s*(\w+)\s*}}", r"\1", role_name)
                sanitized_role_name = sanitize_for_mermaid_id(role_name)
                sanitized_role_title = sanitize_for_title(role_name)
                mermaid_data += f'\n  {last_node}-->|Role| {sanitized_role_name}[{sanitized_role_title}]'
                last_node = sanitized_role_name
        last_node, mermaid_data = process_tasks(tasks, last_node, mermaid_data)
    return mermaid_data


def generate_mermaid_role_tasks_per_file(tasks_per_file):
    mermaid_codes = {}
    for task_info in tasks_per_file:
        task_file = task_info['file']
        tasks = task_info['mermaid']
        mermaid_data = "flowchart TD\n  Start"
        last_node = "Start"
        last_node, mermaid_data = process_tasks(tasks, last_node, mermaid_data)
        mermaid_data += f'\n  {last_node}-->End'
        mermaid_codes[task_file] = mermaid_data

    return mermaid_codes
