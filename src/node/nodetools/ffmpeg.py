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
from shutil import rmtree
import os
import re
import subprocess
import daemon
import sys



class FileInfo:
    dimregexp=re.compile("([\\w]+)x([\\w]+).*")
    def __init__(this, filename):
        this.fps=25
        this.width=0
        this.height=0
        this.duration=0
        this.frames=0
        this.aspect=1
        
        xargs=["ffmpeg","-i",filename]
        ff=subprocess.Popen(args=xargs, executable="ffmpeg", stderr=subprocess.PIPE)
        while ff.returncode==None:
            out=ff.communicate()[1]
            for ret in out.splitlines():
                if ret.startswith("  Duration:"): this.duration=this.parseDuration(ret)
                if ret.find("Stream #0")!=-1 and ret.find("Video")!=-1:
                    (this.width, this.height)=this.parseSize(ret)
                    this.aspect=float(this.width)/float(this.height)
                    this.fps=this.parseFps(ret)
                    this.frames=this.computeFrames()
        ff.wait()
    def parseSize(this,line):
        for token in line.split(","):
            m=FileInfo.dimregexp.match(token.strip())
            if m==None: continue
            return (int(m.group(1)),int(m.group(2)))

    def parseDuration(this,line):
        d=line[12:11+12]
        seconds=int(d[0:2])*3600+int(d[3:5])*60+int(d[6:8])+float(d[9:11])/100
        return seconds

    def parseFps(this,line):
        end=line.find(" fps");
        if end==-1: return 0
        start=line.rfind(" ",0,end-1);
        return float(line[start+1:end])

    def computeFrames(this):
        return int(this.fps*this.duration)
        
    def __str__(this):
        return "V: "+str(this.width)+"x"+str(this.height)+" "+str(this.duration)+"s at "+str(this.fps)+" - "+str(this.frames)+" frames"

class FFmpegHandler(object):
    def __init__(this, eparams ,  localfile,  outfile, frames, progressCb):
        this.eparams=eparams
        this.progressCb=progressCb
        this.infile=localfile
        this.outfile=outfile
        this.frames=frames
        this.commonargs=["ffmpeg", "-y", "-i", localfile]
    def run(this):
        xargs=this.commonargs[:]+[this.outfile]
        print xargs
        ff=subprocess.Popen(args=xargs, executable="ffmpeg" )#,   stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        ret=ff.wait()
        if ret!=0:
            raise Exception("FFMpeg could not process the file");
    def process(this,ff):
        buf=""
        while True:
            l=ff.stdout.read(32)
            if len(l)==0: break
            buf+=l
            print l
            while buf.find("\r")!=-1:
                i=buf.find("\r")
                ret=buf[:i-1]
                buf=buf[i+1:]
                if not ret.startswith("frame=") or this.frames==0: continue
                this.progressCb(int(ret[6:11].strip()))

class VideoFFmpegHandler(FFmpegHandler):
    def __init__(this, eparams ,  localfile,  outfile, frames, progressCb):
        super(VideoFFmpegHandler, this).__init__(eparams, localfile, outfile, frames, progressCb)
        this.commonargs+=[ "-vcodec", this.eparams.vcodec]
        if len(eparams.extraparams)>0: this.commonargs+=eparams.extraparams.split(" ")
        if this.eparams.fps>0: this.commonargs+=["-r", str(this.eparams.fps)]
        if this.eparams.width>0 and this.eparams.height>0: this.commonargs+=["-s", str(this.eparams.width)+"x"+str(this.eparams.height)]
        this.commonargs+=[ "-b", str(this.eparams.bitrate)]
        this.commonargs+=["-acodec", this.eparams.acodec, "-ac","2","-ar", "44100", "-ab",str(this.eparams.audiobitrate)]
