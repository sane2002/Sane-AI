import webbrowser

def handle(action):
    """
    Handles an 'open' action, like 'open youtube' or 'open https://example.com'.
    """

    # Remove the word 'open' from the command to get the site name or URL
    site = action.replace("open", "").strip().lower()

    # If the user already said a full URL (starts with http or www), use it directly
    if site.startswith("http") or site.startswith("www"):
        url = site
    else:
        # Otherwise, guess the user means 'www.[site].com'
        url = f"https://www.{site}.com"

    # Use Python's built-in webbrowser module to open the site
    webbrowser.open(url)

    # Return a text response for the assistant to say
    return f"Opened {url}"

if __name__=='__main__':
    handle("open youtube")