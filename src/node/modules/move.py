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
from nodetools.localstores import LocalStoreList
from nodetools.storelist import StoreList
from nodetools.tools import tools
from shutil import move, rmtree, copy
from os import rename, listdir,  makedirs,stat
from os.path import dirname, exists, split, abspath
import paramiko
import errno
import logging
from nodetools.config import Config

PRIVKEY="/home/"+Config.USER+"/.ssh/id_rsa"
REMUSER=Config.USER


def sftp_exists(path, sftp):
    try:
        sftp.stat(path)
        return True
    except IOError, e:
        if e.errno==errno.ENOENT: return False
        raise

def sftp_makedirs(name, sftp):
    if sftp_exists(name, sftp): return
    head, tail = split(name)
    if not tail:
        head, tail = split(head)
    if head and tail and not sftp_exists(head, sftp):
        try:
            sftp_makedirs(head, sftp)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
    sftp.mkdir(name)


class CopyMoveExecutor(AbstractTaskExecutor):
    requiredParams=["srcStore", "srcAssetItem",  "destStore"]
    optionalParams=["destAssetItem"]
    supportsRemoteDestination=True
    def __init__(self,reporter, workflow,task, move):
        super(CopyMoveExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.move=move
        self.srcassetuid=task.attributes["srcAssetItem"]
        self.dstassetuid=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): self.dstassetuid=task.attributes["destAssetItem"]
        self.overwrite=False
        if task.attributes.has_key("overwrite"): self.overwrite=(task.attributes["overwrite"].lower()=="true")

        self.srcasset=slist.getByUuid(task.attributes["srcStore"]).findAsset(task.attributes["srcAssetItem"])
        self.targetstore=slist.getByUuid(task.attributes["destStore"])
        self.isLocal=True
        if self.targetstore==None:
            self.isLocal=False
            slist2=StoreList()
            self.targetstore=slist2.getByUuid(task.attributes["destStore"])
            if self.targetstore==None: raise Exception("Unknown destination store")
            self.desthost=slist2.getDisk(self.targetstore.diskuuid).host
        
    def run(self):
        if self.isLocal: self.localRun()
        else: self.remoteRun()
        
        
        
    def localRun(self):
	logging.debug("Will copy local asset %s to local asset %s",self.srcassetuid,self.dstassetuid)
        self.destdir=self.targetstore.findAsset(self.dstassetuid)

        if exists(self.destdir):
    	    logging.debug("Destination asset exists")
    	    if self.overwrite:
    		rmtree(self.destdir)
    		logging.debug("Overwriting with source")
    	    else: return
    	    
        makedirs(self.destdir+".tmp")
        for f in listdir(self.srcasset):
            df=f.replace(self.srcassetuid, self.dstassetuid)
            if self.move: move(abspath(self.srcasset)+"/"+f, abspath(self.destdir)+".tmp/"+df)
            else: copy(abspath(self.srcasset)+"/"+f, abspath(self.destdir)+".tmp/"+df)

        rename(self.destdir+".tmp",self.destdir)
    def remoteRun(self):
	logging.debug("Will copy local asset %s to remote asset %s",self.srcassetuid,self.dstassetuid)
        key = paramiko.RSAKey.from_private_key_file(PRIVKEY)
        transport = paramiko.Transport(self.desthost)
        transport.start_client()
        transport.auth_publickey(REMUSER,  key)
#        sftp=transport.open_session()
        sftp = paramiko.SFTPClient.from_transport(transport)
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
        if sftp_exists(self.destdir,sftp):
    	    logging.debug("Destination asset exists")
    	    if self.overwrite: raise Exception("Cannot overwrite remote asset")
    	    else: return
        sftp_makedirs(self.destdir+".tmp", sftp)
        files=listdir(self.srcasset)
        i=0.0
        for f in files:
            sftp.put(self.srcasset+"/"+f, self.destdir+".tmp/"+f.replace(self.srcassetuid, self.dstassetuid))
            i=i+1
            self.updateProgress(i/len(files)*99)
        sftp.rename(self.destdir+".tmp", self.destdir)
        transport.close()
        if self.move: rmtree(self.srcasset)
        
class MoveExecutor(CopyMoveExecutor):
    def __init__(self,reporter, workflow,task):
        super(MoveExecutor, self).__init__(reporter, workflow, task, True)


class CopyExecutor(CopyMoveExecutor):
    def __init__(self,reporter, workflow,task):
        super(CopyExecutor, self).__init__(reporter, workflow, task,False)
    


def pluginInfo():
    return [ ("MOVE", MoveExecutor),  ("COPY", CopyExecutor) ]
