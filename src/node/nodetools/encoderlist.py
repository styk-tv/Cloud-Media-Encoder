##
## This file is part of the Styk.TV API project.
##
## Copyright (c) 2011 Piotr Styk (peter@styk.tv)
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License version 2 
## as published by  the Free Software Foundation
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
##


from xml.dom.minidom import getDOMImplementation, parse
from config import Config
import os
from uuid import uuid4

def getAttributeDef(element, name, default):
    if element.hasAttribute(name): return element.getAttribute(name)
    else: return default

class EncoderParamsBase(object):
  def __init__(self,element):
    self.id=element.getAttribute("guid")
    self.element=element
    self.type=element.getAttribute("type")
    self.width=int(getAttributeDef(element, "width", 0))
    self.height=int(getAttributeDef(element, "height", 0))
    self.extraparams=getAttributeDef(element, "extraparams", "")
    self.outputtype=getAttributeDef(element, "outputType", "mp4")

class EncoderParams(EncoderParamsBase):
  def __init__(self, element):
    super(EncoderParams, self).__init__(element)
    self.bitrate=getAttributeDef(element, "bitrate", 1000000)
    self.fps=getAttributeDef(element, "fps",0)
    self.watermarkFile=getAttributeDef(element, "watermarkFile", "")
    self.watermarkX=int(getAttributeDef(element, "watermarkX", 0))
    self.watermarkY=int(getAttributeDef(element, "watermarkY", 0))
    self.watermarkAsset=getAttributeDef(element, "watermarkAssetItem", "")
    self.watermarkStore=getAttributeDef(element, "watermarkStore", "")
    self.watermarkAssetType=getAttributeDef(element, "watermarkAssetItemType", "")
    self.watermarkStart=float(getAttributeDef(element, "watermarkStart", "0"))
    self.audiobitrate=getAttributeDef(element, "audiobitrate", 64000)
    self.vcodec=getAttributeDef(element, "vcodec", "libx264")
    self.acodec=getAttributeDef(element, "acodec", "aac")
class ThumbnailerParams(EncoderParamsBase):
  def __init__(self, element):
    super(ThumbnailerParams, self).__init__(element)
    self.thumbsCount=int(getAttributeDef(element, "thCount", "0"))
    self.thumbsInterval=float(getAttributeDef(element, "thInterval","0"))
    self.borderWidth=int(getAttributeDef(element, "borderWidth","0"))
    self.borderColor=getAttributeDef(element, "borderColor", "#808080")
    self.borderRadius=int(getAttributeDef(element, "borderRadius", "0"))
    self.backgroundColor=getAttributeDef(element, "backgroundColor", "#00000000")
    self.square=getAttributeDef(element, "square", "0")<>"0"

class ImageTransform(EncoderParamsBase):
  def __init__(self, element):
    super(ImageTransform, self).__init__(element)
    self.watermarkFile=getAttributeDef(element, "watermarkFile", "")
    self.watermarkX=getAttributeDef(element, "watermarkX", 0)
    self.watermarkY=getAttributeDef(element, "watermarkY", 0)
    self.watermarkAsset=getAttributeDef(element, "watermarkAssetItem", "")
    self.watermarkStore=getAttributeDef(element, "watermarkStore", "")
    self.watermarkAssetType=getAttributeDef(element, "watermarkAssetItemType", "")
    self.borderWidth=int(getAttributeDef(element, "borderWidth","0"))
    self.quality=int(getAttributeDef(element, "quality", "80"))
    self.borderColor=getAttributeDef(element, "borderColor", "#808080")
    self.borderRadius=int(getAttributeDef(element, "borderRadius", "0"))
    self.backgroundColor=getAttributeDef(element, "backgroundColor", "#00000000")
    self.square=getAttributeDef(element, "square", "0")<>"0"
    self.watermarkAnchor=getAttributeDef(element, "watermarkAnchor", "00")
    
class EncodersList(object):
  def __init__(self, path=Config.CONFIGDIR+"/Encoders.xml"):
    if os.path.exists(path):
        with open(path,'r') as f: self.doc=parse(f)
    else: self.doc=getDOMImplementation().createDocument(None, "encoders", None)
    self.target=path
    self.encoders={}
    for elm in self.doc.getElementsByTagName("encoder"): 
      encoder=EncoderParams(elm)
      self.encoders[encoder.id]=encoder
    for elm in self.doc.getElementsByTagName("thumbs"): 
      encoder=ThumbnailerParams(elm)
      self.encoders[encoder.id]=encoder
    for elm in self.doc.getElementsByTagName("image"): 
      encoder=ImageTransform(elm)
      self.encoders[encoder.id]=encoder

 
  def save(self):
    with open(self.target, "w") as f: self.doc.writexml(f)
 
  def getByUuid(self,uuid):
    if self.encoders.has_key(uuid):  return self.encoders[uuid]
    else: return None

  def write(self, out):
      self.doc.writexml(out)

  def remove(self, uuid):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown encoder")
    store.element.parentNode.removeChild(store.element)
    self.save()
    return "OK"

  def create(self, indoc):
    elm=parse(indoc).documentElement
    if not elm.hasAttribute("guid"): elm.setAttribute("guid",  uuid4().get_hex())
    if elm.nodeName=="encoder": ep=EncoderParams(elm)
    elif elm.nodeName=="thumbs":  ep=ThumbnailerParams(elm)
    else: raise Exception("Wrong format")
    ep=EncoderParams(elm)
    if ep.type<>"ffmpeg_0612": raise Exception("Unknown encoder type")
    self.doc.documentElement.appendChild(elm)
    self.save()
    return ep.id

  def writeTypes(self, out):
      doc=getDOMImplementation().createDocument(None, "EncoderTypes", None)
      elm=doc.createElement("encoderType");
      elm.setAttribute("name", "ffmpeg_0612")
      doc.documentElement.appendChild(elm)
      doc.writexml(out)
  
