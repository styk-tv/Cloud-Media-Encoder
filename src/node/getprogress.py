from nodetools.xmlqueue import XMLJobManager
from nodetools.tools import xmlmsg
import sys


def main():
  try:
    jman=XMLJobManager()
    doc=jman.load()
    for wfnode in doc.getElementsByTagName("workflow"):
        while wfnode.firstChild<>None: wfnode.removeChild(wfnode.firstChild)
    doc.writexml(sys.stdout)
    
  except Exception,  e:
      return xmlmsg("error", str(e))
  
if __name__=="__main__":
  main()
