import os

EXCLUDE_KEYWORDS = [".build", "Pods", "vendor", "thirdparty", "external", "frameworks"]

def find_swift_files(directory):
    swift_files = set()
    for root, _, files in os.walk(directory):
        lower_root = root.lower()
        if any(keyword in lower_root for keyword in EXCLUDE_KEYWORDS):
            continue

        for file in files:
            if file.endswith(".swift"):
                swift_files.add(os.path.join(root, file))

    output_path ="./output/swift_file_list.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for swift_file in swift_files:
            f.write(f"{swift_file}\n")


def find_internal_files(code_project_dir):
    find_swift_files(code_project_dir)
