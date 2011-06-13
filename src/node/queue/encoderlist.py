from xml.dom.minidom import getDOMImplementation, parse
from config import Config
import os

def getAttributeDef(element, name, default):
    if element.hasAttribute(name): return element.getAttribute(name)
    else: return default

class EncoderParams:
  def __init__(self,element):
    self.id=element.getAttribute("guid")
    self.type=element.getAttribute("type")
    self.extraparams=getAttributeDef(element, "extraparams", "")
    self.width=getAttributeDef(element, "width", 0)
    self.height=getAttributeDef(element, "width", 0)
    self.bitrate=getAttributeDef(element, "bitrate", 1000000)
    self.fps=getAttributeDef(element, "fps",0)
    self.audiobitrate=getAttributeDef(element, "audiobitrate", 64000)
    self.vcodec=getAttributeDef(element, "vcodec", "libx264")
    self.acodec=getAttributeDef(element, "acodec", "aac")
    self.outputtype=getAttributeDef(element, "outputType", "mp4")
    
class EncodersList(object):
  def __init__(self, path=Config.CONFIGDIR+"/Encoders.xml"):
    dom=parse(open(path,'r'))
    self.encoders={}
    for elm in dom.getElementsByTagName("encoder"): 
      encoder=EncoderParams(elm)
      self.encoders[encoder.id]=encoder
      
  def getByUuid(self,uuid):
    if self.encoders.has_key(uuid):  return self.encoders[uuid]
    else: return None
