"""Module with function for manage block and rescue code"""

def escape_pipes(text):
    """Function to escape pipes in string or list"""
    if isinstance(text, str):
        return text.replace("|", r"¦")
    if isinstance(text, list):
        return [escape_pipes(item) for item in text]
    return text  # Return the text as is if it's not a string or list.


def process_special_task_keys(task, task_type='task'):
    """Function to process tasks, including block and rescue constructs."""
    tasks = []
    known_task_params = {
        # All known Ansible task parameters.
        'action', 'any_errors_fatal', 'args', 'async', 'become', 'become_exe',
        'become_flags', 'become_method', 'become_user', 'changed_when', 'check_mode',
        'collections', 'connection', 'debugger', 'delay', 'delegate_facts', 'delegate_to',
        'diff', 'environment', 'failed_when', 'ignore_errors', 'ignore_unreachable',
        'local_action', 'loop', 'loop_control', 'module_defaults', 'name', 'no_log',
        'notify', 'poll', 'port', 'register', 'remote_user', 'retries', 'run_once',
        'tags', 'throttle', 'timeout', 'until', 'vars', 'when', 'with_', 'block',
        'rescue', 'always', 'include', 'include_tasks', 'include_role',
        'import_playbook', 'import_tasks', 'import_role', 'hosts', 'gather_facts',
        'roles', 'tasks', 'handlers', 'post_tasks', 'pre_tasks', 'strategy',
        'max_fail_percentage', 'serial', 'gather_subset', 'gather_timeout',
        'vars_files', 'vars_prompt', 'force_handlers', 'skip_tags', 'pause',
        'prompt', 'wait_for', 'wait_for_connection', 'meta', 'fact_path',
        'host_vars', 'group_vars', 'role'
    }
    
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
    task_when = escape_pipes(task.get('when', None))
    
    # Check for 'action' key
    if 'action' in task:
        action = task['action']
        if isinstance(action, dict):
            # The module name is the first key in the action dict
            task_module = list(action.keys())[0]
        else:
            # The module name is the value of the action key
            task_module = action
    else:
        # Exclude known task parameters and any keys starting with 'with_'
        module_keys = [key for key in task.keys()
                       if key not in known_task_params and not key.startswith('with_')]
        task_module = module_keys[0] if module_keys else 'unknown'

    tasks.append({
        'name': escape_pipes(task_name),
        'module': task_module,
        'type': task_type,
        'when': task_when
    })
    return tasks
