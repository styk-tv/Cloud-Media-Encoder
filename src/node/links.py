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
from nodetools.links import Links
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: links.py <list>|<create>|<remove>|<modify>")
        action=sys.argv[1]
        links=Links()
        if action=="list": links.write(sys.stdout)
        elif action=="create": 
            if len(sys.argv)<7: raise Exception("Usage: links.py create <srcStore> <destStore> <assetItem> <expireDate> <expireTime>")
            ret=links.add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]+" "+sys.argv[6])
            return xmlmsg("result", "OK")
        elif action=="modify": 
            if len(sys.argv)<7: raise Exception("Usage: links.py modify <srcStore> <destStore> <assetItem> <expireDate> <expireTime>")
            ret=links.modify(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]+" "+sys.argv[6])
            return xmlmsg("result", "OK")
        elif action=="remove":
            if len(sys.argv)<5: raise Exception("Usage: links.py remove <srcStore> <destStore> <assetItem>")
            ret=links.remove(sys.argv[2],sys.argv[3], sys.argv[4])
            return xmlmsg("result", "OK")
        else: raise Exception("Usage: links.py <list>|<create>|<remove>|<modify>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
