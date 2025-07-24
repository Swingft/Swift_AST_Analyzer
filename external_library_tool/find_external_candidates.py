import os
import json
import copy

FIND_OVERRIDE = []
FIND_ADOPTED = []

def find_external_element(data):
    if isinstance(data, dict):
        # protocol 채택
        if data.get("E_adoptedClassProtocols"):
            FIND_ADOPTED.append(data)
        
        # class, protocol, struct, enum 확장
        # protocol인 경우, 요구사항 구현 선택 가능
        if data.get("B_kind") == "extension":
            FIND_ADOPTED.append(data)

        # class override
        if "override" in data.get("D_attributes", []):
            data_copy = copy.deepcopy(data)
            if "G_members" in data_copy:
                del data_copy["G_members"]
            FIND_OVERRIDE.append(data_copy)
        
        for member in data.get("G_members", []):
            find_external_element(member)

    elif isinstance(data, list):
        for item in data:
            find_external_element(item)


def find_and_save_function(json_dir_path, output_path):
    for path, _, files in os.walk(json_dir_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    find_external_element(data)

    final_list = []
    final_list.extend(FIND_ADOPTED)
    final_list.extend(FIND_OVERRIDE)
    with open(output_path, "a", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)


def main():
    json_dir_path = "../output/source_json"
    output_path = "../output/external_candidates.json"
    find_and_save_function(json_dir_path, output_path)
    

if __name__ == "__main__":
    main()