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

import PAM
import sys
import subprocess
from getpass import getpass
import socket

MAIN_IFACE="eth0"

def check_password(user):
    auth=PAM.pam()
    auth.start("passwd")
    auth.set_item(PAM.PAM_USER,user)
    print "Enter OLD password"
    auth.authenticate()


def change_password(user):
    check_password(user)
    np=getpass("Enter NEW password: ")
    np2=getpass("Repeat NEW password: ")
    if np<>np2: raise Exception("Password does not match")
    passwd=subprocess.Popen(args=["passwd", "--stdin", user], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    ret=passwd.communicate(np)
    passwd.stdin.close()
    if passwd.wait() != 0: raise Exception("Error changing password")
    

def getMainIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    return s.getsockname()[0]

def getIfaceType():
    with open("/etc/network/interfaces","r") as f:
        for l in f:
            tokens=l.strip().split(" ")
            if tokens[0]=="iface" and tokens[1]==MAIN_IFACE and tokens[2]=="inet":  return tokens[3]
    return "unknown"
    
def setDhcp():
        with open("/etc/network/interfaces","w") as f:
            f.write("auto lo\niface lo inet loopback\n\nallow-hotplug "+MAIN_IFACE+"\niface "+MAIN_IFACE+" inet dhcp\n")

def setStatic(ip, gw, netmask, dns1, dns2):
        with open("/etc/network/interfaces","w") as f:
            f.write("auto lo\niface lo inet loopback\n\nallow-hotplug "+MAIN_IFACE+"\niface "+MAIN_IFACE+" inet static\n")
            f.write("   address "+ip+"\n")
            f.write("   netmask "+netmask+"\n")
            f.write("   gateway "+gw+"\n")
        with open("/etc/resolv.conf","w") as f:
            f.write("nameserver "+dns1+"\nnameserver "+dns2+"\n")

def restartNetwork():
        subprocess.call("/etc/init.d/networking restart", shell=True)
