import os


# Function to build the executable using PyInstaller
def build_executable(script_path, script_name, exe_name):
    # Command to build the executable
    command = f"pyinstaller -F -w {script_path}{script_name}.py"
    new_file = f"dist/{exe_name}.exe"
    # Run the command
    os.system(command)

    # Rename the generated executable
    if os.path.exists(new_file):
        os.remove(new_file)
    os.rename(f"dist/{script_name}.exe", new_file)


if __name__ == "__main__":
    script_path = 'MatrixChatbotGenerator/'
    script_name = "start_user_interface"
    exe_name = "Matrix Quizbot Generator"
    build_executable(script_path, script_name, exe_name)

