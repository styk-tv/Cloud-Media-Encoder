#!/bin/bash

SRCDIR=../src/node

here=$PWD

cd $SRCDIR/nodetools
rm config.py
ln -s testconfig.py config.py

cd $here

rm queue/Queue.xml
cp queue/Queue.xml.bak queue/Queue.xml
chown qba queue/Queue.xml

python $SRCDIR/$1 $2 $3 $4 $5 $6 $7

