import os


# Function to build the executable using PyInstaller
def build_executable(script_name):
    # Command to build the executable
    command = f"pyinstaller -F -w {script_name}.py"

    # Run the command
    os.system(command)


if __name__ == "__main__":
    script_name = "start_user_interface"
    build_executable(script_name)

