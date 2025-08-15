import os

IGNORE_FOLDERS = {".git", "__pycache__"}


def print_folder_tree(start_path, indent=""):
    """
    Recursively prints a directory tree structure.

    This function traverses the directory structure starting from `start_path`
    and prints a visual representation of the folder hierarchy to the console.
    It ignores folders specified in the global `IGNORE_FOLDERS` set.

    Args:
        start_path (str): The absolute or relative path to the root
            directory from which to start building the tree.
        indent (str, optional): The prefix string for indentation, used
            for formatting the tree structure. This is mainly for internal
            use during recursion. Defaults to ''.
    """
    folders = [
        d
        for d in sorted(os.listdir(start_path))
        if os.path.isdir(os.path.join(start_path, d)) and d not in IGNORE_FOLDERS
    ]
    for idx, folder in enumerate(folders):
        is_last = idx == len(folders) - 1
        prefix = "└── " if is_last else "├── "
        print(indent + prefix + folder)
        extension = "    " if is_last else "│   "
        print_folder_tree(os.path.join(start_path, folder), indent + extension)


if __name__ == "__main__":
    print("SmartFlow")
    print_folder_tree("../")
