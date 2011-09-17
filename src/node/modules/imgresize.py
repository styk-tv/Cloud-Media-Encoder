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
from nodetools.abstractqueue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from nodetools.config import Config
from nodetools.piltools import *
import Image
import os


class ImgResizeExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(ImgResizeExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        if self.eparams.type<>"PIL":  raise Exception("Unknown encoder type "+self.eparams.type)
        slist=LocalStoreList()
        self.frames=1
        dstAsset=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): dstAsset=task.attributes["destAssetItem"]

        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(dstAsset)
        if not os.path.exists(targetdir): os.makedirs(targetdir)
        self.outfile=slist.getByUuid(task.attributes["destStore"]).findAssetFile(dstAsset, self.eparams.outputtype)
        self.watermarkFile=None
        
        if self.eparams.watermarkFile<>"":
            self.watermarkFile=Config.CONFIGDIR+"/"+self.eparams.watermarkFile
        elif self.eparams.watermarkAsset<>"":
            slist=LocalStoreList()
            store=slist.getByUuid(self.eparams.watermarkStore)
            self.watermarkFile=store.findAssetFile(self.eparams.watermarkAsset, self.eparams.watermarkAssetType)
 
    def run(self):
        img=Image.open(self.srcfile)
        
        newsize=computeSize(self.eparams, float(img.size[0])/float(img.size[1]))
        img=img.resize(newsize, Image.BICUBIC)
        if self.eparams.square: img=makeSquare(img)
        if self.eparams.borderWidth>0: img=makeBorder( self.eparams, img)
        if self.watermarkFile<>None:
            wmark=Image.open(self.watermarkFile)
            (wx, wy)=computeWatermarkPosition(self.eparams,  wmark.size,  img.size)
            img=composite(img, wmark,  (wx, wy))
        img.save(self.outfile, quality=self.eparams.quality)

def pluginInfo():
    return "IMGRESIZE", ImgResizeExecutor
