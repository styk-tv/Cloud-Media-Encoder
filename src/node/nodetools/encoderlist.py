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

def getAttributeDef(element, name, default):
    if element.hasAttribute(name): return element.getAttribute(name)
    else: return default

class EncoderParams:
  def __init__(self,element):
    self.id=element.getAttribute("guid")
    self.type=element.getAttribute("type")
    self.extraparams=getAttributeDef(element, "extraparams", "")
    self.width=getAttributeDef(element, "width", 0)
    self.height=getAttributeDef(element, "height", 0)
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
