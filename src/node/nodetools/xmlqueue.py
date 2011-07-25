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
from abstractqueue import *
import pkgutil
from localstores import LocalStoreList
from config import Config
from datetime import datetime
import os
import modules

class XMLTask(Task):
  def __init__(self,element):
    super(XMLTask,self).__init__(element.getAttribute("guid"),element.getAttribute("action"))
    self.attributes={}
    for i in range(element.attributes.length):
      self.attributes[element.attributes.item(i).name]=element.attributes.item(i).value
      
  def isSourceReady(self):
    if self.attributes.has_key("srcStore") and self.attributes.has_key("srcAssetItem"):
      slist=LocalStoreList()
      store=slist.getByUuid(self.attributes["srcStore"])
      if store==None: return False
      path=store.findAsset(self.attributes["srcAssetItem"])
      return os.path.exists(path)
    else: return True

class XMLWorkflow(Workflow):
  def __init__(self,element):
    super(XMLWorkflow,self).__init__(element.getAttribute("guid"))
    for elm in element.getElementsByTagName("task"):
      self.tasks.append(XMLTask(elm))
  
  def isSourceReady(self):
      return self.tasks[0].isSourceReady()

   
    
class XMLJobManager(WorkflowManager, AbstractProgressReporter):
  
  def __init__(self,target=Config.QUEUEDIR+"/Queue.xml"):
    super(XMLJobManager,self).__init__()
    self.target=target
     
  def getNextWorkflow(self):
    doc=parse(open(self.target,"r"))
    for wfnode in doc.getElementsByTagName("workflow"):
      if len(wfnode.getAttribute("dateStart"))>0: continue
      wflow=XMLWorkflow(wfnode)
      if wflow.isSourceReady(): return wflow  
    return None
  def load(self):
    with open(self.target, "r") as f: doc=parse(f)
    return doc
  def getProgressReporter(self):
      return self
  def _getWorkflowElement(self, workflow):
    with open(self.target, "r") as f: doc=parse(f)
    for wfnode in doc.getElementsByTagName("workflow"):
      guid=wfnode.getAttribute("guid")
      if guid==workflow.id:  return (doc, wfnode)
    return (doc, None)
  def _getTaskElement(self, workflow, task):
    for wfnode in workflow.getElementsByTagName("task"):
      guid=wfnode.getAttribute("guid")
      if guid==task.id: return wfnode
    return None
  def releaseWorkflow(self,workflow):
      pass
#    (doc, wfnode)=self._getWorkflowElement(workflow)
  #  if wfnode<>None:
    #    doc.documentElement.removeChild(wfnode)
      #  with open(self.target, "w") as f: doc.writexml(f)
       # return
  def setCurrent(self,workflow, task):
      pass
  def setQueueProperty(self, workflow, task, property, value):
      (doc, wfnode)=self._getWorkflowElement(workflow)
      if task<>None: wfnode=self._getTaskElement(wfnode, task)
      wfnode.setAttribute(property, value)
      with open(self.target, "w") as f: doc.writexml(f)
      
  def  setStatus(self, status,progress,message, workflow, task=None):
      (doc, wfnode)=self._getWorkflowElement(workflow)
      if task<>None: wfnode=self._getTaskElement(wfnode, task)
      wfnode.setAttribute('status', str(status))
      wfnode.setAttribute("progress", str(progress))
      dstart=wfnode.getAttribute("dateStart")
      if status==ST_ERROR: wfnode.setAttribute("errorMessage",str(message))
      if len(dstart)==0: wfnode.setAttribute("dateStart",  datetime.now().ctime())
      if status==ST_PENDING or status==ST_FINISHED: wfnode.setAttribute("dateCompleted", datetime.now().ctime())
      with open(self.target, "w") as f: doc.writexml(f)
      
  def _filterQueue(self, status):
    with open(self.target, "r") as f: doc=parse(f)
    nodes=doc.getElementsByTagName("workflow")
    nodes=[node for node in nodes if status==None or self._getStatus(node)==status]
    return (doc, nodes)

  def _filterQueueNeq(self, status):
    with open(self.target, "r") as f: doc=parse(f)
    nodes=doc.getElementsByTagName("workflow")
    if status==None: return (doc, [])
    nodes=[node for node in nodes if self._getStatus(node)<>status]
    return (doc, nodes)
    
  def clear(self, status):
    (doc, nodes)=self._filterQueue(status)
    for node in nodes: doc.documentElement.removeChild(node)
    with open(self.target, "w") as f: doc.writexml(f)
    return len(nodes)
      
  def listByStatus(self):
    ret={}
    ret[0]=0
    ret[1]=0
    ret[2]=0
    ret[3]=0
    with open(self.target, "r") as f: doc=parse(f)
    nodes=doc.getElementsByTagName("workflow")
    for node in nodes:
        st=self._getStatus(node)
        ret[st]=ret[st]+1
    return ret
      
  def list(self, out, status, guid):
      (doc, wfnodes)=self._filterQueueNeq(status)
      if guid<>None: 
          t=Task(guid, "")
          for wfnode in doc.getElementsByTagName("workflow"):
              print wfnode
              if self._getTaskElement(wfnode, t)<>None: break
              doc.documentElement.removeChild(wfnode)
      for i in wfnodes: doc.documentElement.removeChild(i)
      doc.writexml(out)
  def _getStatus(self, wfnode):
      status=0
      if wfnode.hasAttribute("status"): status=int(wfnode.getAttribute("status"))
      return status
  def removeWorkflow(self, guid):
    (doc, wfnode)=self._getWorkflowElement(Workflow(guid))
    if wfnode==None: raise Exception("Unknown workflow")
    doc.documentElement.removeChild(wfnode)
    with open(self.target, "w") as f: doc.writexml(f)
      
  def retryWorkflow(self, guid):
    (doc, wfnode)=self._getWorkflowElement(Workflow(guid))
    if wfnode==None: raise Exception("Unknown workflow")
    if len(wfnode.getAttribute("dateStart"))==0: raise Exception("Workflow not finished yet")
    status=0
    if wfnode.hasAttribute("status"): status=int(wfnode.getAttribute("status"))
    if status<>ST_ERROR and status<>ST_FINISHED: raise Exception("Workflow not finished yet")
    self._resetProgress(wfnode)
    for node in wfnode.getElementsByTagName("task"): self._resetProgress(node)
    with open(self.target, "w") as f: doc.writexml(f)
      
  def _resetProgress(self, wfnode):
    wfnode.setAttribute("status", "0")
    wfnode.setAttribute("dateStart", "")
    if wfnode.hasAttribute("errorMessage"): wfnode.removeAttribute("errorMessage")
    if wfnode.hasAttribute("dateCompleted"): wfnode.removeAttribute("dateCompleted")
    wfnode.setAttribute("progress", "0")
    
  def registerPlugins(self):
      path="/".join(modules.__file__.split("/")[:-1])
      for name in os.listdir(path):
            if name.endswith(".py") and not name.startswith("__"):
                modulename = name.rsplit('.', 1)[0]
                self.registerPlugin(modulename)
  def registerPlugin(self, modulename):
      mainmod=__import__("modules."+modulename)
      submod=mainmod.__dict__[modulename]
      (action, cls)=submod.pluginInfo()
      self.registerExecutor(action, cls)
    
