#!/usr/bin/env python3
"""
Stores OTP challenge to auth file and access OpenVPN

The first time the script creates a configuration file: ~/.vpn-credentials

if we set user nobody and group nogroup, upon disconnection it fails to restore resolv.conf

Author: Massimiliano Adamo <massimiliano.adamo@geant.org>
"""
import os
import shutil
import urllib.request
import configparser

try:
    import pyotp
except ImportError:
    print("Please install onetimepass: pip3 install pyotp\n")
    os.sys.exit()


def get_otp(otp_secret):
    """get OTP"""
    totp = pyotp.TOTP(otp_secret)
    return totp.now()


def write_file(file_content, file_name, file_mode=0o640):
    """write a given file"""
    with open(file_name, "w", encoding="utf-8") as config_file:
        config_file.write(file_content)
    os.chmod(file_name, file_mode)


if __name__ == "__main__":

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SCRIPT_NAME = os.path.basename(__file__)
    SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT_NAME)
    HOME_DIR = os.path.expanduser("~")
    BIN_DIR = os.path.join(HOME_DIR, "bin")
    SCRIPT_LINK = os.path.join(BIN_DIR, SCRIPT_NAME)
    OTPCONFIG = os.path.join(HOME_DIR, ".vpn-credentials")
    OVPNFILE = os.path.join(HOME_DIR, ".client.ovpn")
    AUTHFILE = os.path.join(HOME_DIR, ".vpn-auth")
    APPS_DIR = os.path.join(HOME_DIR, ".local/share/applications")
    SCRIPT_URL = "https://raw.githubusercontent.com/maxadamo/scripting-pot/refs/heads/master/otp-vpn/otp_vpn.py"

    with urllib.request.urlopen(SCRIPT_URL) as response:
        content = response.read().decode("utf-8")

    write_file(content, __file__, 0o755)

    os.system(f"rm -f {BIN_DIR}/jump_*.sh")  # temporary hack: keep it simple

    if not shutil.which("openvpn") or not shutil.which("nc"):
        print("Please ensure that 'openvpn' and 'nc' are installed")
        os.sys.exit()

    if not os.path.isfile("/etc/openvpn/update-systemd-resolved"):
        print("please install openvpn-systemd-resolved")
        os.sys.exit()

    if not os.path.isdir(BIN_DIR):
        print("Creating ~/bin directory")
        os.makedirs(BIN_DIR)

    if SCRIPT_LINK != SCRIPT_PATH and not os.path.islink(SCRIPT_LINK):
        print(f"Creating symlink {SCRIPT_LINK} -> {SCRIPT_PATH}")
        os.symlink(SCRIPT_PATH, SCRIPT_LINK)

    OTPCONFIG_CONTENT = """\
[otp-vpn]
# OTP Secret
otp_secret = XXXXXXXXXXXXXX
# VPN User
vpn_user = username.vpn
# VPN Password
vpn_password = your_password
"""

    if not os.path.isfile(OTPCONFIG):
        write_file(OTPCONFIG_CONTENT, OTPCONFIG, 0o640)
        print(f" Could not open {OTPCONFIG}\n A sample file {OTPCONFIG} was created\n")
        print(" Please edit this file and fill in secret, username and password")
        os.sys.exit()

    CONFIG = configparser.RawConfigParser()
    _ = CONFIG.read(OTPCONFIG)
    OTP_SECRET = CONFIG.get("otp-vpn", "otp_secret")
    VPN_USER = CONFIG.get("otp-vpn", "vpn_user")
    VPN_PASSWORD = CONFIG.get("otp-vpn", "vpn_password")

    CLIENT_OVPN = f"""\
client
verb 2
dev tun
#log {HOME_DIR}/jump.log
remote 83.97.92.126 1194
remote 83.97.92.163 1194
#remote 2001:798:3::96 1194
#remote 2001:798:3::bb 1194
connect-timeout 3
connect-retry 2
connect-retry-max 2
remote-random
script-security 2
# pull-filter ignore "dhcp-option DNS" # usually not needed
push "dhcp-option DNS 83.97.93.200" # usually not needed
# push "dhcp-option DNS 234.56.78.99" # usually not needed
setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#up /etc/openvpn/update-systemd-resolved
down /etc/openvpn/update-systemd-resolved
down-pre
#user nobody
#group nogroup
proto udp
management localhost 7505
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
data-ciphers-fallback AES-256-CBC
reneg-sec 0
auth-nocache
auth-user-pass {AUTHFILE}
<ca>
-----BEGIN CERTIFICATE-----
MIIEzTCCA7WgAwIBAgIJALKAow4vc6w7MA0GCSqGSIb3DQEBCwUAMIGfMQswCQYD
VQQGEwJOTDEWMBQGA1UECBMNTm9vcmQgSG9sbGFuZDESMBAGA1UEBxMJQW1zdGVy
ZGFtMQ4wDAYDVQQKEwVHZWFudDEPMA0GA1UECxMGRGV2T3BzMREwDwYDVQQDEwhH
ZWFudCBDQTEPMA0GA1UEKRMGc2VydmVyMR8wHQYJKoZIhvcNAQkBFhBkZXZvcHNA
Z2VhbnQub3JnMB4XDTE4MDIwMTE0MjAwN1oXDTI4MDEzMDE0MjAwN1owgZ8xCzAJ
BgNVBAYTAk5MMRYwFAYDVQQIEw1Ob29yZCBIb2xsYW5kMRIwEAYDVQQHEwlBbXN0
ZXJkYW0xDjAMBgNVBAoTBUdlYW50MQ8wDQYDVQQLEwZEZXZPcHMxETAPBgNVBAMT
CEdlYW50IENBMQ8wDQYDVQQpEwZzZXJ2ZXIxHzAdBgkqhkiG9w0BCQEWEGRldm9w
c0BnZWFudC5vcmcwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7Exu2
k2MceIdMiIGTeOrMqyuBlDzSL0X7n9IQuOEPjDh1RmoKWSLO97QZ3pB5GC14/NKs
FeO5Pi8zsLlTcoiaTwCtOTWa0y3MQiCbCCzyMgDs0IARkWamXHSuMb/ql9PthAgL
sPMHqV+Zjn9zwG4mWzX2ZhV4mtjFI5I7o9OCOUBQ28+Zyk9z2zxen5FRhkUJONNK
qLLSHz79P4UbPwSK2KNFxXcO+HOikIsqleGk5aRRE/fPsa9CH94vKdtDuazvuira
eHATizrlRminFVcz4XiAqvazdGkmf8dLkfXMIaTQ+AIrt2+iBU7s51OBW0XhIL52
Tq6GnIMsxdrVrCjBAgMBAAGjggEIMIIBBDAdBgNVHQ4EFgQU4OyJA6PGCnTg2g/j
Y6dEItAMfAkwgdQGA1UdIwSBzDCByYAU4OyJA6PGCnTg2g/jY6dEItAMfAmhgaWk
gaIwgZ8xCzAJBgNVBAYTAk5MMRYwFAYDVQQIEw1Ob29yZCBIb2xsYW5kMRIwEAYD
VQQHEwlBbXN0ZXJkYW0xDjAMBgNVBAoTBUdlYW50MQ8wDQYDVQQLEwZEZXZPcHMx
ETAPBgNVBAMTCEdlYW50IENBMQ8wDQYDVQQpEwZzZXJ2ZXIxHzAdBgkqhkiG9w0B
CQEWEGRldm9wc0BnZWFudC5vcmeCCQCygKMOL3OsOzAMBgNVHRMEBTADAQH/MA0G
CSqGSIb3DQEBCwUAA4IBAQBsULSWHVsgvhMYqH7QQiD3QixYYI3PNyjUXr5qL4ve
T0tylgkif4SqZXaG7HiIO+AeDjqImcrolQkFa0n0S4mNAt30+UDUDefaxTGVxyPS
TkEbo3xwseLL/0p2SCfm2n+IOrUlK/RxT09H4G3gphF6MppHRDf0oBWVDpEsmPO8
miNMuWdZapagP70CALq8UgPmPK0lJW2ERLl2yF2muTOJD3QjDSLkI9sjbQs8Kg01
B1tvBOFFVFlEHHK6+eAoIrbG/kzr1onXzxvVTaifUS4KVBcwjrMw89Y0uDSTsXu/
rqmweNTkxr8iU1vPv8stRYdCTrYcfXffNkhNdz++6Jwz
-----END CERTIFICATE-----
</ca>
"""

    JUMP_ON = f"""\
#!/bin/bash
sudo openvpn --config {OVPNFILE}
"""

    JUMP_ON_DESKTOP = f"""\
[Desktop Entry]
Encoding=UTF-8
Name=Jump VPN
GenericName=Jump VPN with OTP
Comment=Launch Jump VPN with OTP
Exec={BIN_DIR}/otp_vpn.py
Icon=network-vpn-symbolic
Terminal=true
Type=Application
MimeType=text/plain;
Categories=Network;
Actions=off;stats;

[Desktop Action off]
Name=Jump VPN OFF
Terminal=false
Exec=bash -c 'echo -e "signal SIGINT\\nquit" | nc 127.0.0.1 7505'

[Desktop Action stats]
Name=Jump VPN Stats
Terminal=false
Exec=bash -c 'echo -e "signal SIGUSR2\\nquit" | nc 127.0.0.1 7505'
"""

    JUMP_OFF_DESKTOP = """\
[Desktop Entry]
Encoding=UTF-8
Name=Jump VPN OFF
GenericName=Close Jump VPN connection
Comment=Close Jump VPN connection
Exec=bash -c 'echo -e "signal SIGINT\\nquit" | nc 127.0.0.1 7505'
Icon=network-vpn-acquiring-symbolic
Terminal=false
Type=Application
MimeType=text/plain;
Categories=Network;
"""

    JUMP_STATS_DESKTOP = """\
[Desktop Entry]
Encoding=UTF-8
Name=Jump VPN Stats
GenericName=Dump VPN Statistics
Comment=Close Jump VPN Statistics
Exec=bash -c 'echo -e "signal SIGUSR2\\nquit" | nc 127.0.0.1 7505'
Icon=network-vpn-no-route-symbolic
Terminal=false
Type=Application
MimeType=text/plain;
Categories=Network;
"""

    write_file(JUMP_ON_DESKTOP, f"{APPS_DIR}/jump-vpn.desktop")
    write_file(JUMP_STATS_DESKTOP, f"{APPS_DIR}/jump-vpn-stats.desktop")
    write_file(JUMP_OFF_DESKTOP, f"{APPS_DIR}/jump-vpn-off.desktop")
    write_file(CLIENT_OVPN, OVPNFILE)

    # Here we go:
    MY_TOKEN = get_otp(OTP_SECRET)
    write_file(f"{VPN_USER}\n{VPN_PASSWORD}{MY_TOKEN}\n", AUTHFILE, 0o600)
    os.system(f"sudo openvpn --config {OVPNFILE}")
