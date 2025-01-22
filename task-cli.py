from src import command_line, interface
from sys import argv
del argv[0]


if not argv:
    command_line.run(['help', 'start'])
elif argv[0].lower() == 'run':
    interface.run()
else:
    command_line.run(argv)