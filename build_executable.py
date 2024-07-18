import os
import subprocess
import shutil


def build_executable(script_path, script_name, exe_name, hidden_imports=None):
    # Full path to the script
    script_full_path = os.path.join(script_path, f"{script_name}.py")

    # Ensure the script exists
    if not os.path.isfile(script_full_path):
        print(f"Error: {script_full_path} does not exist.")
        return

    # Cleanup old build/dist directories
    for directory in ['build', 'dist']:
        if os.path.exists(directory):
            shutil.rmtree(directory)

    # Command to build the executable
    command = ["pyinstaller", "-F", "-w"]

    if hidden_imports:
        for hidden_import in hidden_imports:
            command.extend(["--hidden-import", hidden_import])

    command.append(script_full_path)

    try:
        # Run the command
        subprocess.run(command, check=True)

        # Paths for the new subfolder and data folder
        new_subfolder = os.path.join("dist", "MatrixChatbotGenerator")
        data_folder = os.path.join(new_subfolder, "data")
        new_file = os.path.join(new_subfolder, f"{exe_name}.exe")

        # Create new subfolder and data folder
        os.makedirs(data_folder, exist_ok=True)

        # Move the generated executable to the new subfolder
        old_file = os.path.join("dist", f"{script_name}.exe")
        if os.path.exists(new_file):
            os.remove(new_file)

        if os.path.exists(old_file):
            shutil.move(old_file, new_file)
        else:
            print(f"Error: {old_file} was not created.")
    except subprocess.CalledProcessError as e:
        print(f"Error during PyInstaller execution: {e}")


if __name__ == "__main__":
    script_path = 'MatrixChatbotGenerator'
    script_name = "start_user_interface"
    exe_name = "Matrix Quizbot Generator"
    build_executable(script_path, script_name, exe_name)

