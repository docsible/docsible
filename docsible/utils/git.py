import subprocess


def get_repo_info(path):
    try:
        # Check if inside a git repo
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True
        )
        if result.stdout.strip() != 'true':
            return None

        # Get remote URL
        remote_url = subprocess.run(
            ["git", "-C", path, "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        # Clean URL
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        remote_url = remote_url.rstrip("/")

        # Get current branch
        branch = subprocess.run(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        return {
            "repository": remote_url,
            "branch": branch
        }
    except subprocess.CalledProcessError:
        return None
