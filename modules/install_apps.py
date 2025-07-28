import subprocess
import platform
import os
import shutil
import json
from pathlib import Path
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables and initialize the LLM client
load_dotenv()
try:
    client = Groq()
except Exception as e:
    print(f"[ERROR] Failed to initialize Groq client: {e}")
    client = None

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

# A dictionary of known winget error codes and their meanings
# See: https://learn.microsoft.com/en-us/windows/win32/wininet/wininet-errors
WINGET_ERROR_CODES = {
    # 0x80072ee7 -> WININET_E_NAME_NOT_RESOLVED
    2147954407: "Network error: The server name could not be resolved. Please check your internet connection, firewall, and DNS settings.",
    # 0x80072efd -> WININET_E_CANNOT_CONNECT
    2147954429: "Network error: The connection with the server could not be established. Please check your internet connection and firewall settings.",
    # Add other common codes here as they are discovered
}


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


def _get_package_manager_commands():
    """
    Determines the operating system and returns the appropriate package manager commands.
    """
    os_name = platform.system()
    if os_name == "Windows":
        return {
            "name": "winget",
            "install_cmd": [
                "winget",
                "install",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            "check_cmd": ["winget", "list"],
            "check_success_pattern": None,  # winget list output is usually parsed directly
            "install_success_pattern": "Successfully installed",
        }
    elif os_name == "Darwin":  # macOS
        return {
            "name": "brew",
            "install_cmd": ["brew", "install"],
            "check_cmd": ["brew", "list"],
            "check_success_pattern": None,  # brew list output is usually parsed directly
            "install_success_pattern": "already installed|successfully installed",
        }
    elif os_name == "Linux":
        # Prioritize apt for Debian/Ubuntu, then dnf for Fedora/RHEL
        if shutil.which("apt-get"):
            return {
                "name": "apt",
                "install_cmd": ["sudo", "apt-get", "install", "-y"],
                "check_cmd": ["dpkg", "-s"],
                "check_success_pattern": "Status: install ok installed",
                "install_success_pattern": "Setting up",
            }
        elif shutil.which("dnf"):
            return {
                "name": "dnf",
                "install_cmd": ["sudo", "dnf", "install", "-y"],
                "check_cmd": ["dnf", "list", "--installed"],
                "check_success_pattern": None,  # dnf list output is usually parsed directly
                "install_success_pattern": "Complete!",
            }
        elif shutil.which("yum"):
            return {
                "name": "yum",
                "install_cmd": ["sudo", "yum", "install", "-y"],
                "check_cmd": ["yum", "list", "installed"],
                "check_success_pattern": None,  # yum list output is usually parsed directly
                "install_success_pattern": "Complete!",
            }
    return None  # No supported package manager found


def _run_command(command):
    """
    Runs a shell command and returns its output and success status.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # We handle success/failure manually
            shell=False,  # Always prefer shell=False for security and predictability
        )
        # Determine success based on returncode
        success = result.returncode == 0
        return {
            "success": success,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command not found: {command[0]}",
            "exit_code": 127,  # Standard exit code for command not found
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"An unexpected error occurred: {e}",
            "exit_code": 1,
        }


def _resolve_package_id_with_llm(app_name, pkg_manager_name, error_output):
    """
    Uses an LLM to find the correct package ID from an error message.
    """
    if not client:
        print("[ERROR] LLM client is not available.")
        return None

    prompt = (
        f"You are a command-line package manager expert. Your task is to extract the exact, correct package ID from an error message. "
        f"The user tried to install '{app_name}' using the '{pkg_manager_name}' package manager and got this error:\n\n"
        f"--- ERROR START ---\n{error_output}\n--- ERROR END ---\n\n"
        f"Based on the error, what is the correct package ID for '{app_name}'? "
        f"For example, for 'skype', the ID might be 'Microsoft.Skype'. "
        f"Reply with ONLY the package ID and nothing else. If you cannot determine the ID, reply with 'None'."
    )

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0.0,
            stream=False,
        )
        package_id = response.choices[0].message.content.strip()

        if package_id.lower() == "none" or " " in package_id:
            print(f"[LLM] Could not resolve a specific package ID for '{app_name}'.")
            return None

        # Basic sanitization to prevent command injection
        if not re.match(r"^[a-zA-Z0-9._-]+$", package_id):
            print(
                f"[LLM] Resolved ID '{package_id}' contains invalid characters. Discarding."
            )
            return None

        print(f"[LLM] Resolved '{app_name}' to package ID: '{package_id}'")
        return package_id
    except Exception as e:
        print(f"[ERROR] LLM call failed during package resolution: {e}")
        return None


def is_installed(app_name, pkg_manager_commands):
    """
    Checks if an application is installed using memory, common paths, or package manager.
    """
    memory = load_memory()
    if app_name in memory:
        saved_path = memory[app_name]
        if os.path.exists(saved_path):
            print(f"[Memory] Found {app_name} at saved path: {saved_path}")
            return True
        else:
            print(f"[Memory] Saved path for {app_name} not found anymore. Removing.")
            del memory[app_name]
            save_memory(memory)

    # Check common system paths using shutil.which
    if shutil.which(app_name):
        print(f"[PATH] Found {app_name} in system PATH.")
        return True

    # Check using package manager
    if pkg_manager_commands:
        check_cmd = pkg_manager_commands["check_cmd"]
        os_name = platform.system()

        if os_name == "Windows":
            # winget list output needs to be parsed
            result = _run_command(check_cmd + [app_name])
            if result["success"] and app_name.lower() in result["stdout"].lower():
                print(f"[winget] Found {app_name} via winget list.")
                return True
        elif os_name == "Darwin":
            # brew list output needs to be parsed
            result = _run_command(check_cmd)
            if result["success"] and app_name.lower() in result["stdout"].lower():
                print(f"[brew] Found {app_name} via brew list.")
                return True
        elif os_name == "Linux":
            if "apt-get" in pkg_manager_commands["install_cmd"]:
                # dpkg -s <package>
                result = _run_command(check_cmd + [app_name])
                if (
                    result["success"]
                    and pkg_manager_commands["check_success_pattern"]
                    in result["stdout"]
                ):
                    print(f"[apt] Found {app_name} via dpkg -s.")
                    return True
            elif (
                "dnf" in pkg_manager_commands["install_cmd"]
                or "yum" in pkg_manager_commands["install_cmd"]
            ):
                # dnf/yum list installed <package>
                result = _run_command(check_cmd + [app_name])
                if result["success"] and app_name.lower() in result["stdout"].lower():
                    print(
                        f"[{pkg_manager_commands['install_cmd'][1]}] Found {app_name} via package manager list."
                    )
                    return True
    return False


def _format_error_message(app_name, result, package_id=None):
    """Formats a detailed error message from a _run_command result."""
    exit_code = result["exit_code"]

    # Check for known error codes to provide a more helpful message
    known_error = WINGET_ERROR_CODES.get(exit_code)

    if package_id:
        intro = f"Failed to install '{app_name}' with specific ID '{package_id}'."
    else:
        intro = f"Failed to install '{app_name}'."

    error_message = f"{intro}\n"
    if known_error:
        error_message += f"Reason: {known_error}\n"

    if result["stderr"]:
        error_message += f"Error: {result['stderr']}\n"
    if result["stdout"]:
        error_message += f"Output: {result['stdout']}\n"

    error_message += f"Exit Code: {exit_code}"
    return error_message


def handle(action):
    """
    Handles a user command like 'install chrome' by attempting to install the app
    using the appropriate package manager, with checks and confirmations.
    """
    app_name = action.replace("install", "").strip().lower()

    if app_name not in WHITELIST:
        return f"'{app_name}' is not whitelisted for installation."

    pkg_manager_commands = _get_package_manager_commands()
    if not pkg_manager_commands:
        return "No supported package manager found on this system."

    if is_installed(app_name, pkg_manager_commands):
        return f"'{app_name}' is already installed."

    # --- First Attempt ---
    user_confirm = input(
        f"Are you sure you want to install '{app_name}'? (yes/no): "
    ).lower()
    if user_confirm not in ["yes", "y"]:
        return f"Installation of '{app_name}' cancelled by user."

    print(f"Attempting to install '{app_name}'...")
    install_cmd = pkg_manager_commands["install_cmd"] + [app_name]
    install_result = _run_command(install_cmd)

    # --- Success or Retry Logic ---
    if install_result["success"]:
        return f"Successfully installed '{app_name}'."

    # Check for ambiguity error (e.g., from winget)
    ambiguity_keywords = ["multiple packages found", "refine the input"]
    error_output = install_result["stdout"] + install_result["stderr"]

    if any(keyword in error_output.lower() for keyword in ambiguity_keywords):
        print("[LOG] Ambiguous package name detected. Attempting to resolve with LLM.")
        pkg_manager_name = pkg_manager_commands.get("name", "unknown")

        package_id = _resolve_package_id_with_llm(
            app_name, pkg_manager_name, error_output
        )

        if package_id:
            # --- Second Attempt with specific ID ---
            print(f"Found specific package ID: '{package_id}'.")
            retry_confirm = input(
                "Do you want to try installing with this ID? (yes/no): "
            ).lower()

            if retry_confirm in ["yes", "y"]:
                print(f"Retrying installation with ID '{package_id}'...")
                retry_cmd = pkg_manager_commands["install_cmd"] + [package_id]
                retry_result = _run_command(retry_cmd)

                if retry_result["success"]:
                    return f"Successfully installed '{app_name}' (as '{package_id}')."
                else:
                    # Installation failed even with the specific ID
                    return _format_error_message(app_name, retry_result, package_id)
            else:
                return f"Installation of '{app_name}' cancelled by user."

    # Generic failure or LLM could not resolve
    return _format_error_message(app_name, install_result)


# Removed open_app and log_action as they are not directly used by the new installation logic.
# If needed for other parts of the project, they should be moved or re-evaluated.

if __name__ == "__main__":
    # Example usage
    print("--- Testing install_apps.py ---")

    # Test case 1: Install a whitelisted app (e.g., "skype") that needs resolution
    # This will prompt for user confirmation twice
    response = handle("install skype")
    print(f"Response for 'install skype': {response}\n")

    # # Test case 2: Try to install a non-whitelisted app
    # response = handle("install unknownapp")
    # print(f"Response for 'install unknownapp': {response}\n")

    # # Test case 3: App already installed (if you have one from WHITELIST installed)
    # response = handle("install git")
    # print(f"Response for 'install git' (already installed): {response}\n")
