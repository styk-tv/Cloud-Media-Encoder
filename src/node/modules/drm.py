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


from base64 import b64encode, b64decode
from M2Crypto.EVP import Cipher
from nodetools.localstores import LocalStoreList
from nodetools.abstractqueue import AbstractTaskExecutor,Queue
import os


class AESExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task,  encrypt):
        super(AESExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.srcasset=slist.getByUuid(task.attributes["srcStore"]).findAsset(task.attributes["srcAssetItem"])
        self.targetstore=slist.getByUuid(task.attributes["destStore"])
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
        self.encrypt=encrypt
        if not os.path.exists(self.destdir): os.makedirs(self.destdir)

    def run(self):
        for ifile in os.listdir(self.srcasset):
            srcfile=os.path.join(self.srcasset, ifile)
            if not os.path.isfile(srcfile): continue
            destfile=os.path.join(self.destdir, ifile)
            
            # for encryption add ".aes" 
            if self.encrypt: destfile=destfile+".aes"
            
            # for decryption ignore all files not ending with ".aes"
            if not self.encrypt:
                if destfile[-4:]<>".aes": continue
                destfile=destfile[:-4]
            
            self.processSingle(srcfile, destfile)
    
    def processSingle(self,  srcfile,  destfile):
            f_in=None
            f_out=None
            try:
                f_in=open(srcfile, "rb")
                f_out=open(destfile, "wb")
                self._encryptSingle(f_in, f_out, self._makeCipher(), 0)
            finally:
                if f_in<>None: f_in.close()
                if f_out<>None: f_out.close()
        

    def _encryptSingle(self, input, output, cipher, fullen):
        while True:
            data=input.read(2*1024*1024)
            if len(data)==0:
                output.write(cipher.final())
                break
            output.write(cipher.update(data))
            
    def _makeCipher(self):
        k=b64decode(self.task.attributes["key"])
        iv='\0'*16
        op=0
        if self.encrypt: op=1
        print k, iv
        return Cipher(alg="aes_128_cbc", key=k, iv=iv, op=op,  salt=None)
    
class EncryptExecutor(AESExecutor):
    def __init__(self,reporter, workflow,task):
        super(EncryptExecutor, self).__init__(reporter, workflow, task, True)

class DecryptExecutor(AESExecutor):
    def __init__(self,reporter, workflow,task):
        super(DecryptExecutor, self).__init__(reporter, workflow, task, False)

def pluginInfo():
    return [ ("ENCRYPT", EncryptExecutor),  ("DECRYPT", DecryptExecutor) ]
