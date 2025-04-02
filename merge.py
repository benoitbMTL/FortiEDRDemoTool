import os

def get_project_structure(base_dir, ignore_names=None):
    """
    Returns the project structure as a formatted string, excluding specified files/folders.
    """
    lines = []
    ignore_names = ignore_names or []

    for root, dirs, files in os.walk(base_dir):
        # Filter ignored directories in-place
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

def merge_python_files(include_gui=False):
    output_file = "merged_output.txt"
    base_dir = os.getcwd()

    print("Starting file merge...")

    # 1. Build project structure string
    ignore_list = ["Thumbs.db", ".git", "merge.py"]
    structure = get_project_structure(base_dir, ignore_list)

    # 2. Gather .py files
    print("Collecting Python files...")

    root_files = [f for f in os.listdir(base_dir)
                  if f.endswith(".py") and f not in ignore_list]

    subfolder = "gui" if include_gui else "backend"
    subfolder_path = os.path.join(base_dir, subfolder)
    subfolder_files = []

    if os.path.isdir(subfolder_path):
        subfolder_files = [os.path.join(subfolder, f)
                           for f in os.listdir(subfolder_path)
                           if f.endswith(".py")]

    all_files = root_files + subfolder_files

    # 3. Write output
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
    # Set to True to merge GUI files instead of backend
    merge_python_files(include_gui=False)
