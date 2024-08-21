# Script to install the repository locally via a virtual environment
# the virtual environment will be called "venv"

import subprocess
import os
import venv


def create_virtualenv(env_name):
    if not os.path.exists(env_name):
        print(f"Creating virtual environment '{env_name}'...")
        venv.create(env_name, with_pip=True)
    else:
        print(f"Virtual environment '{env_name}' already exists.")


def install_requirements(env_name):
    # Check if requirements.txt file exists
    if not os.path.isfile('requirements.txt'):
        print("requirements.txt file not found.")
        return

    # Determine the path to the Python executable within the virtual environment
    if os.name == 'nt':
        # Windows
        python_executable = os.path.join(env_name, 'Scripts', 'python.exe')
    else:
        # Linux and macOS
        python_executable = os.path.join(env_name, 'bin', 'python')

    # Install the requirements using the virtual environment's Python executable
    try:
        subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("All requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing requirements: {e}")


if __name__ == "__main__":
    env_name = 'venv'  # Name of the virtual environment
    create_virtualenv(env_name)
    install_requirements(env_name)
