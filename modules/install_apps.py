import subprocess
import platform
import os
import shutil
import json
from pathlib import Path

# ✅ External memory file in user's home directory
MEMORY_FILE = str(Path.home() / ".jarvis_memory.json")

# ✅ Whitelist of safe, common apps we allow to install or open
WHITELIST = [
    "chrome",
    "firefox",
    "visual studio code",
    "vlc",
    "spotify",
    "slack",
    "zoom",
    "discord",
    "notion",
    "postman",
    "git",
    "docker",
    "nodejs",
    "python3",
    "java",
    "pycharm",
    "sublime text",
    "obsidian",
    "brave browser",
    "gimp",
    "inkscape",
    "libreoffice",
    "7zip",
    "audacity",
    "telegram",
    "whatsapp",
    "signal",
    "skype",
]


def load_memory():
    """
    Load saved memory (like found app paths) from external JSON file.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DEBUG] Couldn't load memory file: {e}")
            return {}
    return {}


def save_memory(memory):
    """
    Save current memory back to external JSON file.
    """
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
        print(f"[LOG] Memory saved to {MEMORY_FILE}")
    except Exception as e:
        print(f"[DEBUG] Couldn't save memory: {e}")


def handle(action):
    """
    Handle a user command like 'install chrome':
    1) Check if installed (using memory or paths)
    2) If installed → open it
    3) If not → open official download page
    """
    app = action.replace("install", "").strip().lower()
    os_name = platform.system()

    if app not in WHITELIST:
        return f"'{app}' is not whitelisted for installation."

    # ✅ Step 1: Check if app is installed
    if is_installed(app, os_name):
        print(f"{app} is already installed.")
        opened = open_app(app, os_name)
        if opened:
            return f"{app} opened successfully!"
        else:
            return f"{app} is installed, but couldn't open it automatically."
    else:
        print(f"{app} not found on system. Let's find it...")

    # Search official download page and open in browser
    try:
        import open_web

        result = open_web.handle(f"download {app}")
        log_action(f"Used open_web fallback for {app}: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] open_web fallback failed: {e}")
        return f"Could not find download page for {app}."
    # query = f"{app} official download"
    # urls = list(search(query, num_results=3))

    # if not urls:
    #     return f"Could not find download page for {app}."

    # download_url = urls[0]
    # print(f"Opening official download page: {download_url}")
    # webbrowser.open(download_url)

    # log_action(f"Suggested user to download and install {app} from {download_url}")
    # return f"Please download and install {app} manually from the opened page."


def is_installed(app, os_name):
    """
    Smarter check if app is installed:
    - Check saved memory first
    - Check standard paths
    - Fallback to 'which' for Linux/Windows
    """
    memory = load_memory()

    # ✅ Step 1: check memory
    if app in memory:
        saved_path = memory[app]
        if os.path.exists(saved_path):
            print(f"[Memory] Found {app} at saved path: {saved_path}")
            return True
        else:
            print(f"[Memory] Saved path for {app} not found anymore. Removing.")
            del memory[app]
            save_memory(memory)

    try:
        if os_name == "Windows":
            win_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            if app == "chrome":
                for path in win_paths:
                    if os.path.exists(path):
                        memory[app] = path
                        save_memory(memory)
                        return True
            # fallback: check PATH
            return shutil.which(app) is not None

        elif os_name == "Darwin":  # macOS
            mac_apps = {
                "chrome": "Google Chrome.app",
                "firefox": "Firefox.app",
                "visual studio code": "Visual Studio Code.app",
                "vlc": "VLC.app",
                "spotify": "Spotify.app",
            }
            if app in mac_apps:
                path = f"/Applications/{mac_apps[app]}"
                if os.path.exists(path):
                    memory[app] = path
                    save_memory(memory)
                    return True
            return shutil.which(app) is not None

        elif os_name == "Linux":
            if shutil.which(app):
                return True
            return False
        else:
            return False
    except Exception as e:
        print(f"[DEBUG] Error in is_installed: {e}")
        return False


def open_app(app, os_name):
    """
    Try to open installed app.
    """
    try:
        if os_name == "Windows":
            # best effort: run the saved path from memory if exists
            memory = load_memory()
            if app in memory:
                subprocess.run([memory[app]], shell=True)
                return True
            else:
                subprocess.run(["start", "", app], shell=True)
        elif os_name == "Darwin":
            mac_apps = {
                "chrome": "Google Chrome",
                "firefox": "Firefox",
                "visual studio code": "Visual Studio Code",
                "vlc": "VLC",
                "spotify": "Spotify",
            }
            app_name = mac_apps.get(app, app)
            subprocess.run(["open", "-a", app_name])
        elif os_name == "Linux":
            subprocess.run([app])

        else:
            return False
        return True
    except Exception as e:
        print(f"[DEBUG] Could not open app: {e}")
        return False


def log_action(text):
    """
    Append text to log.txt and print it.
    """
    print("[LOG]", text)
    with open("log.txt", "a") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    # Example usage
    user_input = "install skype"
    response = handle(user_input)
    print(response)

    # You can then route this action to the appropriate module
    # from task_router import route_task
    # response = route_task(user_input)
    # print(response)
