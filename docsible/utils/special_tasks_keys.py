def escape_pipes(text):
    if text is None:
        return None
    elif isinstance(text, str):
        return text.replace("|", "\|")
    elif isinstance(text, list):
        return [escape_pipes(item) for item in text]


def process_special_task_keys(task, task_type='task'):
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
