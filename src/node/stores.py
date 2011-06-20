from nodetools.tools import xmlmsg
from nodetools.localstores import LocalStoreList
import sys

def main():
    try:
        if len(sys.argv)<2: raise Exception("Usage: stores.py <list>|<create>|<remove>|<publish>|<unpublish>")
        action=sys.argv[1]
        stores=LocalStoreList()
        if action=="list": stores.write(sys.stdout)
        elif action=="create": 
            if len(sys.argv)<4: raise Exception("Usage: stores.py create <disk> <type>")
            ret=stores.add(sys.argv[2], sys.argv[3])
            return xmlmsg("result", ret)
        elif action=="remove":
            if len(sys.argv)<3: raise Exception("Usage: stores.py remove <store>")
            ret=stores.remove(sys.argv[2],)
            return xmlmsg("result", ret)
        elif action=="publish":
            if len(sys.argv)<5: raise Exception("Usage: stores.py publish <store> <virtual host> <port>")
            ret=stores.publish(sys.argv[2], sys.argv[3], sys.argv[4])
            return xmlmsg("result", ret)
        elif action=="unpublish":
            if len(sys.argv)<3: raise Exception("Usage: stores.py unpublish <store>")
            ret=stores.unpublish(sys.argv[2])
            return xmlmsg("result", ret)
        else: raise Exception("Usage: stores.py <list>|<create>|<remove>|<publish>|<unpublish>")
    except Exception, e:
        return xmlmsg("error", str(e))
        
main()
