import subprocess
import os
import sys

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)

def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    original_dir = os.getcwd()   
    code_project_dir = sys.argv[1]
    project_name = os.path.basename(os.path.normpath(code_project_dir))

    # 필요한 디렉토리 생성
    output_dir = f"./output/source_json/"
    os.makedirs(output_dir, exist_ok=True) 
    output_dir = "./output/ui_source_json/"
    os.makedirs(output_dir, exist_ok=True)
    output_dir = "./output/typealias_json/"
    os.makedirs(output_dir, exist_ok=True)
    
    # 소스코드 -> ast 변환
    cmd = ["python3", "internal_syntax_run.py", code_project_dir]
    run_command(cmd)

    internal_dir = os.path.join(original_dir, "internal_tool/")
    os.chdir(internal_dir)
    cmd = ["python3", "integration_ast.py"]
    run_command(cmd)
    os.chdir(original_dir)

    # 외부라이브러리 / 표준 SDK 후보 추출
    cmd = ["python3", "find_external_candidates.py"]
    run_command(cmd)

    # 외부라이브러리 정보 추출
    external_dir = os.path.join(original_dir, "external_library_tool/")
    os.chdir(external_dir)
    cmd = ["python3", "find_external_package.py", code_project_dir]
    run_command(cmd)
    cmd = ["python3", "find_external_framework.py", code_project_dir]
    run_command(cmd)

    # 외부라이브러리 요소 식별
    path = os.path.join(original_dir, "output/external_dependencies.txt")
    if os.path.exists(path):
        cmd = ["python3", "match_candidates.py"]
        run_command(cmd)

    # 표준 SDK 정보 추출 & 표준 SDK 요소 식별
    path = os.path.join(original_dir, "output/import_list.txt")
    if os.path.exists(path):
        standard_dir = os.path.join(original_dir, "standard_sdk_tool/")
        os.chdir(standard_dir)
        cmd = ["python3", "find_standard_sdk.py"]
        run_command(cmd)
        cmd = ["python3", "match_candidates.py"]
        run_command(cmd)

    # 사용 완료한 파일 삭제
    file_path = os.path.join(original_dir, "output/not_external_list.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/sdk-signature.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/import_list.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = os.path.join(original_dir, "output/external_dependencies.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
        file_path = os.path.join(original_dir, "output/external_candidates.json")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # 내부 요소 식별


if __name__ == "__main__":
    main()