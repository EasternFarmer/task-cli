from argparse import Namespace
from datetime import datetime  # time stamps
import json
from difflib import get_close_matches as _get_close_matches  # close match for suggestions if the command / status is invalid
import os.path
from pathlib import Path
from typing import Optional

import platformdirs

from . import colors as c  # Colored Output :D


save_path = platformdirs.user_data_path('task-cli')

save_json = dict[str, list]


class TaskCliData:
    commands: list[str] = ['add', 'update', 'undo update', 'delete', 'mark',
                           'mark-in-progress', 'mark-done', 'mark-todo', 'list',
                           'inspect', 'help']

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


def current_time() -> str:
    return str(datetime.now()).split('.')[0]


def _input_exception(mode: str, command: str) -> None:
    if mode == 'invalid command':
        print(
            f'{c.RED}Could not find command "{command}". Did you mean "{_get_close_matches(command, TaskCliData.commands, 1, 0)[0]}"?{c.RESET}'
        )
    elif mode == 'status entry':
        print(
            f'{c.RED}Could not find argument "{command}". Did you mean "{_get_close_matches(command, TaskCliData.status_options, 1, 0)[0]}"?{c.RESET}'
        )
    elif mode == 'not enough inputs':
        print(
            f'{c.RED}Not enough arguments provided for "{command}". Use the command according to it\'s signature: "{TaskCliData.command_signature[command]}".{c.RESET}'
        )
    elif mode == 'error':
        print(
            f'{c.RED}Program encountered errors. Please check if the input was valid. for more information check "crash.log"{c.RESET}'
        )
    elif mode == 'id too large':
        print(
            f'{c.RED}{c.BOLD}The Task ID you inputted is not present in the task list. Please run "{TaskCliData.command_signature["list"]}" to see all available ID\'s{c.RESET}'
        )
    elif mode == 'invalid data type':
        print(
            f'{c.RED}Non-integer passed in as ID ("{command}"). Please use a integer.{c.RESET}'
        )


def _help(page: Optional[str] = None) -> None:
    if page is None:
        page = ''

    if page.lower() == 'add':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["add"]}{c.RESET}'
        )
        print(
            'This command creates a new task and ads it to the list of tasks'
        )
        print("<description> : Description of the task you're creating")
    elif page.lower() == 'update':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["update"]}{c.RESET}'
        )
        print('This command updates an existing task')
        print(
            "<task id> : The id of a task. You can see it during creation and when listing out all of the tasks"
        )
        print(
            "<new description> : New description of the task you're creating"
        )
    elif page.lower() == 'undo':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["undo update"]}{c.RESET}'
        )
        print(
            'This command undo\'s an update executed previously on a existing task'
        )
        print(
            "<task id> : The id of a task. You can see it during creation and when listing out all of the tasks"
        )
    elif page.lower() == 'delete':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["delete"]}{c.RESET}'
        )
        print('This command deletes a task')
        print(
            "<task id> : The id of a task. You can see it during creation and when listing out all of the tasks"
        )
    elif page.lower() in ['mark', 'mark-in-progress', 'mark-done', 'mark-todo']:
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["mark"]}{c.RESET}'
        )
        print(f'This command marks a task as {TaskCliData.status_options}')
        print(
            "<task id> : The id of a task. You can see it during creation and when listing out all of the tasks"
        )
        print(
            f"<status> : status to be marked on the task (one of {TaskCliData.status_options}\n"
        )
        print(
            'This command has 3 shortcuts:\n'
            ' - mark-in-progress <task_id> - executes `mark <task_id> "in-progress"`\n'
            ' - mark-done <task_id> - executes `mark <task_id> "done"`\n'
            ' - mark-todo <task_id> - executes `mark <task_id> "todo"`'
        )
    elif page.lower() == 'list':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["list"]}{c.RESET}'
        )
        print('Lists task matching the status.')
        print(
            'Optional [status] : filter the task list by the given status. Defaults to no filter'
        )
    elif page.lower() == 'inspect':
        print(
            f'Command: {c.MAGENTA}{TaskCliData.command_signature["inspect"]}{c.RESET}'
        )
        print('This command shows very detailed information about the task')
        print(
            "<task id> : The id of a task. You can see it during creation and when listing out all of the tasks"
        )
    elif page.lower() == 'commands':
        print(
            f'Available commands: {c.GREEN}{", ".join(TaskCliData.commands)}{c.RESET}'
        )
    else:
        print('Welcome to this help page.')
        print('Use `help <help_page>`')
        print(
            f'Available help pages:\n{c.GREEN}{", ".join(TaskCliData.help_commands)}{c.RESET}'
        )


