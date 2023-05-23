import re
import sys
import argparse
import subprocess

# Define default branch types (feaitre/..., bugfix/... etc)
DEFAULT_BRANCH_TYPES = [
    "feature",
    "bugfix",
    "hotfix",
    "test",
]

# Define default issue prefixes (feature/issue-..., feature/sre-... etc)
DEFAULT_ISSUE_PREFIXES = ["issue", "sre"]

# Define branch names that are always allowed (main, master, develop etc)
ALWAYS_ALLOWED_BRANCH_NAMES = ["main", "master", "develop"]

# Define max description length
MAX_DESCRIPTION_LENGTH = 50

RESULT_SUCCESS = 0
RESULT_FAIL = 1


class Colors:
    LBLUE = "\033[00;34m"
    LRED = "\033[01;31m"
    RESTORE = "\033[0m"
    YELLOW = "\033[00;33m"


class CalledProcessError(RuntimeError):
    pass


def main(argv=[]):
    # Allow additiional params to be passed in configuration
    parser = argparse.ArgumentParser(
        prog="pre-commit-branch-validation", description="Check if branch name matches defined rules."
    )
    parser.add_argument("branch_types", type=str, nargs="*", help="Optional list of branch types to support")
    parser.add_argument("issue_prefixes", type=str, nargs="*", help="Optional list of issue prefixes to support")
    parser.add_argument(
        "allowed_branch_names", type=str, nargs="*", help="Optional list of branch names that will not be checked"
    )
    parser.add_argument(
        "description_length",
        type=str,
        default=MAX_DESCRIPTION_LENGTH,
        nargs="*",
        help="Optional parameter for maximum allowed description length",
    )

    if len(argv) < 1:
        argv = sys.argv[1:]

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return RESULT_FAIL

    # Get current branch name
    branch_name = get_current_branch()
    if branch_name is None:
        return RESULT_FAIL

    # Check current branch name agains always allowed branch names
    allowed_branch_names = always_allowed_branch_names(args.allowed_branch_names)
    if branch_name in allowed_branch_names:
        return RESULT_SUCCESS

    # Validate branch name against set rules
    if is_branch_name_valid(branch_name, args.branch_types, args.issue_prefixes, args.description_length):
        return RESULT_SUCCESS
    else:
        print(
            f"""
{Colors.LRED}Bad branch name: {Colors.RESTORE} {branch_name}
{Colors.YELLOW}Your branch name does not follow a proper formatting.

Branch name start with one of the below branch types, followed by a slash,
followed by one of the below issue tpes, followed by slash and description:{Colors.RESTORE}

Branch types: {" ".join(branch_types_list())}
Issue types: {" ".join(issue_prefixes_list())}

{Colors.YELLOW}To rename existing local branch you can use the following command:{Colors.RESTORE}
git branch -m <oldname> <newname>

{Colors.YELLOW}Good examples:{Colors.RESTORE}
feature/issue-47/code-styling-improvements
bugfix/issue-125
feature/sre-128/add-new-domain
            """
        )
        return RESULT_FAIL


def regex_branch_types(types):
    """
    Join branch types with the "|" to form or chain for regex
    """
    return "|".join(types)


def regex_issue_prefixes(prefixes):
    """
    Join issue prefixes with the "|" to form or chain for regex
    """
    return r"|".join(prefixes)


def regex_issue_numbers():
    """
    Regex string for mathing issue numbers
    """
    return r"-\d{1,5}"


def regex_delimiter():
    """
    Regex string for forward slash as delimiter
    """
    return r"/"


def regex_description(description_length):
    """
    Regex string for forward slash and up to 30 characters in length that contain no spaces
    """
    return r"([A-Za-z0-9\-]){1,%d}$" % description_length


def get_current_branch():
    """
    Determines current git branch
    """
    command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        branch_name = result.stdout.strip()

        return branch_name
    except subprocess.CalledProcessError as e:
        print("Failed to retrieve current branch name:", e)

        return None


def branch_types_list(types=[]):
    """
    Returns a final list of branch types that is merged from passed types and DEFAULT_BRANCH_TYPES
    """
    if set(types):
        return DEFAULT_BRANCH_TYPES + types

    return DEFAULT_BRANCH_TYPES


def issue_prefixes_list(prefixes=[]):
    """
    Returns a final list of issue prefixes that is merged from passed types and DEFAULT_ISSUE_PREFIXES
    """
    if set(prefixes):
        return DEFAULT_ISSUE_PREFIXES + prefixes

    return DEFAULT_ISSUE_PREFIXES


def always_allowed_branch_names(branch_names=[]):
    """
    Returns a final list of always allowed branch names that is merged from passed branch names and ALWAYS_ALLOWED_BRANCH_NAMES
    """
    if set(branch_names):
        return ALWAYS_ALLOWED_BRANCH_NAMES + branch_names

    return ALWAYS_ALLOWED_BRANCH_NAMES


def is_branch_name_valid(input, branch_types=[], issue_prefixes=[], description_length=MAX_DESCRIPTION_LENGTH):
    """
    Checks if branch name follows set rules and guidelines.

    Description after issue prefix and number is optional
    """

    branch_types = branch_types_list(branch_types)
    issue_prefixes = issue_prefixes_list(issue_prefixes)

    pattern = f"^({regex_branch_types(branch_types)}){regex_delimiter()}({regex_issue_prefixes(issue_prefixes)}){regex_issue_numbers()}{regex_delimiter()}{regex_description(description_length)}"
    regex = re.compile(pattern, re.DOTALL)

    return bool(regex.match(input))


if __name__ == "__main__":
    raise SystemExit(main())
