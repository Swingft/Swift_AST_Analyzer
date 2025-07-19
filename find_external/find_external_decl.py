import os
import sys
import re

EXCLUDE_KEYWORDS = ["test", "example", "sample", "docs"]
DECLARATION_PATTERNS = {
    "protocol": re.compile(r"^\s*protocol\s+(\w+)"),
    "class": re.compile(r"^\s*class\s+(\w+)"),
    "struct": re.compile(r"^\s*struct\s+(\w+)"),
    "function": re.compile(r"^\s*(?:\w+\s+)?func\s+(\w+\s*\(.*\))")
}

def is_exclude_keywords(path):
    path = path.lower()
    parts = path.split(os.sep)
    library_folders = ["checkouts", "pods", "vendor", "thirdparty", "external"]
    idx = -1
    for folder in library_folders:
        if folder in parts:
            idx = parts.index(folder)
            break
    if idx == -1:
        return True
    else:
        sub_parts = parts[idx + 1:]

    for keyword in EXCLUDE_KEYWORDS:
        if keyword in sub_parts:
            return True
    return False


def find_declarations(file):
    declarations = set()
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                for kind, pattern in DECLARATION_PATTERNS.items():
                    match = pattern.match(line)
                    if match:
                        name = match.group(1)
                        declarations.add((kind, name))

    except Exception as e:
        print(f"Error {file}: {e}")
    return declarations


def collect_declarations(directory):
    swift_files = []
    collections = set()
    temp = []
    for path, _, files in os.walk(directory):
        if is_exclude_keywords(path):
            continue
        for file in files:
            if file.endswith(".swift"):
                file_path = os.path.join(path, file)
                swift_files.append(file_path)
    
    for file in swift_files:
        collections.update(find_declarations(file))
    return collections


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    library_dir = sys.argv[1]
    declarations = collect_declarations(library_dir)

    output_dir = "../output"
    output_file = "external_dependencies.txt"
    output_path = os.path.join(output_dir, output_file)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"--{library_dir}\n\n")
        for kind, name in declarations:
            f.write(f"{kind}: {name}\n")


if __name__ == "__main__":
    main()
