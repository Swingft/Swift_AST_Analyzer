import os
import subprocess
import sys

EXCLUDE_KEYWORDS = [".build", "Pods", "vendor", "thirdparty", "external"]

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


def find_swift_files(directory):
    swift_files = []
    for root, _, files in os.walk(directory):
        lower_root = root.lower()
        if any(keyword in lower_root for keyword in EXCLUDE_KEYWORDS):
            continue

        for file in files:
            if file.endswith(".swift"):
                swift_files.append(os.path.join(root, file))
    return swift_files


def run_swift_code(directory, target_name):
    swift_files = find_swift_files(directory)

    for swift_file in swift_files:
        cmd = ["swift", "run", target_name, swift_file]
        run_command(cmd)


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    target_project_dir = "SyntaxAST"
    target_name = "SyntaxAST"
    code_project_dir = sys.argv[1]
    # "/Users/seunghye/Desktop/SampleProject/Test"

    os.chdir(target_project_dir)
    run_command(["swift", "build"])
    run_swift_code(code_project_dir, target_name)


if __name__ == "__main__":
    main()