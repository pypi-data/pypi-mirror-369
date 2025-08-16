import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def env_int(key: str, default: int) -> int:
    """
    Get an integer environment variable or return a default value
    If the key is not found, return the default value
    If the key is found but the value is not an integer, return the default value
    Otherwise, return the integer value
    """
    try:
        return int(os.getenv(key, default))
    except ValueError:
        return default


def env_float(key: str, default: float) -> float:
    """
    Get a float environment variable or return a default value
    If the key is not found, return the default value
    If the key is found but the value is not an float, return the default value
    Otherwise, return the float value
    """
    try:
        return float(os.getenv(key, default))
    except ValueError:
        return default


_host = os.getenv("SAPIO_SEL_HOST", "localhost")
_port = env_int("SAPIO_SEL_PORT", 443)
_guid = os.getenv("SAPIO_SEL_GUID", "")
headless = os.getenv("SAPIO_SEL_HEADLESS", "False").lower() == "true"
username = os.getenv("SAPIO_SEL_USERNAME", "user@example.com")
password = os.getenv("SAPIO_SEL_PASSWORD", "password")
default_timeout = env_float("SAPIO_SEL_DEFAULT_TIMEOUT", 60)

HOMEPAGE_URL = "https://" + _host + ":" + str(_port) + "/veloxClient"
if _guid:
    HOMEPAGE_URL += "/VeloxClient.html?app=" + _guid
else:
    HOMEPAGE_URL += "/localauth"
