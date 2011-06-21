import psutil
from xml.dom.minidom import getDOMImplementation
from nodetools.xmlqueue import XMLJobManager
from nodetools.tools import xmlmsg
import sys
from time import sleep

def printStatus(out):
    jman=XMLJobManager()
    doc=jman.load()
    currenttask=None
    for wfnode in doc.getElementsByTagName("workflow"):
        if wfnode.getAttribute("status")=="1":
            for tasknode in wfnode.getElementsByTagName("task"):
                if tasknode.getAttribute("status")=="1":
                    currenttask=tasknode
                    currenttask.name="currenttask"
                    break
    
    doc=getDOMImplementation().createDocument(None, "status", None)
    if currenttask<>None: doc.documentElement.appendChild(currenttask)
    mem=doc.createElement("memory")
    mem.setAttribute("total_physical", str(psutil.TOTAL_PHYMEM))
    mem.setAttribute("avail_physical", str(psutil.avail_phymem()))
    mem.setAttribute("total_virtual", str(psutil.total_virtmem()))
    mem.setAttribute("avail_virtual", str(psutil.avail_virtmem()))
    doc.documentElement.appendChild(mem)
    cpu=doc.createElement("cpu")
    cpu.setAttribute("usage", str(psutil.cpu_percent(1)))
    doc.documentElement.appendChild(cpu)
    doc.writexml(out)

def main():
    while True:
        printStatus(sys.stdout)
        sys.stdout.write("\n")
        sleep(10)

main()
