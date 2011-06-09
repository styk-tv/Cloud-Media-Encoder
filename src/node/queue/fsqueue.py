from xml.dom.minidom import getDOMImplementation
from queue import *
import os

class FSProgressReporter(ProgressReporter):
  def __init__(self, directory):
    self.target=directory+"/status"
    if not os.path.exists(self.target): os.makedirs(self.target)
  def  def setStatus(self, jdesc,status,progress,message):
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
    
class FSJobManager(JobManager):
  def __init__(self,directory):
    self.target=directory+"/queue"
    self.pgrep=FSProgressReporter(directory)
    if not os.path.exists(self.target): os.makedirs(self.target)
  def getNextJob(self):
    for fname in os.listdir(self.target)
      if fname[0]=='.': continue
      jdesc=JobDescription(fname)
      self.parseJob(jdesc,fname)
      return jdesc
    return None
  def releaseJob(self,jdesc):
    if os.path.exists(self.target+"/"+jdesc.id): os.unlink(self.target+"/"+jdesc.id)
  def parseJob(self,obj,f):
    pass
