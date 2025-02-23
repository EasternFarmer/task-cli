from . import command_line, interface
from sys import argv

def main() -> None:
    if (not argv[1:]) or (argv[1].lower() in ['--help', '--h', '-h', '-help']):
        argv[1:] = ['help']
        command_line.run()
    elif argv[1].lower() == 'run':
        interface.run()
    else:
        command_line.run()

if __name__ == '__main__':
    main()