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


from nodetools.tools import tools,xmlmsg
from nodetools.volume import volume
import sys
from xml.dom.minidom import getDOMImplementation
import fdisk


def main():
   if len(sys.argv)<2: return xmlmsg("error","Usage: mount.py <device>|--all. Example: mount.py /dev/sdc")
   if sys.argv[1]=="--all": 
        out=fdisk.volumelist()
        mounted=0
        for disk in out.disks:
            vol=volume(disk.device)
            if vol.type<>"node-data": continue
            (ok, errmsg)=vol.mount()
            if ok: mounted=mounted+1
        return xmlmsg("return", str(mounted))
   else:
      vol=volume(sys.argv[1])
      if vol.type<>"node-data": return xmlmsg("error","Disk "+sys.argv[1]+" is of unknown type")
      (ok,errmsg)=vol.mount()
      if ok==False: return xmlmsg("error",str(errmsg))
      else: return xmlmsg("result",str(errmsg))
   
   
 
 
if __name__=="__main__":
   main()
   
