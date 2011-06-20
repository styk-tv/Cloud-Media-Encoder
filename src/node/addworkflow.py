from xml.dom.minidom import getDOMImplementation,parse
from nodetools.config import Config
import sys

def xmlmsg(node,msg,rc=1):
    impl=getDOMImplementation()
    doc=impl.createDocument(None, node, None)
    doc.documentElement.appendChild(doc.createTextNode(msg))
    doc.writexml(sys.stdout)
    doc.unlink()
    return rc


try:
    if len(sys.argv<2): raise Exception("Usage: addworkflow.py <workflow>")
    workflow=parse(sys.argv[1])
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
