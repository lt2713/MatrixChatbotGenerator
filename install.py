import subprocess
import sys
import os


def install_requirements():
    # Check if requirements.txt file exists
    if not os.path.isfile('requirements.txt'):
        print("requirements.txt file not found.")
        return

    # Install the requirements
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("All requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing requirements: {e}")


if __name__ == "__main__":
    install_requirements()
