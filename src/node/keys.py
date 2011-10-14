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
from nodetools.config import Config


PUBKEY="/home/"+Config.USER+"/.ssh/id_rsa.pub"
KEYSTORE="/home/"+Config.USER+"/.ssh/authorized_keys"


def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: keys.py <get>|<authorize>|<unauthorize>")
        action=sys.argv[1]
        if action=="get":   # list  <status> <task guid>
          with open(PUBKEY, "r") as f:   return xmlmsg("result", f.read().split(" ")[1])
        elif action=="authorize":
            if len(sys.argv)<3: raise Exception("Usage: keys.py authorize <key>")
            found=False
            with open(KEYSTORE, "r+") as f: 
                for line in f:
                    if line.split(" ")[1]==sys.argv[2]: return xmlmsg("result", "0")
                f.write("ssh-rsa "+sys.argv[2]+" node\n")
            return xmlmsg("result", "1")
        elif action=="unauthorize":
            if len(sys.argv)<3: raise Exception("Usage: keys.py unauthorize <key>")
            with open(KEYSTORE, "r") as f: lines=[l for l in f.readlines() if l.split(" ")[1]<>sys.argv[2]]
            with open(KEYSTORE, "w") as f: f.writelines(lines)
            return xmlmsg("result", "OK")
        else: raise Exception("Usage: keys.py <get>|<authorize>|<unauthorize>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
