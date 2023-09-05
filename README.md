# Docsible

## About

Docsible is a command-line interface (CLI) written in Python that automates the documentation of Ansible roles. It generates a Markdown-formatted README file for each role by scanning the Ansible YAML files.

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

## Installation

To install Docsible, you can run:

```bash
pip install docsible
```

## Usage

To use Docsible, you can run the following command in your terminal:

```bash
docsible --role /path/to/ansible/role --playbook /path/to/playbook.yml
```

```bash
docsible --role /path/to/ansible/role # without include a playbook into readme
```

```bash
$ docsible --help
Usage: docsible [OPTIONS]

Options:
  --role TEXT      Path to the Ansible roles directory.
  --playbook TEXT  Path to the playbook file.
  --help           Show this message and exit.
```

### Flags

- `--role`: Specifies the directory path to the Ansible role.
- `--playbook`: Specifies the path to the Ansible playbook (Optional).

## Data Sources

Docsible fetches information from the following files within the specified Ansible role:

- `defaults/main.yml`: For default variables
- `vars/main.yml`: For role-specific variables
- `meta/main.yml`: For role metadata
- `tasks/*.yml`: For tasks, including special task types

## Prerequisites

Docsible works with Python 3.x and requires the following libraries:

- Click
- Jinja2
- PyYAML

## Contributing

For details on how to contribute, please read the [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
