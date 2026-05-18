from gi.repository import Gtk


def add_escape_close(window):
    controller = Gtk.EventControllerKey()

    def on_key(_, keyval, *_args):
        # Esc key
        if keyval == 65307:
            window.close()
            return True

        return False

    controller.connect(
        "key-pressed",
        on_key,
    )

    window.add_controller(controller)
