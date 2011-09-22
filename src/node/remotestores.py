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


from nodetools.tools import xmlmsg
from nodetools.storelist import StoreList
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: remotestores.py <list>|<create>|<remove>|<createDisk>|<removeDisk>")
        action=sys.argv[1]
        stores=StoreList()
        if action=="list": stores.write(sys.stdout)
        elif action=="create": 
            if len(sys.argv)<5: raise Exception("Usage: remotestores.py create <disk uuid> <store uuid> <type>")
            ret=stores.addStore(sys.argv[2], sys.argv[3], sys.argv[4])
            return xmlmsg("result", ret)
        elif action=="remove":
            if len(sys.argv)<3: raise Exception("Usage: remotestores.py remove <store uuid>")
            ret=stores.removeStore(sys.argv[2])
            return xmlmsg("result", ret)
        elif action=="createDisk":
            if len(sys.argv)<4: raise Exception("Usage: remotestores.py createDisk <disk uuid> <host>")
            ret=stores.addDisk(sys.argv[2], sys.argv[3])
            return xmlmsg("result", ret)
        elif action=="removeDisk":
            if len(sys.argv)<3: raise Exception("Usage: remotestores.py removeDisk <disk uuid>")
            ret=stores.removeDisk(sys.argv[2])
            return xmlmsg("result", ret)
        else: raise Exception("Usage: stores.py <list>|<create>|<remove>|<createDisk>|<removeDisk>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
