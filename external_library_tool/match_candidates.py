import json

MATCHED_LIST = []
EXTERNAL_KEYWORDS = {}
    
# 프로토콜 요구사항 확인
def match_protocol_requirements(candidate, keywords):
    members = candidate.get("G_members", [])
    for member in members:
        name = member.get("A_name")
        kind = member.get("B_kind")
        signature = f"{kind}: {name}"
        for keyword in keywords:
            if signature in keyword:
                is_matched = True
                if kind == "function":
                    parameters = member.get("I_parameters", [])
                    for param in parameters:
                        if param not in keyword:
                            is_matched = False
                            break
                if is_matched and member not in MATCHED_LIST:
                    MATCHED_LIST.append(member)     

# override 확인
def check_override(node, keywords):
    node_member = node.get("G_members", [])
    for member in node_member:
        if "override" in member.get("D_attributes", []):
            name = member.get("A_name")
            kind = member.get("B_kind")
            parameters = member.get("I_parameters")
            signature = f"{kind}: {name}("
            
            for keyword in keywords:
                if signature in keyword:
                    is_matched = True
                    for param in parameters:
                        if param not in keyword:
                            is_matched = False
                            break
                    if is_matched and member not in MATCHED_LIST:
                        MATCHED_LIST.append(member)

def match_candidates(data):
    if isinstance(data, list):
        for item in data:
            match_candidates(item)
        return
    
    node = data.get("node")
    if node:
        extensions = data.get("extension", [])
        children = data.get("children", [])
        adopted = node.get("E_adoptedClassProtocols", [])
    else:
        node = data
        extensions = []
        children = []
        adopted = node.get("E_adoptedClassProtocols", [])

    for name in adopted:
        # 프로토콜 채택
        signature = f"protocol: {name}"
        for _, keywords in EXTERNAL_KEYWORDS.items():
            for keyword in keywords:
                if signature in keyword:
                    match_protocol_requirements(node, keywords)
                    for extension in extensions:
                        match_protocol_requirements(extension, keywords)
                    for child in children:
                        match_protocol_requirements(child, keywords)
        
        # 클래스 상속 - override
        signature = f"class: {name}"
        for _, keywords in EXTERNAL_KEYWORDS.items():
            for keyword in keywords:
                if signature in keyword:
                    check_override(node, keywords)
                    for extension in extensions:
                        check_override(extension, keywords)
                    for child in children:
                        check_override(child, keywords)
                    
    # extension
    if node.get("B_kind") == "extension":
        name = node.get("A_name")
        for kind in ["protocol", "class", "struct", "enum", "extension"]:
            signature = f"{kind}: {name}"
            for _, keywords in EXTERNAL_KEYWORDS.items():
                for keyword in keywords:
                    if signature in keyword:
                        if node not in MATCHED_LIST:
                            MATCHED_LIST.append(node)
                        if kind == "protocol":
                            match_protocol_requirements(node, keywords)
                            for extension in extensions:
                                match_protocol_requirements(extension, keywords)
                            for child in children:
                                match_protocol_requirements(child, keywords)
                        else:
                            if extensions:
                                for extension in extensions:
                                    if extension not in MATCHED_LIST:
                                        MATCHED_LIST.append(extension)
                    

def match_and_save(candidate_path, external_list_path):
    matched_output_path = "../output/external_list.json"
    with open(candidate_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    current_file = None
    with open(external_list_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("--/"):
                current_file = line[2:]
                EXTERNAL_KEYWORDS[current_file] = []
            else:
                if current_file is not None:
                    EXTERNAL_KEYWORDS[current_file].append(line)
       
    match_candidates(candidates)
    with open(matched_output_path, "w", encoding="utf-8") as f:
        json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)


def main():
    candidate_path = "../output/external_candidates.json"
    external_list_path = "../output/external_dependencies.txt"

    match_and_save(candidate_path, external_list_path)


if __name__ == "__main__":
    main()