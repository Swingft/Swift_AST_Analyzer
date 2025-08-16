import json
import re
import os

MATCHED_LIST = []

# 제외 대상 MATCHED_LIST에 추가
def in_matched_list(node):
    if node not in MATCHED_LIST:
        MATCHED_LIST.append(node)

# @objc dynamic, @objcMembers, @Model, @NSManaged 속성을 가질 경우, 제외
def check_attribute(node):
    def check_member():
        members = node.get("G_members", [])
        for member in members:
            check_attribute(member)

    attributes = node.get("D_attributes", [])
    members = node.get("G_members", [])

    if "objc" in attributes or "dynamic" in attributes or "NSManaged" in attributes:
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

    if "globalActor" in attributes:
        in_matched_list(node)
        for member in members:
            if member.get("A_name") == "shared" and member.get("B_kind") == "variable":
                in_matched_list(member)
    
    if node.get("A_name") in ["get", "set", "willSet", "didSet"]:
        in_matched_list(node)

    check_member()

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

    check_attribute(node)
    for extension in extensions:
        repeat_match_member(extension)
    for child in children:
        repeat_match_member(child)

# node 처리
def find_node(data):
    if isinstance(data, list):
        for item in data:
            repeat_match_member(item)

    elif isinstance(data, dict):
        for _, node in data.items():
            check_attribute(node)
def main():
    input_file_1 = "../output/inheritance_node.json"
    input_file_2 = "../output/no_inheritance_node.json"
    output_file = "../output/internal_exception_list.json"

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