# Conventional Commits pre-commit hook

A [`pre-commit`](https://pre-commit.com) hook to check branch name formatting.

## Installation
Add the following entry into your `.pre-commit-config.yaml` file:
```
repos:
  # - repo: ...

  - repo: https://github.com/igorhrcek/pre-commit-branch-name-validation
    rev: v1.0.0
    hooks:
      - id: pre-commit-branch-validation
        stages: [pre-push, post-checkout]
        args: [] # optional: list of allowed branch types, issue prefixes and maximum length of branch description
```

Install the script:
```
pre-commit install --hook-type pre-push --hook-type post-checkout
```

## Usage
Create a branch using incorrect format:
```bash
$ git checkout -b wrong_name
$ git push origin wrong_name

Branch Name Validation ..............................................Failed
- hook id: pre-commit-branch-validation
- duration: 0.05s
- exit code: 1

Bad branch name: wrong format
Your branch name does not follow a proper formatting.

Branch name start with one of the below branch types, followed by a slash,
followed by one of the below issue tpes, followed by slash and optional description:

Branch types: feature bugfix hotfix test
Issue prefixes: issue sre

Good examples:
feature/issue-47/code-styling-improvements
bugfix/issue-125
feature/sre-128/add-new-domain
```

Create a branch using correct format:
```bash
$ git checkout -b feature/issue-12345

Branch Name Validation ..............................................Passed
```
