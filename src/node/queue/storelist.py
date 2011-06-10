from xml.dom.minidom import getDOMImplementation, parse
import os


STORELIST="/opt/nodes/etc/Stores.xml"
STORES_ROOT="/var/www/volumes"



class Store:
  def __init__(self,element,diskuuid):
    self.type=element.getAttribute("type")
    self.uuid=element.getAttribute("uuid")
    self.diskuuid=diskuuid
    self.path=_findPath()
  def _findPath(self):
    p=STORES_ROOT+"/"+self.diskuuid+"/"+self.uuid
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
    self.uuid=element.getAttribute("uuid")
    self.host=element.getAttribute("host")
    self.stores=[]
    for elm in dom.getElementByTagName("store"): self.stores.append(Store(elm))
    

    
    
class StoreList:
  def __init__(self):
    dom=parse(open(STORELIST,'r'))
    self.stores={}
    self.disks=[]
    for elm in dom.getElementByTagName("disk"): 
      disk=Disk(elm)
      disks.append(disk)
      for store in disk.stores: self.stores[store.uuid]=store
      
  def getByUuid(self,uuid):
    return self.stores[uuid]