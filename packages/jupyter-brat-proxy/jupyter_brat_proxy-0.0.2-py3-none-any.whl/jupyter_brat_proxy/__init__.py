import os
import logging
import shutil
import pwd
import getpass

logging.basicConfig(level="INFO")
log = logging.getLogger("jupyter-brat-proxy")
log.setLevel("INFO")

APP_TITLE = "BRAT_APP"
APP_NAME = "brat"
APP_TITLE = "BRAT"


TRUTHY = ("true", "1", "yes", "on", "y")


def truthy(val):
    return str(val).strip('"').strip("'").lower() in TRUTHY


def _get_env(port, base_url):
    """
    Returns a dict containing environment settings to launch the Web App.

    Args:
        port (int): Port number on which the Web app will be started. Ex: 8888
        base_url (str): Controls the prefix in the url on which
                        the Web App will be available.
                        Ex: localhost:8888/base_url/index.html

    Returns:
        [Dict]: Containing environment settings to launch the Web application.
    """

    return {
        # "FLASK_RUN_PORT": str(port),
        # "FLASK_APP_URL_PREFIX": f"{base_url}{APP_NAME}",
        "BRAT_AUTH_ENABLED": "false",
    }


def get_icon_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "brat_favicon.svg"
    )


def _get_timeout(default=300):
    try:
        return float(os.getenv(f"{os.getenv('APP_TITLE')}_TIMEOUT", default))
    except Exception:
        return default


def get_system_user():
    try:
        user = pwd.getpwuid(os.getuid())[0]
    except Exception:
        user = os.getenv('USER', getpass.getuser())
    return user


def run_app():
    """
    Setup application.

    This method is run by jupyter-server-proxy package to launch the Web app.
    """
    log.info("Initializing Jupyter Workbench Proxy")

    icon_path = get_icon_path()

    try:
        executable_name = shutil.which("brat")
    except Exception:
        executable_name = "brat"

    host = "127.0.0.1"
    port = "{port}"
    user = get_system_user()
    log.debug(f"[{user}] Icon_path:  {icon_path}")
    log.debug(f"[{user}] Launch Command: {executable_name}")
    return {
        "command": [
            "brat", f"{port}",
        ],
        "timeout": _get_timeout(),
        "environment": _get_env,
        "absolute_url": False,
        # "rewrite_response": rewrite_netloc,
        "launcher_entry": {
            "title": APP_TITLE,
            "icon_path": icon_path,
            "enabled": truthy(os.getenv(f"{os.getenv('APP_TITLE')}_ENABLED", "true")),
        },
    }
