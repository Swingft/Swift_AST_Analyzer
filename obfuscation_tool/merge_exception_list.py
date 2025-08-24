import json
import copy
import os

MERGED_NODE = []
LOCATIONS = set()

def merged_file_node():
    paths = ["./output/external_list.json", "./output/internal_exception_list.json", "./output/standard_list.json"]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for node in data:
                    location = node.get("F_location")
                    if location not in LOCATIONS:
                        node_copy = copy.deepcopy(node)
                        if "G_members" in node_copy:
                            del node_copy["G_members"]
                        MERGED_NODE.append(node_copy)
                        LOCATIONS.add(location)

def merge_exception_list():
    merged_file_node()

    output_path = "./output/exception_list.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(MERGED_NODE, f, indent=2, ensure_ascii=False)
