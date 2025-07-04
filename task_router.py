from modules import install_apps, send_email, knowledge_base

def route_task(action):
    """
    Figure out which module should handle the action.
    """
    if action.startswith("install"):
        return install_apps.handle(action)
    elif action.startswith("open"):
        return open_web.handle(action)
    elif action.startswith("send email"):
        return send_email.handle(action)
    elif action.startswith("remember") or action.startswith("recall"):
        return knowledge_base.handle(action)
    else:
        return "Sorry, I don't know how to do that yet."
