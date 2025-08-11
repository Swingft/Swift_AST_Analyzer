import json
import re
import os
from collections import defaultdict

MATCHED_LIST = []
EXTERNAL_NAME = defaultdict(list)
EXTERNAL_NAME_TO_FILE = defaultdict(list)

# 외부 요소 MATCHED_LIST에 추가
def in_matched_list(node):
    if node not in MATCHED_LIST:
        MATCHED_LIST.append(node)

def match_member(node, ex_node):
    members = node.get("G_members", [])
    ex_members = ex_node.get("G_members", [])
    for member in members:
        member_name = member.get("A_name")
        member_kind = member.get("B_kind")
        for ex in ex_members:
            ex_name = ex.get("A_name")
            ex_kind = ex.get("B_kind")
            if member_name == ex_name and member_kind == ex_kind:
                if ex_node.get("B_kind") == "protocol":
                    in_matched_list(member)
                elif ex_node.get("B_kind") == "class":
                    attributes = member.get("D_attributes", [])
                    if "override" in attributes:
                        in_matched_list(member)

# 자식 노드가 자식 노드를 가지는 경우
def repeat_match_member(in_node, ex_node):
    node = in_node.get("node")
    if node:
        extensions = in_node.get("extension", [])
        children = in_node.get("children", [])
    else:
        node = in_node
        extensions = []
        children = []
    
    match_member(node, ex_node)

    for extension in extensions:
        repeat_match_member(extension, ex_node)
    for child in children:
        repeat_match_member(child, ex_node)

# extension 이름 확인
def repeat_extension(in_node, name):
    node = in_node.get("node")
    if not node:
        node = in_node
    
    c_name = node.get("A_name")
    c_name = c_name.split(".")[-1]
    if c_name == name:
        in_matched_list(node)
        extensions = in_node.get("extension", [])
        for extension in extensions:
            repeat_extension(extension, name)

# 외부 요소와 노드 비교
def compare_node(in_node, ex_node):
    if isinstance(ex_node, list):
        for n in ex_node:
            compare_node(in_node, n)

    elif isinstance(ex_node, dict):
        node = in_node.get("node")
        if not node:
            node = in_node
        
        name = node.get("A_name")
        name = name.split(".")[-1]
        # extension x {}
        if (name == ex_node.get("A_name")) and (node.get("B_kind") == "extension"):
            repeat_extension(in_node, node.get("A_name"))
            repeat_match_member(in_node, ex_node)

        # 클래스 상속, 프로토콜 채택, extension x: y {}
        adopted = node.get("E_adoptedClassProtocols", [])
        for ad in adopted:
            if ex_node.get("A_name") == ad:
                repeat_match_member(in_node, ex_node)

# 외부 요소와 이름이 같은지 확인
def match_ast_name(data, external_ast_dir):
    if isinstance(data, list):
        for item in data:
            match_ast_name(item, external_ast_dir)
    elif isinstance(data, dict):
        node = data.get("node")
        if not node:
            node = data
        
        candidate_files = []
        # extension -> 이름이 같은지
        name = node.get("A_name")
        name = name.split(".")[-1]
        if name in EXTERNAL_NAME_TO_FILE.keys() and node.get("B_kind") == "extension":
            candidate_files.extend(EXTERNAL_NAME_TO_FILE[name])
         
        # 나머지 -> 상속 정보
        adopted = node.get("E_adoptedClassProtocols", [])
        for ad in adopted:
            if ad in EXTERNAL_NAME_TO_FILE.keys():
                candidate_files.extend(EXTERNAL_NAME_TO_FILE[ad])

        for file in candidate_files:
            file_path = os.path.join(external_ast_dir, file)
            with open(file_path, "r", encoding="utf-8") as f:
                ex_data = json.load(f)
                compare_node(data, ex_data)

# 외부라이브러리 AST에서 노드 이름 추출
def extract_ast_name(ast, file):
    def ast_name(node):
        if isinstance(node, list):
            for item in node:
                ast_name(item)
        elif isinstance(node, dict):
            EXTERNAL_NAME[file].append(node.get("A_name"))   
    ast_name(ast)

def match_and_save(candidate_path, external_ast_path):
    if os.path.exists(candidate_path):
        with open(candidate_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        
        for file in os.listdir(external_ast_path):
            file_path = os.path.join(external_ast_path, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    extract_ast_name(data, file)
            except Exception as e:
                print(e)
        for file_name, names in EXTERNAL_NAME.items():
            for name in names:
                if file_name not in EXTERNAL_NAME_TO_FILE[name]:
                    EXTERNAL_NAME_TO_FILE[name].append(file_name)

        match_ast_name(candidates, external_ast_path)

        matched_output_path = "../output/external_list.json"
        with open(matched_output_path, "w", encoding="utf-8") as f:
            json.dump(MATCHED_LIST, f, indent=2, ensure_ascii=False)
    

def main():
    candidate_path = "../output/external_candidates.json"
    external_ast_path = "../output/external_to_ast/"

    match_and_save(candidate_path, external_ast_path)


if __name__ == "__main__":
    main()