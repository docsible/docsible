import pytest
from docsible.utils.git import clean_and_standardize_url

TEST_CASES = [
    # Standard credentials
    ("https://user:password@github.com/org/repo.git", "https://github.com/org/repo"),
    # Complex password with special characters
    ("https://user:p@ss:w%20rd!$*()@gitlab.com/group/project.git", "https://gitlab.com/group/project"),
    # Complex password with an @ symbol
    ("https://user:secretp@ss@bitbucket.org/team/repo", "https://bitbucket.org/team/repo"),
    # Username only
    ("https://user@gitea.com/owner/repo/", "https://gitea.com/owner/repo"),
    # Non-standard port
    ("https://user:pass@host.com:8443/path/to/repo.git", "https://host.com:8443/path/to/repo"),
    # SCP-like syntax
    ("git@github.com:org/repo.git", "https://github.com/org/repo"),
    # SSH protocol
    ("ssh://git@gitlab.com/group/project.git", "https://gitlab.com/group/project"),
    # SSH protocol with credentials
    ("ssh://user:pass@gitea.com/owner/repo.git", "https://gitea.com/owner/repo"),
    # Complex SSH protocol with credentials
    ("ssh://user:p@ss:w%20rd!$*()%2FD%2F%E0%E7890_*%2F%2F%27(%27(%27(%27(%5C@gitea.com/owner/repo.git", "https://gitea.com/owner/repo"),
    # No credentials, just cleanup
    ("https://github.com/org/repo.git/", "https://github.com/org/repo"),
    # HTTP URL should be upgraded to HTTPS due to credentials
    ("http://user:pass@github.com/org/repo", "https://github.com/org/repo"),
    # No-op, already clean
    ("https://github.com/org/repo", "https://github.com/org/repo"),
    # git protocol
    ("git://host.xz/path/to/repo.git", "https://host.xz/path/to/repo"),
    # Trailing slash
    ("https://github.com/org/repo/", "https://github.com/org/repo"),
    # Empty URL
    ("", ""),
    # Malformed SCP-like
    ("git@github.com:", "https://github.com"),
]

@pytest.mark.parametrize("input_url, expected_url", TEST_CASES)
def test_clean_and_standardize_url(input_url, expected_url):
    assert clean_and_standardize_url(input_url) == expected_url