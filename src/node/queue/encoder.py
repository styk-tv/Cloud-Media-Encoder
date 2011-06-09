from fsqueue import FSJobManager
from queue import Process
from shutil import rmtree
import os


class Preset:
    def __init__(this, name):
        f=open(presetsdir+"/"+name+".size")
        this.fps="25"
        this.name=name
        try:
            this.size=f.readline().strip()
        finally:
            f.close()
        this.bitrates=[]
        f=open(presetsdir+"/"+name+".bitrates")
        try:
            for line in f:
                this.bitrates+=[line.strip()]
        finally:
            f.close()
        this.audiobitrate=this.bitrates[0]
        this.bitrates=this.bitrates[1:]
        print "Using preset ", name, " bitrates", this.bitrates


class FileInfo:
    dimregexp=re.compile("([\\w]+)x([\\w]+).*")
    def __init__(this, filename):
        this.fps=25
        this.width=0
        this.height=0
        this.duration=0
        this.frames=0
        
        xargs=["ffmpeg","-i",filename]
        ff=subprocess.Popen(args=xargs, executable=ffmpeg_exec, stderr=subprocess.PIPE)
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
        end=line.find(" tbr");
        if end==-1: return 0
        start=line.rfind(" ",0,end-1);
        return float(line[start+1:end])

    def computeFrames(this):
        return this.fps*this.duration
        
    def __str__(this):
        return "V: "+str(this.width)+"x"+str(this.height)+" "+str(this.duration)+"s at "+str(this.fps)+" - "+str(this.frames)+" frames"

class FFmpegHandler:
    def __init__(this, preset,  localfile,  outfile,  bitrate, frames):
        this.preset=preset
        this.infile=localfile
        this.outfile=outfile
        this.env={"FFMPEG_DATADIR" : presetsdir}
        this.bitrate=bitrate
        this.frames=frames
        this.commonargs=["ffmpeg", "-y", "-i", localfile,  "-threads", "0", "-vcodec", "libx264", "-r", this.preset.fps, "-vpre", this.preset.name, "-s", this.preset.size, "-b", bitrate]
    def pass1(this): 
        xargs=this.commonargs[:]
        xargs+=["-an", "-pass", "1", "-f", "mpegts", "/dev/null"]
        print "Starting first pass", xargs
        ff=subprocess.Popen(args=xargs, executable=ffmpeg_exec,  env=this.env, stderr=subprocess.PIPE)
        this.process(ff)
        ret=ff.wait()
        if ret!=0:
            raise Exception("FFMpeg could not process the file");
    def pass2(this):
        xargs=this.commonargs[:]
        xargs+=["-acodec", "aac", "-ac","2","-ar", "44100", "-ab",this.preset.audiobitrate, "-pass", "2", this.outfile]
        print "Starting second pass", xargs
        ff=subprocess.Popen(args=xargs, executable=ffmpeg_exec,  env=this.env, stderr=subprocess.PIPE)
        this.process(ff)
        ret=ff.wait()
        if ret!=0:
            raise Exception("FFMpeg could not process the file");
    def process(this,ff):
        buf=""
        while True:
            l=ff.stderr.read(32)
            if len(l)==0: break
            buf+=l
            while buf.find("\r")!=-1:
                i=buf.find("\r")
                ret=buf[:i-1]
                buf=buf[i+1:]
                if not ret.startswith("frame=") or this.frames==0: continue
    #            this.onProgress(int(ret[6:11].strip())/this.frames*100.0)



class EncodingProcess(Process):
  def __init__(self,jdesc,rep,workdir):
    super(EncodingProcess,self).__init__(jdesc,rep)
    self.workdir=workdir
    os.makedirs(self.workdir)
  def run(self):
    pass
  def cleanup(self):
    rmtree(self.workdir)
    

class EncodingJobManager(FSJobManager):
  def createProcess(self,jdesc):
    return EncodingProcess(jdesc,self.reporter,self.workdirs+"/"+jdesc.id)