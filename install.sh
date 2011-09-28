#!/bin/bash

MULTIMEDIA_REPO=http://debian-multimedia.fx-services.com/
MAIN_REPO=http://ftp.pl.debian.org/debian
TARGET_VERSION=wheezy

if [ ! -e .git ]; then
    echo "Run install.sh from main source directory"
    exit 1
fi

if [ -e /opt/node ]; then
    echo "Node already installed, finishing update"
    bash src/node/debian/init.d stop
fi


cat << EOF > /etc/apt/sources.list.d/node.list
deb $MULTIMEDIA_REPO $TARGET_VERSION main
deb $MAIN_REPO $TARGET_VERSION main
EOF


echo "Installing dependencies"

apt-get update
apt-get install --force-yes -y ffmpeg python openssh-server python-daemon python-psutil python-paramiko python-m2crypto nginx make python-pam mediainfo python-imaging python-simplejson python-pyexiv2 || exit 1 


echo "Installing"

adduser --system --shell /bin/sh node || true
mkdir -p /home/node/.ssh

if [ ! -f /home/node/.ssh/id_rsa.pub ]; then
	ssh-keygen -t rsa -f /home/node/.ssh/id_rsa -P "" -q
	touch /home/node/.ssh/authorized_keys
	chown -R node /home/node/.ssh
	chmod 0600 /home/node/.ssh/*
fi


if [ "$PWD" != "/home/node/styk.tv" ]; then
    rm -rf /home/node/styk.tv
    mv ${PWD} /home/node/styk.tv
    echo "Source directory moved to /home/node/styk.tv"
    cd /home/node/styk.tv
fi

chown -R node /home/node/styk.tv

rm /etc/udev/rules.d/80-nodedisk.rules || true
rm /etc/init.d/node-encoding || true
rm /etc/init.d/stock-footage-node || true
rm /etc/rc[2345].d/stock-footage-node || true

cd src/node
rm nodetools/config.py

if [ ! -d /opt/node ]; then
    ln -s ${PWD} /opt/node
fi


ln -s /opt/node/nodetools/prodconfig.py /opt/node/nodetools/config.py

mkdir -p /var/www/volumes
chown -R node /var/www/volumes


mkdir -p /opt/node/queue 
echo "<queue />" > /opt/node/queue/Queue.xml

if [ ! -d /opt/node/etc ]; then
    cp -r /opt/node/extra /opt/node/etc
fi
chown node /opt/node/etc
chown node /opt/node/etc/*

if [ ! -f /opt/node/etc/Links.xml ]; then
    echo "<links />" > /opt/node/etc/Links.xml
fi
if [ ! -f /opt/node/etc/Stores.xml ]; then
    echo "<stores />" > /opt/node/etc/Stores.xml
fi


chmod ugo+x /opt/node/debian/init.d
ln -s /opt/node/extra/80-nodedisk.rules /etc/udev/rules.d
ln -s /opt/node/debian/init.d /etc/init.d/stock-footage-node

ln /etc/init.d/stock-footage-node /etc/rc2.d/stock-footage-node
ln /etc/init.d/stock-footage-node /etc/rc3.d/stock-footage-node
ln /etc/init.d/stock-footage-node /etc/rc4.d/stock-footage-node
ln /etc/init.d/stock-footage-node /etc/rc5.d/stock-footage-node

rm -f /etc/rc.local.orig
mv -f /etc/rc.local /etc/rc.local.orig || true
ln -s /opt/node/console.py /etc/rc.local
chmod ugo+x /etc/rc.local


/etc/init.d/stock-footage-node start
