import os
import gi

gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk4LayerShell


def setup_overlay_window(window):
    is_wayland = (os.environ.get("XDG_SESSION_TYPE") == "wayland")

    if not is_wayland:
        return

    window.set_decorated(False)
    window.set_resizable(False)

    Gtk4LayerShell.init_for_window(window)

    Gtk4LayerShell.set_layer(
        window,
        Gtk4LayerShell.Layer.OVERLAY,
    )

    Gtk4LayerShell.set_keyboard_mode(
        window,
        Gtk4LayerShell.KeyboardMode.EXCLUSIVE,
    )

    Gtk4LayerShell.set_anchor(
        window,
        Gtk4LayerShell.Edge.TOP,
        True,
    )

    Gtk4LayerShell.set_anchor(
        window,
        Gtk4LayerShell.Edge.RIGHT,
        True,
    )

    Gtk4LayerShell.set_margin(
        window,
        Gtk4LayerShell.Edge.TOP,
        20,
    )

    Gtk4LayerShell.set_margin(
        window,
        Gtk4LayerShell.Edge.RIGHT,
        20,
    )
