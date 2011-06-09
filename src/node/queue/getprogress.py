from xml.dom.minidom import getDOMImplementation, parse
import os
from tools import xmlmsg
import sys


def main():
  defaultdir="encroot"
  if len(sys.argv)>1: defaultdir=sys.argv[1]
  if not os.path.exists(defaultdir+"/status") or not os.path.exists(defaultdir+"/queue"):  return xmlmsg("error","Wrong directory "+defaultdir)

  waiting=len(os.listdir(defaultdir+"/queue"))-2
  current=None

  cfile=defaultdir+"/status/current.xml"
  if os.path.exists(cfile):
    current_doc=parse(open(cfile,'r'))
    curid=os.readlink(cfile)
    current=current_doc.documentElement
    current.tagName="current"

  impl=getDOMImplementation()
  doc=impl.createDocument(None, "queue", None)
  doc.documentElement.setAttribute("waiting",str(waiting))
  if current<>None:
    current.setAttribute("id",str(curid))
    doc.documentElement.appendChild(current)

  doc.writexml(sys.stdout)
  
if __name__=="__main__":
  main()