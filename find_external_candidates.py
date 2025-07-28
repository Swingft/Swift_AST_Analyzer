import os
import json
import copy

FIND_CANDIDATE = []

def find_external_element(data):
    if isinstance(data, dict):
        # protocol 채택
        if data.get("E_adoptedClassProtocols"):
            FIND_CANDIDATE.append(data)
        
        # class, protocol, struct, enum 확장
        # protocol인 경우, 요구사항 구현 선택 가능
        if data.get("B_kind") == "extension":
            if data not in FIND_CANDIDATE:
                FIND_CANDIDATE.append(data)

        # class override
        if "override" in data.get("D_attributes", []):
            data_copy = copy.deepcopy(data)
            if "G_members" in data_copy:
                del data_copy["G_members"]
            if data_copy not in FIND_CANDIDATE:
                FIND_CANDIDATE.append(data_copy)
        
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

    with open(output_path, "a", encoding="utf-8") as f:
        json.dump(FIND_CANDIDATE, f, indent=2, ensure_ascii=False)


def main():
    json_dir_path = "./output/source_json"
    output_path = "./output/external_candidates.json"
    find_and_save_function(json_dir_path, output_path)
    

if __name__ == "__main__":
    main()