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
from nodetools.tools import xmlmsg,  LockedFile
from nodetools.xmlqueue import XMLJobManager,  XMLWorkflow
from nodetools.abstractqueue import AbstractTaskExecutor
from nodetools.storelist import StoreList
from nodetools.localstores import LocalStoreList
from uuid import uuid4
import sys

def getTaskExecutor(mng, task):
    if mng.executors.has_key(task.action): 
        exc=mng.executors[task.action]
        AbstractTaskExecutor.verify(exc, task)
        return exc
    else: raise Exception("Don't know how to execute "+task.action)


def verify(doc):
    mng=XMLJobManager()
    slist=StoreList()
    llist=LocalStoreList()
    mng.registerPlugins()
    workflow=XMLWorkflow(doc.documentElement)
    for task in workflow.tasks:
        exc=getTaskExecutor(mng, task)
        if task.attributes.has_key("destStore"):
            store=llist.getByUuid(task.attributes["destStore"])
            if store<>None: continue
            store=slist.getByUuid(task.attributes["destStore"])
            if store==None: raise Exception("Unknown destination store")
            # oops, requested remote destination store and executor does not support it
            # change destination store to local one and add MOVE task after that
            if  not exc.supportsRemoteDestination:
                task.element.setAttribute("destStore", task.attributes["srcStore"])
                extra=doc.createElement("task")
                extra.setAttribute("guid",  uuid4().get_hex())
                extra.setAttribute("action", "MOVE")
                extra.setAttribute("srcStore", task.attributes["srcStore"])
                if task.attributes.has_key("destAssetItem"):  extra.setAttribute("srcAssetItem", task.attributes["destAssetItem"])
                else: extra.setAttribute("srcAssetItem", task.attributes["srcAssetItem"])
                extra.setAttribute("destStore", store.uuid)
                doc.documentElement.insertBefore(extra, task.element.nextSibling)

        


try:
    workflow=parse(sys.stdin)
    if workflow.documentElement.tagName<>"workflow": raise Exception("Root tag should be workflow")
    if not workflow.documentElement.hasAttribute("guid"): workflow.documentElement.setAttribute("guid",  uuid4().get_hex())

    guid=workflow.documentElement.getAttribute("guid")
    with LockedFile(Config.QUEUEDIR+"/Queue.xml","r") as f:
        doc=parse(f)
    for wfnode in doc.getElementsByTagName("workflow"):
      oldguid=wfnode.getAttribute("guid")
      if guid==oldguid:  raise Exception("Duplicate workflow guid")
    verify(workflow)
    doc.documentElement.appendChild(workflow.documentElement)
    doc.documentElement.setAttribute("dateStart", "")
    doc.documentElement.setAttribute("dateFinished", "")
    with LockedFile(Config.QUEUEDIR+"/Queue.xml","w") as f:
        doc.writexml(f)
    xmlmsg("result", guid)
except Exception,   e:
    xmlmsg("error", str(e))
