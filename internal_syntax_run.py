import os
import subprocess
import sys

EXCLUDE_KEYWORDS = [".build", "Pods", "vendor", "thirdparty", "external"]

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


def find_swift_files(directory):
    swift_files = set()
    for root, _, files in os.walk(directory):
        lower_root = root.lower()
        if any(keyword in lower_root for keyword in EXCLUDE_KEYWORDS):
            continue

        for file in files:
            if file.endswith(".swift"):
                swift_files.add(os.path.join(root, file))

    output_path ="output/swift_file_list.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for swift_file in swift_files:
            f.write(f"{swift_file}\n")


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    target_project_dir = "SyntaxAST"
    target_name = "SyntaxAST"
    code_project_dir = sys.argv[1]
    # "/Users/seunghye/Desktop/SampleProject/Test"
    
    original_dir = os.getcwd() 
    swift_list_dir = "output/swift_file_list.txt"
    swift_list_dir = os.path.join(original_dir, swift_list_dir)


    find_swift_files(code_project_dir)

    external_list_dir = "output/external_file_list.txt"
    external_list_dir = os.path.join(original_dir, external_list_dir) 

    os.chdir(target_project_dir)
    run_command(["swift", "build"])
    run_command(["swift", "run", target_name, swift_list_dir, external_list_dir])


if __name__ == "__main__":
    main()