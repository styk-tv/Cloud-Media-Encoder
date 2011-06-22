from xml.dom.minidom import getDOMImplementation, parse
from config import Config
import os
from uuid import uuid4
from shutil import rmtree
from storelist import StoreList

# <store disk="GUID" type="TYPE" vhost="host" port="port" />


    
class LocalStoreList(StoreList):
  def __init__(self, path=Config.CONFIGDIR+"/LocalStores.xml"):
    super(LocalStoreList, self).__init__(path)
    
  def save(self):
    with open(self.target, "w") as f: self.doc.writexml(f)
  def add(self,disk,type):
    uuid=uuid4().get_hex()
    diskobj=self.getDisk(disk)
    if diskobj<>None: diskelement=diskobj.element
    else: 
        diskelement=self.doc.createElement("disk")
        diskelement.setAttribute("guid", disk)
        self.doc.documentElement.appendChild(diskelement)
    os.mkdir(Config.STORES_ROOT+"/"+disk+"/"+uuid)
    element=self.doc.createElement("store")
    element.setAttribute("guid",uuid)
    element.setAttribute("type",type)
    diskelement.appendChild(element)
    self.save()
    return uuid
        
  def publish(self, uuid, vhost, port):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
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
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
    if store.vhost<>"" or store.port<>"": self.unpublish(uuid)
    rmtree(Config.STORES_ROOT+"/"+store.diskuuid+"/"+uuid)
    store.element.parentNode.removeChild(store.element)
    self.save()
    return "OK"
  def unpublish(self,uuid):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
    if store.vhost=="" and store.port=="": raise Exception("Store is not published")
    os.unlink(Config.NGINX_DIR+"/"+uuid)
    store.element.removeAttribute("port")
    store.element.removeAttribute("vhost")
    self.save()
    return "OK"
  
    
   
