from xml.dom.minidom import getDOMImplementation, parse
from config import Config
import os
from uuid import uuid4
from shutil import rmtree

# <store disk="GUID" type="TYPE" vhost="host" port="port" />

class Store:
  def __init__(self,element):
    self.type=element.getAttribute("type")
    self.uuid=element.getAttribute("uuid")
    self.diskuuid=element.getAttribute("disk")
    self.path=self._findPath()
    self.vhost=element.getAttribute("vhost")
    self.port=element.getAttribute("port")
    self.element=element
    
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
   
    
class LocalStoreList:
  def __init__(self, path=Config.CONFIGDIR+"/LocalStores.xml"):
    self.target=path
    if os.path.exists(path):
        with open(path,'r') as f: self.doc=parse(f)
    else: self.doc=getDOMImplementation().createDocument(None, "stores", None)
    self.stores={}
    for elm in self.doc.getElementsByTagName("store"): 
      disk=Store(elm)
      self.stores[disk.uuid]=disk
      
  def getByUuid(self,uuid):
    if self.stores.has_key(uuid):  return self.stores[uuid]
    else: return None
  def save(self):
    with open(self.target, "w") as f: self.doc.writexml(f)
  def add(self,disk,type):
    uuid=uuid4().get_hex()
    os.mkdir(Config.STORES_ROOT+"/"+disk+"/"+uuid)
    element=self.doc.createElement("store")
    element.setAttribute("uuid",uuid)
    element.setAttribute("disk",disk)
    element.setAttribute("type",type)
    self.doc.documentElement.appendChild(element)
    self.save()
    return uuid
        
  def publish(self, uuid, vhost, port):
    if not self.stores.has_key(uuid): raise Exception("Unknown store")
    store=self.stores[uuid]
    if store.vhost<>"" or store.port<>"": raise Exception("Store is already published")
    with open(Config.NGINX_DIR+"/"+uuid, 'w''') as f:
        f.write("server {\n ")
        f.write("   listen "+port+";\n")
        f.write("   server_name "+vhost+";\n")
        f.write("   access_log /var/log/nginx/"+uuid+".access;\n")
        f.write("   location / { root /var/www/volumes/"+store.diskuuid+"/"+uuid+"; } \n")
        f.write("}\n")
    store.element.setAttribute("vhost", vhost)
    store.element.setAttribute("port", str(port))
    self.save()
    return vhost+":"+str(port)
      
  def remove(self, uuid):
    if not self.stores.has_key(uuid):  raise Exception("Unknown store")
    store=self.stores[uuid]
    if store.vhost<>"" or store.port<>"": self.unpublish(uuid)
    rmtree(Config.STORES_ROOT+"/"+store.diskuuid+"/"+uuid)
    self.doc.documentElement.removeChild(store.element)
    self.save()
    return "OK"
  def unpublish(self,uuid):
    if not self.stores.has_key(uuid): raise Exception("Unknown store")
    store=self.stores[uuid]
    if store.vhost=="" and store.port=="": raise Exception("Store is not published")
    os.unlink(Config.NGINX_DIR+"/"+uuid)
    store.element.removeAttribute("port")
    store.element.removeAttribute("vhost")
    self.save()
    return "OK"
  def write(self, out):
      self.doc.writexml(out)
  
    
   
