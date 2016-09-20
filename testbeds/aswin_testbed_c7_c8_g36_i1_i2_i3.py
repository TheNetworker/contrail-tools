from fabric.api import env
import os

host1 = 'root@10.204.216.64'
host2 = 'root@10.204.216.65'
host3 = 'root@10.204.217.76'
host4 = 'root@10.204.217.113'
host5 = 'root@10.204.217.114'
host6 = 'root@10.204.217.115'

ext_routers = [('hooper','192.168.192.253'),('blr-mx1','192.168.192.240')]
router_asn = 64512
public_vn_rtgt = 2223
public_vn_subnet = '10.204.221.176/28'

host_build = 'stack@10.204.216.49'


env.roledefs = {
    'all': [host1, host2, host3, host4, host5, host6],
    'cfgm': [host1, host2, host3],
    'openstack': [host1, host2, host3],
    'webui': [host2],
    'control': [host1, host2],
    'compute': [host4, host5, host6],
    'collector': [host1, host2, host3],
    'database': [host1, host2, host3],
    'build': [host_build],
}

env.hostnames = {
    'all': ['nodec7', 'nodec8', 'nodeg36', 'nodei1', 'nodei2', 'nodei3']
}
env.physical_routers={
'hooper'     : {       'vendor': 'juniper',
                     'model' : 'mx',
                     'asn'   : '64512',
                     'name'  : 'hooper',
                     'ssh_username' : 'root',
                     'ssh_password' : 'c0ntrail123',
                     'mgmt_ip'  : '10.204.217.240',
             }
}

env.openstack_admin_password = 'contrail123'
env.password = 'c0ntrail123'
env.passwords = {
    host1: 'c0ntrail123',
    host2: 'c0ntrail123',
    host3: 'c0ntrail123',
    host4: 'c0ntrail123',
    host5: 'c0ntrail123',
    host6: 'c0ntrail123',

    host_build: 'stack@123',
}

env.ostypes = {
    host1:'ubuntu',
    host2:'ubuntu',
    host3:'ubuntu',
    host4:'ubuntu',
    host5:'ubuntu',
    host6:'ubuntu',
}

control_data = {
    host1 : { 'ip': '192.168.192.6/24', 'gw' : '192.168.192.254', 'device':'p1p2' },
    host2 : { 'ip': '192.168.192.5/24', 'gw' : '192.168.192.254', 'device':'p1p2' },
    host3 : { 'ip': '192.168.192.4/24', 'gw' : '192.168.192.254', 'device':'p1p2' },
    host4 : { 'ip': '192.168.192.1/24', 'gw' : '192.168.192.254', 'device':'p6p2', 'vlan': '128' },
    host5 : { 'ip': '192.168.192.2/24', 'gw' : '192.168.192.254', 'device':'p6p2', 'vlan': '128' },
    host6 : { 'ip': '192.168.192.3/24', 'gw' : '192.168.192.254', 'device':'p6p2', 'vlan': '128' },
}

env.ha = {
    'internal_vip' : '192.168.192.251',
}
ha_setup = True

env.cluster_id='clusterc7c8g36i1i2i3'
minimum_diskGB=32
env.test_repo_dir='/home/stack/multi_interface_parallel/ubuntu-14.04/icehouse/contrail-test'
env.rsyslog_params = {'port':19876, 'proto':'tcp', 'collector':'dynamic', 'status':'enable'}
env.mail_from='contrail-build@juniper.net'
env.mail_to='dl-contrail-sw@juniper.net'
multi_tenancy=True
env.interface_rename = True
env.encap_priority =  "'VXLAN','MPLSoUDP','MPLSoGRE'"
env.log_scenario='Multi-Interface HA Sanity[mgmt, ctrl=data]'
env.enable_lbaas = True
do_parallel = True

enable_ceilometer = True
ceilometer_polling_interval = 60