def _save(json_path: tuple[Path, str], json_data: dict) -> None:
    if not os.path.exists(json_path[0]):
        os.makedirs(json_path[0])
    with open(json_path[0] / json_path[1], 'w') as f:
        f.write(json.dumps(json_data, indent = 4))


def _load(json_path: tuple[Path, str]) -> dict[str, list]:
    try:
        with open(json_path[0] / json_path[1], 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        new_data = {"tasks": []}
        _save(json_path, new_data)
        return new_data


def _print_tasks_from_list(
    json_data: save_json,
    list_of_tasks: list[dict[str, str]],
    status: str
) -> None:
    print(f'{c.BLUE}Displaying tasks with a status of \'{status}\':{c.RESET}')
    if status.lower() == 'all':
        for task in list_of_tasks:
            if task['status'] == 'todo':
                print(
                    f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.RED}(Status: Todo){c.RESET}"
                )
            elif task['status'] == 'done':
                print(
                    f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.GREEN}(Status: Done){c.RESET}"
                )
            elif task['status'] == 'in-progress':
                print(
                    f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}. {c.YELLOW}(Status: In Progress){c.RESET}"
                )
    else:
        for task in list_of_tasks:
            print(
                f"{c.CYAN}Task (id: {json_data['tasks'].index(task)}):{c.RESET} {task['description']}."
            )


def _add(json_data: save_json, description: Optional[str]) -> dict[str, list]:
    if description is None:
        _input_exception('not enough inputs', 'add')
        return json_data
    json_data["tasks"].append(
        {
            "description": description,
            "old_description": description,
            "status": "todo",
            "created_at": current_time(),
            "updated_at": current_time()
        }
    )
    print(
        f'{c.GREEN}Task added successfully (ID: {len(json_data["tasks"]) - 1}){c.RESET}'
    )
    return json_data


def _update(
    json_data: save_json,
    option1: Optional[str],
    new_description: Optional[str]
) -> save_json:
    if option1 is None or new_description is None:
        _input_exception('not enough inputs', 'update')
        return json_data

    try:
        task_id = int(option1)
    except ValueError:
        _input_exception('invalid data type', option1)
        return json_data

    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', option1)
        return json_data
    json_data['tasks'][task_id]['old_description'] = \
    json_data['tasks'][task_id]['description']
    json_data['tasks'][task_id]['description'] = new_description
    json_data['tasks'][task_id]['updated_at'] = current_time()
    print(f'{c.GREEN}Task updated successfully (ID: {task_id}){c.RESET}')
    return json_data


def _delete(json_data: save_json, option1: Optional[str]) -> save_json:
    if option1 is None:
        _input_exception('not enough inputs', 'delete')
        return json_data
    try:
        task_id = int(option1)
    except ValueError:
        _input_exception('invalid data type', option1)
        return json_data

    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', option1)
        return json_data
    print(
        f'{c.BOLD}{c.RED}This will result in all task ids after task "{json_data["tasks"][task_id]["description"]}" to decrease by one.{c.RESET}'
    )
    if input(
            f'Are you sure you want to delete Task "{json_data["tasks"][task_id]["description"]}" with an id of {task_id}? (y/n) '
    ).lower() in ['y', 'yes', 'agree', 'why not', 'let\'s ball', 'we live once',
                  'if you say so', 'qwerty']:
        del json_data['tasks'][task_id]
        print(
            f'{c.GREEN}Task deleted successfully (previous ID: {task_id}){c.RESET}'
        )
    else:
        print(
            f'{c.RED}Task deletion successfully cancelled (ID: {task_id}){c.RESET}'
        )

    return json_data


def _undo_update(json_data: save_json, option1: Optional[str]) -> save_json:
    if option1 is None:
        _input_exception('not enough inputs', 'undo update')
        return json_data
    try:
        task_id = int(option1)
    except ValueError:
        _input_exception('invalid data type', option1)
        return json_data

    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', option1)
        return json_data
    json_data['tasks'][task_id]['description'], json_data['tasks'][task_id][
        'old_description'] = json_data['tasks'][task_id]['old_description'], \
        json_data['tasks'][task_id]['description']
    json_data['tasks'][task_id]['updated_at'] = str(datetime.now()).split('.')[
        0]
    print(f'{c.GREEN}Task rolled back successfully (ID: {task_id}){c.RESET}')
    return json_data


