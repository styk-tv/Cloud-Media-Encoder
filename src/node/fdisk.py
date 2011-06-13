#!/usr/bin/python

import re
from xml.dom.minidom import getDOMImplementation
import sys
from nodetools.tools import tools
from nodetools.volume import volume

class partition:
  partre=re.compile("([^\s]+)\s([^\d]*)(\d+)[\s]*(\d+)[\s]*([\d]+\+?)[\s]*(\d+)[\s]*(.*)")
  def __init__(self,line):
    match=partition.partre.match(line)
    self.device=match.group(1)
    self.boot="false"
    if match.group(2).find("*")>-1: self.boot="true"
    self.start=match.group(3)
    self.end=match.group(4)
    self.blocks=match.group(5)
    self.id=match.group(6)
    self.system=match.group(7)

  @staticmethod
  def canParse(line):
     return partition.partre.match(line)<>None
  def storeDOM(self,doc):
    elm=doc.createElement("partition")
    elm.setAttribute("device",self.device)
    elm.setAttribute("blocks",self.blocks)
    elm.setAttribute("boot",self.boot)
    elm.setAttribute("id",self.id)
    elm.setAttribute("system",self.system)
    elm.setAttribute("start",self.start)
    elm.setAttribute("end",self.end)
    return elm
    

#  Disk can be either:
#	- empty: no partitions, no volume created. Disk is considered ready to create volume
#	- other: there are partitions or there is volume with wrong type or label: the disk is used for something else, don't touch
#	- storage nodes: a disk with no partitions, but ext4 volume on whole device and label starting with TXSTUDIO-DATA-[storage type]

class disk:
  diskre=re.compile("Disk (.+?): .*?, (\d*) bytes")
  diskid=re.compile("Disk identifier: (.*)")
  def __init__(self,line):
    self.partitions=[]
    match=self.diskre.match(line)
    self.device=match.group(1)
    self.bytes=match.group(2)
    self.diskId=""
    self.vol=volume(self.device)
    
  @staticmethod
  def canParse(line):
    return disk.diskre.match(line)<>None
    
  def parseLine(self,line):
    if (partition.canParse(line)): self.partitions.append(partition(line))
    elif self.diskId=="":
      match=disk.diskid.match(line)
      if match<>None: self.diskId=match.group(1)
      
    
  def storeDOM(self,doc):
    elm=doc.createElement("disk")
    elm.setAttribute("device",self.device)
    elm.setAttribute("bytes",self.bytes)
    elm.setAttribute("diskId",self.diskId)
    elm.setAttribute("type",self.vol.type)
    if self.vol.uuid<>None: elm.setAttribute("uuid",self.vol.uuid)
    for partition in self.partitions: elm.appendChild(partition.storeDOM(doc))
    return elm
    

class volumelist:
  def __init__(self):
    self.disks=[]
    text=tools.listAll()
    itr=text.splitlines().__iter__();
    current=None
    for line in text.splitlines():
	if disk.canParse(line):
	  current=disk(line)
	  self.disks.append(current)
	elif current<>None: current.parseLine(line)

  def write(self,out):
    impl=getDOMImplementation()
    doc=impl.createDocument(None, "fdisk", None)
    for xdisk in self.disks:
      doc.documentElement.appendChild(xdisk.storeDOM(doc))
    doc.writexml(out)
    doc.unlink()

    

def main():
   out=volumelist()
   out.write(sys.stdout)
 
 
if __name__=="__main__":
   main()
   
