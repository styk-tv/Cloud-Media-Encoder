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
from nodetools.ffmpeg import VideoFFmpegHandler, FileInfo
from shutil import rmtree
import os
import re
import subprocess
import daemon
import sys



class EncoderExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(EncoderExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        if self.eparams.type<>"ffmpeg_0612": raise Exception("Unknown encoder type "+self.eparams.type)
        slist=LocalStoreList()
        self.frames=1
        
        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(task.attributes["srcAssetItem"])
        if not os.path.exists(targetdir): os.makedirs(targetdir)
        self.outfile=slist.getByUuid(task.attributes["destStore"]).findAssetFile(task.attributes["destAssetItem"], self.eparams.outputtype)
        
    def progressCb(self, progress):
        self.reporter.setQueueProperty(self.workflow, self.task, "frame", str(progress))
        self.reporter.setQueueProperty(self.workflow, self.task, "progress", str(progress*100.0/self.frames))
    def run(self):
        fi=FileInfo(self.srcfile)
        self.frames=fi.frames
        self.reporter.setQueueProperty(self.workflow, self.task, "all_frames", str(fi.frames))
        
        #FIXME: progress!
        fmpg=VideoFFmpegHandler(self.eparams,   self.srcfile, self.outfile,  fi.frames, self.progressCb)
        fmpg.run()
        
def pluginInfo():
    return "ENCODE", EncoderExecutor
