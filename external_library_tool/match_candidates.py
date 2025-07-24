import json
import copy

MATCHED_LIST = []
NOT_MATCHED_LIST = []
EXTERNAL_KEYWORDS = []
    
# extension -> protocol, class, struct, enum
# extension x: y {} -> y == protocol -> 요구사항 메서드/변수 확인
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
                elif not is_true and item not in NOT_MATCHED_LIST:
                    NOT_MATCHED_LIST.append(item)

    elif isinstance(candidates, dict):
        name = candidates.get("A_name")
        for keyword in EXTERNAL_KEYWORDS:
            for kind in ["protocol", "class", "struct", "enum"]:
                signature = f"{kind}: {name}"
                if signature == keyword:
                    if kind == "protocol":
                        match_protocol_requirements(candidates)
                    return True
        adopted = candidates.get("E_adoptedClassProtocols", [])
        for name in adopted:
            signature = f"protocol: {name}"
            for keyword in EXTERNAL_KEYWORDS:
                if signature == keyword:
                    match_protocol_requirements(candidates)
                    break
        return False
    
def match_protocol_requirements(candidate):
    members = candidate.get("G_members", [])
    for member in members:
        name = member.get("A_name")
        kind = member.get("B_kind")
        signature = f"{kind}: {name}"
        for keyword in EXTERNAL_KEYWORDS:
            if signature in keyword:
                if member not in MATCHED_LIST:
                    MATCHED_LIST.append(member)

# protocol 채택 -> 요구사항 메서드/변수 확인
def match_candidates_protocol(candidates):
    if isinstance(candidates, list):
        for item in candidates:
            if item.get("E_adoptedClassProtocols", []):
                is_true = match_candidates_protocol(item)
                if is_true and item not in MATCHED_LIST:
                    item_copy = copy.deepcopy(item)
                    if "G_members" in item_copy:
                        del item_copy["G_members"]
                    MATCHED_LIST.append(item_copy)
                elif not is_true and item not in NOT_MATCHED_LIST:
                    NOT_MATCHED_LIST.append(item)
    
    elif isinstance(candidates, dict):
        adopted = candidates.get("E_adoptedClassProtocols", [])
        for name in adopted:
            signature = f"protocol: {name}"
            for keyword in EXTERNAL_KEYWORDS:
                if signature == keyword:
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
                elif not is_true and item not in NOT_MATCHED_LIST:
                    NOT_MATCHED_LIST.append(item)
    
    elif isinstance(candidates, dict):
        name = candidates.get("A_name")
        kind = candidates.get("B_kind")
        parameters = candidates.get("I_parameters")
        signature = f"{kind}: {name}("

        for keyword in EXTERNAL_KEYWORDS:
            if signature in keyword:
                is_matched = True
                for param in parameters:
                    if param not in keyword:
                        is_matched = False
                        break
                if is_matched:
                    return True
    return False
        

def match_and_save(candidate_path, external_list_path):
    global EXTERNAL_KEYWORDS

    matched_output_path = "../output/external_list.json"
    unmatched_output_path = "../output/not_external_list.json"
    with open(candidate_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    with open(external_list_path, "r", encoding="utf-8") as f:
        external_keywords = [line.strip() for line in f if line.strip() ]
    EXTERNAL_KEYWORDS = copy.deepcopy(external_keywords)

    match_candidates_override(candidates)
    match_candidates_protocol(candidates)
    match_candidates_extension(candidates)
    with open(matched_output_path, "a", encoding="utf-8") as f:
        json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)
    with open(unmatched_output_path, "a", encoding="utf-8") as f:
        json.dump(NOT_MATCHED_LIST, f, indent=2, ensure_ascii=False)


def main():
    candidate_path = "../output/external_candidates.json"
    external_list_path = "../output/external_dependencies.txt"

    match_and_save(candidate_path, external_list_path)


if __name__ == "__main__":
    main()