def _mark(
    json_data: save_json,
    option1: Optional[str],
    status: Optional[str]
) -> save_json:
    if option1 is None or status is None:
        _input_exception('not enough inputs', 'mark')
        return json_data
    try:
        task_id = int(option1)
    except ValueError:
        _input_exception('invalid data type', option1)
        return json_data

    status = '-'.join(status.split())
    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', option1)
        return json_data
    if status in TaskCliData.status_options:
        json_data['tasks'][task_id]['status'] = status
        json_data['tasks'][task_id]['updated_at'] = \
            str(datetime.now()).split('.')[0]
        print(f'{c.GREEN}Task marked successfully (ID: {task_id}){c.RESET}')
        return json_data
    _input_exception('status entry', status)
    return json_data


def _list(json_data: save_json, status: Optional[str]) -> None:
    if status is None:
        _print_tasks_from_list(
            json_data,
            [json_data['tasks'][task_id] for task_id in
             range(len(json_data['tasks']))],
            'ALL'
        )
    elif status == 'todo':
        todo_tasks = [json_data['tasks'][task_id] for task_id
                      in range(len(json_data['tasks']))
                      if json_data['tasks'][task_id]['status'] == 'todo']
        _print_tasks_from_list(json_data, todo_tasks, 'TODO')
    elif status == 'in-progress':
        in_progress_tasks = [json_data['tasks'][task_id] for task_id in
                             range(len(json_data['tasks'])) if
                             json_data['tasks'][task_id][
                                 'status'] == 'in-progress']
        _print_tasks_from_list(json_data, in_progress_tasks, 'TODO')
    elif status == 'done':
        done_tasks = [json_data['tasks'][task_id] for task_id in
                      range(len(json_data['tasks'])) if
                      json_data['tasks'][task_id]['status'].lower() == 'done']
        _print_tasks_from_list(json_data, done_tasks, 'DONE')
    else:
        _input_exception('status entry', status)


def _inspect(json_data: save_json, option1: Optional[str]) -> None:
    try:
        task_id = int(option1)
    except ValueError:
        _input_exception('invalid data type', option1)
        return

    if task_id >= len(json_data['tasks']):
        _input_exception('id too large', option1)
        return
    print(
        f'{c.CYAN}Task description:{c.RESET} {json_data["tasks"][task_id]["description"]}'
    )
    print(
        f'{c.CYAN}Task\'s old description:{c.RESET} {json_data["tasks"][task_id]["old_description"]} {c.YELLOW}(for the "undo update" command){c.RESET}'
    )
    print(
        f'{c.CYAN}Task status:{c.RESET} {json_data["tasks"][task_id]["status"]}'
    )
    print(
        f'{c.CYAN}Task created at:{c.RESET} {json_data["tasks"][task_id]["created_at"]}'
    )
    print(
        f'{c.CYAN}Task last updated at:{c.RESET} {json_data["tasks"][task_id]["updated_at"]}'
    )


def parse_args() -> Namespace:
    import argparse
    parser = argparse.ArgumentParser(
        prog = 'task-cli',
        epilog = 'for full help use the `help` command'
    )
    parser.add_argument(
        'command',
        type = str,
    )
    parser.add_argument('option1', nargs = '?', default = None)
    parser.add_argument('option2', nargs = '?', default = None)
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    if args.command.lower() == 'help':  # help
        _help(args.option1)
        return
    data = _load((save_path, 'task_list.json'))

    if args.command.lower() == 'add':
        data = _add(data, args.option1)
    elif args.command.lower() == 'list':
        _list(data, args.option1)
    elif args.command.lower() == 'update':
        data = _update(data, args.option1, args.option2)
    elif args.command.lower() == 'mark':
        data = _mark(data, args.option1, args.option2)
    elif args.command.lower() == 'mark-todo':
        data = _mark(data, args.option1, 'todo')
    elif args.command.lower() == 'mark-done':
        data = _mark(data, args.option1, 'done')
    elif args.command.lower() == 'mark-in-progress':
        data = _mark(data, args.option1, 'in-progress')
    elif args.command.lower() == 'delete':
        data = _delete(data, args.option1)
    elif args.command.lower() == 'inspect':
        _inspect(data, args.option1)
    elif args.command == 'undo' and args.option1 == 'update':
        data = _undo_update(data, args.option2)
    else:
        _input_exception('invalid command', args.command)
    _save((save_path, 'task_list.json'), data)