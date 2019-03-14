#!/usr/bin/env python2
'''
Stores OTP challenge to auth file and access OpenVPN

The first time the script creates a configuration file: ~/.vpn-credentials

Author: Massimiliano Adamo <massimiliano.adamo@geant.org>
'''
import subprocess
import os
try:
    import onetimepass as otp
except ImportError:
    print "Please install onetimepass libray: pip install onetimepass\n"
    quit()


def check_config(config):
    """ check if otp_secret, user and password are properly set """
    if not os.path.isfile(config):
        secret_file = open(config, 'w')
        secret_file.write("# OTP Secret\nOTP_SECRET = 'XXXXXXXXXXXXXX'\n")
        secret_file.write("# VPN User\nVPN_USERNAME = 'username.vpn'\n")
        secret_file.write("# VPN Password\nVPN_PASSWORD = 'your_password'\n")
        secret_file.close()
        print " Could not open {0}\n A sample file {0} was created\n" \
              " Please edit this file and fill in your secret, username and password".format(config)
        os.sys.exit(1)


def get_otp(otp_secret):
    """ common commands """
    return otp.get_totp(otp_secret, as_string=True)


def write_auth(user, password, otp_token, auth_file):
    """ write auth file """
    authentication_file = open(auth_file, 'w')
    authentication_file.write("{}\n{}{}\n".format(user, password, otp_token))
    authentication_file.close()
    os.chmod(auth_file, 0600)


def write_ovpn(client_file, ovpn_file):
    """ write ovpn client """
    config_file = open(ovpn_file, 'w')
    config_file.write(client_file)
    config_file.close()


if __name__ == "__main__":
    MY_USER_DIR = os.path.expanduser('~')
    OTPCONFIG = os.path.join(MY_USER_DIR, '.vpn-credentials')
    OVPNFILE = os.path.join(MY_USER_DIR, '.client.ovpn')
    AUTHFILE = os.path.join(MY_USER_DIR, '.vpn-auth')
    check_config(OTPCONFIG)
    # make pylint happy
    OTP_SECRET = None
    VPN_USER = None
    VPN_PASSWORD = None
    execfile(OTPCONFIG)
    CLIENT_OVPN = """\
client
verb 2
dev tun
# log {0}/jump.log
remote 83.97.92.126 1194
script-security 2
# pull-filter ignore "dhcp-option DNS" # usually not needed
# push "dhcp-option DNS 123.45.56.89" # usually not needed
# push "dhcp-option DNS 234.56.78.99" # usually not needed
setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
down-pre
user nobody
group nogroup
proto udp
management localhost 7505
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
comp-lzo
reneg-sec 0
auth-nocache
auth-user-pass {0}/.vpn-auth
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
""".format(MY_USER_DIR)

    write_ovpn(CLIENT_OVPN, OVPNFILE)
    MY_TOKEN = get_otp(OTP_SECRET)
    XTERM_CMD = 'xterm -geometry 160x15 -fg green -bg black'
    write_auth(VPN_USER, VPN_PASSWORD, MY_TOKEN, AUTHFILE)
    PROC = subprocess.Popen(
        '{} -e /bin/bash -c "sudo openvpn --config {}"'.format(XTERM_CMD, OVPNFILE),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
