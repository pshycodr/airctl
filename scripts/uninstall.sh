#!/usr/bin/env bash
set -e

echo "Uninstalling AIRCTL..."

sudo rm -f /usr/local/bin/airctl
sudo rm -f /usr/local/share/applications/airctl.desktop
sudo rm -f /usr/local/share/icons/hicolor/256x256/apps/airctl.png

echo "Updating icon cache..."
sudo gtk-update-icon-cache -f /usr/local/share/icons/hicolor || true

echo "AIRCTL uninstalled successfully."
