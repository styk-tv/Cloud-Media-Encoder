#!/bin/bash

rm config.py
ln -s prodconfig.py config.py

python encoder.py