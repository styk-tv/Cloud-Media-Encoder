from xml.dom.minidom import getDOMImplementation,parse
from queue import *
from storelist import StoreList
import os

QUEUEFILE="Queue.xml"

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

class XMLProgressReporter(ProgressReporter):
  def __init__(self, directory):
    self.target=directory+"/status"
    if not os.path.exists(self.target): os.makedirs(self.target)
  def  setStatus(self, jdesc,status,progress,message):
    impl=getDOMImplementation()
    doc=impl.createDocument(None, "status", None)
    doc.documentElement.setAttribute("code",status)
    doc.documentElement.setAttribute("progress",progress)
    doc.documentElement.appendChild(doc.createTextNode(message))
    f=open(self.target+"/current.xml", 'w')
    doc.writexml(f)
    doc.unlink()
   
  def setCurrent(self, jdesc):
    os.remove(self.target+"/current.xml")
    os.symlink(self.target+"/"+jdesc.id+".xml",self.target+"/current.xml")
    
   
    
class XMLJobManager(WorkflowManager):
  
  def __init__(self,directory):
    super(XMLJobManager,self).__init__()
    self.target=directory+"/"+QUEUEFILE
    self.pgrep=XMLProgressReporter(directory)
     
  def getNextWorkflow(self):
    doc=parse(open(self.target,"r"))
    for wfnode in doc.getElementsByTagName("workflow"):
      wflow=XMLWorkflow(wfnode)
      if wflow.isSourceReady(): return wflow  
    return None
  def releaseJob(self,jdesc):
    pass

