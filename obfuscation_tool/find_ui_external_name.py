import os
import json

M_SAME_NAME = []
P_SAME_NAME = []

# function, variable 정보 수집
def get_members(node):
    if node.get("B_kind") in ["struct", "class", "protocol", "enum"]:
        P_SAME_NAME.append(node.get("A_name"))

    members = node.get("G_members", [])
    for member in members:
        if member.get("B_kind") in ["function", "variable", "case"]:
            M_SAME_NAME.append(member.get("A_name"))
        
        if member.get("G_members"):
            get_members(member)
        
# 자식 노드가 자식 노드를 가지는 경우
def repeat_match_node(item):
    node = item.get("node")
    if not node:
        node = item
    extensions = item.get("extension", [])
    children = item.get("children", [])
    get_members(node)
    for extension in extensions:
        repeat_match_node(extension)
    for child in children:
        repeat_match_node(child)

def find_ui_external_name():
    file_paths = ["./output/ui_source_json", "./output/external_to_ast"]
    for file_path in file_paths:
        for filename in os.listdir(file_path):
            path = os.path.join(file_path, filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
                if isinstance(data, list):
                    for item in data:
                        repeat_match_node(item)
    
    return M_SAME_NAME, P_SAME_NAME
