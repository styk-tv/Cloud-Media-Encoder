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

def freespace(p):
    s = os.statvfs(p)
    return s.f_bsize * s.f_bavail

class Store:
  def __init__(self,element,diskuuid):
    self.type=element.getAttribute("type")
    self.uuid=element.getAttribute("guid")
    self.diskuuid=diskuuid
    self.path=Config.STORES_ROOT+"/"+self.diskuuid+"/"+self.uuid
    self.vhost=element.getAttribute("vhost")
    self.port=element.getAttribute("port")
    self.element=element
    self.local=os.path.exists(self.path)

  def isLocal(self):
    return self.local
    
  # returns directory containing given asset
  def findAsset(self,assetId):
    return self.path+"/"+assetId[0]+"/"+assetId[1]+"/"+assetId
  
  # returns path to main asset file
  def findAssetFile(self,assetId,extension):
    return self.findAsset(assetId)+"/"+assetId+"."+extension

class Disk:
  def __init__(self,element):
    self.uuid=element.getAttribute("guid")
    self.host=element.getAttribute("host")
    self.online=os.path.exists(Config.STORES_ROOT+"/"+self.uuid)
    self.freespace=0
    if self.online: self.freespace=freespace(Config.STORES_ROOT+"/"+self.uuid)
    self.stores=[]
    self.element=element
    for elm in element.getElementsByTagName("store"): self.stores.append(Store(elm,self.uuid))

  
    
    
class StoreList(object):
  def __init__(self, path=Config.CONFIGDIR+"/Stores.xml"):
    if os.path.exists(path):
        with open(path,'r') as f: self.doc=parse(f)
    else: self.doc=getDOMImplementation().createDocument(None, "stores", None)
    self.stores={}
    self.target=path
    self.disks=[]
    for elm in self.doc.getElementsByTagName("disk"): 
      disk=Disk(elm)
      self.disks.append(disk)
      for store in disk.stores: self.stores[store.uuid]=store
      
  def getDisk(self, uuid):
    for disk in self.disks:
        if disk.uuid==uuid: return disk
    return None
  def getByUuid(self,uuid):
    if self.stores.has_key(uuid):  return self.stores[uuid]
    else: return None
  def write(self, out):
      for disk in self.disks:
          disk.element.setAttribute("online", str(disk.online))
      self.doc.writexml(out)
