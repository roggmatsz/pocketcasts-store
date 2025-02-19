import re
import subprocess
import os

def get_current_version():
    try:
        with open("setup.py", "r") as f:
            content = f.read()
            match = re.search(r"version='([^']+)'", content)  # Use regex
            if match:
                return match.group(1)
            else:
                match = re.search(r"version=\"([^\"]+)\"", content)  # Check for double quotes
                if match:
                    return match.group(1)
                else:
                    return None  # Handle error if version not found
    except FileNotFoundError:
        return None


def get_commit_count():
    try:
        output = subprocess.check_output(["git", "rev-list", "--count", "main"])  # Or master
        return int(output.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit count: {e}")
        return 0


def bump_version(current_version):
    # ... (rest of your bump_version logic remains the same)
    major, minor, revision = map(int, current_version.split("."))
    commit_count = get_commit_count()

    if commit_count > 0:  # Only bump if there are commits since last tag.
        minor += 1
        revision = 0  # Reset revision when minor is incremented
    else:
      revision = 0  # reset revision if no commits.

    new_version = f"{major}.{minor}.{revision}"
    return new_version


def update_setup_py(new_version):
    try:
        with open("setup.py", "r") as f:
            content = f.read()

        new_content = re.sub(r"version='[^']+'", f"version='{new_version}'", content) # Update with regex
        if new_content == content:
            new_content = re.sub(r"version=\"[^\"]+\"", f"version=\"{new_version}\"", content) # Update with regex

        with open("setup.py", "w") as f:
            f.write(new_content)
        print("setup.py updated successfully")
    except FileNotFoundError:
        print("setup.py not found")
    except Exception as e:
        print(f"Error updating setup.py: {e}")

if __name__ == "__main__":
    current_version = get_current_version()
    if current_version:
        new_version = bump_version(current_version)

        with open("version.txt", "w") as f:  # Used to pass version to github actions
            f.write(new_version)

        print(f"New version: {new_version}")
        update_setup_py(new_version)

    else:
        print("Error: Could not retrieve current version.")