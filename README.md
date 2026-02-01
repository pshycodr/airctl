<div align="center">
  <img src="assets/banner.png" alt="Project Logo" width="full">

---

<br/>

  <p align="center">
    <i>A modern WiFi management tool for Linux built with GTK4 and Python.</i>
    <br/>
    <i>AIRCTL provides a clean interface to scan, connect, and manage wireless networks.</i>
  </p>

---

<br/>

[![GitHub stars](https://img.shields.io/github/stars/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/watchers)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![GTK](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)
[![Arch Linux](https://img.shields.io/badge/Arch-AUR-blue.svg)](https://aur.archlinux.org/packages/airctl-bin)

[![GitHub issues](https://img.shields.io/github/issues/pshycodr/airctl)](https://github.com/pshycodr/airctl/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/pshycodr/airctl)](https://github.com/pshycodr/airctl/pulls)
[![Last commit](https://img.shields.io/github/last-commit/pshycodr/airctl)](https://github.com/pshycodr/airctl/commits/main)

![AIRCTL Demo](assets/demo.png)

</div>

## Features

* Scan available WiFi networks
* Connect to secured and open networks
* View detailed network information
* Manage saved connections
* Disconnect and forget networks
* Auto-refresh network list
* Modern GTK4 interface
* Distributed via AUR (`airctl-bin`)

## Installation

### Arch Linux (Recommended)

Install directly from AUR:

```bash
yay -S airctl-bin
```

OR

```bash
curl -fsSL https://raw.githubusercontent.com/pshycodr/airctl/main/scripts/install.sh | bash
```

After installation, launch it from your app launcher or run:

```bash
airctl
```

---

### From Source

Clone the repository:

```bash
git clone https://github.com/pshycodr/airctl.git
cd airctl
```

Install dependencies using uv:

```bash
uv sync
```

Run the application:

```bash
uv run airctl/main.py
```

Build the application

```bash
# activate the venv
source .venv/bin/activate

# run the build script
./scripts/build.sh
```

## Requirements

* Python 3.12 or higher
* GTK 4
* NetworkManager
* nmcli

## Usage

Launch AIRCTL and toggle WiFi on or off using the switch at the top.

* The connected network appears as a highlighted card.
* Available networks are listed below.
* Click any network to connect.
* For secured networks, enter the password when prompted.
* Use the settings icon on a connected network to view details or disconnect.

## Project Structure

```
airctl/
├── airctl/
│   ├── main.py               # Entry point
│   ├── models.py             # Data models
│   ├── network_manager.py    # NetworkManager interface
│   ├── styles/
│   │   └── style.css         # Application styling
│   └── ui/
│       ├── app_header.py
│       ├── dialog_box.py
│       ├── network_info.py
│       ├── network_list.py
│       └── wifi_off_widget.py
│
├── assets/                   # Icons, banners, demo images
├── pyproject.toml            # Project metadata and dependencies
└── LICENSE
```

## Dependencies

* PyGObject (gi)
* nmcli

All dependencies are defined in `pyproject.toml` and handled via `uv`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.

## Credits

Built by [pshycodr](https://github.com/pshycodr)

Special thanks to the NetworkManager team, GTK developers, and the open source community.

## Show Your Support

If you found this project useful, consider giving it a star ⭐

[![Star this repo](https://img.shields.io/github/stars/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl)

Found a bug or have a feature request? Open an issue on GitHub.
