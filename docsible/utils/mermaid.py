import re


def sanitize_for_mermaid_id(text):
    text = text.replace("|", "_")
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
    try:
        sanitized_text = re.sub(r'[^a-z0-9À-ÿ]', ' ', text.lower())
        return break_text(sanitized_text)
    except Exception as e:
        return "cannot handle"


def sanitize_for_condition(text, max_length=50):
    sanitized_text = re.sub(r'[^a-z0-9À-ÿ]', ' ', text.lower())
    return break_text(sanitized_text, max_length)


def process_tasks(tasks, last_node, mermaid_data, parent_node=None, level=0, in_rescue_block=False):
    for i, task in enumerate(tasks):
        has_rescue = False
        task_name = task.get("name", f"Unnamed_task_{i}")
        task_module_include_tasks = task.get(
            "ansible.builtin.include_tasks") or task.get("include_tasks", False)
        task_module_import_tasks = task.get(
            "ansible.builtin.import_tasks") or task.get("import_tasks", False)
        task_module_import_playbook = task.get(
            "ansible.builtin.import_playbook") or task.get("import_playbook", False)
        task_module_include_role = task.get(
            "ansible.builtin.include_role") or task.get("include_role", False)
        task_module_import_role = task.get(
            "ansible.builtin.import_role") or task.get("import_role", False)
        task_module_include_vars = task.get(
            "ansible.builtin.include_vars") or task.get("include_vars", False)
        when_condition = task.get("when", False)
        block = task.get("block", False)
        rescue = task.get("rescue", False)
        task_name = re.sub(r"{{\s*(\w+)\s*}}", r"\1", task_name)
        sanitized_task_name = sanitize_for_mermaid_id(f"{task_name}{i}")
        sanitized_task_title = sanitize_for_title(task_name)
        if when_condition:
            if isinstance(when_condition, list):
                when_condition = " AND ".join(when_condition)
            sanitized_when_condition = f"**{sanitize_for_condition(str(when_condition)).strip()}**"
            if 'When:' not in sanitized_task_title:
                sanitized_task_title += f'<br>When: {sanitized_when_condition}'
        if block:
            block_start_node = sanitized_task_name + f'_block_start_{level}'
            mermaid_data += f'\n  {last_node}-->|Block Start| {block_start_node}[[{sanitized_task_title}]]:::block'
            last_node, mermaid_data = process_tasks(
                block, block_start_node, mermaid_data, block_start_node, level + 1, in_rescue_block=False)
            if rescue:
                has_rescue = True
                rescue_start_node = sanitized_task_name + \
                    f'_rescue_start_{level}'
                mermaid_data += f'\n  {last_node}-->|Rescue Start| {rescue_start_node}[{sanitized_task_title}]:::rescue'
                last_node, mermaid_data = process_tasks(
                    rescue, rescue_start_node, mermaid_data, block_start_node, level + 1, in_rescue_block=True)
                end_label = "End of Rescue Block"
                mermaid_data += f'\n  {last_node}-.->|{end_label}| {block_start_node}'
        elif rescue:
            rescue_start_node = sanitized_task_name + f'_rescue_start_{level}'
            mermaid_data += f'\n  {last_node}-->|Rescue Start| {rescue_start_node}[{sanitized_task_title}]:::rescue'
            last_node, mermaid_data = process_tasks(
                rescue, rescue_start_node, mermaid_data, parent_node, level + 1, in_rescue_block=True)
            end_label = "End of Rescue Block"
            mermaid_data += f'\n  {last_node}-.->|{end_label}| {parent_node}'
        else:

            if task_module_include_tasks:
                if isinstance(task_module_include_tasks, dict):
                    check_style_included_tasks = task_module_include_tasks.get(
                        'file', task_module_include_tasks)
                else:
                    check_style_included_tasks = task_module_include_tasks
                sanitized_include_tasks_name = sanitize_for_mermaid_id(
                    f"{check_style_included_tasks}{i}")
                sanitized_include_tasks_title = sanitize_for_title(
                    f"{check_style_included_tasks}")
                mermaid_data += f'\n  {last_node}-->|Include task| {sanitized_include_tasks_name}[{sanitized_task_title}<br>include_task: {sanitized_include_tasks_title}]:::includeTasks'
                last_node = sanitized_include_tasks_name

            elif task_module_import_tasks:
                if isinstance(task_module_import_tasks, dict):
                    check_style_imported_tasks = task_module_import_tasks.get(
                        'file', task_module_import_tasks)
                else:
                    check_style_imported_tasks = task_module_import_tasks
                sanitized_imported_tasks_name = sanitize_for_mermaid_id(
                    f"{check_style_imported_tasks}{i}")
                sanitized_imported_tasks_title = sanitize_for_title(
                    f"{check_style_imported_tasks}")
                mermaid_data += f'\n  {last_node}-->|Import task| {sanitized_imported_tasks_name}[/{sanitized_task_title}<br>import_task: {sanitized_imported_tasks_title}/]:::importTasks'
                last_node = sanitized_imported_tasks_name

            elif task_module_import_playbook:
                if isinstance(task_module_import_playbook, dict):
                    check_style_import_playbook = task_module_import_playbook.get(
                        'file', task_module_import_playbook)
                else:
                    check_style_import_playbook = task_module_import_playbook
                sanitized_import_playbook_name = sanitize_for_mermaid_id(
                    f"{check_style_import_playbook}{i}")
                sanitized_import_playbook_title = sanitize_for_title(
                    f"{check_style_import_playbook}")
                mermaid_data += f'\n  {last_node}-->|Import playbook| {sanitized_import_playbook_name}[/{sanitized_task_title}<br>import_playbook: {sanitized_import_playbook_title}/]:::importPlaybook'
                last_node = sanitized_import_playbook_name

            elif task_module_include_role:
                if isinstance(task_module_include_role, dict):
                    check_style_include_role = task_module_include_role.get(
                        'name', task_module_include_role)
                else:
                    check_style_include_role = task_module_include_role
                sanitized_include_role_name = sanitize_for_mermaid_id(
                    f"{check_style_include_role}{i}")
                sanitized_include_role_title = sanitize_for_title(
                    check_style_include_role)
                mermaid_data += f'\n  {last_node}-->|Include role| {sanitized_include_role_name}({sanitized_task_title}<br>include_role: {sanitized_include_role_title}):::includeRole'
                last_node = sanitized_include_role_name

            elif task_module_import_role:
                if isinstance(task_module_import_role, dict):
                    check_style_import_role = task_module_import_role.get(
                        'name', task_module_import_role)
                else:
                    check_style_import_role = task_module_import_role
                sanitized_import_role_name = sanitize_for_mermaid_id(
                    f"{check_style_import_role}{i}")
                sanitized_import_role_title = sanitize_for_title(
                    check_style_import_role)
                mermaid_data += f'\n  {last_node}-->|Import role| {sanitized_import_role_name}([{sanitized_task_title}<br>import_role: {sanitized_import_role_title}]):::importRole'
                last_node = sanitized_import_role_name

            elif task_module_include_vars:
                if isinstance(task_module_include_vars, dict):
                    check_style_include_vars = task_module_include_vars.get(
                        'file', False) or task_module_include_vars.get('dir', task_module_include_vars)
                else:
                    check_style_include_vars = task_module_include_vars
                sanitized_include_vars_name = sanitize_for_mermaid_id(
                    f"{check_style_include_vars}{i}")
                sanitized_include_vars_title = sanitize_for_title(
                    check_style_include_vars)
                mermaid_data += f'\n  {last_node}-->|Include vars| {sanitized_include_vars_name}[{sanitized_task_title}<br>include_vars: {sanitized_include_vars_title}]:::includeVars'
                last_node = sanitized_include_vars_name

            else:
                mermaid_data += f'\n  {last_node}-->|Task| {sanitized_task_name}[{sanitized_task_title}]:::task'
                last_node = sanitized_task_name

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
        mermaid_data = """flowchart TD
Start
classDef block stroke:#3498db,stroke-width:2px;
classDef task stroke:#4b76bb,stroke-width:2px;
classDef includeTasks stroke:#16a085,stroke-width:2px;
classDef importTasks stroke:#34495e,stroke-width:2px;
classDef includeRole stroke:#2980b9,stroke-width:2px;
classDef importRole stroke:#699ba7,stroke-width:2px;
classDef includeVars stroke:#8e44ad,stroke-width:2px;
classDef rescue stroke:#665352,stroke-width:2px;
"""
        last_node = "Start"
        last_node, mermaid_data = process_tasks(tasks, last_node, mermaid_data)
        mermaid_data += f'\n  {last_node}-->End'
        mermaid_codes[task_file] = mermaid_data

    return mermaid_codes
