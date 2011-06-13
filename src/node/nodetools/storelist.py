from xml.dom.minidom import getDOMImplementation, parse
from config import Config
import os


class Store:
  def __init__(self,element,diskuuid):
    self.type=element.getAttribute("type")
    self.uuid=element.getAttribute("guid")
    self.diskuuid=diskuuid
    self.path=self._findPath()
  def _findPath(self):
    p=Config.STORES_ROOT+"/"+self.diskuuid+"/"+self.uuid
    if os.path.exists(p): return p
    else: return None
  def isLocal(self):
    return self.path<>None
    
  # returns directory containing given asset
  def findAsset(self,assetId):
    return self.path+"/"+assetId
  
  # returns path to main asset file
  def findAssetFile(self,assetId,extension):
    return self.findAsset(assetId)+"/"+assetId+"."+extension

class Disk:
  def __init__(self,element):
    self.uuid=element.getAttribute("guid")
    self.host=element.getAttribute("host")
    self.stores=[]
    for elm in element.getElementsByTagName("store"): self.stores.append(Store(elm,self.uuid))
    

    
    
class StoreList:
  def __init__(self, path=Config.CONFIGDIR+"/Stores.xml"):
    dom=parse(open(path,'r'))
    self.stores={}
    self.disks=[]
    for elm in dom.getElementsByTagName("disk"): 
      disk=Disk(elm)
      self.disks.append(disk)
      for store in disk.stores: self.stores[store.uuid]=store
      
  def getByUuid(self,uuid):
    if self.stores.has_key(uuid):  return self.stores[uuid]
    else: return None
