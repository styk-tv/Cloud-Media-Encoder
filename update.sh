#!/bin/bash

if [ ! -e .git ]; then
    echo "Run update.sh from main source directory (/home/node/styk.tv"
    exit 1
fi

git pull
./install.sh
