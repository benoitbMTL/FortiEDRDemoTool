import os

INCLUDE_GUI = True       # Set to True to include files from the 'gui' folder
INCLUDE_BACKEND = True   # Set to True to include files from the 'backend' folder

def get_project_structure(base_dir, ignore_names=None):
    """
    Returns the project structure as a formatted string, excluding specified files/folders.
    """
    lines = []
    ignore_names = ignore_names or []

    for root, dirs, files in os.walk(base_dir):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_names]

        level = root.replace(base_dir, "").count(os.sep)
        indent = " " * 4 * level
        lines.append(f"{indent}{os.path.basename(root)}/")

        sub_indent = " " * 4 * (level + 1)
        for f in files:
            if f in ignore_names:
                continue
            lines.append(f"{sub_indent}{f}")
    return "\n".join(lines)

def merge_python_files(include_gui=False, include_backend=False):
    output_file = "merged_output.txt"
    base_dir = os.getcwd()

    print("Starting file merge...")

    # 1. Build the directory structure string
    ignore_list = ["Thumbs.db", ".git", "merge.py"]
    structure = get_project_structure(base_dir, ignore_list)

    # 2. Collect .py files from root and selected folders
    print("Collecting Python files...")

    root_files = [f for f in os.listdir(base_dir)
                  if f.endswith(".py") and f not in ignore_list]

    subfolder_files = []

    if include_gui:
        gui_path = os.path.join(base_dir, "gui")
        if os.path.isdir(gui_path):
            subfolder_files += [os.path.join("gui", f)
                                for f in os.listdir(gui_path)
                                if f.endswith(".py")]

    if include_backend:
        backend_path = os.path.join(base_dir, "backend")
        if os.path.isdir(backend_path):
            subfolder_files += [os.path.join("backend", f)
                                for f in os.listdir(backend_path)
                                if f.endswith(".py")]

    all_files = root_files + subfolder_files

    # 3. Write to the output file
    print("Writing merged_output.txt...")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Merged Python Files\n")
        out.write("====================\n")
        out.write("Directory structure:\n")
        out.write(structure)
        out.write("\n\nSelected Python files:\n")
        for f in all_files:
            out.write(f" - {f}\n")

        for f in all_files:
            out.write(f"\n=================\n{f}\n=================\n")
            with open(f, "r", encoding="utf-8") as src:
                out.write(src.read())

    print("Merge complete. Output saved to: merged_output.txt")

if __name__ == "__main__":
    merge_python_files(include_gui=INCLUDE_GUI, include_backend=INCLUDE_BACKEND)
