# Contributing to AIRCTL

Thank you for your interest in contributing to AIRCTL. This document provides guidelines for contributing to the project.

## Getting Started

Fork the repository and clone your fork:

```bash
git clone https://github.com/pshycodr/airctl.git
cd airctl
```

## Project Structure

```
airctl/
├── airctl/
│   ├── main.py               # Entry point
│   ├── main_cli.py           # CLI argument parser
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

## Development Setup

AIRCTL uses uv for dependency management. Install uv if you have not already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install project dependencies:

```bash
uv sync
```

This creates a virtual environment and installs all required packages.

## Running the Application

Run AIRCTL in development mode:

```bash
uv run airctl/main.py
```

To Build the application

```bash
# activate the venv
source .venv/bin/activate

# run the build script
./scripts/build.sh
```

## Project Structure

Familiarize yourself with the codebase:

- `airctl/models.py`: Data structures for network information
- `airctl/network_manager.py`: Interface to NetworkManager via nmcli
- `airctl/ui/`: All GTK4 UI components
- `airctl/styles/style.css`: Application styling
- `airctl/main.py`: Application entry point

## Making Changes

Create a new branch for your feature or fix:

```bash
git checkout -b feature/your-feature-name
```

Make your changes and test them thoroughly. Run the application and verify your changes work as expected.

## Code Style

Follow these guidelines:

- Use clear, descriptive variable names
- Keep functions focused on a single task
- Add docstrings to complex functions
- Follow PEP 8 style guidelines
- Keep line length under 88 characters

## Testing Your Changes

Before submitting, test your changes:

1. Run the application and verify all features work
2. Test WiFi scanning and connection
3. Check that the UI renders correctly
4. Verify error handling works properly

## Committing Changes

Write clear commit messages:

```bash
git commit -m "<commit tag>: brief description"
# commit tag : fix, add, chore, update, refactor etc.
```

Good commit messages are concise and describe what changed and why.

## Submitting a Pull Request

Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

Open a pull request on GitHub. In your PR description:

- Describe what you changed
- Explain why you made the change
- Reference any related issues
- Include screenshots for UI changes

## Reporting Bugs

Found a bug? Open an issue on GitHub with:

- Clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- System information (OS, Python version, GTK version)
- Error messages or logs if applicable

## Feature Requests

Have an idea for a new feature? Open an issue describing:

- What you want to add
- Why this feature would be useful
- How you envision it working

## Code Review Process

All submissions require review. We will:

- Review your code for quality and correctness
- Test the changes locally
- Provide feedback or request changes
- Merge approved pull requests

## Dependencies

Adding new dependencies requires discussion. Open an issue first to discuss whether the dependency is necessary.

If approved, add dependencies using uv:

```bash
uv add <package-name>
```

## Questions?

Not sure about something? Open an issue and ask. We are here to help.

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.
