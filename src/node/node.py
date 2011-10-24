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
from nodetools.abstractqueue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.localstores import LocalStoreList
from nodetools.config import Config
from nodetools import processtools
from shutil import rmtree
from nodetools.links import linkschecker
import os
from nodetools.pidlockfile import PIDLockFile
import re
import pwd
import logging
import grp
from datetime import datetime
import subprocess
import daemon
import sys
from threading import Thread
def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

def setupLogging():
  logfile=Config.CONFIGDIR+"/node.log"
  if os.path.exists(logfile):
      os.rename(logfile, logfile+"."+str(datetime.now()))
  logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(msecs)d %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d %H:%M:%S',
                    filename=logfile,
                    filemode='w')
  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(msecs)d %(name)-12s %(levelname)-8s %(message)s')
  console.setFormatter(formatter)
  logging.getLogger('').addHandler(console)



        
def main():
  drop_privileges(Config.USER)
  setupLogging()
  with PIDLockFile(Config.CONFIGDIR+"/node.pid"):
      jman=XMLJobManager()
      jman.registerPlugins()
      queue=Queue(jman)
      
      linkthread=Thread(target=linkschecker)
      linkthread.daemon=True
      linkthread.start()
      
      # remove old interrupted tasks
      jman.unfinishedToError()
      queue.run()

def foreground_run():
    if processtools.is_running():
        print "Node is already running"
        return 1
    main()
    return 0

def try_start():
    if processtools.is_running():
        print "Node is already running"
        return 1
    with daemon.DaemonContext():
        main()
    return 0
    
def try_stop():
    if not processtools.is_running():
        print "Node is not running"
        return 1
    processtools.stop()
    return 0

def check_running():
    ret=3
    if processtools.is_running(): ret=0
    return ret

if __name__=="__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="start":  sys.exit(try_start())
        elif sys.argv[1]=="stop": sys.exit(try_stop())
        elif sys.argv[1]=="check":  sys.exit(check_running())
        elif sys.argv[1]=="run":  foreground_run()
    else: 
            print "Usage: node.py start|stop|check|run"
            sys.exit(1)

