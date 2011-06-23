#!/usr/bin/python


from xml.dom.minidom import getDOMImplementation,parse
from nodetools.config import Config, xmlmsg
import sys

try:
    workflow=parse(sys.stdin)
    if workflow.documentElement.tagName<>"workflow": raise Exception("Root tag should be workflow")
    guid=workflow.documentElement.getAttribute("guid")
    doc=parse(open(Config.QUEUEDIR+"/Queue.xml","r"))
    doc.documentElement.appendChild(workflow.documentElement)
    doc.documentElement.setAttribute("dateStart", "")
    doc.documentElement.setAttribute("dateFinished", "")
    doc.writexml(open(Config.QUEUEDIR+"/Queue.xml","w"))
    xmlmsg("result", guid)
except Exception, e:
    xmlmsg("error", str(e))
