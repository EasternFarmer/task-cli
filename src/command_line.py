from datetime import datetime # time stamps
import json
from difflib import get_close_matches as _get_close_matches # close match for suggestions if the command / status is invalid

from src import colors as c # Colored Output :D


commands: list[str] = ['add', 'update', 'undo update', 'delete', 'mark', 'mark-in-progress', 'mark-done', 'mark-todo', 'list', 'inspect', 'help']

status_options: list[str] = ['todo', 'in-progress', 'done']


command_signature: dict[str, str] = {
    "add": 'add <description>',
    "update": 'update <task_id> <new description>',
    "undo update": 'undo update <task_id>',
    "delete": 'delete <task_id>',
    "mark": 'mark <task_id> <status>',
    "list": 'list [status]',
    "inspect": 'inspect <task_id>',
    "help": 'help [command]'
}

help_commands: list[str] = ['main_page', 'commands'] + commands[:-1]


def _input_exception(mode: str, argv: list[str]) -> None:
    if mode == 'invalid command':
        print(f'{c.RED}Could not find command "{argv[0]}". Did you mean "{_get_close_matches(argv[0], commands, 1, 0)[0]}"?{c.RESET}')
    elif mode == 'status entry':
        print(f'{c.RED}Could not find argument "{argv[0]}". Did you mean "{_get_close_matches(argv[0], status_options, 1, 0)[0]}"?{c.RESET}')
    elif mode == 'not enough inputs':
        print(f'{c.RED}Not enough arguments provided for "{argv[0]}". Use the command according to it\'s signature: "{command_signature[argv[0]][0]}".{c.RESET}')
    elif mode == 'error':
        print(f'{c.RED}Program encountered errors. Please check if the input was valid. for more information check "crash.log"{c.RESET}')
    elif mode == 'id too large':
        print(f'{c.RED}{c.BOLD}The Task ID you inputted is not present in the task list. Please run "{command_signature['list'][0]}" to see all available ID\'s{c.RESET}')
    elif mode == 'invalid data type':
        print(f'{c.RED}Non-integer passed in as ID ("{argv[0]}"). Please use a integer.{c.RESET}')


def _help(argv: list[str]) -> None:
    if not argv:
        _help(['main_page'])
        return
    match argv[0].lower():
        case 'add':
            print(f'Command: {c.MAGENTA}{command_signature['add']}{c.RESET}')
            print('This command creates a new task and ads it to the list of tasks')
            print("<description> : Description of the task you're creating")
        case 'update':
            print(f'Command: {c.MAGENTA}{command_signature['update']}{c.RESET}')
            print('This command updates an existing task')
            print("<task id> : The id of a task. You can see it during creation and when listing out all of the tasks")
            print("<new description> : New description of the task you're creating")
        case 'undo':
            print(f'Command: {c.MAGENTA}{command_signature['undo update']}{c.RESET}')
            print('This command undo\'s an update executed previously on a existing task')
            print("<task id> : The id of a task. You can see it during creation and when listing out all of the tasks")
        case 'delete':
            print(f'Command: {c.MAGENTA}{command_signature['delete']}{c.RESET}')
            print('This command deletes a task')
            print("<task id> : The id of a task. You can see it during creation and when listing out all of the tasks")
        case 'mark' | 'mark-in-progress' | 'mark-done' | 'mark-todo':
            print(f'Command: {c.MAGENTA}{command_signature['mark']}{c.RESET}')
            print(f'This command marks a task as {status_options}')
            print("<task id> : The id of a task. You can see it during creation and when listing out all of the tasks")
            print(f"<status> : status to be marked on the task (one of {status_options}\n")
            print('This command has 3 shortcuts:\n - mark-in-progress <task_id> - executes `mark <task_id> "in-progress"`\n - mark-done <task_id> - executes `mark <task_id> "done"`\n - mark-todo <task_id> - executes `mark <task_id> "todo"`')
        case 'list':
            print(f'Command: {c.MAGENTA}{command_signature['list']}{c.RESET}')
            print('Lists task matching the status.')
            print('Optional [status] : filter the task list by the given status. Defaults to no filter')
        case 'inspect':
            print(f'Command: {c.MAGENTA}{command_signature['inspect']}{c.RESET}')
            print('This command shows very detailed information about the task')
            print("<task id> : The id of a task. You can see it during creation and when listing out all of the tasks")
        case 'commands':
            print(f'Available commands: {c.GREEN}{', '.join(commands)}{c.RESET}')
        case 'main_page' | _:
            print('Welcome to this help page.')
            print('Use `help <help_page>`')
            print(f'Available help pages:\n{c.GREEN}{', '.join(help_commands)}{c.RESET}')

