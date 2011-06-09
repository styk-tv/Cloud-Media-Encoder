from time import sleep


interval=10

# abstract classes


class JobDescription:
  def __init__(self,id):
    self.id=id


ST_PENDING,ST_WORKING,ST_FINISHED,ST_ERROR=range(4)

class ProgressReporter:
  def setStatus(self, jdesc,status,progress,message):
    pass
  def setCurrent(self, jdesc):
    pass
  
class Process:
  def __init__(self,jdesc,reporter):
    self.jdesc=jdesc
    self.reporter=reporter
  def run(self):
    pass
  def cleanup(self):
    pass


class JobManager:
  def getNextJob(self):
    return None
  def createProcess(self,jdesc,self.getProgressReporter()):
    return None
  def getProgressReporter(self):
    return ProgressReporter()
  def releaseJob(self,jdesc):
    pass
  
  
class Queue:
  def __init__(self, jman):
    self.jman=jman
    self.reporter=self.jman.getProgressReporter()
    
  def run(self):
    while True:
      jdesc=self.jman.getNextJob()
      if jdesc<>None: self.perform(jdesc)
      else: sleep(interval)
  
  def perform(self,jdesc):
    self.reporter.setCurrent(jdesc)
    try:
      process=self.jman.createProcess(jdesc)
      self.reporter.setStatus(jdesc,ST_WORKING,0,"WORKING")
      process.run()
      self.reporter.setStatus(jdesc,ST_FINISHED,100,"OK")
    except Exception, e:
      self.reporter.setStatus(jdesc,ST_ERROR,100,e)
    finally:
      self.jman.releaseJob(jdesc)
      if process<>None: process.cleanup()
  