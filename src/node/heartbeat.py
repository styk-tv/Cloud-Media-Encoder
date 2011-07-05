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



import psutil
from xml.dom.minidom import getDOMImplementation
from nodetools.tools import xmlmsg
import sys
from time import sleep

def printStatus(out):
    doc=getDOMImplementation().createDocument(None, "status", None)
    mem=doc.createElement("memory")
    mem.setAttribute("total_physical", str(psutil.TOTAL_PHYMEM))
    mem.setAttribute("avail_physical", str(psutil.avail_phymem()))
    mem.setAttribute("total_virtual", str(psutil.total_virtmem()))
    mem.setAttribute("avail_virtual", str(psutil.avail_virtmem()))
    doc.documentElement.appendChild(mem)
    cpu=doc.createElement("cpu")
    cpu.setAttribute("usage", str(psutil.cpu_percent()))
    doc.documentElement.appendChild(cpu)
    doc.writexml(out)

def main():
    sleep(2)
    while True:
        printStatus(sys.stdout)
        sys.stdout.write("\n")
        sleep(10)

main()
