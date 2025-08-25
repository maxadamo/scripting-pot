#!/bin/bash
#
# inspired by this comment: https://askubuntu.com/a/1316231/205255
#
# No crontab, no systemd-timer needed.
# This script will download the latest Zoom .deb package and create a local APT repository.
#
KEEP=3  # versions to keep

PKG=zoom_amd64
URL=https://zoom.us/client/latest/${PKG}.deb
CDN_URL=https://cdn.zoom.us/prod
DEB_DIR=/usr/local/zoomdebs
APT_CONF=/etc/apt/apt.conf.d/999update_zoom
SOURCE_LIST=/etc/apt/sources.list.d/zoomdebs.sources
SCRIPT_PATH=$(realpath $0)
ZOOM_VER=$(curl -I -L $URL 2>&1 | awk -F/ '/location/{print $5}')

if [ "$(id -gn)" != "root" ]; then
    echo "this script must be run as root"
    exit
fi

# setup files and directories
set +o noclobber
if ! echo "APT::Update::Pre-Invoke {\"${SCRIPT_PATH}\";};" | cmp -s $APT_CONF -; then
    echo "creating $APT_CONF"
    echo "APT::Update::Pre-Invoke {\"${SCRIPT_PATH}\";};" >$APT_CONF
fi

if ! echo -e "Types: deb
URIs: file:/usr/local/zoomdebs/
Suites: ./
Components: 
Allow-Insecure: yes
Signed-By: /dev/null
Trusted: yes" | cmp -s $SOURCE_LIST -; then
    echo "creating $SOURCE_LIST"
    echo -e "Types: deb
URIs: file:/usr/local/zoomdebs/
Suites: ./
Components: 
Allow-Insecure: yes
Signed-By: /dev/null
Trusted: yes" >$SOURCE_LIST
fi
if [ ! -d "$DEB_DIR" ]; then
    echo "creating $DEB_DIR"
    mkdir -p "$DEB_DIR"
fi
# end setup

cd "$DEB_DIR"
test -f "${PKG}-${ZOOM_VER}.deb" && exit
curl -s --remove-on-error "${CDN_URL}/${ZOOM_VER}/${PKG}.deb" -o "${PKG}-${ZOOM_VER}.deb"

real_keep=$(($KEEP + 1))
to_delete=$(ls *deb | sort -V | tail -n +$real_keep)
test -n "$to_delete" && rm -f $to_delete

apt-ftparchive packages . >Packages && apt-ftparchive release . >Release
