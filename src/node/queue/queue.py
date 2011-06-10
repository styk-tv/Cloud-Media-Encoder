from time import sleep


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

class ProgressReporter(object):
  def setStatus(self, workflow,jdesc,status,progress,message):
    pass
  def setStatus(self,workflow,status,progress,message):
    pass
  def setCurrent(self, workflow,jdesc):
    pass

class Executor(object):
  def __init__(self,workflow,task):
    self.workflow=workflow
    self.task=task
  def run(self):
    pass

class WorkflowManager(object):
  def __init__(self):
    self.executors={}
    
  def getNextWorkflow(self):
    return None
  def getProgressReporter(self):
    return ProgressReporter()
  def releaseWorkflow(self,jdesc):
    pass
  def getTaskExecutor(self,workflow,task):
    if self.executors.hasKey(task.action): return self.executors[task.action](workflow,task)
    else: raise Exception("Don't know how to execute "+task.action)
 
  def registerExecutor(self,action,cls):
    assert(issubclass(cls,Executor))
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
  
  def perform(self,jdesc):
    self.reporter.setStatus(workflow,ST_WORKING,0,"WORKING")
    i=0
    for task in workflow.tasks:
      self.reporter.setCurrent(workflow,task)
      self.reporter.setStatus(workflow,task,ST_WORKING,0,"WORKING")
      try:
	executor=this.jman.getTaskExecutor(self.workflow,task)
	executor.execute(task,reporter)
	self.reporter.setStatus(self.workflow,task,ST_FINISHED,100,"FINISHED")
	i=i+1
        self.reporter.setStatus(workflow,ST_WORKING,i/len(workflow.tasks),"WORKING")
      except Exception,e:
	self.reporter.setStatus(workflow,task,ST_ERROR,100,e)
	self.jman.releaseWorkflow(workflow)
	return
    self.reporter.setStatus(workflow,task,ST_FINISHED,100,"FINISHED")
    self.jman.releaseWorkflow(workflow)
      
  