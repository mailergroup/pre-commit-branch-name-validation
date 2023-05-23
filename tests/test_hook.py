import re
import pytest
import os.path
import pre_commit_branch_validation.hook as hook

TEST_PATH = os.path.abspath(os.path.dirname(__file__))

CUSTOM_BRANCH_TYPES = ["custom", "quirk"]
CUSTOM_ISSUE_PREFIXES = ["dev", "qa"]


@pytest.fixture(autouse=True)
def bad_branch():
    return "bad_name"


@pytest.fixture(autouse=True)
def branch_with_description():
    return "feature/issue-1234/this-is-description"


@pytest.fixture(autouse=True)
def bugfix_branch():
    return "bugfix/issue-890"


@pytest.fixture(autouse=True)
def custom_branch_type():
    return "custom/issue-1234"


@pytest.fixture(autouse=True)
def custom_issue_prefix():
    return "feature/dev-1234"


@pytest.fixture(autouse=True)
def feature_branch():
    return "feature/issue-150"


@pytest.fixture(autouse=True)
def hotfix_branch():
    return "hotfix/issue-1111"


@pytest.fixture(autouse=True)
def custom_branch_type_custom_issue_prefix():
    return "quirk/qa-1234/this-is-description"


class TestHooks:
    def test_given_custom_branch_types_when_calling_regex_types_it_will_include_custom_types(self):
        result = hook.regex_branch_types(CUSTOM_BRANCH_TYPES)
        regex = re.compile(result)

        assert regex.match("custom")
        assert regex.match("quirk")

    def test_given_custom_issue_types_when_calling_regex_types_it_will_include_custom_types(self):
        result = hook.regex_issue_prefixes(CUSTOM_ISSUE_PREFIXES)
        regex = re.compile(result)

        assert regex.match("dev")
        assert regex.match("qa")

    def test_given_delimiter_in_branch_name_when_calling_regex_delimiter_it_will_pass(self):
        result = hook.regex_delimiter()
        regex = re.compile(result)

        assert regex.match("/")

    def test_given_five_digits_in_issue_name_when_calling_regex_issue_numbers_it_will_pass(self):
        result = hook.regex_issue_numbers()
        regex = re.compile(result)

        assert regex.match("-12345")

    def test_given_default_branch_types_when_calling_hook_it_will_return_only_default_branch_types(self):
        assert hook.branch_types_list() == hook.DEFAULT_BRANCH_TYPES

    def test_given_additional_branch_types_when_calling_hook_it_will_include_custom_types(self):
        result = hook.branch_types_list(["superduper"])

        assert set(["superduper", *hook.DEFAULT_BRANCH_TYPES]) == set(result)

    def test_given_default_issue_prefixes_when_calling_hook_it_will_return_only_default_prefixes(self):
        assert hook.issue_prefixes_list() == hook.DEFAULT_ISSUE_PREFIXES

    def test_given_additional_issue_prefixes_when_calling_hook_it_will_include_custom_prefixes(self):
        result = hook.issue_prefixes_list(["dupersuper"])

        assert set(["dupersuper", *hook.DEFAULT_ISSUE_PREFIXES]) == set(result)

    def test_given_always_allowed_branch_names_when_calling_hook_it_will_return_only_allowed_branch_names(self):
        assert hook.always_allowed_branch_names() == hook.ALWAYS_ALLOWED_BRANCH_NAMES

    @pytest.mark.parametrize("branch_type", hook.DEFAULT_BRANCH_TYPES)
    def test_given_each_type_from_default_types_when_calling_hook_it_will_return_true(self, branch_type):
        input = f"{branch_type}/issue-1234"

        assert hook.is_branch_name_valid(input)

    @pytest.mark.parametrize("issue_prefix", hook.DEFAULT_ISSUE_PREFIXES)
    def test_given_each_prefix_from_default_issue_prefixes_when_calling_hook_it_will_return_true(self, issue_prefix):
        input = f"feature/{issue_prefix}-1234"

        assert hook.is_branch_name_valid(input)

    @pytest.mark.parametrize("custom_branch_type", CUSTOM_BRANCH_TYPES)
    def test_given_each_type_from_custom_branch_types_when_calling_hook_it_will_return_true(self, custom_branch_type):
        input = f"{custom_branch_type}/issue-1234"

        assert hook.is_branch_name_valid(input, CUSTOM_BRANCH_TYPES)

    @pytest.mark.parametrize("custom_issue_prefix", CUSTOM_ISSUE_PREFIXES)
    def test_given_each_prefix_from_custom_issue_prefixes_when_calling_hook_it_will_return_true(self, custom_issue_prefix):
        input = f"feature/{custom_issue_prefix}-1234"

        assert hook.is_branch_name_valid(input, [], CUSTOM_ISSUE_PREFIXES)

    def test_given_bad_branch_name_when_calling_main_it_will_return_result_fail(self, bad_branch):
        assert not hook.is_branch_name_valid(bad_branch)

    def test_given_branch_name_with_description_when_calling_main_it_will_return_result_success(self, branch_with_description):
        assert hook.is_branch_name_valid(branch_with_description)

    def test_given_branch_name_with_description_that_exceeds_max_length_when_calling_main_it_will_return_result_fail(
        self, branch_with_description
    ):
        assert not hook.is_branch_name_valid(branch_with_description, [], [], 5)

    def test_given_bugfix_branch_name_when_calling_main_it_will_return_result_success(self, bugfix_branch):
        assert hook.is_branch_name_valid(bugfix_branch)

    def test_given_hotfix_branch_name_when_calling_main_it_will_return_result_success(self, hotfix_branch):
        assert hook.is_branch_name_valid(hotfix_branch)

    def test_given_custom_branch_name_when_calling_main_it_will_return_result_success(self, custom_branch_type):
        assert hook.is_branch_name_valid(custom_branch_type, CUSTOM_BRANCH_TYPES)

    def test_given_custom_issue_prefix_when_calling_main_it_will_return_result_success(self, custom_issue_prefix):
        assert hook.is_branch_name_valid(custom_issue_prefix, [], CUSTOM_ISSUE_PREFIXES)

    def test_given_custom_branch_type_custom_issue_prefix_when_calling_main_it_will_return_result_success(
        self, custom_branch_type_custom_issue_prefix
    ):
        assert hook.is_branch_name_valid(custom_branch_type_custom_issue_prefix, CUSTOM_BRANCH_TYPES, CUSTOM_ISSUE_PREFIXES)
