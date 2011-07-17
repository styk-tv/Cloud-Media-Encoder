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


from nodetools.xmlqueue import XMLJobManager
from nodetools.abstractqueue import AbstractTaskExecutor,Queue, ST_WORKING
from nodetools.localstores import LocalStoreList
import os
import urllib2



class DownloadExecutor(AbstractTaskExecutor):
    def __init__(self,reporter, workflow,task):
        super(DownloadExecutor, self).__init__(reporter, workflow, task)
        slist=LocalStoreList()
        self.destAsset=task.attributes["destAssetItem"]
        self.targetdir=slist.getByUuid(task.attributes["destStore"]).findAsset(self.destAsset)
        self.url=task.attributes["url"]
        
    def run(self):
        if not os.path.exists(self.targetdir): os.makedirs(self.targetdir)
        self.httpDownload(self.url, (self.targetdir+"/"+self.url.split("/")[-1:][0]),  {}, self.reportDownloadProgress)
        
    def reportDownloadProgress(self, blocknum, bs, size):
        self.updateProgress(blocknum*bs*100.0/size)

    def httpDownload(self, url, filename, headers=None, reporthook=None, postData=None):
        reqObj = urllib2.Request(url, postData, headers)
        fp = urllib2.urlopen(reqObj)
        headers = fp.info()
    ##    This function returns a file-like object with two additionalmethods:
    ##
    ##    * geturl() -- return the URL of the resource retrieved
    ##    * info() -- return the meta-information of the page, as adictionary-like object
    ##
    ##Raises URLError on errors.
    ##
    ##Note that None may be returned if no handler handles the request
    ##(though the default installed global OpenerDirector uses UnknownHandler to
    ##ensure this never happens).

        #read & write fileObj to filename
        tfp = open(filename, 'wb')
        result = filename, headers
        bs = 1024*8
        size = -1
        read = 0
        blocknum = 0

        if reporthook:
            if "content-length" in headers:
                size = int(headers["Content-Length"])
            reporthook(blocknum, bs, size)

        while 1:
            block = fp.read(bs)
            if block == "":
                break
            read += len(block)
            tfp.write(block)
            blocknum += 1
            if reporthook:
                reporthook(blocknum, bs, size)

        fp.close()
        tfp.close()
        del fp
        del tfp

        # raise exception if actual size does not match content-length header
        if size >= 0 and read < size:
            raise ContentTooShortError("retrieval incomplete: got only %i out "
                                        "of %i bytes" % (read, size), result)

        return result
        
def pluginInfo():
    return "DOWNLOAD", DownloadExecutor
