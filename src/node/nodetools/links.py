#!/usr/bin/python

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

from config import  Config
from localstores import LocalStoreList
from xml.dom.minidom import getDOMImplementation, parse
from time import time, sleep
import os
from shutil import rmtree
from tools import tools, LockedFile
from datetime import datetime
from calendar import timegm


DATEFORMAT="%d/%m/%Y %H:%M:%S"
SLEEPTIME=60

class Links(object):
    def __init__(self, path=Config.CONFIGDIR+"/Links.xml"):
        if os.path.exists(path):
            with LockedFile(path,'r') as f: self.doc=parse(f)
        else: self.doc=getDOMImplementation().createDocument(None, "links", None)
        self.stores=LocalStoreList()
        self.target=path
    def checkAll(self):
        now=time()
        changed=False
        for elm in self.doc.getElementsByTagName("link"): 
            if not self.check(elm, now): 
                elm.parentNode.removeChild(elm)
                changed=True
        if changed: self.save()
        
    def check(self, elm, now):
        exptime=float(elm.getAttribute("expire"))
        if exptime>now: return True
        self.removeFromDisk(elm)
        return False
        
    def save(self):
       with LockedFile(self.target, "w") as f: self.doc.writexml(f)

    def write(self, out):
        self.doc.writexml(out)
        
    def removeFromDisk(self, elm):
        src=elm.getAttribute("srcStore")
        dest=elm.getAttribute("destStore")
        ait=elm.getAttribute("destAssetItem")
        srcS=self.stores.getByUuid(src)
        if srcS==None: return 
        dstS=self.stores.getByUuid(dest)
        if dstS==None: return 
        dstDir=dstS.findAsset(ait)
        if not os.path.exists(dstDir): return 
        rmtree(dstDir)
        
    def find(self, dest, asset): 
        for elm in self.doc.getElementsByTagName("link"): 
            if elm.getAttribute("destStore")==dest and elm.getAttribute("destAssetItem")==asset: return elm
        return None

    def remove(self,  dest,  asset):
        elm=self.find(dest, asset)
        if elm==None: raise Exception("Link not found")
        self.removeFromDisk(elm)
        elm.parentNode.removeChild(elm)
        self.save()
    def parseDate(self, date):
        return timegm(datetime.strptime(date, DATEFORMAT).utctimetuple())
        
    def modify(self, dest, asset, expire):
        elm=self.find(dest, asset)
        if elm==None: raise Exception("Link not found")
        elm.setAttribute("expire",str(self.parseDate(expire)) )
        self.save()
       
        
    def add(self, src, dest, asset, destasset,  expire):
        ex=self.find( dest, destasset)
        if ex<>None: raise Exception("Link already exists")
        srcS=self.stores.getByUuid(src)
        destS=self.stores.getByUuid(dest)
        if srcS==None or destS==None: raise Exception("Invalid store")
        srcpath=srcS.findAsset(asset)
        if not os.path.exists(srcpath): raise Exception("Source asset does not exist")
        destpath=destS.findAsset(destasset)
        if os.path.exists(destpath): raise Exception("Destination already exists")
        elm=self.doc.createElement("link")
        elm.setAttribute("srcStore", src)
        elm.setAttribute("destStore", dest)
        elm.setAttribute("assetItem", asset)
        elm.setAttribute("destAssetItem",destasset)
        elm.setAttribute("expire", str(self.parseDate(expire)))
        self.createLink(srcpath, destpath, asset, destasset)
        self.doc.documentElement.appendChild(elm)
        self.save()
    def createLink(self, srcpath, destpath,  srcasset, dstasset):
        os.makedirs(destpath)
        for f in os.listdir(srcpath):
            df=f.replace(srcasset, dstasset)
            os.symlink(os.path.abspath(srcpath)+"/"+f, os.path.abspath(destpath)+"/"+df)
 
    
def linkschecker():
    while True:
        a=Links()
        a.checkAll()
        sleep(SLEEPTIME)
