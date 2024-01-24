"""Module with function for manage block and rescue code"""

def escape_pipes(text):
    """Function to escape pipes in string or list"""
    if isinstance(text, str):
        return text.replace("|", r"\|")
    if isinstance(text, list):
        return [escape_pipes(item) for item in text]
    return None


def process_special_task_keys(task, task_type='task'):
    """Function to process block and rescue tasks"""
    tasks = []
    if 'block' in task:
        task_name = task.get('name', 'Unnamed_block')
        task_module = 'block'
        task_when = escape_pipes(task.get('when', None))
        tasks.append({
            'name': escape_pipes(task_name),
            'module': task_module,
            'type': 'block',
            'when': task_when
        })
        for sub_task in task['block']:
            processed_tasks = process_special_task_keys(sub_task, 'block')
            tasks.extend(processed_tasks)
    elif 'rescue' in task:
        task_name = task.get('name', 'Unnamed_rescue')
        task_module = 'rescue'
        task_when = escape_pipes(task.get('when', None))
        tasks.append({
            'name': escape_pipes(task_name),
            'module': task_module,
            'type': 'rescue',
            'when': task_when
        })
        for sub_task in task['rescue']:
            processed_tasks = process_special_task_keys(sub_task, 'rescue')
            tasks.extend(processed_tasks)
    else:
        task_name = task.get('name', 'Unnamed')
        task_module = list(task.keys())[1] if 'name' in task else list(task.keys())[0]
        task_when = escape_pipes(task.get('when', None))
        tasks.append({
            'name': escape_pipes(task_name),
            'module': task_module,
            'type': task_type,
            'when': task_when
        })
    return tasks
