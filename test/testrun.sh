#!/bin/bash

SRCDIR=../src/node

rm $SRCDIR/nodetools/config.py
ln -s $SRCDIR/nodetools/testconfig.py $SRCDIR/nodetools/config.py
rm queue/Queue.xml
cp queue/Queue.xml.bak queue/Queue.xml

python $SRCDIR/encoder.py
