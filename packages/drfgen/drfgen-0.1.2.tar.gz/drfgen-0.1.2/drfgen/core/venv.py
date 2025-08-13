import subprocess
import sys
import os
import platform

def create_venv(venv_path: str):
    print(f"Generating virtual environment in this path: {venv_path}")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    
def get_venv_bin(venv_path: str):
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts")
    else:
        return os.path.join(venv_path, "bin")
    
def get_pip_path(venv_path: str):
    return os.path.join(get_venv_bin(venv_path), "pip")

def get_python_path(venv_path: str):
    return os.path.join(get_venv_bin(venv_path), "python")


def install_package(pip_path: str, package: str):
    print(f"📦 Installing {package}")
    subprocess.run([pip_path, "install", package], check=True)