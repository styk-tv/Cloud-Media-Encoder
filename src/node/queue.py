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
from nodetools.xmlqueue import XMLJobManager
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: queue.py <list>|<clear>|<remove>|<retry>")
        action=sys.argv[1]
        queue=XMLJobManager()
        if action=="list":   # list  <status> <task guid>
           status=None
           startTask=None
           try:
             if len(sys.argv)>2: status=int(sys.argv[2])
           except Exception, e:
               pass
           if len(sys.argv)>3: startTask=sys.argv[3]
           queue.list(sys.stdout, status, startTask)
        elif action=="remove":
            if len(sys.argv)<3: raise Exception("Usage: queue.py remove <workflow>")
            ret=queue.removeWorkflow(sys.argv[2])
            return xmlmsg("result", "OK")
        elif action=="retry":
            if len(sys.argv)<3: raise Exception("Usage: queue.py retry <workflow>")
            ret=queue.retryWorkflow(sys.argv[2])
            return xmlmsg("result", "OK")
        elif action=="clear":
            if len(sys.argv)<3: raise Exception("Usage: queue.py clear <status>")
            if sys.argv[2].lower()=="all": ret=queue.clearAll()
            else: ret=queue.clear(int(sys.argv[2]))
            return xmlmsg("result", str(ret))
        else: raise Exception("Usage: stores.py <list>|<create>|<remove>|<retry>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
