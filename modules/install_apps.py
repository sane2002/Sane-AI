import subprocess
import platform

def handle(action):
    """
    Install an app: detect OS and run appropriate command.
    """
    app = action.replace("install", "").strip()
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(f"brew install {app}", shell=True)
        elif os_name == "Linux":
            subprocess.run(f"sudo apt install -y {app}", shell=True)
        elif os_name == "Windows":
            subprocess.run(f"choco install {app} -y", shell=True)
        return f"Installed {app} successfully!"
    except Exception as e:
        return f"Failed to install {app}: {e}"
