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


def main():
   if len(sys.argv)<2: return xmlmsg("error","Usage: prepare.py <device> [-f]. Example: prepare.py /dev/sdb")
   vol=volume(sys.argv[1])
   force=False
   if len(sys.argv)>2 and sys.argv[2]=="-f": force=True
   if vol.type<>"empty" and not force: return xmlmsg("error","Disk "+sys.argv[1]+" is not empty")
   (ok,errmsg)=vol.prepare()
   if ok==False: return xmlmsg("error",errmsg)
   else:
         (ok,errmsg2)=vol.mount()
         if ok==False: return xmlmsg("error",errmsg2)
         return xmlmsg("result",errmsg)
   
 
 
if __name__=="__main__":
   main()
   
