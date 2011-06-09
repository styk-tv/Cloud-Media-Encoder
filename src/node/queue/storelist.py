from xml.dom.minidom import getDOMImplementation, parse
import os


STORELIST="/opt/nodes/etc/stores.xml"
STORES_ROOT="/var/www/volumes"


class Store:
  def __init__(self,element):
    self.type=element.getAttribute("type")
    self.name=element.getAttribute("name")
    self.uuid=element.getAttribute("uuid")
    self.path=_findPath("uuid")
    self.ip=element.getAttribute("hostInternal")
    self.external=element.getAttribute("hostExternal")
  def _findPath(self,uuid):
    if os.path.exists(STORES_ROOT+"/"+self.uuid): return STORES_ROOT+"/"+self.uuid
    else: return None
  def isLocal(self):
    return self.path<>None
    
    
class StoreList:
  def __init__(self):
    dom=parse(open(STORELIST,'r'))
    self.stores={}
    for elm in dom.getElementByTagName("store"): self.stores[elm.getAttribute("uuid")]=Store(elm)
  def getByUuid(self,uuid):
    return self.stores[uuid]