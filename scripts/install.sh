#!/usr/bin/env bash
set -e

BASE_URL="https://github.com/pshycodr/airctl/releases/latest/download"

echo "Downloading AIRCTL (latest release)..."
curl -fL "$BASE_URL/airctl.bin" -o airctl
curl -fL "$BASE_URL/airctl.desktop" -o airctl.desktop
curl -fL "$BASE_URL/airctl.png" -o airctl.png

chmod +x airctl

echo "Installing..."
sudo install -Dm755 airctl /usr/local/bin/airctl
sudo install -Dm644 airctl.desktop /usr/local/share/applications/airctl.desktop
sudo install -Dm644 airctl.png /usr/local/share/icons/hicolor/256x256/apps/airctl.png

echo "Updating icon cache..."
sudo gtk-update-icon-cache -f /usr/local/share/icons/hicolor || true

echo "Done. You can now launch AIRCTL from your app menu."
