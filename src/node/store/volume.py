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
    if "UUID" in self.data: self.uuid=self.data["UUID"]
    else: self.uuid=None
    
  def setup(self,hasPartitions):
    self.type="other"
    if hasPartitions: return
    if len(self.data)==0: self.type="empty"
    elif "TYPE" in self.data and self.data["TYPE"]=="ext4" and "LABEL" in self.data:
      if self.data["LABEL"]=="TX-DATA-WWW": self.type="www"
  def prepare(self,dtype):
    (ret,msg)=tools.makeFs(self.device,dtype)
    if ret==0: 
      self.probe()
      msg=self.uuid
    return (ret==0,msg)
  def mount(self):
    target=MOUNTROOT+"/"+self.data["UUID"]
    try:
      if not os.path.exists(target): os.makedirs(target)
    except OSError, e:
      return (False,e.msg)
    (ret,msg)=tools.mount(self.device,target)
    if ret==0: msg=target
    return (ret==0,msg)
 