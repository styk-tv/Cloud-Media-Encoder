from nodetools.xmlqueue import XMLJobManager
from nodetools.queue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.encoderlist import EncodersList
from nodetools.localstores import LocalStoreList
from nodetools.move import MoveExecutor
from nodetools.drm import EncryptExecutor
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
        
        xargs=["ffmpeg","-i",filename]
        ff=subprocess.Popen(args=xargs, executable="ffmpeg", stderr=subprocess.PIPE)
        while ff.returncode==None:
            out=ff.communicate()[1]
            for ret in out.splitlines():
                if ret.startswith("  Duration:"): this.duration=this.parseDuration(ret)
                if ret.find("Stream #0")!=-1 and ret.find("Video")!=-1:
                    (this.width, this.height)=this.parseSize(ret)
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

class FFmpegHandler:
    def __init__(this, eparams ,  localfile,  outfile, frames, progressCb):
        this.eparams=eparams
        this.progressCb=progressCb
        this.infile=localfile
        this.outfile=outfile
    #    this.env={"FFMPEG_DATADIR" : presetsdir}
        this.frames=frames
        this.commonargs=["ffmpeg", "-y", "-i", localfile]
        this.commonargs+=[ "-vcodec", this.eparams.vcodec]
        if len(eparams.extraparams)>0: this.commonargs+=eparams.extraparams.split(" ")
        if this.eparams.fps>0: this.commonargs+=["-r", this.eparams.fps]
        if this.eparams.width>0 and this.eparams.height>0: this.commonargs+=["-s", this.eparams.width+"x"+this.eparams.height]
        this.commonargs+=[ "-b", this.eparams.bitrate]
    def run(this):
        xargs=this.commonargs[:]
        xargs+=["-acodec", this.eparams.acodec, "-ac","2","-ar", "44100", "-ab",this.eparams.audiobitrate,  this.outfile]
        print "Starting second pass", xargs
        ff=subprocess.Popen(args=xargs, executable="ffmpeg" )#,   stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#        this.process(ff)
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

class EncoderExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(EncoderExecutor, self).__init__(reporter, workflow, task)
        elist=EncodersList()
        self.eparams=elist.getByUuid(task.attributes["encoder"]) 
        if self.eparams==None: raise Exception("No encoder with guid "+task.attributes["encoder"])
        if self.eparams.type<>"ffmpeg": raise Exception("Unknown encoder type "+self.eparams.type)
        slist=LocalStoreList()
        self.frames=1
        
        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(task.attributes["srcAssetItem"])
        if not os.path.exists(targetdir): os.makedirs(targetdir)
        self.outfile=slist.getByUuid(task.attributes["destStore"]).findAssetFile(task.attributes["srcAssetItem"], self.eparams.outputtype)
        
    def progressCb(self, progress):
        self.reporter.setQueueProperty(self.workflow, self.task, "frame", str(progress))
        self.reporter.setQueueProperty(self.workflow, self.task, "progress", str(progress*100.0/self.frames))
    def run(self):
        fi=FileInfo(self.srcfile)
        self.frames=fi.frames
        self.reporter.setQueueProperty(self.workflow, self.task, "all_frames", str(fi.frames))
        
        #FIXME: progress!
        fmpg=FFmpegHandler(self.eparams,   self.srcfile, self.outfile,  fi.frames, self.progressCb)
        fmpg.run()
        
def main():
  jman=XMLJobManager()
  jman.registerExecutor("ENCODE",  EncoderExecutor)
  jman.registerExecutor("MOVE", MoveExecutor)
  jman.registerExecutor("ENCRYPT", EncryptExecutor)
  queue=Queue(jman)
  queue.run()

if len(sys.argv)>1 and sys.argv[1]=="-d": main()
else: 
    with daemon.DaemonContext():
	main()
