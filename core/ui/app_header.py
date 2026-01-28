import gi
from gi.repository import Gtk

gi.require_version("Gtk", "4.0")


class AppHeader(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        start_button = Gtk.Button(label="start button")
        self.pack_start(start_button)

        menu_button = Gtk.Button(icon_name="open-menu-symbolic")
        self.pack_end(menu_button)
