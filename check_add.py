import json

# JSON 파일 읽기
def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 서로에게 없는 노드 찾기
def find_missing_nodes(file1_path, file2_path):
    data1 = read_json(file1_path)
    data2 = read_json(file2_path)

    node1 = {node["F_location"] for node in data1}
    node2 = {node["F_location"] for node in data2}
    only_in_file2 = [node for node in data2 if node["F_location"] not in node1]
    print(only_in_file2)



# 사용 예시
find_missing_nodes("./output_1/exception_list.json", "./output/exception_list.json")
