import subprocess
from xml.dom.minidom import getDOMImplementation
import sys

def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return (retcode,output,unused_err)
    

def xmlmsg(node,msg,rc=1):
    impl=getDOMImplementation()
    doc=impl.createDocument(None, node, None)
    doc.documentElement.appendChild(doc.createTextNode(msg))
    doc.writexml(sys.stdout)
    doc.unlink()
    return rc


class tools:
  def __init__(self):
    pass
  @staticmethod
  def listAll():
    return check_output(["/sbin/fdisk","-lu"],env={ "LC_ALL" : "C"} )[1]
    
  @staticmethod
  def hasPartitions(dev):
    (code,ret,err)=check_output(["/sbin/fdisk","-lu",dev],env={ "LC_ALL" : "C"} )
    return ret.find("Device Boot")>-1
 
  @staticmethod
  def getId(dev):
    lines=check_output(["/sbin/blkid","-o","export",dev],env={"LC_ALL" : "C"} )[1].splitlines()
    ret={}
    for line in lines:
      (k,s,v)=line.partition("=")
      ret[k]=v
    return ret
  @staticmethod
  def makeFs(dev,type):
    (retcode,output,err)=check_output(["/sbin/mkfs.ext4","-F",dev,"-L","TX-DATA-"+type],env={"LC_ALL" : "C"} )
    return (retcode,err)
  @staticmethod
  def mount(dev,path):
    (retcode,output,err)=check_output(["/bin/mount",dev,path],env={"LC_ALL" : "C"} )
    return (retcode,err)
    

    