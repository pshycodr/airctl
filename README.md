

<div align="center">
  <img src="assets/banner.png" alt="Project Logo" width="full">

---

  <p align="center">
    <i>A modern WiFi management tool for Linux built with GTK4 and Python.</i>
    <i>AIRCTL provides a clean interface to scan, connect, and manage wireless networks.</i>
  </p>

  [![GitHub stars](https://img.shields.io/github/stars/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/stargazers)
  [![GitHub forks](https://img.shields.io/github/forks/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/network/members)
  [![GitHub watchers](https://img.shields.io/github/watchers/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl/watchers)

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![GTK](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)

  [![GitHub issues](https://img.shields.io/github/issues/pshycodr/airctl)](https://github.com/pshycodr/airctl/issues)
  [![GitHub pull requests](https://img.shields.io/github/issues-pr/pshycodr/airctl)](https://github.com/pshycodr/airctl/pulls)
  [![Last commit](https://img.shields.io/github/last-commit/pshycodr/airctl)](https://github.com/pshycodr/airctl/commits/main)


![AIRCTL Demo](assets/demo.png)

</div>

## Features

- Scan available WiFi networks
- Connect to secured and open networks
- View detailed network information
- Manage saved connections
- Disconnect and forget networks
- Auto-refresh network list
- Modern GTK4 interface

## Requirements

- Python 3.10 or higher
- GTK 4.0
- NetworkManager
- nmcli

## Installation

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

## Usage

Launch AIRCTL and toggle WiFi on or off using the switch at the top. The app displays your connected network in a large card at the top. Available networks appear below in a list.

Click any network to connect. For secured networks, you will need to enter the password. Click the settings icon on your connected network to view details or disconnect.

## Project Structure

```
airctl/
├── airctl/
│   ├── main.py                # Entry point
│   ├── models.py           # Data models
│   ├── network_manager.py  # NetworkManager interface
│   ├── styles/
│   │   └── style.css          # Application styling
│   └── ui/                 # UI components
│       ├── app_header.py
│       ├── dialog_box.py
│       ├── network_info.py
│       ├── network_list.py
│       └── wifi_off_widget.py
│
└── pyproject.toml         # Project dependencies
```

## Dependencies

- gi (PyGObject)
- nmcli
- python-nmcli

All dependencies are managed through uv and defined in pyproject.toml.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.

## Credits

Built by [pshycodr](https://github.com/pshycodr)

Special thanks to the nmcli team, GTK developers, and the open source community.

## Show Your Support

If you found this project helpful, please consider giving it a star! It helps others discover the project.

[![Star this repo](https://img.shields.io/github/stars/pshycodr/airctl?style=social)](https://github.com/pshycodr/airctl)

Found a bug or have a feature request? Open an issue on [GitHub](https://github.com/pshycodr/airctl/issues).
