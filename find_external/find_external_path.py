import os
import sys
import subprocess

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
            subprocess.run(["python3", "find_external_decl.py", p])
    else:
        print("외부 라이브러리 경로 없음")


if __name__ == "__main__":
    main()