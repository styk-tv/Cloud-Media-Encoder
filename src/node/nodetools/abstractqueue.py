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
  def setQueueProperty(self, workflow, task, property, value):
    pass
  def setCurrent(self, workflow,jdesc):
    pass

class AbstractTaskExecutor(object):
  def __init__(self,reporter, workflow,task):
    self.workflow=workflow
    self.task=task
    self.reporter=reporter
    self.taskNr=self.workflow.tasks.index(self.task)
  def run(self):
    pass
  def updateProgress(self, progress):
    self.reporter.setStatus(ST_WORKING, progress, "Working", self.workflow, self.task)
    self.reporter.setStatus(ST_WORKING,100.0*self.taskNr/len(self.workflow.tasks)+progress/len(self.workflow.tasks),"Working",self.workflow)
    
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
    print 'Registered executor '+action
  
  
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
        i=i+1
      except Exception,e:
        self.reporter.setStatus(ST_ERROR,0,e,workflow,task)
        self.reporter.setStatus(ST_ERROR,0,e,workflow)
        logging.exception("Error during workflow "+workflow.id+" task "+task.id)
        self.jman.releaseWorkflow(workflow)
        return
    self.reporter.setStatus(ST_FINISHED,100,"FINISHED",workflow)
    self.jman.releaseWorkflow(workflow)
      
  
