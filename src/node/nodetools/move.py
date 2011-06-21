from nodetools.xmlqueue import XMLJobManager
from nodetools.queue import AbstractTaskExecutor,Queue
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from nodetools.storelist import StoreList
from shutil import move
import paramiko

class MoveExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(MoveExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.srcasset=slist.getByUuid(task.attributes["srcStore"]).findAsset(task.attributes["srcAssetItem"])
        self.targetstore=slist.getByUuid(task.attributes["destStore"])
        self.isLocal=True
        if self.targetstore==None:
            self.isLocal=False
            slist2=StoreList()
            self.targetstore=slist2.getByUuid(task.attributes["destStore"])
            if self.targetstore==None: raise Exception("Unknown destinatioin store")
        
    def run(self):
        if self.isLocal: self.localRun()
        else: raise Exception("Remote move not implemented")
    def localRun(self):
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
        move(self.srcasset,self.destdir+".tmp")
        move(self.destdir+".tmp",self.destdir)
        
