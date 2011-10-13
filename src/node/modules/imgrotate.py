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


class ImgRotateExecutor(AbstractTaskExecutor):
    requiredParams=["srcStore", "srcAssetItem", "srcAssetItemType", "encoder", "destStore", "direction"]
    optionalParams=["destAssetItem"]

    def __init__(self,reporter, workflow,task):
        super(ImgRotateExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        slist=LocalStoreList()
        dstAsset=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): dstAsset=task.attributes["destAssetItem"]

        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(dstAsset)
        if not os.path.exists(targetdir): os.makedirs(targetdir)
        self.outfile=slist.getByUuid(task.attributes["destStore"]).findAssetFile(dstAsset, self.eparams.outputtype)
        type=task.attributes["direction"]
        if type=="CCW90" or type=="CW270": self.type=Image.ROTATE_90
        elif type=="CCW180" or type=="CW180": self.type=Image.ROTATE_180
        elif type=="CCW270" or type=="CW90": self.type=Image.ROTATE_270
        elif type=="VFLIP": self.type=Image.FLIP_TOP_BOTTOM
        elif type=="HFLIP": self.type=Image.FLIP_LEFT_RIGHT
        else: raise Exception("Wrong direction")
 
    def run(self):
        img=Image.open(self.srcfile)
        img=img.transpose(self.type)
        
        img.save(self.outfile, quality=self.eparams.quality)

def pluginInfo():
    return "IMGROTATE", ImgRotateExecutor