def _save(json_path: str, json_data: dict) -> None:
    with open(json_path, 'w') as f:
        f.write(json.dumps(json_data, indent = 4))


def _load(json_path: str) -> dict[str, list]:
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        new_data = {"tasks": []}
        _save(json_path, new_data)
        return new_data


def _print_tasks_from_list(json_data, list_of_tasks: list[dict[str, list]], status: str) -> None:
    print(f'{c.BLUE}Displaying tasks with a status of \'{status}\':{c.RESET}')
    if status.lower() == 'all':
        for task in list_of_tasks:
            if task['status'] == 'todo':
                print(f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.RED}(Status: Todo){c.RESET}")
            elif task['status'] == 'done':
                print(f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.GREEN}(Status: Done){c.RESET}")
            elif task['status'] == 'in-progress':
                print(f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.YELLOW}(Status: In Progress){c.RESET}")
    else:
        for task in list_of_tasks:
            print(f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}.")


def _add(json_data: dict[str, list], argv: list[str]) -> dict[str, list]:
    if not argv:
        _input_exception('not enough inputs', ['add'])
        return json_data
    description = ' '.join(argv)
    json_data["tasks"].append(
        {
            "description": description,
            "old_description": description,
            "status": "todo",
            "created_at": str(datetime.now()).split('.')[0],
            "updated_at": str(datetime.now()).split('.')[0]
        }
    )
    print(f'{c.GREEN}Task added successfully (ID: {len(json_data['tasks']) - 1}){c.RESET}')
    return json_data


def _update(json_data: dict[str, list], argv: list[str]) -> dict[str, list]:
    if len(argv) < 2:
        _input_exception('not enough inputs', ['update'])
        return json_data

    try:
        task_id = int(argv[0])
    except ValueError:
        _input_exception('invalid data type', argv)
        return json_data

    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', argv)
        return json_data
    new_description = ' '.join(argv[1:])
    json_data['tasks'][task_id]['old_description'] = json_data['tasks'][task_id]['description']
    json_data['tasks'][task_id]['description'] = new_description
    json_data['tasks'][task_id]['updated_at'] = str(datetime.now()).split('.')[0]
    print(f'{c.GREEN}Task updated successfully (ID: {task_id}){c.RESET}')
    return json_data


def _delete(json_data: dict[str, list], argv: list[str]) -> dict[str, list]:
    if not argv:
        _input_exception('not enough inputs', ['delete'])
        return json_data
    task_id = int(argv[0])
    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', argv)
        return json_data
    print(f'{c.BOLD}{c.RED}This will result in all task ids after task "{json_data['tasks'][task_id]['description']}" to decrease by one.{c.RESET}')
    match input(f'Are you sure you want to delete Task "{json_data['tasks'][task_id]['description']}" with an id of {task_id}? (y/n) ').lower():
        case 'y' | 'yes' | 'agree' | 'why not' | 'let\'s ball' | 'we live once' | 'if you say so' | 'qwerty':
            del json_data['tasks'][task_id]
            print(f'{c.GREEN}Task deleted successfully (previous ID: {task_id}){c.RESET}')
        case _:
            print(f'{c.RED}Task deletion successfully cancelled (ID: {task_id}){c.RESET}')

    return json_data


def _undo_update(json_data: dict[str, list], argv: list[str]) -> dict[str, list]:
    if not argv:
        _input_exception('not enough inputs', ['undo update'])
        return json_data
    task_id = int(argv[0])
    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', argv)
        return json_data
    json_data['tasks'][task_id]['description'], json_data['tasks'][task_id]['old_description'] = json_data['tasks'][task_id]['old_description'], json_data['tasks'][task_id]['description']
    json_data['tasks'][task_id]['updated_at'] = str(datetime.now()).split('.')[0]
    print(f'{c.GREEN}Task rolled back successfully (ID: {task_id}){c.RESET}')
    return json_data


