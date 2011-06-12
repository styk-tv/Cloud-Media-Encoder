#!/bin/bash

rm config.py
ln -s testconfig.py config.py
rm test/queue/Queue.xml
cp test/queue/Queue.xml.bak test/queue/Queue.xml

cd test
python ../encoder.py
