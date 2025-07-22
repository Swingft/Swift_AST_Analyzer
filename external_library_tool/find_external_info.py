import os
import sys
import subprocess
import re

# path
def get_project_name(project_root):
    names = []
    for item in os.listdir(project_root):
        if item.endswith(".xcodeproj") or item.endswith(".xcworkspace"):
            name = item.split(".")[0]
            names.append(name)
    return names


def find_external_library_path(project_root):
    paths = []

    build_checkouts = os.path.join(project_root, ".build", "checkouts")
    if os.path.isdir(build_checkouts):
        paths.append(build_checkouts)
    
    pods = os.path.join(project_root, "Pods")
    if os.path.isdir(pods):
        paths.append(pods)

    for folder in ["Vendor", "vendor", "ThirdParty", "thirdparty", "External", "external"]:
        path = os.path.join(project_root, folder)
        if os.path.isdir(path):
            paths.append(path)
    
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
    
    output_path = "../output/external_dependencies.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"--{directory}\n\n")
        for kind, name in collections:
            f.write(f"{kind}: {name}\n")


def main():
    if len(sys.argv) != 2:
        exit(1)
    
    project_dir = sys.argv[1]
    path = find_external_library_path(project_dir)
    derived_path = find_external_library_path_in_derived(get_project_name(project_dir))
    path.extend(derived_path)

    # external_syntax_run.py로 전달
    if path:
        for p in path:
            collect_declarations(p)
    else:
        print("외부 라이브러리 경로 없음")


if __name__ == "__main__":
    main()