def _mark(json_data: dict[str, list], argv: list[str]) -> dict[str, list]:
    task_id = int(argv[0])
    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', argv)
        return json_data
    status = '-'.join(argv[1:]).lower()
    if status in status_options:
        json_data['tasks'][task_id]['status'] = status
        json_data['tasks'][task_id]['updated_at'] = str(datetime.now()).split('.')[0]
        print(f'{c.GREEN}Task marked successfully (ID: {task_id}){c.RESET}')
        return json_data
    _input_exception('status entry', [status])
    return json_data


def _list(json_data: dict[str, list], argv: list[str]) -> None:
    if not argv:
        _print_tasks_from_list(json_data, [json_data['tasks'][task_id] for task_id in range(len(json_data['tasks']))], 'ALL')
    elif argv[0] == 'todo':
        todo_tasks = [json_data['tasks'][task_id] for task_id in range(len(json_data['tasks'])) if json_data['tasks'][task_id]['status'] == 'todo']
        _print_tasks_from_list(json_data, todo_tasks, 'TODO')
    elif argv[0] == 'in-progress':
        in_progress_tasks = [json_data['tasks'][task_id] for task_id in range(len(json_data['tasks'])) if json_data['tasks'][task_id]['status'] == 'in-progress']
        _print_tasks_from_list(json_data, in_progress_tasks, 'TODO')
    elif argv[0] == 'done':
        done_tasks = [json_data['tasks'][task_id] for task_id in range(len(json_data['tasks'])) if json_data['tasks'][task_id]['status'].lower() == 'done']
        _print_tasks_from_list(json_data, done_tasks, 'DONE')
    else:
        _input_exception('status entry', argv)


def _inspect(json_data: dict[str, list], argv: list[str]) -> None:
    task_id = int(argv[0])
    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', argv)
    print(f'{c.CYAN}Task description:{c.RESET} {json_data['tasks'][task_id]['description']}')
    print(f'{c.CYAN}Task\'s old description:{c.RESET} {json_data['tasks'][task_id]['old_description']} {c.YELLOW}(for the "undo update" command){c.RESET}')
    print(f'{c.CYAN}Task status:{c.RESET} {json_data['tasks'][task_id]['status']}')
    print(f'{c.CYAN}Task created at:{c.RESET} {json_data['tasks'][task_id]['created_at']}')
    print(f'{c.CYAN}Task last updated at:{c.RESET} {json_data['tasks'][task_id]['updated_at']}')


def run(argv: list[str]) -> None:
    if not argv:
        _help(['main_page'])
        return
    elif argv[0].lower() == 'help':  # help
        _help(argv[1:])
        return
    data = _load('task_list.json')

    if argv[0].lower() == 'add':                                                        # add
        data = _add(data, argv[1:])
    elif argv[0].lower() == 'list':                                                     # list
        _list(data, argv[1:])
    elif argv[0].lower() == 'update':                                                   # update
        data = _update(data, argv[1:])
    elif argv[0].lower() == 'mark':                                                     # mark
        data = _mark(data, argv[1:])
    elif argv[0].lower() == 'mark-todo':                                                # mark
        data = _mark(data, [argv[1], 'todo'])
    elif argv[0].lower() == 'mark-done':                                                # mark
        data = _mark(data, [argv[1], 'done'])
    elif argv[0].lower() == 'mark-in-progress':                                         # mark
        data = _mark(data, [argv[1], 'in-progress'])
    elif argv[0].lower() == 'delete':                                                   # delete
        data = _delete(data, argv[1:])
    elif argv[0].lower() == 'inspect':                                                  # inspect
        _inspect(data, argv[1:])
    elif len(argv) >= 2:
        if argv[0] == 'undo' and argv[1] == 'update':                                   # undo update
            data = _undo_update(data, argv[2:])
    else:
        _input_exception('invalid command', argv)
    _save('task_list.json', data)