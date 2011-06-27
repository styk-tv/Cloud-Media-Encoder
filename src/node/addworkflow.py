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


from xml.dom.minidom import getDOMImplementation,parse
from nodetools.config import Config
from nodetools.tools import xmlmsg
import sys

try:
    workflow=parse(sys.stdin)
    if workflow.documentElement.tagName<>"workflow": raise Exception("Root tag should be workflow")
    guid=workflow.documentElement.getAttribute("guid")
    doc=parse(open(Config.QUEUEDIR+"/Queue.xml","r"))
    doc.documentElement.appendChild(workflow.documentElement)
    doc.documentElement.setAttribute("dateStart", "")
    doc.documentElement.setAttribute("dateFinished", "")
    doc.writexml(open(Config.QUEUEDIR+"/Queue.xml","w"))
    xmlmsg("result", guid)
except Exception, e:
    xmlmsg("error", str(e))
