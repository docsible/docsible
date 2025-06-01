import subprocess
import re


def get_repo_info(path: str) -> dict | None:
    """
    Retrieves repository information (URL, branch, type) for a given path.
    Converts SSH Git URLs to their HTTPS equivalents.
    """
    try:
        # Check if inside a git repo
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True, timeout=5
        )
        if result.stdout.strip() != 'true':
            return None

        # Get remote URL configured for 'origin'
        raw_remote_url = subprocess.run(
            ["git", "-C", path, "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True, timeout=5
        ).stdout.strip()

        # Attempt to convert SSH-style URLs to HTTPS
        processed_url = raw_remote_url
        if processed_url.startswith("git@"):
            # Handles git@hostname:path/to/repo.git
            # Example: git@gitlab.com:user/project.git -> https://gitlab.com/user/project.git
            processed_url = "https://" + processed_url[4:].replace(":", "/", 1)
        elif processed_url.startswith("ssh://"):
            # Handles ssh://git@hostname/path/to/repo.git
            # Example: ssh://git@gitlab.com/user/project.git -> https://gitlab.com/user/project.git
            # Example: ssh://git@gitlab.com:2222/user/project.git -> https://gitlab.com/user/project.git
            # This regex also handles an optional user part before @ (e.g. ssh://myuser@...)
            # and an optional port number.
            match = re.match(
                r"ssh://(?:[^@]+@)?([^:/]+)(?::[0-9]+)?/(.+)", processed_url)
            if match:
                hostname = match.group(1)
                repo_path = match.group(2)
                processed_url = f"https://{hostname}/{repo_path}"
            # If regex doesn't match, it might be an unhandled ssh format; proceed with original raw_remote_url
            # or let it be cleaned by subsequent steps if it resembles HTTPS partially.

        # Standard cleaning: remove .git suffix and trailing slash
        if processed_url.endswith(".git"):
            processed_url = processed_url[:-4]
        processed_url = processed_url.rstrip("/")

        remote_url = processed_url

        # Get current branch
        branch = subprocess.run(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True, timeout=5
        ).stdout.strip()

        # Detect repository type from the (potentially converted) HTTPS URL
        repo_type = "default"  # Default value
        if "github.com" in remote_url:
            repo_type = "github"
        elif "gitlab" in remote_url:
            repo_type = "gitlab"
        elif "gitea" in remote_url:
            repo_type = "gitea"
        elif "bitbucket.org" in remote_url:
            repo_type = "bitbucket"

        return {
            "repository": remote_url,
            "branch": branch,
            "repository_type": repo_type
        }
    except subprocess.CalledProcessError:
        # This can happen if not a git repo, or git commands fail
        return None
    except subprocess.TimeoutExpired:
        print(f"Git command timed out for path: {path}")
        return None
    except Exception as e:
        # Catch any other unexpected error during git processing
        print(
            f"An unexpected error occurred while getting repo info for {path}: {e}")
        return None
