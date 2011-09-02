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

import subprocess
from xml.dom.minidom import getDOMImplementation
import sys
from signal import SIGHUP
import os
import fcntl
from contextlib import *
from grp import getgrnam
from pwd import getpwnam

NGINX_PID="/var/run/nginx.pid"

def _get_gid(name):
    """Returns a gid, given a group name."""
    if getgrnam is None or name is None:
        return None
    try:
        result = getgrnam(name)
    except KeyError:
        result = None
    if result is not None:
        return result[2]
    return None

def _get_uid(name):
    """Returns an uid, given a user name."""
    if getpwnam is None or name is None:
        return None
    try:
        result = getpwnam(name)
    except KeyError:
        result = None
    if result is not None:
        return result[2]
    return None


def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return (retcode,output,unused_err)
    

def xmlmsg(node,msg,rc=1):
    impl=getDOMImplementation()
    doc=impl.createDocument(None, node, None)
    doc.documentElement.appendChild(doc.createTextNode(msg))
    doc.writexml(sys.stdout)
    doc.unlink()
    return rc
    

class tools:
  def __init__(self):
    pass
  @staticmethod
  def listAll():
    return check_output(["/sbin/fdisk","-lu"],env={ "LC_ALL" : "C"} )[1]
    
  @staticmethod
  def hasPartitions(dev):
    (code,ret,err)=check_output(["/sbin/fdisk","-lu",dev],env={ "LC_ALL" : "C"} )
    return ret.find("Device Boot")>-1
 
  @staticmethod
  def rescanScsi():
     for ifile in os.listdir("/sys/class/scsi_host"):
            srcfile=os.path.join("/sys/class/scsi_host", ifile)
            if not os.path.isdir(srcfile): continue
            with open(srcfile+"/scan", "w") as f: f.write("- - -\n")
            
  @staticmethod
  def getId(dev):
    lines=check_output(["/sbin/blkid","-o","udev",dev],env={"LC_ALL" : "C"} )[1].splitlines()
    ret={}
    for line in lines:
      (k,s,v)=line.partition("=")
      ret[k]=v
    return ret
  @staticmethod
  def umount(dev):
      (retcode, output,err)=check_output(["/bin/umount","-l",dev],env={"LC_ALL" : "C"} )
      return (retcode,err)
  @staticmethod
  def makeFs(dev):
    (retcode,output,err)=check_output(["/sbin/mkfs.ext4","-F",dev,"-L","TX-DATA-NODE"],env={"LC_ALL" : "C"} )
    return (retcode,err)
  @staticmethod
  def mount(dev,path):
    (retcode,output,err)=check_output(["/bin/mount",dev,path],env={"LC_ALL" : "C"} )
    return (retcode,err)
  @staticmethod
  def reloadNginx():
      with open(NGINX_PID, "r") as f:
          pid=int(f.read())
          os.kill(pid, SIGHUP)
  @staticmethod
  def chown(path, user=None, group=None):
    """Change owner user and group of the given path (file or dir).

    user and group can be the uid/gid or the user/group names, and in that case,
    they are converted to their respective uid/gid.
    """

    if user is None and group is None:
        raise ValueError("user and/or group must be set")
    _user = user
    _group = group

    # -1 means don't change it
    if user is None:
        _user = -1
    # user can either be an int (the uid) or a string (the system username)
    elif not isinstance(user, int):
        _user = _get_uid(user)
        # it means we weren't able to get the uid from the name
        if _user is None:
            raise ValueError("no such user, %s" % user)

    if group is None:
        _group = -1
    elif not isinstance(group, int):
        _group = _get_gid(group)
        if _group is None:
            raise ValueError("no such group, %s" % group)

    os.chown(path, _user, _group)


@contextmanager
def LockedFile(target, type):
    lock=None
    file=None
    try:
        lock=open(target, "r")
        ltype=fcntl.LOCK_EX
        if type=="r": ltype=fcntl.LOCK_SH
        fcntl.flock(lock, ltype)
        file=open(target, type)
        yield file
    finally:
        if file<>None: file.close()
        if lock<>None: lock.close()
