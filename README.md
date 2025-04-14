# Docsible

## About

Docsible is a command-line interface (CLI) written in Python that automates the documentation of Ansible roles and collections. It generates a Markdown-formatted README file for role or collection by scanning the Ansible YAML files.

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

How to create virtual env with python3
```bash
python3 -m venv docsible
source docsible/bin/activate
```

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

### Document collection
```bash
docsible --collection ./collections_tests/lucian/ --no-backup --graph
```

### Only role without playbook
```bash
docsible --role /path/to/ansible/role # without include a playbook into readme
```

```bash
$ docsible --help
Usage: docsible [OPTIONS]

Options:
  -r, --role TEXT                 Path to the Ansible role directory.
  -c, --collection TEXT           Path to the Ansible collection directory.
  -p, --playbook TEXT             Path to the playbook file.
  -g, --graph                     Generate Mermaid graph for tasks.
  -nob, --no-backup               Do not backup the readme before remove.
  -nod, --no-docsible             Do not generate .docsible file and do not include it in README.md.
  -com, --comments                Read comments from tasks files
  -ctpl, --md-collection-template TEXT Path to the collection markdown template file.
  -rtpl, -tpl, --md-role-template, --md-template TEXT
                                  Path to the role markdown template file.
  -a, --append                    Append to the existing README.md instead of
                                  replacing it.
  -o, --output TEXT               Output readme file name.
  -ru, --repository-url TEXT      Repository base URL (used for standalone roles)
  -rt, --repo-type TEXT           Repository type: github, gitlab, gitea, etc.
  -rb, --repo-branch TEXT         Repository branch name (e.g., main or master)
  --version                       Show the module version. Actual is 0.7.17
  --help                          Show this message and exit.
```

### Flags

- `--role`: Specifies the directory path to the Ansible role.
- `--collection`: Specifies the directory path to the Ansible collection.
- `--playbook`: Specifies the path to the Ansible playbook (Optional). (Works only with roles)
- `--graph`: Generate mermaid for role and playbook.
- `--no-backup`: Ignore existent README.md and remove before generate a new one. (Optional).
- `--no-docsible`: Do not generate `.docsible` metadata file and exclude it from the README.md. (Optional).
- `--comments`: Read comments from tasks files. (Optional).
- `--md-template`: Specifies the path to the markdown template file (Optional). (Works only with roles)
- `--md-collection-template`: Specifies the path to the markdown template file for documenting collections. (Optional).
- `--append`: Append existing readme.md if needed.
- `--output`: Output readme file name. Defaults to `README.md`.
- `--repository-url`: Repository base URL (used for standalone roles). Use `detect` to auto-detect using Git, or provide a full URL.
- `--repo-type`: Repository type: github, gitlab, gitea, etc. (Optional but needed if `detect` is not used with `--repository-url`).
- `--repo-branch`: Repository branch name (e.g., main or master). (Optional but needed if `detect` is not used with `--repository-url`).
- `--version`: Show the current module version and exit.
- `--help`: Show this message and exit.

## Data Sources

Docsible fetches information from the following files within the specified Ansible role:

- `defaults/*.yml/yaml`: For default variables
- `vars/*.yml/yaml`: For role-specific variables
- `meta/main.yml/yaml`: For role metadata
- `tasks/*.yml/yaml`: For tasks, including special task types and subfolders

## Example
[Thermo core simulator](https://github.com/docsible/thermo-core)

## Prerequisites

Docsible works with Python 3.x and requires the following libraries:

- Click
- Jinja2
- PyYAML

## TODO
- Clean the code
- Add more features
- Multiple playbooks handle into mermaid for collection and role

## About comments

This tool work whith several type of comments.

### On variables and defaults
The tool read comments placed before a variable, only if it begin with specific tag:

`# title:` This tag will be used for popiulate the column **Title** of the README.md. It is a short description of the variable

`# required:` This tag will be used for popiulate the column **Required** of the README.md

`# choices:` This optional tag will be used for popiulate the column **Choices** of the README.md

### On tasks

The tool will read all the line before each `- name:` of the tasks that begin with `#`.
All comment will be reported to the column **Comments** of the tasks tables.

## Contributing

For details on how to contribute, please read the [Contributing Guidelines](CONTRIBUTING.md).
Merge requests that do not follow the guidelines may be closed or require changes before being accepted.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
