#!/usr/bin/python

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

from nodetools import version
from nodetools import pwdtools
from nodetools.config import Config
from nodetools import processtools
import node
from time import sleep
import os
import sys
from nodetools.xmlqueue import XMLJobManager

def cls():
    print("\x1B[2J")

def main_menu():
    cls()
    a=XMLJobManager()
    status=a.listByStatus()
    running=processtools.is_running()
    idle=status[1]==0
    
    print "(c) 2011 Node Styk.Tv v0.2 ", version.commit, " (", version.date+")"
    print "Node ID:",  version.nodeid
    print "IP: ", pwdtools.getMainIp(), "  (", pwdtools.getIfaceType()+")"
    print
    print "Node is running: ",   running,  "idle ", idle
    print "WORKFLOWS: ", status[0], " pending, ", status[1], " processing, ", status[2], " finished, ",  status[3], " failed"
    print
    print "1) Network settings"
    print "2) Change root password"
    print "3) Change node password"
    if running:
        print "4) Stop node"
    else:
        print "5) Start node"
    print "0) Exit"
    print
    sys.stdout.write("Enter choice: ")
    
    return sys.stdin.readline().strip()
    
def network_menu():
    print "Network settings"
    print
    print "1) Use DHCP"
    print "2) Use static configuration"
    print "0) Exit"
    print
    sys.stdout.write("Enter choice: ")
    return sys.stdin.readline().strip()

def readStaticSettings():
    print "IP Address:"
    ip=sys.stdin.readline().strip()
    print "Netmask (xxx.xxx.xxx.xxx):"
    netmask=sys.stdin.readline().strip()
    print "Gateway"
    gateway=sys.stdin.readline().strip()
    print 'First DNS server:'
    dns1=sys.stdin.readline().strip()
    print 'Second DNS server:'
    dns2=sys.stdin.readline().strip()
    return (ip, netmask, gateway, dns1, dns2)

def network_settings():
    while True:
        opt=network_menu()
        if opt=="1":
            pwdtools.setDhcp()
            pwdtools.restartNetwork()
        elif opt=="2":
            (ip, netmask, gateway, dns1, dns2)=readStaticSettings()
            pwdtools.setStatic(ip, gateway, netmask, dns1, dns2)
            pwdtools.restartNetwork()
        elif opt=="0":
            return
    
def root_pwd():
    try:
        pwdtools.change_password("root")
    except Exception, e:
        print e

def node_pwd():
    try:
        pwdtools.change_password(Config.USER)
    except Exception, e:
        print e


def main():
    while True:
        opt=main_menu()
        if opt=="1": network_settings()
        elif opt=="2": root_pwd()
        elif opt=="3": node_pwd()
        elif opt=="4": 
            node.try_stop()
            sleep(3)
        elif opt=="5": 
            os.system("python /opt/node/node.py start")
            sleep(3)
        elif opt=="0": 
            print "Console can be opened again by running /etc/rc.local"
            return
        

if __name__=="__main__":
    main()
    
