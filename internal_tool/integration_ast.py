import json
import os

UI_AST_NODE = {}
AST_NODE = {}
INHERITANCE = {}
NO_INHERITANCE = {}
ALIAS_INFO = {}

# swift 파일 단위의 ast.json을 읽고, 노드 저장
def load_ast_files():
    dir_path = "../output/source_json/"
    ui_dir_path = "../output/ui_source_json/"
    alias_dir_path = "../output/typealias_json/typealias.json"

    nodes = []
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            nodes.extend(data)
    
    ui_nodes = []
    for file in os.listdir(ui_dir_path):
        path = os.path.join(ui_dir_path, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            ui_nodes.extend(data)
    
    if os.path.exists(alias_dir_path):
        with open(alias_dir_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            alias_name = item.get("aliasName")
            protocols = item.get("protocols", [])
            if alias_name and protocols:
                ALIAS_INFO[alias_name] = []
                for protocol in protocols:
                    protocol = protocol.rstrip(" &")
                    ALIAS_INFO[alias_name].append(protocol)

    return nodes, ui_nodes

# 상속/채택 관계 연결
def check_inheritance(nodes):
    extension_nodes = []

    for node in nodes:
        name = node.get("A_name")
        kind = node.get("B_kind")
        adopted = node.get("E_adoptedClassProtocols", [])

        # typealias인 경우
        alias_adopted = []
        for parent in adopted:
            if parent in ALIAS_INFO:
                alias_adopted.extend(ALIAS_INFO[parent])
            else:
                alias_adopted.append(parent)
        node["E_adoptedClassProtocols"] = alias_adopted
        
        if kind == "extension":
            extension_nodes.append(node)
            continue
            
        if alias_adopted:
            AST_NODE[name] = node
            for parent in alias_adopted:
                if parent not in INHERITANCE:
                    INHERITANCE[parent] = {
                        "parent_node": None,
                        "extension": [],
                        "children": []
                    }
                INHERITANCE[parent]["children"].append(node)
        else:   
            AST_NODE[name] = node
            NO_INHERITANCE[name] = node
    
    # extension 연결
    for node in extension_nodes:
        name = node.get("A_name")
        if name not in INHERITANCE:
            INHERITANCE[name] = {
                "parent_node": None,
                "extension": [],
                "children": []
            }
        INHERITANCE[name]["extension"].append(node)
    
    # 부모 노드 연결
    link_parent_node()
       
# 부모 노드 연결
def link_parent_node():
    for parent in list(INHERITANCE.keys()):
        node = AST_NODE.get(parent)        
        if node:
            INHERITANCE[parent]["parent_node"] = node
            if parent in NO_INHERITANCE:   
                 del NO_INHERITANCE[parent]
            link_adopted_info_from_extension(parent)

# 확장에서 추가한 프로토콜 연결  
def link_adopted_info_from_extension(parent_node):
    root_node = INHERITANCE[parent_node]
    node = root_node.get("parent_node")
    extensions = root_node.get("extension", [])
    for extension in extensions:
        adopted = extension.get("E_adoptedClassProtocols", [])
        for ad in adopted:
            if node is None:
                continue

            if ad not in node.get("E_adoptedClassProtocols", []):
                ex_adopted = node.get("E_adoptedClassProtocols", [])
                ex_adopted.append(ad)
                node["E_adoptedClassProtocols"] = ex_adopted
                if ad not in INHERITANCE:
                    INHERITANCE[ad] = {
                        "parent_node": None,
                        "extension": [],
                        "children": []
                    }
                INHERITANCE[ad]["children"].append(node)
                link_parent_node()

# ui <-> not ui
def check_inheritance_ui(ui_nodes):
    for node in ui_nodes:
        name = node.get("A_name")
        kind = node.get("B_kind")
        adopted = node.get("E_adoptedClassProtocols", [])

        # typealias인 경우
        alias_adopted = []
        for parent in adopted:
            if parent in ALIAS_INFO:
                alias_adopted.extend(ALIAS_INFO[parent])
            else:
                alias_adopted.append(parent)
        node["E_adoptedClassProtocols"] = alias_adopted

        UI_AST_NODE[name] = node
        for parent in alias_adopted:
            if parent in INHERITANCE and INHERITANCE[parent]["parent_node"]:
                INHERITANCE[parent]["children"].append(node)
        
        if kind == "extension":
            if name in INHERITANCE:
                INHERITANCE[name]["extension"].append(node)
    
    for parent in INHERITANCE.keys():
        node = UI_AST_NODE.get(parent)
        if node:
            INHERITANCE[parent]["parent_node"] = node

# ast 트리 구조 생성
def make_inheritance_tree():
    def make_root_tree(root, visited = None):
        if visited is None:
            visited = set()
        if root in visited:
            return None
        visited.add(root) 

        root_node = INHERITANCE[root]
        node = root_node.get("parent_node")
        extension = root_node.get("extension", [])
        children = root_node.get("children", [])

        extension_node  = []
        for child in extension:
            if child.get("A_name") in INHERITANCE:
                child_tree = make_root_tree(child.get("A_name"), visited)
                extension_node.append(child_tree)
            else:
                extension_node.append(child)

        children_node = []
        for child in children:
            if child.get("A_name") in INHERITANCE:
                child_tree = make_root_tree(child.get("A_name"), visited)
                children_node.append(child_tree)
            else:
                children_node.append(child)

        return {
            "node": node if node else {"A_name": root},
            "extension": extension,
            "children": children_node
        }

    root = []
    for parent in INHERITANCE:
        is_not_root = any(
            any(child.get("A_name") == parent for child in node["children"]) for node in INHERITANCE.values()
        )
        if not is_not_root:
            root_tree = make_root_tree(parent)
            root.append(root_tree)
    return root

def main():
    output_path = "../output/inheritance_node.json"
    no_output_path = "../output/no_inheritance_node.json"

    nodes, ui_nodes = load_ast_files()
    check_inheritance(nodes)
    check_inheritance_ui(ui_nodes)
    root = make_inheritance_tree()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(root, f, indent=2, ensure_ascii=False)
    with open(no_output_path, "w", encoding="utf-8") as f:
        json.dump(NO_INHERITANCE, f, indent=2, ensure_ascii=False)
    
if __name__ == "__main__":
    main()