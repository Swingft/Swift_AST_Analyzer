import json
import re
import os

MATCHED_LIST = []
KEYPASS_LIST = []

# KeyPath로 사용되는 타입 탐색
def find_keypath_type():
    paths = []
    file_path = "../output/swift_file_list.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            paths.append(line.strip())
    
    # Swift 파일 읽어서 KeyPath 탐색
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for _, line in enumerate(lines, 1):
                    if "\"" not in line and "\'" not in line:
                        match = re.search(r"\\\(*\s*(\w+)\)*\.(\w+)", line)
                        if match:
                            KEYPASS_LIST.append((match.group(1), match.group(2)))
                        
        except FileNotFoundError:
            print(f"File not found: {path}")

# 제외 대상 MATCHED_LIST에 추가
def in_matched_list(node):
    if node not in MATCHED_LIST:
        MATCHED_LIST.append(node)

# KeyPath 제외
def check_is_keypath(node, extensions, children):    
    name = node.get("A_name")
    kind = node.get("B_kind")
    members = node.get("G_members", [])
    find_member_name = []
    if kind in ["protocol", "class", "struct"]:
        is_keypath = False
        for member in members:
            member_name = member.get("A_name")
            member_kind = member.get("B_kind")
            if member_kind == "variable" and (name, member_name) in KEYPASS_LIST:
                find_member_name.append(member_name)
                is_keypath = True
                in_matched_list(node)
                in_matched_list(member)
        
        if is_keypath:
            for extension in extensions:
                if extension.get("A_name") == name:
                    in_matched_list(extension)
                ex_members = extension.get("G_members", [])
                for member in ex_members:
                    if member.get("B_kind") == "variable" and member.get("A_name") in find_member_name:
                        if (kind == "class" and "override" in member.get("D_attributes", [])) or kind == "protocol":
                            in_matched_list(member)
            for child in children:
                ch_members = child.get("G_members", [])
                for member in ch_members:
                    if member.get("B_kind") == "variable" and member.get("A_name") in find_member_name:
                        if (kind == "class" and "override" in member.get("D_attributes", [])) or kind == "protocol":
                            in_matched_list(member)

# enum case 제외
def check_is_enum(node):
    if node.get("B_kind") == "enum":
        members = node.get("G_members", [])
        for member in members:
            if member.get("B_kind") == "case":
                in_matched_list(member)

# @objc dynamic, @objcMembers, @Model, @NSManaged, @_silgen_name, @_cdecl 속성을 가질 경우, 제외
def check_attribute(node):
    def check_member():
        members = node.get("G_members", [])
        for member in members:
            check_attribute(member)

    attributes = node.get("D_attributes", [])
    members = node.get("G_members", [])

    if "objc" in attributes or "dynamic" in attributes or "NSManaged" in attributes or "_silgen_name" in attributes or "_cdecl" in attributes:
        in_matched_list(node)

    if "objcMembers" in attributes:
        in_matched_list(node)
        for member in members:
            in_matched_list(member)
    
    if "Model" in attributes:
        in_matched_list(node)
        for member in members:
            if member.get("B_kind") == "variable":
                in_matched_list(member)

    check_member()

def find_exception_target(node):
    check_attribute(node)
    check_is_enum(node)

# 자식 노드가 자식 노드를 가지는 경우
def repeat_match_member(data):
    node = data.get("node")
    if node:
        extensions = data.get("extension", [])
        children = data.get("children", [])
    else:
        node = data
        extensions = []
        children = []

    find_exception_target(node)
    for extension in extensions:
        repeat_match_member(extension)
    for child in children:
        repeat_match_member(child)
    check_is_keypath(node, extensions, children)

# node 처리
def find_node(data):
    if isinstance(data, list):
        for item in data:
            repeat_match_member(item)

    elif isinstance(data, dict):
        for _, node in data.items():
            find_exception_target(node)
            check_is_keypath(node, [], [])

def main():
    input_file_1 = "../output/inheritance_node.json"
    input_file_2 = "../output/no_inheritance_node.json"
    output_file = "../output/internal_exception_list.json"

    find_keypath_type()
    if os.path.exists(input_file_1):
        with open(input_file_1, "r", encoding="utf-8") as f:
            nodes = json.load(f)
        find_node(nodes)
    if os.path.exists(input_file_2):
        with open(input_file_2, "r", encoding="utf-8") as f:
            nodes = json.load(f)
        find_node(nodes)
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)

    

if __name__ == "__main__":
    main()