#!/bin/bash

if [ ! -e .git ]; then
    echo "Run install.sh from main source directory"
    exit 1
fi


echo "Uninstalling"
rm /etc/udev/rules.d/80-nodedisk.rules || true
rm /etc/init.d/stock-footage-node
rm /etc/init.d/node-encoding
rm /etc/rc[2345].d/S99stock-footage-node || true

rm -rf /opt/node
cd src/node
rm -rf etc

if [ -f /etc/rc.local.orig ]; then
    rm /etc/rc.local
    mv /etc/rc.local.orig /etc/rc.local
fi
