import os
import sys
import re

SWIFT_FILES = []

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
    for dir_path in dir_paths:
        for path, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".swift"):
                    file_path = os.path.join(path, file)
                    SWIFT_FILES.append(file_path)

# 프레임워크 탐색
def find_external_framework(project_root):
    dir_paths = set()
    for dirpath, dirnames, _ in os.walk(project_root):
        for dirname in dirnames:
            if dirname.lower() == "frameworks":
                path = os.path.join(dirpath, dirname)
                dir_paths.add(path)
    
    for dir_path in dir_paths:
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename.endswith(".swiftinterface") or filename.endswith(".swift"):
                    path = os.path.join(dirpath, filename)
                    SWIFT_FILES.append(path)

def find_external_files(project_dir):
    
    find_external_library(project_dir)
    find_external_framework(project_dir)
    
    output_dir = "./output/external_file_list.txt"
    with open(output_dir, "w", encoding="utf-8") as f:
        for swift_file in SWIFT_FILES:
            f.write(f"{swift_file}\n")