import os
import sys
import re

# 프로젝트 이름 탐색
def get_project_name(project_root):
    names = []
    for _, dirname, _ in os.walk(project_root):
        for item in dirname:
            if item.endswith(".xcodeproj") or item.endswith(".xcworkspace"):
                name = item.split(".")[0]
                names.append(name)
    return names

# 외부라이브러리 탐색
def find_external_library(project_root):
    dir_paths = set()

    # 프로젝트 파일 내부 경로
    for dirpath, _, _ in os.walk(project_root):
        for dir in [".build/checkouts", "Pods"]:
            candidate = os.path.join(dirpath, dir)
            if os.path.isdir(candidate):
                dir_paths.add(candidate)
    
    # 프로젝트 파일 외부 경로
    derived_data = os.path.expanduser("~/Library/Developer/Xcode/DerivedData/")
    project_names = get_project_name(project_root)
    if os.path.isdir(derived_data):
        for item in os.listdir(derived_data):
            for name in project_names:
                if item.startswith(name + "-"):
                    derived_path = os.path.join(derived_data, item, "SourcePackages", "checkouts")
                    dir_paths.add(derived_path)
   
    # .swift 파일 수집 및 저장
    swift_flles = []
    for dir_path in dir_paths:
        for path, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".swift"):
                    file_path = os.path.join(path, file)
                    swift_flles.append(file_path)
    return swift_flles


# 선언부 추출
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

def collect_declarations(swift_files):
    for file in swift_files:
        collections = find_declarations(file)
        output_path = "../output/external_dependencies.txt"
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n--{file}\n\n")
            for kind, name in collections:
                f.write(f"{kind}: {name}\n")


def main():
    if len(sys.argv) != 2:
        exit(1)
    
    project_dir = sys.argv[1]
    swift_files = find_external_library(project_dir)
    collect_declarations(swift_files)


if __name__ == "__main__":
    main()