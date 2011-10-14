#!/bin/bash

if [ ! -e .git ]; then
    if [ -e /home/node/styk.tv ]; then
        cd /home/node/styk.tv
    else
        echo "Run update.sh from main source directory (/home/node/styk.tv)"
        exit 1
    fi
fi

git reset --hard
git pull
./install.sh
