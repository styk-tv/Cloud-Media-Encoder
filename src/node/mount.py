#!/usr/bin/python

from nodetools.tools import tools,xmlmsg
from nodetools.volume import volume
import sys
from xml.dom.minidom import getDOMImplementation


def main():
   if len(sys.argv)<2: return xmlmsg("error","Usage: mount.py <device>. Example: mount.py /dev/sdc")
   vol=volume(sys.argv[1])
   if vol.type<>"www": return xmlmsg("error","Disk "+sys.argv[1]+" is of unknown type")
   (ok,errmsg)=vol.mount()
   if ok==False: return xmlmsg("error",str(errmsg))
   else: return xmlmsg("result",str(errmsg))
   
   
 
 
if __name__=="__main__":
   main()
   