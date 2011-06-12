from time import sleep
import logging

interval=10

# abstract classes


class Task(object):
  def __init__(self,id,action):
    self.id=id
    self.action=action

class Workflow(object):
  def __init__(self,id):
    self.id=id
    self.tasks=[]

ST_PENDING,ST_WORKING,ST_FINISHED,ST_ERROR=range(4)

class AbstractProgressReporter(object):
  def setStatus(self,status,progress,message, workflow,task=None):
    pass
  def setCurrent(self, workflow,jdesc):
    pass

class AbstractTaskExecutor(object):
  def __init__(self,reporter, workflow,task):
    self.workflow=workflow
    self.task=task
    self.reporter=reporter
  def run(self):
    pass
    
class WorkflowManager(object):
  def __init__(self):
    self.executors={}
    
  def getNextWorkflow(self):
    return None
  def getProgressReporter(self):
    return AbstractProgressReporter()
  def releaseWorkflow(self,jdesc):
    pass
  def getTaskExecutor(self,workflow,task):
    if self.executors.has_key(task.action): return self.executors[task.action](self.getProgressReporter(), workflow,task)
    else: raise Exception("Don't know how to execute "+task.action)
 
  def registerExecutor(self,action,cls):
    assert(issubclass(cls,AbstractTaskExecutor))
    self.executors[action]=cls
  
  
class Queue:
  def __init__(self, jman):
    self.jman=jman
    self.reporter=self.jman.getProgressReporter()
    
  def run(self):
    while True:
      jdesc=self.jman.getNextWorkflow()
      if jdesc<>None: self.perform(jdesc)
      else: sleep(interval)
  
  def perform(self,workflow):
    logging.info("Starting workflow "+workflow.id)
    self.reporter.setStatus(ST_WORKING,0,"WORKING",workflow)
    i=0
    for task in workflow.tasks:
      self.reporter.setCurrent(workflow,task)
      self.reporter.setStatus(ST_WORKING,0,"WORKING",workflow,task)
      try:
        executor=self.jman.getTaskExecutor(workflow,task)
        logging.info("Starting task "+task.id)
        executor.run()
        logging.info("Finished task "+task.id)
        self.reporter.setStatus(ST_FINISHED,100,"FINISHED",workflow,task)
#	i=i+1
#       self.reporter.setStatus(ST_WORKING,i/len(workflow.tasks),"WORKING",workflow)
      except Exception,e:
        self.reporter.setStatus(ST_ERROR,100,e,workflow,task)
        logging.exception("Error during workflow "+workflow.id+" task "+task.id)
        self.jman.releaseWorkflow(workflow)
        return
    self.reporter.setStatus(ST_FINISHED,100,"FINISHED",workflow,task)
    self.jman.releaseWorkflow(workflow)
      
  
