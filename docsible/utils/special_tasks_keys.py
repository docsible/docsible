"""Module with function for manage block and rescue code"""

def escape_pipes(text):
    """Function to escape pipes in string or list"""
    if isinstance(text, str):
        return text.replace("|", r"¦")
    if isinstance(text, list):
        return [escape_pipes(item) for item in text]
    return text  # Return the text as is if it's not a string or list


def process_special_task_keys(task, task_type='task'):
    """Function to process tasks, including block and rescue constructs."""
    tasks = []
    # All Ansible task keywords
    special_keys = {
        'action', 'any_errors_fatal', 'args', 'async', 'become', 'become_exe',
        'become_flags', 'become_method', 'become_user', 'changed_when', 'check_mode',
        'collections', 'connection', 'debugger', 'delay', 'delegate_facts', 'delegate_to',
        'diff', 'environment', 'failed_when', 'ignore_errors', 'ignore_unreachable',
        'local_action', 'loop', 'loop_control', 'module_defaults', 'name', 'no_log',
        'notify', 'poll', 'port', 'register', 'remote_user', 'retries', 'run_once',
        'tags', 'throttle', 'timeout', 'until', 'vars', 'when', 'with_', 'block',
        'rescue', 'always', 'notify', 'args', 'become_flags', 'become_exe', 'become_user',
        'become_method', 'delegate_facts', 'local_action', 'environment', 'ignore_errors',
        'register', 'remote_user', 'run_once', 'poll', 'async', 'port', 'any_errors_fatal',
        'changed_when', 'failed_when', 'diff', 'check_mode', 'loop', 'loop_control',
        'become', 'vars', 'notify', 'with_', 'until', 'retries', 'delay', 'pause',
        'prompt', 'wait_for', 'wait_for_connection', 'meta', 'import_playbook',
        'include', 'include_tasks', 'include_role', 'import_tasks', 'import_role',
        'hosts', 'gather_facts', 'roles', 'tasks', 'handlers', 'post_tasks', 'pre_tasks',
        'strategy', 'max_fail_percentage', 'serial', 'connection', 'gather_subset',
        'gather_timeout', 'remote_user', 'vars_files', 'vars_prompt', 'force_handlers',
        'tags', 'skip_tags', 'become', 'become_user', 'become_method', 'become_flags',
        'run_once', 'delegate_to', 'any_errors_fatal', 'environment', 'diff', 'check_mode',
        'fact_path', 'host_vars', 'group_vars'
    }
    
    # Remove any empty strings from special_keys
    special_keys.discard('')
    
    for block_type in ('block', 'rescue', 'always'):
        if block_type in task:
            task_name = task.get('name', f'Unnamed_{block_type}')
            task_module = block_type
            task_when = escape_pipes(task.get('when', None))
            tasks.append({
                'name': escape_pipes(task_name),
                'module': task_module,
                'type': block_type,
                'when': task_when
            })
            for sub_task in task[block_type]:
                processed_tasks = process_special_task_keys(sub_task, block_type)
                tasks.extend(processed_tasks)
            return tasks  # Exit after processing block, rescue, or always

    # Handle regular tasks
    task_name = task.get('name', 'Unnamed')
    # Exclude special keys to find the module name
    module_keys = [key for key in task.keys() if not any(key.startswith(special_key) for special_key in special_keys)]
    task_module = module_keys[0] if module_keys else 'unknown'
    task_when = escape_pipes(task.get('when', None))
    tasks.append({
        'name': escape_pipes(task_name),
        'module': task_module,
        'type': task_type,
        'when': task_when
    })
    return tasks
