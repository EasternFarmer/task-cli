from . import command_line, interface
from sys import argv

def main() -> None:
    if not argv[1:]:
        command_line._help()
    elif argv[1].lower() == 'run':
        interface.run()
    else:
        command_line.run()

if __name__ == '__main__':
    main()