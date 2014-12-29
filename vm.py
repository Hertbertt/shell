#!/usr/bin/python
import os,time,re,socket,sys,json
from socket import *
from thread import *

def base_info():
    get_hostname = '/bin/hostname'
    hostname = os.popen(get_hostname).readline().strip()
    get_os_version = "/bin/uname -a|awk '{print $1,$3}'"
    os_version = os.popen(get_os_version).readline().strip()
    get_LAN_IP = "/sbin/ifconfig |grep 'inet '|awk '{print $2}'|grep -E '192.168.|172.16.|10.1.'"
    LAN_IP = os.popen(get_LAN_IP).readline().strip('\n')
    #get_WAN_IP = "/sbin/ifconfig |grep 'inet '|awk '{print $2}'|grep -v -E '192.168.|172.16.|10.1.|127.0.0.1'"
    #WAN_IP = os.popen(get_WAN_IP).readline().strip('\n')
    return {'hostname':hostname,'os_version':os_version,'LAN_IP':LAN_IP}
#print base_info()

def load_stat():
    load = open('/proc/loadavg').read().split()
    return {'lavg_1':load[0],'lavg_5':load[1],'lavg_15':load[2]}
#print load_stat() 

def cpuinfo():
    cpu = open('/proc/stat').readlines()
    for line in cpu:
        c = line.split()
        if c[0].startswith('cpu'):
            cpu_total = float(c[1]) + float(c[2]) + float(c[3]) + float(c[4]) + float(c[5]) + float(c[6]) +float(c[7]) + float(c[8]) + float(c[9]) + float(c[10])
            cpu_idle = float(c[4])
        return {'cputotal':cpu_total,'cpuidle':cpu_idle}


def meminfo():
    mem = open('/proc/meminfo').readlines()
    memdict = {}
    for memline in mem:
        memline = memline.rstrip('\n')
        name,value = memline.split(':')
        name = name.strip()
        value = value.strip('kB')
        memdict[name] = value
    mem_use = (long(memdict['MemTotal'])-long(memdict['MemFree'])-long(memdict['Buffers'])-long(memdict['Cached']))/1024
    mem_total = long(memdict['MemTotal'])/1024
    mem_per = long(mem_use*100/mem_total)
    return mem_per;
#print meminfo()

def diskuse():
    disk01 = os.statvfs("/")
    capacity01 = disk01.f_bsize * disk01.f_blocks
    available01 = disk01.f_bsize * disk01.f_bavail
    used01 = disk01.f_bsize * (disk01.f_blocks - disk01.f_bavail)
    diskper01 = int(used01 * 100 / capacity01)
    disk_home = os.statvfs("/home")
    capacity_home = disk_home.f_bsize * disk_home.f_blocks
    available_home = disk_home.f_bsize * disk_home.f_bavail
    used_home = disk_home.f_bsize * (disk_home.f_blocks - disk_home.f_bavail)
    diskper_home = int(used_home * 100 / capacity_home)
    return {'diskper':diskper01,'diskper_home':diskper_home}
#print diskuse()

def diskstat():
    try:
        io_str = open('/proc/diskstats').read()
    except:
        try:
            io_str = open('/proc/partitions').read()
        except:
            print 'is error'
    hd_io = {}
    re_obj = re.compile(r'(?P<dev>sda)\s(?P<rio>\d+)\s(?P<rmerge>\d+)\s(?P<rsect>\d+)\s(?P<ruse>\d+)\s(?P<wio>\d+)\s(?P<wmerge>\d+)\s(?P<wsect>\d+)\s(?P<wuse>\d+)')
    match = re_obj.search(io_str)
    if match is not None:
        hd_io.update(match.groupdict())
    else:
        print "error"
    return hd_io
#print diskstat()

def netstat():
    get_net = "cat /proc/net/dev|grep -E 'eno|eth|em'|awk '{print $1,$2,$4,$5,$10,$12,$13}'"
    net = os.popen(get_net).readlines()
    netdict = {}
    netstat_dict = {}
    for netstat in net:
        netstat = netstat.rstrip('\n')
        name,value = netstat.split(':')
        netdict[name] = value
    eth0_stat = netdict.get('eth0').split()
    #eth1_stat = netdict.get('eth1').split()
    netstat_dict['RFLOW_eth0'] = eth0_stat[0]
    netstat_dict['TFLOW_eth0'] = eth0_stat[3]
    #netstat_dict['RFLOW_eth1'] = eth1_stat[0]
    #netstat_dict['TFLOW_eth1'] = eth1_stat[3]
    return netstat_dict
 
