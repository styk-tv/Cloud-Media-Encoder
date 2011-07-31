#!/bin/bash

if [ -e /opt/node ]; then
    echo "Node already installed, aborting"
    exit 1 
fi

echo "Installing dependencies"

apt-get install -y ffmpeg python openssh-server python-daemon python-psutil python-paramiko python-m2crypto nginx make python-pam mediainfo || exit 1 


echo "Installing"
rm /etc/udev/rules.d/80-nodedisk.rules || true
rm /etc/init.d/node-encoding || true
cd src/node
rm nodetools/config.py
rm -rf etc
make gitinstall DESTDIR=/
/etc/init.d/node-encoding start
