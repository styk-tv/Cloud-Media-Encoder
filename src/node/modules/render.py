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

import simplejson
from nodetools.localstores import LocalStoreList 
from nodetools.abstractqueue import AbstractTaskExecutor
from PIL import Image,  ImageColor,  ImageEnhance
import os


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

#too bloody slow
def alpha_composite(front,back):
    # The formula comes from http://en.wikipedia.org/wiki/Alpha_compositing
    # front, back are assumed to be RGBA Images
    front=np.asarray(front)
    back=np.asarray(back)    
    result=np.empty(front.shape,dtype='float')
    alpha=np.index_exp[:,:,3:]
    rgb=np.index_exp[:,:,:3]
    falpha=front[alpha]/255.0
    balpha=back[alpha]/255.0
    result[alpha]=falpha+balpha*(1-falpha)
    result[rgb]=(front[rgb]*falpha + back[rgb]*balpha*(1-falpha))/result[alpha]
    result[alpha]*=255
    front_transparent=(falpha<=0.001)&(balpha>0.001)
    result[front_transparent]=back[front_transparent]
    back_transparent=(balpha<=0.001)&(falpha>0.001)
    result[back_transparent]=front[back_transparent]
    result[result>255]=255
    # astype('uint8') maps np.nan and np.inf to 0
    result=result.astype('uint8')
    result=Image.fromarray(result,'RGBA')
    return result


def composite(im, mark, position):
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)

    r, g, b, a = layer.split()
    layer = Image.merge("RGB", (r, g, b))
    mask = Image.merge("L", (a,))
    im.paste(layer, (0, 0), mask)
    return im


class RenderObject(object):
    def __init__(self, json, slist):
        self.x=json["x"]
        self.y=json["y"]
        self.z=json["z"]
        self.start=json["start"]
        self.stop=json["finish"]
        self.alpha=json["alpha"]
        src=slist.getByUuid(json["store"]).findAssetFile(json["assetItem"], json["assetItemType"])
        self.image=Image.open(src)
        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")

        
        #apply alpha
        if self.alpha<1:
#            aimg=Image.new("RGBA", self.image.size, (0,0,0,0))
#            print self.image.size,  aimg.size
 #           self.image=Image.blend(aimg, self.image, self.alpha)
            self.image=reduce_opacity(self.image, self.alpha)
    def render(self, target):
#        target.paste(self.image, (self.x, self.y), self.image)
        return composite(target,  self.image,  (self.x,  self.y))
    def mayRender(self, target, n):
        if n>=self.start and n<=self.stop: return self.render(target)
        else: return target
        
class RenderExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(RenderExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.frames=1
        self.dstAsset=task.attributes["srcAssetItem"]
        if task.attributes.has_key("destAssetItem"): dstAsset=task.attributes["destAssetItem"]

        self.srcfile=slist.getByUuid(task.attributes["srcStore"]).findAssetFile(task.attributes["srcAssetItem"], task.attributes["srcAssetItemType"])
        self.targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(self.dstAsset)
        (self.ext, fps)=slist.getByUuid(task.attributes["destStore"]).decodeAssetType(task.attributes["destAssetItemType"])
        print self.ext
        if not os.path.exists(self.targetdir): os.makedirs(self.targetdir)
        
    def run(self):
        with open(self.srcfile, "r") as f:
            desc=simplejson.load(f)
        
        slist=LocalStoreList()
        self.width=desc["main"]["width"]
        self.height=desc["main"]["height"]
        self.background=tuple(desc["main"]["background"])
        print self.background
        self.objects=[]
        frames=0
        for itm in desc["objects"]:
            object=RenderObject(itm, slist)
            if object.stop>frames: frames=object.stop
            self.objects+=[object]
        self.objects=sorted(self.objects,  key=lambda  frame: frame.z)
        
        for i in range(frames):
            img=self.createFrame()
            for obj in self.objects:
                img=obj.mayRender(img, i)
            name=self.targetdir+"/"+self.dstAsset+("_%05d" % i)+"."+self.ext
            img.save(name)
    def createFrame(self):
        return Image.new("RGBA",  (self.width, self.height),  self.background)
        
        
def pluginInfo():
    return "RENDER", RenderExecutor
