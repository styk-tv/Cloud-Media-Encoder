#!/bin/bash

if [ -e /opt/node ]; then
    echo "Node already installed, aborting"
    exit 1 
fi

if [ ! -e .git ]; then
    echo "Run install.sh from main source directory"
    exit 1
fi

echo "Installing dependencies"

apt-get install --force-yes -y ffmpeg python openssh-server python-daemon python-psutil python-paramiko python-m2crypto nginx make python-pam mediainfo python-imaging || exit 1 

DESTDIR=/

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
rm -rf etc

mkdir -p /var/www/volumes
chown -R node /var/www/volumes


ln -s ${PWD} ${DESTDIR}/opt/node
mkdir -p ${DESTDIR}/opt/node/queue 
echo "<queue />" > ${DESTDIR}/opt/node/queue/Queue.xml
echo "<links />" > ${DESTDIR}/opt/node/etc/Links.xml
chmod ugo+x ${DESTDIR}/opt/node/debian/init.d
cp -r ${DESTDIR}/opt/node/extra ${DESTDIR}/opt/node/etc
chown node ${DESTDIR}/opt/node/etc
chown node ${DESTDIR}/opt/node/etc/*
ln -s ${DESTDIR}/opt/node/extra/80-nodedisk.rules ${DESTDIR}/etc/udev/rules.d
ln -s ${DESTDIR}/opt/node/nodetools/prodconfig.py ${DESTDIR}/opt/node/nodetools/config.py
ln -s ${DESTDIR}/opt/node/debian/init.d ${DESTDIR}/etc/init.d/stock-footage-node
ln ${DESTDIR}/etc/init.d/stock-footage-node ${DESTDIR}/etc/rc2.d/stock-footage-node
ln ${DESTDIR}/etc/init.d/stock-footage-node ${DESTDIR}/etc/rc3.d/stock-footage-node
ln ${DESTDIR}/etc/init.d/stock-footage-node ${DESTDIR}/etc/rc4.d/stock-footage-node
ln ${DESTDIR}/etc/init.d/stock-footage-node ${DESTDIR}/etc/rc5.d/stock-footage-node

rm -f /etc/rc.local.orig
mv -f /etc/rc.local /etc/rc.local.orig || true
ln -s /opt/node/console.py /etc/rc.local
chmod ugo+x /etc/rc.local


/etc/init.d/stock-footage-node start
