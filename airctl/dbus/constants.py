NM_SERVICE = "org.freedesktop.NetworkManager"

NM_PATH = "/org/freedesktop/NetworkManager"
NM_SETTINGS_PATH = "/org/freedesktop/NetworkManager/Settings"

NM_INTERFACE = "org.freedesktop.NetworkManager"

DEVICE_INTERFACE = "org.freedesktop.NetworkManager.Device"

WIRELESS_INTERFACE = "org.freedesktop.NetworkManager.Device.Wireless"

WIRED_INTERFACE = "org.freedesktop.NetworkManager.Device.Wired"

ACCESS_POINT_INTERFACE = "org.freedesktop.NetworkManager.AccessPoint"

SETTINGS_INTERFACE = "org.freedesktop.NetworkManager.Settings"

CONNECTION_INTERFACE = "org.freedesktop.NetworkManager.Settings.Connection"

ACTIVE_CONNECTION_INTERFACE = "org.freedesktop.NetworkManager.Connection.Active"

IP4_CONFIG_INTERFACE = "org.freedesktop.NetworkManager.IP4Config"

IP6_CONFIG_INTERFACE = "org.freedesktop.NetworkManager.IP6Config"

DHCP4_CONFIG_INTERFACE = "org.freedesktop.NetworkManager.DHCP4Config"

PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

DEVICE_TYPE_ETHERNET = 1
DEVICE_TYPE_WIFI = 2

ACTIVE_CONNECTION_STATE_ACTIVATING = 1
ACTIVE_CONNECTION_STATE_ACTIVATED = 2
ACTIVE_CONNECTION_STATE_DEACTIVATING = 3
ACTIVE_CONNECTION_STATE_DEACTIVATED = 4

AP_FLAG_PRIVACY = 0x1

AP_SEC_KEY_MGMT_PSK = 0x100
AP_SEC_KEY_MGMT_802_1X = 0x200
AP_SEC_KEY_MGMT_SAE = 0x400
AP_SEC_KEY_MGMT_OWE = 0x800

DEVICE_STATE_NAMES = {
    0: "unknown",
    10: "unmanaged",
    20: "unavailable",
    30: "disconnected",
    40: "prepare",
    50: "config",
    60: "need-auth",
    70: "ip-config",
    80: "ip-check",
    90: "secondaries",
    100: "activated",
    110: "deactivating",
    120: "failed",
}
