import os
import re
import shutil


def empty_directory(directory_path):
    """
    Removes all files and subdirectories within the specified directory,
    leaving the directory itself empty.

    Args:
        directory_path (str): The absolute path to the directory to empty.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Attempting to empty directory: {directory_path}")
    for item_name in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item_name)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # or os.remove(item_path)
                print(f"Removed file/link: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
        except Exception as e:
            print(f"Failed to remove {item_path}. Reason: {e}")
    print(f"Directory {directory_path} has been emptied.")


def update_version(version):
    """Updates the version number in __init__.py and setup.py."""
    update_init_version(version)
    update_setup_version(version)


def update_init_version(version):
    """Updates the version number in __init__.py."""
    init_file = os.path.join(os.path.dirname(__file__), "__init__.py")
    if not os.path.exists(init_file):
        print("__init__.py not found, skipping version update.")
        return

    with open(init_file, "r") as f:
        content = f.read()

    new_content = re.sub(
        r"__version__ = \"\d+\.\d+\.\d+\"", f'__version__ = "{version}"', content
    )

    with open(init_file, "w") as f:
        f.write(new_content)


def update_setup_version(version):
    """Updates the version number in setup.py."""
    setup_file = os.path.join(os.path.dirname(__file__), "setup.py")
    if not os.path.exists(setup_file):
        print("setup.py not found, skipping version update.")
        return

    with open(setup_file, "r") as f:
        content = f.read()

    new_content = re.sub(
        r"__version__ = \"\d+\.\d+\.\d+\"", f'__version__ = "{version}"', content
    )

    with open(setup_file, "w") as f:
        f.write(new_content)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update the version number of the project."
    )
    parser.add_argument("version", help="The new version number (e.g., 1.2.3)")

    args = parser.parse_args()
    update_version(args.version)
    print(f"Version updated to {args.version}")

    empty_directory("dist")
