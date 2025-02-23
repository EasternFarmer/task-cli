from os import system, name as os_name
import sys
import shlex
from . import command_line


# def smart_split(user_input: str) -> 'list[str]':
#     current_word: str = ''
#     words: 'list[str]' = []
#     in_string: bool = False
#     for char in user_input.strip():
#         if char == ' ' and not in_string:
#             words.append(current_word)
#             current_word = ''
#         elif char == "'" or char == '"':
#             in_string = not in_string
#         else:
#             current_word += char
#     words.append(current_word)
#     return words


def run() -> None:
    while True:
        user_input = shlex.split(input('>>> task-cli '))
        if user_input[0].lower() in ['exit', 'quit', 'q']:
            break
        if user_input[0] in ['cls', 'clear']:
            system('cls' if os_name == 'nt' else 'clear')
            continue
        sys.argv[1:] = user_input
        command_line.run()