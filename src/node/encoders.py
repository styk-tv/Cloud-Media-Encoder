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
from nodetools.encoderlist import EncodersList
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: encoders.py <types>|<list>|<create>|<remove>")
        action=sys.argv[1]
        stores=EncodersList()
        if action=="list": stores.write(sys.stdout)
        elif action=="types": stores.writeTypes(sys.stdout)
        elif action=="create": 
            ret=stores.create(sys.stdin)
            return xmlmsg("result", ret)
        elif action=="remove":
            if len(sys.argv)<3: raise Exception("Usage: encoders.py remove <encoder>")
            ret=stores.remove(sys.argv[2],)
            return xmlmsg("result", ret)
        else: raise Exception("Usage: encoders.py <types>|<list>|<create>|<remove>")
    except Exception, e:
        raise 
        return xmlmsg("error", str(e))
        
main()
