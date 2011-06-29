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


from tools import tools
import os

MOUNTROOT="/var/www/volumes"


class volume:
  def __init__(self,device):
    self.device=device
    self.probe()
    self.setup(tools.hasPartitions(device))
  def probe(self):
    self.data=tools.getId(self.device)
    if "ID_FS_UUID" in self.data: self.uuid=self.data["ID_FS_UUID"].replace("-", "")
    else: self.uuid=None
    
  def setup(self,hasPartitions):
    self.type="other"
    if hasPartitions: return
    if len(self.data)==0: self.type="empty"
    elif "ID_FS_TYPE" in self.data and self.data["ID_FS_TYPE"]=="ext4" and "ID_FS_LABEL" in self.data:
      if self.data["ID_FS_LABEL"]=="TX-DATA-NODE": self.type="node-data"
  def prepare(self):
    (ret,msg)=tools.makeFs(self.device)
    if ret==0: 
      self.probe()
      msg=self.uuid
    return (ret==0,msg)
  def mount(self):
    target=MOUNTROOT+"/"+self.data["ID_FS_UUID"].replace("-", "")
    try:
      if not os.path.exists(target): os.makedirs(target)
    except OSError, e:
      return (False,e.msg)
    (ret,msg)=tools.mount(self.device,target)
    if ret==0: msg=target
    return (ret==0,msg)
 
