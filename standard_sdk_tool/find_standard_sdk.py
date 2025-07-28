import subprocess
import os
import json

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# import_list.txt 읽고 중복 제거
def read_import_list():
    import_list = set()
    path = "../output/import_list.txt"
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                import_list.add(line.strip())
    with open(path, "w", encoding="utf-8") as f:
        for i in import_list:
            f.write(f"{i}\n")
    
    return import_list

# api 경로 확인
def find_path():
    digester_cmd = ["xcrun", "--find", "swift-api-digester"]
    digester_path = run_command(digester_cmd)
    sdk_cmd = ["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]
    sdk_path = run_command(sdk_cmd)
    return digester_path, sdk_path

# sdk api - json 추출
def dump_to_json(digester_path, sdk_path, import_list):
    output_dir = "../output/sdk-json/"

    for name in import_list:
        output_path = os.path.join(output_dir, f"{name}-sdk.json")
        cmd = [
            digester_path, 
            "-dump-sdk", 
            "-sdk", sdk_path, 
            "-target", "arm64-apple-ios16.0", 
            "-module", name,
            "-o", output_path
        ]
        result = run_command(cmd)

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        root = data.get("ABIRoot", {})
        name = root.get("name", "")
        if name == "NO_MODULE":
            os.remove(output_path)

# 핵심 필드 추출 -> json 저장
def signature_to_json():
    file_dir = "../output/sdk-json/"
    output_path = "../output/sdk-signature.json"
    signature_list = []

    def collect_signature(item):
        if isinstance(item, list):
            for member in item:
                collect_signature(member)
        elif isinstance(item, dict):    
            signature_list.append(extract_signature(item))
            for value in item.values():
                if isinstance(value, list):
                    collect_signature(value)

    for file in os.listdir(file_dir):
        input_file = os.path.join(file_dir, file)
        with open(input_file, "r", encoding="utf-8") as f:
            sdk_data = json.load(f)
        root = sdk_data.get("ABIRoot", {})
        items = root.get("children", [])
        for item in items:
            collect_signature(item)
                
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(signature_list, f, indent=2, ensure_ascii=False)

def extract_signature(item):
    name = item.get("name")
    kind = item.get("kind")
    usr = item.get("usr")
    param = []

    children = item.get("children", [])
    for child in children:
        param.append(child.get("name"))

    return {
        "name": name,
        "kind": kind,
        "usr": usr,
        "param": param
    }

def main():
    digester_path, sdk_path = find_path()
    import_list = read_import_list()

    output_dir = "../output/sdk-json/"
    os.makedirs(output_dir, exist_ok=True)
    dump_to_json(digester_path, sdk_path, import_list)
    signature_to_json()

if __name__ == "__main__":
    main()