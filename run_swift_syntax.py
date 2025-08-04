import sys
import os
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

def main():
    target_project_dir = "SyntaxAST"
    target_name = "SyntaxAST"
    # "/Users/seunghye/Desktop/SampleProject/Test"
    
    original_dir = os.getcwd() 
    swift_list_dir = "output/swift_file_list.txt"
    swift_list_dir = os.path.join(original_dir, swift_list_dir)

    external_list_dir = "output/external_file_list.txt"
    external_list_dir = os.path.join(original_dir, external_list_dir) 

    os.chdir(target_project_dir)
    run_command(["swift", "build"])
    run_command(["swift", "run", target_name, swift_list_dir, external_list_dir])


if __name__ == "__main__":
    main()