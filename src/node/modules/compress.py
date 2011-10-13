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
from nodetools.tools import tools
from os import rename, listdir,  makedirs
from os.path import dirname, exists, split, abspath

from zipfile import ZipFile

class ZipExecutor(AbstractTaskExecutor):
    requiredParams=["srcStore", "srcAssetItem",  "destStore"]
    optionalParams=["destAssetItem"]
    def __init__(self,reporter, workflow,task):
        super(ZipExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.srcassetuid=task.attributes["srcAssetItem"]
        self.dstassetuid=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): self.dstassetuid=task.attributes["destAssetItem"]

        self.srcasset=slist.getByUuid(task.attributes["srcStore"]).findAsset(task.attributes["srcAssetItem"])
        targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(self.dstassetuid)
        if not exists(targetdir): os.makedirs(targetdir)
        self.outfile=slist.getByUuid(task.attributes["destStore"]).findAssetFile(self.dstassetuid, "zip")
        
    def run(self):
        with ZipFile(self.outfile, "a") as zip:
          files=listdir(self.srcasset)
          i=0.0
          for f in files:
            zip.write(self.srcasset+"/"+f, f)
            i=i+1
            self.updateProgress(i/len(files)*99)
            

def pluginInfo():
    return "COMPRESS", ZipExecutor
