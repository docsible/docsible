import re
import subprocess
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse, urlunparse


class GitInfoError(Exception):
    pass


class GitCommandError(GitInfoError):
    def __init__(self, message: str, stderr: str | None = None):
        super().__init__(message)
        self.stderr = stderr


class GitTimeoutError(GitInfoError):
    pass


class NotGitRepositoryError(GitInfoError):
    pass


def clean_and_standardize_url(url: str) -> str:
    processed_url = url

    scp_like_match = re.match(r"^git@([^:]+):(.*)$", processed_url)
    if scp_like_match:
        hostname = scp_like_match.group(1)
        path = scp_like_match.group(2)
        processed_url = f"ssh://git@{hostname}/{path}"

    try:
        parsed = urlparse(processed_url)
        netloc = parsed.netloc
        path = parsed.path
        force_https = False

        if "@" in netloc:
            force_https = True
            netloc_parts = netloc.rsplit('@', 1)
            if len(netloc_parts) == 2:
                netloc = netloc_parts[1]
            else:
                return ""

        if parsed.scheme in ("ssh", "git"):
            force_https = True

        final_scheme = "https" if force_https and netloc else parsed.scheme

        path = parsed.path.rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]

        return urlunparse((
            final_scheme,
            netloc,
            path,
            "",
            "",
            ""
        ))
    except (ValueError, IndexError):
        return ""


def get_repo_info(path: str | Path) -> Dict[str, str]:
    dir_path = str(path)
    timeout = 5

    try:
        is_repo_check = subprocess.run(
            ["git", "-C", dir_path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True, timeout=timeout
        )
        if is_repo_check.stdout.strip() != 'true':
            raise NotGitRepositoryError(f"Path is not inside a Git work tree: {dir_path}")

        raw_url = subprocess.run(
            ["git", "-C", dir_path, "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True, timeout=timeout
        ).stdout.strip()

        branch = subprocess.run(
            ["git", "-C", dir_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True, timeout=timeout
        ).stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise GitTimeoutError(f"Git command timed out for path: {dir_path}") from e
    except subprocess.CalledProcessError as e:
        raise GitCommandError(
            f"A Git command failed for path: {dir_path}",
            stderr=e.stderr.strip()
        ) from e

    repository_url = clean_and_standardize_url(raw_url)
    hostname = urlparse(repository_url).hostname or ""

    repo_type = "default"
    if "github" in hostname:
        repo_type = "github"
    elif "gitlab" in hostname:
        repo_type = "gitlab"
    elif "gitea" in hostname:
        repo_type = "gitea"
    elif "bitbucket.org" in hostname:
        repo_type = "bitbucket"

    return {
        "repository": repository_url,
        "branch": branch,
        "repository_type": repo_type,
    }
