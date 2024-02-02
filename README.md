# Docsible

## About

Docsible is a command-line interface (CLI) written in Python that automates the documentation of Ansible roles. It generates a Markdown-formatted README file for role by scanning the Ansible YAML files.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Prerequisites](#prerequisites)
- [Contributing](#contributing)
- [License](#license)

## Features
- Generates a README in Markdown format
- Scans and includes default variables and role-specific variables
- Parses tasks, including special Ansible task types like 'block' and 'rescue'
- Optionally includes playbook content in the README
- CLI-based, easy to integrate into a CI/CD pipeline
- Provides a templating feature to customize output
- Supports multiple YAML files within `tasks`, `defaults`, `vars` directory
- Includes meta-data like author and license from `meta/main.[yml/yaml]`
- Generates a well-structured table for default and role-specific variables
- Support for encrypted Ansible Vault variables

## Installation

To install Docsible, you can run:

```bash
pip install docsible
```

## Usage

To use Docsible, you can run the following command in your terminal:

### Specific path
```bash
docsible --role /path/to/ansible/role --playbook /path/to/playbook.yml --graph
```

### Current dir
```bash
docsible --graph # by default it's take tests/test.yml playbook from role if not specified any
```

### Only role without playbook
```bash
docsible --role /path/to/ansible/role # without include a playbook into readme
```

```bash
$ docsible --help
Usage: docsible [OPTIONS]

Options:
  --role TEXT      Path to the Ansible role directory.
  --playbook TEXT  Path to the playbook file.
  --graph          Generate Mermaid graph for tasks.
  --no-backup      Do not backup the readme before remove.
  --no-docsible    Do not create .docsible file and do not print relative variable to generated README.md.
  --comments       Read comments from tasks files.
  --version        Show the module version.
  --help           Show this message and exit.
```

### Flags

- `--role`: Specifies the directory path to the Ansible role.
- `--playbook`: Specifies the path to the Ansible playbook (Optional).
- `--graph`: Generate mermaid for role and playbook.
- `--no-backup`: Ignore existent README.md and remove before generate a new one. (Optional).
- `--comments`: Read comments from tasks files. (Optional).

## Data Sources

Docsible fetches information from the following files within the specified Ansible role:

- `defaults/*.yml/yaml`: For default variables
- `vars/*.yml/yaml`: For role-specific variables
- `meta/main.yml/yaml`: For role metadata
- `tasks/*.yml/yaml`: For tasks, including special task types and subfolders

## Examples
[Demo1 coffeemaker_midday role](https://github.com/exaluc/docsible/blob/main/examples/README_demo1.md)

[Demo2 coffeemaker_morning role](https://github.com/exaluc/docsible/blob/main/examples/README_demo2.md)

## Prerequisites

Docsible works with Python 3.x and requires the following libraries:

- Click
- Jinja2
- PyYAML

## TODO
- Clean the code
- Add more features

## About comments

This tool work whith several type of comments.

### On variables and defaults
The tool read comments placed before a variable, only if it begin with specific tag:

`# title:` This tag will be used for popiulate the column **Title** of the README.md. It is a short description of the variable

`# required:` This tag will be used for popiulate the column **Required** of the README.md

### On tasks

The tool will read all the line before each `- name:` of the tasks that begin with `#`.
All comment will be reported to the column **Comments** of the tasks tables.

## Contributing

For details on how to contribute, please read the [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Author

- [Lucian BLETAN](https://github.com/exaluc)