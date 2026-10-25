import json
import threading
import urllib.request
import webbrowser

from config.constants import VERSION
from config.settings import (
    get_setting,
    set_setting,
)
from gi.repository import Gio, GLib

GITHUB_API = "https://api.github.com/repos/pshycodr/airctl/releases/latest"

LATEST_RELEASE_URL = "https://github.com/pshycodr/airctl/releases/latest"

LATEST_AVAILABLE_VERSION = None


def _parse_version(version: str) -> tuple:
    version = version.strip().lstrip("v")
    return tuple(int(part) for part in version.split("."))


def _show_update_notification(app, latest_version):
    try:
        notification = Gio.Notification.new(f"Airctl {latest_version} Available")

        notification.set_body("A newer version of Airctl is available.")

        notification.add_button(
            "Check What's New",
            "app.open-release",
        )

        notification.add_button(
            "Don't Show Again",
            "app.dismiss-update-notification",
        )

        app.send_notification(
            "Airctl-update",
            notification,
        )

    except Exception:
        pass

    return False


def _check_for_updates(app):
    global LATEST_AVAILABLE_VERSION

    try:
        request = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": "Airctl"},
        )

        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data["tag_name"].lstrip("v")

        if get_setting("dismissed_update_version") == latest_version:
            return

        print("LATEST AVAILABLE VERSION: ", latest_version)

        if _parse_version(latest_version) > _parse_version(VERSION):
            LATEST_AVAILABLE_VERSION = latest_version

            GLib.idle_add(
                _show_update_notification,
                app,
                latest_version,
            )

    except Exception:
        pass


def setup_update_notifications(app):
    try:
        open_action = Gio.SimpleAction.new(
            "open-release",
            None,
        )

        open_action.connect(
            "activate",
            lambda *_: webbrowser.open(LATEST_RELEASE_URL),
        )

        app.add_action(open_action)

        dismiss_action = Gio.SimpleAction.new(
            "dismiss-update-notification",
            None,
        )

        dismiss_action.connect(
            "activate",
            lambda *_: (
                set_setting(
                    "dismissed_update_version",
                    LATEST_AVAILABLE_VERSION,
                )
                if LATEST_AVAILABLE_VERSION
                else None
            ),
        )

        app.add_action(dismiss_action)

    except Exception:
        pass


def check_for_updates_async(app):
    threading.Thread(
        target=_check_for_updates,
        args=(app,),
        daemon=True,
        name="AirctlUpdateChecker",
    ).start()
