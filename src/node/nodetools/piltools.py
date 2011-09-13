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

from PIL import Image,  ImageColor, ImageDraw,  ImageEnhance
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

def computeSize(eparams, aspect):
        origratio=aspect
        w=eparams.width
        h=eparams.height
        newratio=float(w)/float(h)
        if origratio<newratio: w=int(h*origratio)
        else: h=int(w/origratio)
        return (w, h)

def round_corner(radius, fill, bg):
        """Draw a round corner"""
        corner = Image.new('RGBA', (radius, radius),bg)
        draw = ImageDraw.Draw(corner)
        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
        return corner
 
def round_rectangle(size, radius, fill,   bg):
        """Draw a rounded rectangle"""
        width, height = size
        rectangle = Image.new('RGBA', size, fill)
        if radius==0: return rectangle 
        corner = round_corner(radius, fill, bg)
        rectangle.paste(corner, (0, 0))
        rectangle.paste(corner.rotate(90), (0, height - radius)) # Rotate the corner and paste it
        rectangle.paste(corner.rotate(180), (width - radius, height - radius))
        rectangle.paste(corner.rotate(270), (width - radius, 0))
        return rectangle
 
        
def makeBorder(eparams, img):
        w=eparams.borderWidth
        bg=(0, 0, 0, 0)
       
        if eparams.backgroundColor<>"" and eparams.backgroundColor<>"#00000000": bg=eparams.backgroundColor
        print eparams.borderColor
        dest= round_rectangle(img.size, eparams.borderRadius, eparams.borderColor, bg)
        inside=round_rectangle((img.size[0]-2*w, img.size[1]-2*w), eparams.borderRadius, "white", (0, 0, 0, 0))

        mask=Image.new("RGBA", img.size, (0, 0, 0, 0))
        mask.paste(inside, (w, w))

        dest.paste(img, (0, 0), mask)
        return dest
    
        
def makeSquare(img):
        box=img.size
        if img.size[0]==img.size[1]: return img
        diff=abs(img.size[0]-img.size[1])/2
        if img.size[0]>img.size[1]: box=(diff, 0, img.size[0]-diff, img.size[1])
        else: box=(0, diff, img.size[0], img.size[1]-diff)
        img=img.crop(box)
        return img
        
