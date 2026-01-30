import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk



class AppHeader(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()

        menu = Gio.Menu()

        menu.append("About", "app.about")
        menu.append("View on GitHub", "app.github")

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)

        self.pack_end(menu_button)
