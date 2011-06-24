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


from nodetools.xmlqueue import XMLJobManager
from nodetools.tools import xmlmsg
import sys


def main():
  try:
    jman=XMLJobManager()
    doc=jman.load()
    for wfnode in doc.getElementsByTagName("workflow"):
        while wfnode.firstChild<>None: wfnode.removeChild(wfnode.firstChild)
    doc.writexml(sys.stdout)
    
  except Exception,  e:
      return xmlmsg("error", str(e))
  
if __name__=="__main__":
  main()
