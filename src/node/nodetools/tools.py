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
import os

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
  def makeFs(dev,type):
    (retcode,output,err)=check_output(["/sbin/mkfs.ext4","-F",dev,"-L","TX-DATA-"+type],env={"LC_ALL" : "C"} )
    return (retcode,err)
  @staticmethod
  def mount(dev,path):
    (retcode,output,err)=check_output(["/bin/mount",dev,path],env={"LC_ALL" : "C"} )
    return (retcode,err)
    

    
