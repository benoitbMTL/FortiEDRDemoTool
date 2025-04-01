import os

def merge_python_files():
    output_file = "merged_output.txt"
    current_dir = os.getcwd()
    py_files = []

    print("Scanning current directory for Python files...\n")

    for file in os.listdir(current_dir):
        if file.endswith(".py") and file != "merge.py":
            py_files.append(file)

    if not py_files:
        print("No .py files found.")
        return

    print("Found the following Python files:")
    for f in py_files:
        print(f" - {f}")

    print("\nWriting to output file...\n")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Merged Python Files\n")
        out.write("====================\n")
        out.write("Directory structure:\n")
        for f in py_files:
            out.write(f" - {f}\n")

        for f in py_files:
            out.write(f"\n=================\n{f}\n=================\n")
            with open(f, "r", encoding="utf-8") as src:
                out.write(src.read())

    print(f"\nMerging complete! Output saved to: {output_file}")

if __name__ == "__main__":
    merge_python_files()
