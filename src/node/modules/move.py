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


from nodetools.xmlqueue import XMLJobManager
from nodetools.abstractqueue import AbstractTaskExecutor,Queue
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from nodetools.storelist import StoreList
from shutil import move
from os import rename, makedirs
from os.path import dirname, exists
import paramiko
from nodetools.config import Config

PRIVKEY="/home"+Config.USER+"/.ssh/id_rsa"

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
        else: self.remoteRun()
    def localRun(self):
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
        if not exists(dirname(self.destdir)): makedirs(dirname(self.destdir))
        move(self.srcasset,self.destdir+".tmp")
        rename(self.destdir+".tmp",self.destdir)
    def remoteRun(self):
        key = paramiko.RSAKey.from_private_key_file(PRIVKEY)
        transport = paramiko.Transport(self.targetstore.host)
        transport.start_client()
        transport.auth_publickey(Config.USER,  key)
        sftp=transport.open_session()
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
        sftp.mkdir(self.destdir+".tmp")
        for f in os.listdir(self.srcasset):
            sftp.put(self.srcasset+"/"+f, f)
        # FIXME: progress
        sftp.rename(self.destdir+".tmp", self.destdir)
        
        
        

def pluginInfo():
    return "MOVE", MoveExecutor
