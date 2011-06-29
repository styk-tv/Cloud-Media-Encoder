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
from nodetools.queue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from nodetools.ffmpeg import FFmpegHandler, FileInfo
from shutil import rmtree
import os
import re
import subprocess
import daemon
import sys


class ThumbFFmpegHandler(FFmpegHandler):
    def __init__(self, eparams ,  localfile,  outfile, frames, width, height, seek):
        super(ThumbFFmpegHandler, self).__init__(eparams, localfile, outfile, frames, None)
        self.commonargs+=["-ss", str(seek), "-s", str(width)+"x"+str(height), "-qscale","3","-vframes","1"]
        if len(eparams.extraparams)>0: this.commonargs+=eparams.extraparams.split(" ")


class ThumbsExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(ThumbsExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        if self.eparams.type<>"ffmpeg": raise Exception("Unknown encoder type "+self.eparams.type)
        slist=LocalStoreList()
        self.frames=1
        
        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        self.targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(task.attributes["srcAssetItem"])
        if not os.path.exists(self.targetdir): os.makedirs(self.targetdir)
        
    def progressCb(self, progress):
        pass
    def computeSize(self, fi):
        origratio=fi.aspect
        w=self.eparams.width
        h=self.eparams.height
        newratio=float(w)/float(h)
        if origratio<newratio: w=int(h*origratio)
        else: h=int(w/origratio)
        return (w, h)

        
    def run(self):
        fi=FileInfo(self.srcfile)
        self.frames=fi.frames
        (w, h)=self.computeSize(fi)
        
        nr=0
        point=0.0
        ival=self.eparams.thumbsInterval
        if ival==0: ival=float(fi.duration+1.0)/self.eparams.thumbsCount
        if ival==0: raise Exception("Wrong thumbs interval")
        while True:
            outfile=self.targetdir+"/th_"+self.task.attributes["srcAssetItem"]+"_"+str(nr)+"."+self.eparams.outputtype
            fmpg=ThumbFFmpegHandler(self.eparams,   self.srcfile, outfile,  fi.frames, w, h, point)
            fmpg.run()
            point+=ival
            nr+=1
            if point>=fi.duration: break
        
def pluginInfo():
    return "THUMBS", ThumbsExecutor
