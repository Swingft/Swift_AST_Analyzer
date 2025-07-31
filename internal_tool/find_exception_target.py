import json

def ff(nodes):
    if isinstance(nodes, list):
        for node in nodes:
            ff(node)
        return
    
    node = nodes.get("node")
    if node:
        extensions = nodes.get("extension", [])
        children = nodes.get("children", [])
    else:
        node = nodes
        extensions = []
        children = []
    
    adopted = node.get("E_adoptedClassProtocols", [])


def main():
    input_file_1 = "../output/external_candidates.json"
    input_file_2 = "../output/no_inheritance_node.json"
    with open(input_file_1, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    ff(nodes)
    

if __name__ == "__main__":
    main()

# def find_candidate_node():
#     input_path = "./output/inheritance_node.json"
#     with open(input_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     for item in data:
#         node = item.get("node")
#         if "B_kind" not in node:
#             extension = item.get("extension")
#             children = item.get("children")
#             for ext in extension:
#                 if ext not in CANDIDATE_NODE:
#                     CANDIDATE_NODE.append(ext)
#             for child in children:
#                 if child not in CANDIDATE_NODE:
#                     CANDIDATE_NODE.append(child)
    
#     input_path = "./output/no_inheritance_node.json"
#     with open(input_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     for item in data:
#         if "B_kind" == "extension":
#             if item not in CANDIDATE_NODE:
#                 CANDIDATE_NODE.append(item)