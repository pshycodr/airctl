import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "airctl"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "dismissed_update_version": None,
}


def load_settings():
    try:
        if not SETTINGS_FILE.exists():
            save_settings(DEFAULT_SETTINGS.copy())
            return DEFAULT_SETTINGS.copy()

        with open(
            SETTINGS_FILE,
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    try:
        CONFIG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                settings,
                f,
                indent=4,
            )

    except Exception:
        pass


def get_setting(key):
    return load_settings().get(
        key,
        DEFAULT_SETTINGS.get(key),
    )


def set_setting(key, value):
    settings = load_settings()

    settings[key] = value

    save_settings(settings)
