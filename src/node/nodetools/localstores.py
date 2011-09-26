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
from shutil import rmtree
from storelist import StoreList
from tools import tools, LockedFile

# <store disk="GUID" type="TYPE" vhost="host" port="port" />



class DestAsset:
    def __init__(self, store,  assetname):
        self.store=store
        self.assetname=assetname
        self.path=store.findAsset(assetname)
        self.tmppath=self.path+".tmp"
    def __enter__(self):
        os.mkdir
        return self.tmppath
    def __exit__(self, type, value, traceback):
        if isinstance(value, Exception):
            rmtree(self.tmppath)
        else: rename(self.tmppath, self.path)
    
class LocalStoreList(StoreList):
  def __init__(self, path=Config.CONFIGDIR+"/LocalStores.xml"):
    super(LocalStoreList, self).__init__(path)
    
  def save(self):
    with LockedFile(self.target, "w") as f: self.doc.writexml(f)
  def add(self,disk,type):
    uuid=uuid4().get_hex()
    diskobj=self.getDisk(disk)
    if diskobj<>None: diskelement=diskobj.element
    else: 
        diskelement=self.doc.createElement("disk")
        diskelement.setAttribute("guid", disk)
        self.doc.documentElement.appendChild(diskelement)
    if not os.path.exists(Config.STORES_ROOT+"/"+diskelement.getAttribute("guid")): raise Exception("Cannot create store on offline disk")
    os.mkdir(Config.STORES_ROOT+"/"+disk+"/"+uuid)
    tools.chown(Config.STORES_ROOT+"/"+disk+"/"+uuid, Config.USER)
    element=self.doc.createElement("store")
    element.setAttribute("guid",uuid)
    element.setAttribute("type",type)
    diskelement.appendChild(element)
    self.save()
    return uuid
        
  def publish(self, uuid, vhost, port,  redirect404):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
    if store.vhost<>"" or store.port<>"": raise Exception("Store is already published")
    with open(Config.NGINX_DIR+"/"+uuid, 'w''') as f:
        f.write("server {\n ")
        f.write("   listen "+port+";\n")
        f.write("   server_name "+vhost+";\n")
        f.write("   access_log /var/log/nginx/"+uuid+".access;\n")
        if store.type=="LI": f.write("   types { } \n")
        if redirect404<>None: f.write("   error_page 404  "+redirect404+" ;\n")
        f.write("   location / { root /var/www/volumes/"+store.diskuuid+"/"+uuid+"; } \n")
        f.write("}\n")
    store.element.setAttribute("vhost", vhost)
    store.element.setAttribute("port", str(port))
    if redirect404<>None: store.element.setAttribute("redirect404", redirect404)
    self.save()
    tools.reloadNginx()
    return vhost+":"+str(port)
      
  def remove(self, uuid):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
    if store.vhost<>"" or store.port<>"": self.unpublish(uuid)
    try:
        rmtree(Config.STORES_ROOT+"/"+store.diskuuid+"/"+uuid)
    except Exception, e:
        pass
    store.element.parentNode.removeChild(store.element)
    self.save()
    return "OK"
  def unpublish(self,uuid):
    store=self.getByUuid(uuid)
    if store==None: raise Exception("Unknown store")
    if store.vhost=="" and store.port=="": raise Exception("Store is not published")
    try:
        os.unlink(Config.NGINX_DIR+"/"+uuid)
    except Exception, e:
        pass
    store.element.removeAttribute("port")
    store.element.removeAttribute("vhost")
    self.save()
    tools.reloadNginx()
    return "OK"
  
    
   
