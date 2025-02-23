# Task-cli project
> **Cli package for managing your tasks**

## Installation

pip install this repo.
(Note: Incompatible with Python 2.x)

```sh
pip3 install task-command-line
```

(or)

```sh
pip install task-command-line
```


## Usage example

### To get help with commandline arguments

```sh
task-cli help
```

### Using Command-line Arguments

```sh
task-cli add "feed the dogs"
```


### Disable Color Output

```sh
task-cli help --no_color
```

(or)

```sh
task-cli help -nc
```

## IO Redirection

the response is written to stdout and headers/status are written to stderr so that users can take IO redirection to their advantage. This works on windows, linux and mac.

```sh
task-cli help > output.txt 2> error.txt
```

both stdout and stderr can be redirected to the same file

```sh
task-cli help > output.txt 2>&1
```
