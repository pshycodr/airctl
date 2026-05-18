import subprocess

from gi.repository import Gio, Gtk


def setup_actions(window):
    about_action = Gio.SimpleAction.new(
        "about",
        None,
    )

    about_action.connect(
        "activate",
        window.show_about_dialog,
    )

    window.get_application().add_action(
        about_action
    )

    github_action = Gio.SimpleAction.new(
        "github",
        None,
    )

    github_action.connect(
        "activate",
        window.open_github,
    )

    window.get_application().add_action(
        github_action
    )


def open_github(window, action, param):
    try:
        subprocess.Popen([
            "xdg-open",
            "https://github.com/pshycodr/airctl",
        ])

    except Exception as e:
        print(
            f"Failed to open GitHub link: {e}"
        )


def show_about_dialog(window, action, param):
    about = Gtk.AboutDialog()

    about.set_transient_for(window)

    about.set_modal(True)

    about.set_program_name(
        "AIRCTL"
    )

    about.set_version("v0.4.0")

    about.set_comments(
        "A modern WiFi management tool for Linux"
    )

    about.set_website(
        "https://github.com/pshycodr/airctl"
    )

    about.set_website_label(
        "View on GitHub"
    )

    about.set_authors(
        ["pshycodr"]
    )

    about.set_license_type(
        Gtk.License.GPL_3_0
    )

    about.set_logo_icon_name(
        "network-wireless-symbolic"
    )

    about.set_copyright(
        "© 2026 pshycodr"
    )

    about.add_credit_section(
        "Thanks to",
        [
            "nmcli team",
            "GTK developers",
            "Open source community",
        ],
    )

    about.present()