if __name__=='__main__':
    import commands
   
    (s,a) = commands.getstatusoutput('ps -ef|grep caiji_simple|grep -v grep|wc -l')
    if int(a) > 1:
        exit()

    while 1:	
	rflow_eth0_tmp = int(netstat()['RFLOW_eth0'])
        #rflow_eth1_tmp = int(netstat()['RFLOW_eth1'])
        tflow_eth0_tmp = int(netstat()['TFLOW_eth0'])
        #tflow_eth1_tmp = int(netstat()['TFLOW_eth1'])
	cputotal_tmp = int(cpuinfo()['cputotal'])
	cpuidle_tmp = int(cpuinfo()['cpuidle'])
	rio_tmp = float(diskstat()['rio'])
        wio_tmp = float(diskstat()['wio'])
	rkbs_tmp = float(diskstat()['rsect'])/2
	wkbs_tmp = float(diskstat()['wsect'])/2
	wuse_tmp = float(diskstat()['wuse'])
        ruse_tmp = float(diskstat()['ruse'])
		
	time.sleep(30)
	hostname = base_info()['hostname']
        os_version = base_info()['os_version']
        LAN_IP = base_info()['LAN_IP']
        #WAN_IP = base_info()['WAN_IP']
	lavg_1 = load_stat()['lavg_1']
	lavg_5 = load_stat()['lavg_5']
	lavg_15 = load_stat()['lavg_15']
        rflow_eth0 = (int(netstat()['RFLOW_eth0'])-rflow_eth0_tmp)/30
        #rflow_eth1 = (int(netstat()['RFLOW_eth1'])-rflow_eth1_tmp)/30
        tflow_eth0 = (int(netstat()['TFLOW_eth0'])-tflow_eth0_tmp)/30
        #tflow_eth1 = (int(netstat()['TFLOW_eth1'])-tflow_eth1_tmp)/30
	cputotal = (int(cpuinfo()['cputotal']) - cputotal_tmp)/30
	cpuidle = (int(cpuinfo()['cpuidle']) - cpuidle_tmp)/30
	cpu_per = int((1 - cpuidle/cputotal)*100)
        mem_per = meminfo()
	disk_use_per = diskuse()['diskper']
        disk_use_per_home = diskuse()['diskper_home']
        rio = (float(diskstat()['rio']) - rio_tmp)/30
        wio = (float(diskstat()['wio']) - wio_tmp)/30
	rkbs = (float(diskstat()['rsect'])/2 - rkbs_tmp)/30
	wkbs = (float(diskstat()['wsect'])/2 -wkbs_tmp)/30
	wuse = (float(diskstat()['wuse']) - wuse_tmp)/30
        ruse = (float(diskstat()['ruse']) - ruse_tmp)/30
        rio = round(rio,2) 
        wio = round(wio,2)
        rkbs = round(rkbs,2)
        wkbs = round(wkbs,2)
        ruse = round(ruse,2)
        wuse = round(wuse,2)
#	await = (ruse+wuse)/(rio+wio)
    
        sendmsg = {'hostname':hostname,'os_version':os_version,'LAN_IP':LAN_IP,'lavg_1':lavg_1,'lavg_5':lavg_5,'lavg_15':lavg_15,'rflow_eth0':rflow_eth0,'tflow_eth0':tflow_eth0,'cpu_per':cpu_per,'mem_per':mem_per,'disk_use_per':disk_use_per,'disk_use_per_home':disk_use_per_home,'rio':rio,'wio':wio,'rkbs':rkbs,'wkbs':wkbs,'wuse':wuse,'ruse':ruse}
        client=socket(AF_INET,SOCK_STREAM)
        client.connect(('192.168.1.12',1122))
        client.send(json.dumps(sendmsg))
        print client.recv(1024) 
    



		
  



  

        
