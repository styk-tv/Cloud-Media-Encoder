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
from nodetools.localstores import LocalStoreList
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: stores.py <list>|<create>|<remove>|<publish>|<unpublish>")
        action=sys.argv[1]
        stores=LocalStoreList()
        if action=="list": stores.write(sys.stdout)
        elif action=="create": 
            if len(sys.argv)<4: raise Exception("Usage: stores.py create <disk> <type>")
            ret=stores.add(sys.argv[2], sys.argv[3])
            return xmlmsg("result", ret)
        elif action=="remove":
            if len(sys.argv)<3: raise Exception("Usage: stores.py remove <store>")
            ret=stores.remove(sys.argv[2],)
            return xmlmsg("result", ret)
        elif action=="publish":
            if len(sys.argv)<5: raise Exception("Usage: stores.py publish <store> <virtual host> <port> [redirect404]")
            redirect404=None
            if len(sys.argv)>5: redirect404=sys.argv[5]
            ret=stores.publish(sys.argv[2], sys.argv[3], sys.argv[4], redirect404)
            return xmlmsg("result", ret)
        elif action=="unpublish":
            if len(sys.argv)<3: raise Exception("Usage: stores.py unpublish <store>")
            ret=stores.unpublish(sys.argv[2])
            return xmlmsg("result", ret)
        else: raise Exception("Usage: stores.py <list>|<create>|<remove>|<publish>|<unpublish>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
