#!/bin/bash

echo "Uninstalling"
rm /etc/udev/rules.d/80-nodedisk.rules || true
rm -rf /opt/node
cd src/node
rm -rf etc
