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


from nodetools.localstores import LocalStoreList
from nodetools.abstractqueue import AbstractTaskExecutor,Queue
from nodetools.tools import check_output
from xml.dom.minidom import getDOMImplementation, parseString
import os
import pyexiv2



class MediaInfoExecutor(AbstractTaskExecutor):
    requiredParams=["srcStore", "srcAssetItem", "srcAssetItemType"]

    def __init__(self,reporter, workflow,task):
        super(MediaInfoExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        self.dstfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], "xml")
        
    def run(self):
         (ret, out, err)=check_output(["mediainfo", "--Language=raw","--Output=XML", self.srcfile] )
         if ret<>0: raise Exception("MediaInfo failed")
         doc=parseString(out)
         (ret, out, err)=check_output(["sha1sum", "-b", self.srcfile])
         if ret<>0: raise Exception("SHA1SUM failed")
         out=out.split(" ")[0]
         for flm in doc.getElementsByTagName("File"):  flm.setAttribute("sha1sum", out)
         try:
             exif=pyexiv2.ImageMetadata(self.srcfile)
             exif.read()
             el=doc.createElement("exif")
             doc.getElementsByTagName("File")[0].appendChild(el)
             for k in exif.values():
                if len(k.human_value)>128: continue
                e2=doc.createElement(k.key[5:])
                v=doc.createTextNode(k.human_value)
                e2.appendChild(v)
                el.appendChild(e2)
         except:
             pass
         with open(self.dstfile, "w") as out: doc.writexml(out)

def pluginInfo():
    return "MEDIAINFO", MediaInfoExecutor
