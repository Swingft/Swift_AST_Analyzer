import json
from collections import defaultdict

MATCHED_LIST = []
SDK_SIGNATURE = defaultdict(list)

def match_protocol_requirements(candidate, modules):
    members = candidate.get("G_members", [])
    for member in members:
        key = (
            member["A_name"],
            "var" if member["B_kind"] == "variable" else member["B_kind"]
        )
        if key not in SDK_SIGNATURE:
            continue

        for item in SDK_SIGNATURE[key]:
            if item["module"] not in modules:
                continue
            
            is_matched = True
            if member.get("B_kind") == "function":
                parameters = member.get("I_parameters")
                params = item.get("param", [])
                for p in parameters:
                    if p not in params:
                        is_matched = False
                        break
            
            if is_matched and member not in MATCHED_LIST:
                MATCHED_LIST.append(member)

# override 확인
def check_override(item, modules):
    members = item.get("G_members", [])
    for member in members:
        if "override" in member.get("D_attributes", []):
            key = (member.get("A_name"), "function")
            if key not in SDK_SIGNATURE:
                continue
            
            for sdk in SDK_SIGNATURE[key]:
                if sdk["module"] not in modules:
                    continue
                is_matched = True
                parameters = member.get("I_parameters")
                params = sdk.get("param", [])
                for p in parameters:
                    if p not in params:
                        is_matched = False
                        break
                
                if is_matched and member not in MATCHED_LIST:
                    MATCHED_LIST.append(member)

def codable_variable(item):
    members = item.get("G_members", [])
    for member in members:
        if member.get("B_kind") == "variable" and member not in MATCHED_LIST:
            MATCHED_LIST.append(member) 

def enum_raw_value(item):
    members = item.get("G_members", [])
    for member in members:
        if member.get("B_kind") == "case" and member not in MATCHED_LIST:
            MATCHED_LIST.append(member)
        elif member.get("B_kind") == "enum":
            enum_raw_value(member)

def match_candidates(data):
    if isinstance(data, list):
        for item in data:
            match_candidates(item)
        return

    node = data.get("node")
    if node:
        extensions = data.get("extension", [])
        children = data.get("children", [])
    else:
        node = data
        extensions = []
        children = []
    adopted = node.get("E_adoptedClassProtocols", [])

    for name in adopted:
        # rawValue enum
        if name in ["String", "Int", "UInt", "Double", "Float", "Character"]:
            enum_raw_value(node)

        # 프로토콜 채택
        for kind in ["conformance", "typeNominal"]:
            key = (name, kind)
            if key in SDK_SIGNATURE or name in ["Codable"]:
                # Codable : 직접 채택, 채택한 프로토콜을 채택
                if name in ["Codable", "Decodable", "Encodable"]:
                    codable_variable(node)
                    if node.get("B_kind") == "protocol":
                        for child in children:
                            codable_variable(child)
                else:
                    modules = {item["module"] for item in SDK_SIGNATURE[key]}
                    match_protocol_requirements(node, modules)
                    for extension in extensions:
                        match_protocol_requirements(extension, modules)
                    for child in children:
                        match_protocol_requirements(child, modules)
            
        # 클래스 상속 - override
        key = (node.get("A_name"), "class")
        if key in SDK_SIGNATURE:
            modules = {item["module"] for item in SDK_SIGNATURE[key]}
            check_override(node, modules)
            for extension in extensions:
                check_override(extension, modules)
            for child in children:
                check_override(child, modules)
        
    # extension
    if node.get("B_kind") == "extension":
        name = node.get("A_name")
        for kind in ["protocol", "class", "struct", "enum", "extension", "conformance"]:
            key = (name, kind)
            if key in SDK_SIGNATURE:
                if node not in MATCHED_LIST:
                    MATCHED_LIST.append(node)
                if kind == "protocol" or kind == "conformance":
                    modules = {item["module"] for item in SDK_SIGNATURE[key]}
                    match_protocol_requirements(node, modules)
                    for extension in extensions:
                        match_protocol_requirements(extension, modules)
                    for child in children:
                        match_protocol_requirements(child, modules)
                else:
                    if extensions:
                        for extension in extensions:
                            if extension not in MATCHED_LIST:
                                MATCHED_LIST.append(extension)

def match_and_save(candidate_path, sdk_file_path):
    matched_output_path = "../output/standard_list.json"
    with open(candidate_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    with open(sdk_file_path, "r", encoding="utf-8") as f:
        sdk = json.load(f)
    
    for module, items in sdk.items():
        for item in items:
            key = (item["name"], item["kind"].lower())
            item["module"] = module
            SDK_SIGNATURE[key].append(item)
    
    match_candidates(candidates)
    with open(matched_output_path, "w", encoding="utf-8") as f:
        json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)
    

def main():
    candidate_path = "../output/external_candidates.json"
    sdk_file_path = "../output/sdk-signature.json"
    match_and_save(candidate_path, sdk_file_path)

if __name__ == "__main__":
    main()