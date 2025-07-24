import os
import sys
import re

# path
def get_project_name(project_root):
    names = []
    for _, dirname, _ in os.walk(project_root):
        for item in dirname:
            if item.endswith(".xcodeproj") or item.endswith(".xcworkspace"):
                name = item.split(".")[0]
                names.append(name)
    return names

def find_external_library_path(project_root):
    paths = set()

    build_checkouts = os.path.join(project_root, ".build", "checkouts")
    if os.path.isdir(build_checkouts):
        paths.add(build_checkouts)
    
    pods = os.path.join(project_root, "Pods")
    if os.path.isdir(pods):
        paths.add(pods)

    for dirpath, _, _ in os.walk(project_root):
        build_checkouts = os.path.join(dirpath, ".build", "checkouts")
        if os.path.isdir(build_checkouts):
            paths.add(build_checkouts)
        
        pods = os.path.join(dirpath, "Pods")
        if os.path.isdir(pods):
            paths.add(pods)
    
    return paths

def find_external_library_path_in_derived(proejct_names):
    paths = []
    derived_data = os.path.expanduser("~/Library/Developer/Xcode/DerivedData/")
    
    if os.path.isdir(derived_data):
        for item in os.listdir(derived_data):
            for name in proejct_names:
                if item.startswith(name + "-"):
                    derived_path = os.path.join(derived_data, item, "SourcePackages", "checkouts")
                    paths.append(derived_path)
    return paths


# declaration
EXCLUDE_KEYWORDS = ["test", "example", "sample", "docs"]
DECLARATION_PATTERNS = {
    "protocol": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*protocol\s+([\w\.]+)", re.MULTILINE),
    "class": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*class\s+([\w\.]+)", re.MULTILINE),
    "struct": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*struct\s+([\w\.]+)", re.MULTILINE),
    "function": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*func\s+([\w\d_]+\s*\(.*?\))", re.MULTILINE),    "variable": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]*)*(?:\w+\s+)*(?:var|let)\s+([\w\d_]+)", re.MULTILINE),
    "extension": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*extension\s+([\w\.]+)", re.MULTILINE),
    "enum": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]*)*(?:\w+\s+)*enum\s+([\w\.]+)", re.MULTILINE)
}

def find_declarations(file):
    declarations = set()
    try:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
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
    for path, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".swift"):
                file_path = os.path.join(path, file)
                swift_files.append(file_path)
    
    for file in swift_files:
        collections.update(find_declarations(file))
    
    output_path = "../output/external_dependencies.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"--{directory}\n\n")
        for kind, name in collections:
            f.write(f"{kind}: {name}\n")


def main():
    if len(sys.argv) != 2:
        exit(1)
    
    project_dir = sys.argv[1]
    path = find_external_library_path(project_dir)
    derived_path = find_external_library_path_in_derived(get_project_name(project_dir))
    path.update(derived_path)

    if path:
        for p in path:
            collect_declarations(p)


if __name__ == "__main__":
    main()