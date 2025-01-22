import src.command_line as command_line
from os import system, name as os_name

def smart_split(user_input: str) -> list[str]:
    current_word: str = ''
    words: list[str] = []
    in_string: bool = False
    for char in user_input.strip():
        if char == ' ' and not in_string:
            words.append(current_word)
            current_word = ''
        elif char == "'" or char == '"':
            in_string = not in_string
        else:
            current_word += char
    words.append(current_word)
    return words


def run() -> None:
    while True:
        user_input = smart_split(input('>>> task-cli '))
        if user_input[0].lower() in ['exit', 'quit']:
            break
        if user_input[0] == 'cls':
            system('cls' if os_name == 'nt' else 'clear')
            continue
        command_line.run(user_input)