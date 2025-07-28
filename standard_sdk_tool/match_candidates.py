import json
from collections import defaultdict
import copy

MATCHED_LIST = []

def match_candidates_extension(candidates):
    if isinstance(candidates, list):
        for item in candidates:
            if item.get("B_kind") == "extension":
                is_true = match_candidates_extension(item)
                if is_true and item not in MATCHED_LIST:
                    item_copy = copy.deepcopy(item)
                    if "G_members" in item_copy:
                        del item_copy["G_members"]
                    MATCHED_LIST.append(item_copy) 

    elif isinstance(candidates, dict):
        for kind in ["protocol", "class", "struct", "enum", "extension", "conformance"]:
            key = (
                candidates["A_name"],
                kind
            )
            if key in SDK_SIGNATURE:
                if kind == "protocol" or kind == "conformance":
                    match_protocol_requirements(candidates)
                return True
        adopted = candidates.get("E_adoptedClassProtocols", [])
        for name in adopted:
            key = (
                name, "protocol"
            )
            if key in SDK_SIGNATURE:
                match_protocol_requirements(candidates)
                break
        return False

def match_protocol_requirements(candidate):
    members = candidate.get("G_members", [])
    for member in members:
        key = (
            member["A_name"],
            "var" if member["B_kind"] == "variable" else member["B_kind"]
        )
        if key in SDK_SIGNATURE:
            is_matched = True
            if member.get("B_kind") == "function":
                parameters = member.get("I_parameters")
                for item in SDK_SIGNATURE[key]:
                    params = item.get("param", [])
                    for p in parameters:
                        if p not in params:
                            is_matched = False
                            break
            if is_matched and member not in MATCHED_LIST:
                MATCHED_LIST.append(member)

# protocol 채택 
# codable, decodable, encodable -> codingkeys가 없으면 내부 변수 난독화 X
def match_candidates_protocol(candidates):
    if isinstance(candidates, list):
        for item in candidates:
            if item.get("E_adoptedClassProtocols", []):
                match_candidates_protocol(item)
    
    elif isinstance(candidates, dict):
        adopted = candidates.get("E_adoptedClassProtocols", [])
        for name in adopted:
            key = (
                name, "conformance"
            )
            if key in SDK_SIGNATURE or name == "Codable":
                if name == "Codable" or name == "Decodable" or name == "Encodable":
                    members = candidates.get("G_members", [])
                    for member in members:
                        if member.get("B_kind") == "variable" and member not in MATCHED_LIST:
                            MATCHED_LIST.append(member)
                else:
                    match_protocol_requirements(candidates)
                return True
        return False

# class override
def match_candidates_override(candidates):
    if isinstance(candidates, list):
        for item in candidates:
            if "override" in item.get("D_attributes", []):
                is_true = match_candidates_override(item)
                if is_true and item not in MATCHED_LIST:
                    MATCHED_LIST.append(item)
    
    elif isinstance(candidates, dict):
        key = (
            candidates["A_name"],
            candidates["B_kind"]
        )
        if key in SDK_SIGNATURE:
            parameters = candidates.get("I_parameters")
            for item in SDK_SIGNATURE[key]:
                params = item.get("param", [])
                include_params = True
                for p in parameters:
                    if p not in params:
                        include_params = False
                        break
                if include_params:
                    return True
        return False


def match_and_save(candidate_path, sdk_file_path):
    global SDK_SIGNATURE 

    matched_output_path = "../output/standard_list.json"
    with open(candidate_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    with open(sdk_file_path, "r", encoding="utf-8") as f:
        sdk = json.load(f)
    
    SDK_SIGNATURE = defaultdict(list)
    for item in sdk:
        key = (item["name"], item["kind"].lower())
        SDK_SIGNATURE[key].append(item)
    
    match_candidates_override(candidates)
    match_candidates_protocol(candidates)
    match_candidates_extension(candidates)
    with open(matched_output_path, "w", encoding="utf-8") as f:
        json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)


def main():
    candidate_path = "../output/not_external_list.json"
    sdk_file_path = "../output/sdk-signature.json"
    match_and_save(candidate_path, sdk_file_path)

if __name__ == "__main__":
    main()