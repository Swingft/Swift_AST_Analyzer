import subprocess
import os
import sys

from internal_tool.find_internal_files import find_internal_files
from internal_tool.integration_ast import integration_ast
from internal_tool.find_exception_target import find_exception_target
from external_library_tool.find_external_files import find_external_files
from external_library_tool.find_external_candidates import find_external_candidates
from external_library_tool.match_candidates import match_candidates_external
from standard_sdk_tool.find_standard_sdk import find_standard_sdk
from standard_sdk_tool.match_candidates import match_candidates_sdk
from obfuscation_tool.find_ui_external_name import find_ui_external_name
from obfuscation_tool.merge_exception_list import merge_exception_list
from obfuscation_tool.exception_tagging import exception_tagging

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)

def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    original_dir = os.getcwd()   
    code_project_dir = sys.argv[1]

    # 필요한 디렉토리 생성
    os.makedirs("./output/source_json/", exist_ok=True) 
    os.makedirs("./output/ui_source_json/", exist_ok=True)
    os.makedirs("./output/typealias_json/", exist_ok=True)
    os.makedirs("./output/external_to_ast/", exist_ok=True)
    os.makedirs("./output/sdk-json/", exist_ok=True)

    # 소스코드 & 외부 라이브러리 파일 위치 수집 
    find_internal_files(code_project_dir)
    find_external_files(code_project_dir)

    # 소스코드, 외부 라이브러리 AST 파싱 & 소스코드 AST 선언부 통합
    os.chdir(original_dir)
    cmd = ["python3", "run_swift_syntax.py"]
    run_command(cmd)
    integration_ast()

    # 외부 라이브러리 / 표준 SDK 후보 추출 & 외부 라이브러리 요소 식별
    find_external_candidates()
    match_candidates_external()

    m_same_name = []
    p_same_name = []
    # 표준 SDK 정보 추출 & 표준 SDK 요소 식별
    path = os.path.join(original_dir, "output/import_list.txt")
    if os.path.exists(path):
        m_same_name, p_same_name = find_standard_sdk()
        match_candidates_sdk()
    
    # 내부 제외 대상 식별
    s_n, p_n = find_ui_external_name()
    m_same_name.extend(s_n)
    p_same_name.extend(p_n)
    find_exception_target(m_same_name, p_same_name)

    # 제외 대상 리스트 병합
    merge_exception_list()
    exception_tagging()

    # 사용 완료한 파일 삭제
    file_path = os.path.join(original_dir, "output/import_list.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/external_file_list.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/external_candidates.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/external_list.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/internal_exception_list.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/standard_list.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/inheritance_node.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/no_inheritance_node.json")
    if os.path.exists(file_path):
        os.remove(file_path)


if __name__ == "__main__":
    main()