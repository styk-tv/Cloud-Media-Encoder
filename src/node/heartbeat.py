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
from nodetools.localstores import LocalStoreList
from nodetools.processtools import is_running
from nodetools.xmlqueue import XMLJobManager
import sys
from time import sleep

def printStatus(out, checkcpu):
    doc=getDOMImplementation().createDocument(None, "status", None)
    node=doc.createElement("node")
    a=XMLJobManager()
    status=a.listByStatus()
    node.setAttribute("running", str(is_running()))
    node.setAttribute("pending", str(status[0]))
    node.setAttribute("processing", str(status[1]))
    node.setAttribute("finished", str(status[2]))
    node.setAttribute("failed", str(status[3]))
    doc.documentElement.appendChild(node)
    mem=doc.createElement("memory")
    phy=psutil.phymem_usage()
    virt=psutil.virtmem_usage()
    mem.setAttribute("total_physical", str(phy.total))
    mem.setAttribute("avail_physical", str(phy.total-phy.used))
    mem.setAttribute("total_virtual", str(virt.total))
    mem.setAttribute("avail_virtual", str(virt.total-virt.used))
    doc.documentElement.appendChild(mem)
    if checkcpu:
        cpu=doc.createElement("cpu")
        cpu.setAttribute("usage", str(psutil.cpu_percent(3)))
        doc.documentElement.appendChild(cpu)
    lsl=LocalStoreList()
    for disk in lsl.disks:
        d=doc.createElement("disk")
        d.setAttribute("guid", disk.uuid)
        d.setAttribute("online", str(disk.online))
        d.setAttribute('freespace', str(disk.freespace))
        doc.documentElement.appendChild(d)
    doc.writexml(out)

def main():
        checkcpu=len(sys.argv)>1 and sys.argv[1]=="--cpu"
        printStatus(sys.stdout, checkcpu)
        sys.stdout.write("\n")

main()
