import webbrowser
import requests
import os
import re


def handle(action):
    """
    Handles 'open' actions:
    - Opens a website (e.g., 'open youtube')
    - Searches for a query (e.g., 'open python tutorials')
    - Downloads a setup file if asked (e.g., 'open chrome download' or 'download chrome')
    """
    action = action.lower().strip()
    # Download intent
    download_match = re.search(r"(download|setup|install)\s+([a-zA-Z0-9 .\-]+)", action)
    if download_match:
        app_name = download_match.group(2).strip()
        url = get_official_download_url(app_name)
        if url:
            file_path = download_file(url, app_name)
            if file_path:
                return f"Downloaded {app_name} setup to {file_path}"
            else:
                return f"Could not download {app_name} automatically. Opened download page."
        else:
            # Fallback: open a Google search for download
            search_url = f"https://www.google.com/search?q=download+{app_name}"
            webbrowser.open(search_url)
            return f"Opened browser to search for {app_name} download."
    # Open direct URL
    site = action.replace("open", "", 1).strip()
    if site.startswith("http") or site.startswith("www"):
        url = site if site.startswith("http") else f"https://{site}"
        webbrowser.open(url)
        return f"Opened {url}"
    # Otherwise, treat as a search query
    if site:
        search_url = f"https://www.google.com/search?q={site.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searched Google for '{site}'"
    return "Please specify what you want to open."


def get_official_download_url(app_name):
    """
    Returns the official download URL for popular apps.
    Extend this dictionary as needed.
    """
    known_downloads = {
        "chrome": "https://dl.google.com/chrome/install/latest/chrome_installer.exe",
        "firefox": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win&lang=en-US",
        "vlc": "https://get.videolan.org/vlc/last/win64/vlc-3.0.20-win64.exe",
        "python": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe",
        # Add more as needed
    }
    key = app_name.lower().split()[0]
    return known_downloads.get(key)


def download_file(url, app_name):
    """
    Downloads a file from the given URL to the current directory.
    """
    try:
        local_filename = url.split("/")[-1]
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return os.path.abspath(local_filename)
    except Exception as e:
        print(f"Download error: {e}")
        # Open the download page in browser as fallback
        webbrowser.open(url)
        return None


if __name__ == "__main__":
    print(handle("open youtube"))
    print(handle("open https://github.com"))
    print(handle("download chrome"))
    print(handle("open python"))
    print(handle("download vlc media player"))
