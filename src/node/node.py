#!/usr/bin/python

##
## This file is part of the Styk.TV API project.
##
## Copyright (c) 2011 Piotr Styk (peter@styk.tv)
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License version 2 
## as published by  the Free Software Foundation
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
##


from nodetools.xmlqueue import XMLJobManager
from nodetools.queue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from shutil import rmtree
import os
import re
import subprocess
import daemon
import sys


        
def main():
  jman=XMLJobManager()
  jman.registerPlugins()
  queue=Queue(jman)
  queue.run()

if len(sys.argv)>1 and sys.argv[1]=="-d": main()
else: 
    with daemon.DaemonContext():
	main()
