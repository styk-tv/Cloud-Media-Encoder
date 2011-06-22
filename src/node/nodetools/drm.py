from base64 import b64encode, b64decode
from M2Crypto.EVP import Cipher
from nodetools.localstores import LocalStoreList
from nodetools.queue import AbstractTaskExecutor,Queue
import os


class EncryptExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(EncryptExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.srcasset=slist.getByUuid(task.attributes["srcStore"]).findAsset(task.attributes["srcAssetItem"])
        self.targetstore=slist.getByUuid(task.attributes["destStore"])
        self.destdir=self.targetstore.findAsset(self.task.attributes["destAssetItem"])
    def run(self):
        for ifile in os.listdir(self.srcasset):
            srcfile=os.path.join(self.srcasset, ifile)
            if not os.path.isfile(srcfile): continue
            destfile=os.path.join(self.destdir, ifile)
            try:
                f_in=open(srcfile, "rb")
                f_out=open(destfile+".enc", "wb")
                self._encryptSingle(f_in, f_out, self._makeCipher(), 0)
            finally:
                f_in.close()
                f_out.close()
             

    def _encryptSingle(self, input, output, cipher, fullen):
        while True:
            data=input.read(2*1024*1024)
            if len(data)==0:
                output.write(cipher.final())
                break
            output.write(cipher.update(data))
            
    def _makeCipher(self):
#        k=b64decode(self.task.attributes["key"])
        iv='\0'*16
        k='\x00'*16
        print k, iv
        return Cipher(alg="aes_128_cbc", key=k, iv=iv, op=1, salt=None)
    
