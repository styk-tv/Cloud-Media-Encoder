#!/usr/bin/python

from nodetools.tools import tools,xmlmsg
from nodetools.volume import volume
import sys
from xml.dom.minidom import getDOMImplementation


def main():
   if len(sys.argv)<3: return xmlmsg("error","Usage: prepare.py <device> <type>. Example: prepare.py /dev/sdb www")
   vol=volume(sys.argv[1])
   if vol.type<>"empty": return xmlmsg("error","Disk "+sys.argv[1]+" is not empty")
   (ok,errmsg)=vol.prepare(sys.argv[2].upper())
   if ok==False: return xmlmsg("error",errmsg)
   else:
         (ok,errmsg2)=vol.mount()
         if ok==False: return xmlmsg("error",errmsg2)
         return xmlmsg("result",errmsg)
   
 
 
if __name__=="__main__":
   main()
   