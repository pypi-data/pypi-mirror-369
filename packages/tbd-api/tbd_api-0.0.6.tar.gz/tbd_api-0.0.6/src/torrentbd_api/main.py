import argparse
import json
import os
from typing import Any

import uvicorn
from dotenv import load_dotenv

from torrentbd_api.login import (
    check_login_status,
    get_config_dir,
    login,
    set_credentials,
)

load_dotenv()  # Load environment variables from .env file


def load_config() -> dict[str, Any]:
    """Load configuration from config file"""
    config_file = get_config_dir() / "config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                loaded_config = json.load(f)
                if isinstance(loaded_config, dict):
                    return loaded_config
                print("Error: Config file does not contain a dictionary")
        except Exception as e:
            print(f"Error loading config file: {e}")
    return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to config file"""
    config_file = get_config_dir() / "config.json"
    try:
        with open(config_file, "w") as f:
            json.dump(config, f)
        print(f"✅ Configuration saved to {config_file}")
    except Exception as e:
        print(f"❌ Error saving config file: {e}")


def check_custom_cookies() -> str | None:
    """Check for custom cookies file in config directory"""
    cookies_path = get_config_dir() / "cookies.txt"
    if cookies_path.exists():
        return str(cookies_path)
    return None


def ensure_login(
    username: str | None = None,
    password: str | None = None,
    totp_secret: str | None = None,
    cookies_path: str | None = None,
) -> None:
    """Ensure user is logged in using provided credentials or saved cookies"""
    # Set credentials if provided
    if username or password or totp_secret:
        set_credentials(username, password, totp_secret)

    # Check if custom cookies file exists
    custom_cookies = cookies_path or check_custom_cookies()
    if custom_cookies:
        os.environ["COOKIES_PATH"] = custom_cookies

    # Check login status and login if needed
    if not check_login_status():
        login()


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TorrentBD API Server")
    parser.add_argument("--username", help="TorrentBD username")
    parser.add_argument("--password", help="TorrentBD password")
    parser.add_argument("--totp-secret", help="TOTP secret for 2FA")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",  # nosec B104
        help="Host to bind the server to (default: 0.0.0.0, "
        "use 0.0.0.0 for all interfaces)",
    )
    parser.add_argument("--cookies", help="Path to cookies file")
    args = parser.parse_args()

    # Load existing config
    config = load_config()

    # Auto-save credentials if provided
    config_updated = False
    if args.username:
        config["username"] = args.username
        config_updated = True
    if args.password:
        config["password"] = args.password
        config_updated = True
    if args.totp_secret:
        config["totp_secret"] = args.totp_secret
        config_updated = True
    if args.port:
        config["port"] = args.port
        config_updated = True
    if args.host:
        config["host"] = args.host
        config_updated = True

    # Save config if it was updated
    if config_updated:
        save_config(config)

    # Set environment variables from config if not already set
    if "username" in config and not os.environ.get("TORRENTBD_USERNAME"):
        os.environ["TORRENTBD_USERNAME"] = config["username"]
    if "password" in config and not os.environ.get("TORRENTBD_PASSWORD"):
        os.environ["TORRENTBD_PASSWORD"] = config["password"]
    if "totp_secret" in config and not os.environ.get("TORRENTBD_TOTP_SECRET"):
        os.environ["TORRENTBD_TOTP_SECRET"] = config["totp_secret"]

    # Ensure login
    ensure_login(args.username, args.password, args.totp_secret, args.cookies)

    # Start server
    port = args.port or config.get("port", 5000)
    host = args.host or config.get("host", "0.0.0.0")  # nosec B104

    print(f"Starting TorrentBD API server on {host}:{port}")
    uvicorn.run("torrentbd_api.api:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
