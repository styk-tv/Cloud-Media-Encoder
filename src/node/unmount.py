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
import sys
import os


def main():
   if len(sys.argv)<2: return xmlmsg("error","Usage: unmount.py <device>. Example: unmount.py /dev/sdc")
   dev=sys.argv[1]
   dir=None
   for line in open("/etc/mtab","r"):
        tab=line.split(" ")
        if len(tab)>1 and tab[0]==dev and tab[1][:16]=="/var/www/volumes": dir=tab[1]
   if dir==None: return xmlmsg("error","Not a node-data volume")
   (ok,errmsg)=tools.umount(dev)
  
  
   if ok<>0: return xmlmsg("error",str(errmsg))
   try:
     os.rmdir(dir)
   except Exception,e:
     return xmlmsg("error",str(e))
   return xmlmsg("result","OK")
   
   
 
 
if __name__=="__main__":
   main()
   
