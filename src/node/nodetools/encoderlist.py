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

class EncoderParams:
  def __init__(self,element):
    self.id=element.getAttribute("guid")
    self.element=element
    self.type=element.getAttribute("type")
    self.extraparams=getAttributeDef(element, "extraparams", "")
    self.width=int(getAttributeDef(element, "width", 0))
    self.height=int(getAttributeDef(element, "height", 0))
    self.bitrate=getAttributeDef(element, "bitrate", 1000000)
    self.fps=getAttributeDef(element, "fps",0)
    self.audiobitrate=getAttributeDef(element, "audiobitrate", 64000)
    self.vcodec=getAttributeDef(element, "vcodec", "libx264")
    self.acodec=getAttributeDef(element, "acodec", "aac")
    self.outputtype=getAttributeDef(element, "outputType", "mp4")
    self.thumbsCount=int(getAttributeDef(element, "thCount", "0"))
    self.thumbsInterval=int(getAttributeDef(element, "thInterval","0"))
    
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
      encoder=EncoderParams(elm)
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
    if elm.nodeName<>"encoder": raise Exception("Wrong format")
    if not elm.hasAttribute("guid"): elm.setAttribute("guid",  uuid4().get_hex())
    ep=EncoderParams(elm)
    if ep.type<>"ffmpeg_0612": raise Exception("Unknown encoder type")
    self.doc.documentElement.appendChild(elm)
    self.save()
    return ep.id

  def writeTypes(self, out):
      doc=getDOMImplementation().createDocument(None, "EncoderTypes", None)
      elm=doc.createElement("tencoderType");
      elm.setAttribute("name", "ffmpeg_0612")
      doc.documentElement.appendChild(elm)
      doc.writexml(out)
  
