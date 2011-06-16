from xml.dom.minidom import getDOMImplementation,parse
from queue import *
from storelist import StoreList
from config import Config
from datetime import datetime
import os

class XMLTask(Task):
  def __init__(self,element):
    super(XMLTask,self).__init__(element.getAttribute("guid"),element.getAttribute("action"))
    self.attributes={}
    for i in range(element.attributes.length):
      self.attributes[element.attributes.item(i).name]=element.attributes.item(i).value
      
  def isSourceReady(self):
    if self.attributes.has_key("srcStore") and self.attributes.has_key("srcAssetItem"):
      slist=StoreList()
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
  def releaseWorkflow(self,workflow):
      pass
#    (doc, wfnode)=self._getWorkflowElement(workflow)
  #  if wfnode<>None:
    #    doc.documentElement.removeChild(wfnode)
      #  with open(self.target, "w") as f: doc.writexml(f)
       # return
  def setCurrent(self,workflow, task):
      pass
  def  setStatus(self, status,progress,message, workflow, task=None):
      (doc, wfnode)=self._getWorkflowElement(workflow)
      wfnode.setAttribute('status', str(status))
      wfnode.setAttribute("progress", str(progress))
      dstart=wfnode.getAttribute("dateStart")
      if len(dstart)==0: wfnode.setAttribute("dateStart",  datetime.now().ctime())
      if status==ST_PENDING or status==ST_FINISHED: wfnode.setAttribute("dateCompleted", datetime.now().ctime())
      with open(self.target, "w") as f: doc.writexml(f)
      
