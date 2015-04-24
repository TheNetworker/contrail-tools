from fabric.api import env

host1 = 'root@10.204.216.7'
host2 = 'root@10.204.216.14'
host3 = 'root@10.204.216.15'
host4 = 'root@10.204.216.25'
host5 = 'root@10.204.217.75'

ext_routers = [('blr-mx1', '192.168.249.1')]
router_asn = 64510
public_vn_rtgt = 19006
public_vn_subnet = "10.204.219.80/29"

host_build = 'sandipd@10.204.216.4'


env.roledefs = {
    'all': [host1, host2, host3,host4, host5],
    'cfgm': [host1,host2,host3],
    'webui': [host1],
    'openstack': [host1],
    'control': [host2, host3],
    'collector': [host1],
    'database': [host1],
    'compute': [host4, host5],
    'build': [host_build]
}

env.hostnames = {
    'all': ['nodea11', 'nodea18', 'nodea19', 'nodea29', 'nodeg35']
}
#env.interface_rename = False
#
control_data = {
    host1 : { 'ip': '192.168.250.1/24', 'gw' : '192.168.250.254', 'device':'eth0' },
    host2 : { 'ip': '192.168.250.2/24', 'gw' : '192.168.250.254', 'device':'eth0' },
    host3 : { 'ip': '192.168.250.3/24', 'gw' : '192.168.250.254', 'device':'eth0' },
    host4 : { 'ip': '192.168.250.4/24', 'gw' : '192.168.250.254', 'device':'eth0' },
    host5 : { 'ip': '192.168.251.5/24', 'gw' : '192.168.251.254', 'device':'eth1' },
}

static_route  = {
    host1 : [{ 'ip': '192.168.251.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.249.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.239.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' }
],
    host2 : [{ 'ip': '192.168.251.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.249.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.239.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' }
],
    host3 : [{ 'ip': '192.168.251.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.249.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.239.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' }
],
    host4 : [{ 'ip': '192.168.251.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.249.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' },
                { 'ip': '192.168.239.0', 'netmask' : '255.255.255.0', 'gw':'192.168.250.254', 'intf': 'eth0' }
],
    host5 : [{ 'ip': '192.168.250.0', 'netmask' : '255.255.255.0', 'gw':'192.168.251.254', 'intf': 'eth1' },
                { 'ip': '192.168.249.0', 'netmask' : '255.255.255.0', 'gw':'192.168.251.254', 'intf': 'eth1' },
                { 'ip': '192.168.238.0', 'netmask' : '255.255.255.0', 'gw':'192.168.251.254', 'intf': 'eth1' }
],
}

env.openstack_admin_password = 'contrail123'
env.password = 'c0ntrail123'
env.passwords = {
    host1: 'c0ntrail123',
    host2: 'c0ntrail123',
    host3: 'c0ntrail123',
    host4: 'c0ntrail123',
    host5: 'c0ntrail123',
    host_build: 'stack@123',
}

env.ostypes = {
    host1:'ubuntu',
    host2:'ubuntu',
    host3:'ubuntu',
    host4:'ubuntu',
    host5:'ubuntu',
}
minimum_diskGB=32
env.test_repo_dir='/home/stack/multi_interface_parallel/ubuntu/icehouse/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='sandipd@juniper.net'
multi_tenancy=True
env.interface_rename = False
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"
env.log_scenario='Five node sanity'
env.enable_lbaas = True
