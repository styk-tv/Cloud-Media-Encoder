import os.path
from config import Config

PIDFILE=Config.CONFIGDIR+"/node.pid"

def pid_exists(pid):
        return os.path.exists("/proc/"+pid)

def get_pid():
    try:
	with open(PIDFILE,"r") as pidf:
	    return pidf.read().strip()
    except:
	pass
    return None

def remove_stale_pidfile():
    try:
	os.remove(PIDFILE)
    except:
	pass

def is_running():
    pid=get_pid()
    if pid==None: return False
    if not pid_exists(pid):
	remove_stale_pidfile()
	return False
    return True

def stop():
    pid=get_pid()
    if pid<>None: os.kill(int(pid),15)    
