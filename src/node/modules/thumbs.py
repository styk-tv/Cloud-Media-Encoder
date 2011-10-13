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
from nodetools.ffmpeg import FFmpegHandler, FileInfo
from nodetools.piltools import *
from shutil import rmtree
import os
import re
import subprocess
import daemon
import sys
import Image
import ImageDraw


class ThumbFFmpegHandler(FFmpegHandler):
    FAST_SEEK_THRESHOLD=15
    def __init__(self, eparams ,  localfile,  outfile, frames, width, height, seek, interval):
        super(ThumbFFmpegHandler, self).__init__(eparams, localfile, outfile, frames, None)
        if interval>ThumbFFmpegHandler.FAST_SEEK_THRESHOLD: 
            self.commonargs=self.commonargs[:2]+["-ss", str(seek)]+self.commonargs[2:]
        else: 
            self.commonargs+=["-ss", str(seek)]
        self.commonargs+=[ "-s", str(width)+"x"+str(height), "-qscale","3","-vframes","1"]
        if len(eparams.extraparams)>0: this.commonargs+=eparams.extraparams.split(" ")


class ThumbsExecutor(AbstractTaskExecutor):
    requiredParams=["srcStore", "srcAssetItem", "srcAssetItemType", "encoder", "destStore"]
    optionalParams=["destAssetItem"]
    
    def __init__(self,reporter, workflow,task):
        super(ThumbsExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        if self.eparams.type<>"ffmpeg_0612": raise Exception("Unknown encoder type "+self.eparams.type)
        slist=LocalStoreList()
        self.frames=1
        self.destAsset=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): self.destAsset=task.attributes["destAssetItem"]
        
        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        self.targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(self.destAsset)
        if not os.path.exists(self.targetdir): os.makedirs(self.targetdir)
        
    def progressCb(self, progress):
        pass
 
    def makeBorderF(self, file):
        img=Image.open(file)
        img=makeBorder(self.eparams, img)
        img.save(file, quality=80, optimize=True)
        
    def makeSquareF(self, file):
        img=Image.open(file)
        img=makeSquare(img)
        img.save(file, quality=80, optimize=True)

    def run(self):
        fi=FileInfo(self.srcfile)
        self.frames=fi.frames
        (w, h)=computeSize(self.eparams, fi.aspect)
        
        nr=0
        point=0.0
        ival=self.eparams.thumbsInterval
        if ival==0: ival=float(fi.duration+1.0)/self.eparams.thumbsCount
        if ival==0: raise Exception("Wrong thumbs interval")
        while True:
            outfile=self.targetdir+"/th_"+self.destAsset+"_"+str(nr)+"."+self.eparams.outputtype
            fmpg=ThumbFFmpegHandler(self.eparams,   self.srcfile, outfile,  fi.frames, w, h, point,  ival)
            fmpg.run()
            if self.eparams.square: self.makeSquareF( outfile)
            if self.eparams.borderWidth>0: self.makeBorderF( outfile)
            point+=ival
            nr+=1
            if point>=fi.duration: break
        
def pluginInfo():
    return "THUMBS", ThumbsExecutor
