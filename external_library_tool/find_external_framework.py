import os
import sys
import re

# path
# frameworks 디렉토리 탐색
def find_external_library_path(project_root):
    paths = set()
    for dirpath, dirnames, _ in os.walk(project_root):
        for dirname in dirnames:
            if dirname.lower() == "frameworks":
                path = os.path.join(dirpath, dirname)
                paths.add(path)
    return paths

# swiftinterface 파일 탐색
def find_swiftinterface(dir_paths):
    paths = set()
    for dir_path in dir_paths:
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename.endswith(".swiftinterface"):
                    path = os.path.join(dirpath, filename)
                    paths.add(path)
    return paths

# declaration
DECLARATION_PATTERNS = {
    "protocol": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*protocol\s+([\w\.]+)", re.MULTILINE),
    "class": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*class\s+([\w\.]+)", re.MULTILINE),
    "struct": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*struct\s+([\w\.]+)", re.MULTILINE),
    "function": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*func\s+([\w\d_]+\s*\(.*?\))", re.MULTILINE),
    "variable": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]*)*(?:\w+\s+)*(?:var|let)\s+([\w\d_]+)", re.MULTILINE),
    "extension": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]+)*(?:\w+\s+)*extension\s+([\w\.]+)", re.MULTILINE),
    "enum": re.compile(r"^\s*(?:@[\w\._\(\)]+[\s]*)*(?:\w+\s+)*enum\s+([\w\.]+)", re.MULTILINE)
}

def find_declarations(si_paths, directory):
    declarations = set()
    for path in si_paths:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for key, pattern in DECLARATION_PATTERNS.items():
            find_list = pattern.findall(content)
            for name in find_list:
                declarations.add(f"{key}: {name}")
    
    output_path = "../output/external_dependencies.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n--{directory}\n\n")
        for dec in declarations:
            f.write(f"{dec}\n")
    return declarations


def main():
    if len(sys.argv) != 2:
        exit(1)
    
    project_dir = sys.argv[1]
    dir_paths = find_external_library_path(project_dir)
    si_paths = find_swiftinterface(dir_paths)
    find_declarations(si_paths, project_dir)
    
    
if __name__ == "__main__":
    main()