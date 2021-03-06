from fabric.api import env
import os

host1 = 'root@10.204.216.64'
host2 = 'root@10.204.216.65'
host3 = 'root@10.204.216.153'
host4 = 'root@10.204.217.76'
host5 = 'root@10.204.216.150'
host6 = 'root@10.204.217.114'
host7 = 'root@10.204.217.115'

ext_routers = [('hooper','192.168.192.253')]
#IP Fabric gateway info, name and IP tuple
#eg: [('mx1', '1.1.1.1')]
fabric_gw =[('sw166', '10.204.217.254')]
router_asn = 64512
public_vn_rtgt = 2223
public_vn_subnet = '10.204.221.176/28'

host_build = 'stack@10.204.216.49'


env.roledefs = {
    'all': [host1, host2, host3, host4, host5, host6, host7],
    'contrail-controller': [host1, host2, host3],
    'openstack': [host1, host2, host3],
    'contrail-analytics': [host1, host2, host3],
    'contrail-lb': [host4],
    'contrail-compute': [host5, host6, host7],
    'contrail-analyticsdb': [host1, host2, host3],
    'build': [host_build],
}

if os.getenv('AUTH_PROTOCOL',None) == 'https':
    env.log_scenario='Multi-Interface Container Contrail HA Sanity[mgmt, ctrl=data, SSL]'
    env.keystone = {
        'auth_protocol': 'https'
    }
    env.cfgm = {
        'auth_protocol': 'https'
    }
else:
    env.log_scenario='Multi-Interface Container Contrail HA Sanity[mgmt, ctrl=data]'

if os.getenv('ENABLE_RBAC',None) == 'true':
    cloud_admin_role = 'admin'
    aaa_mode = 'rbac'

env.hostnames = {
    'all': ['nodec7', 'nodec8', 'nodec57', 'nodeg36', 'nodei1', 'nodei2', 'nodei3']
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

env.kernel_upgrade=False
env.openstack = {  
    'manage_amqp': "true"
}

env.keystone = {   
    'admin_password': 'contrail123'
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
    host7: 'c0ntrail123',

    host_build: 'stack@123',
}

env.ostypes = {
    host1:'ubuntu',
    host2:'ubuntu',
    host3:'ubuntu',
    host4:'ubuntu',
    host5:'ubuntu',
    host6:'ubuntu',
    host7:'ubuntu',
}

control_data = {
    host1 : { 'ip': '192.168.192.6/24', 'gw' : '192.168.192.254', 'device':'enp1s0f1' },
    host2 : { 'ip': '192.168.192.5/24', 'gw' : '192.168.192.254', 'device':'enp1s0f1' },
    host3 : { 'ip': '192.168.192.7/24', 'gw' : '192.168.192.254', 'device':'enp1s0f1' },
    host4 : { 'ip': '192.168.192.4/24', 'gw' : '192.168.192.254', 'device':'enp1s0f1' },
    host5 : { 'ip': '192.168.192.1/24', 'gw' : '192.168.192.254', 'device':'enp4s0f1', 'vlan': '128' },
    host6 : { 'ip': '192.168.192.2/24', 'gw' : '192.168.192.254', 'device':'enp4s0f1', 'vlan': '128' },
    host7 : { 'ip': '192.168.192.3/24', 'gw' : '192.168.192.254', 'device':'enp4s0f1', 'vlan': '128' }
}

env.ha = {
    'contrail_internal_vip' : '192.168.192.4',
    'contrail_external_vip' : '10.204.217.76',
    'internal_vip' : '192.168.192.8',
    'external_vip' : '10.204.216.130'
}

env.test = {
  'mail_to' : 'dl-contrail-sw@juniper.net',
  'webserver_host': '10.204.216.50',
  'webserver_user' : 'bhushana',
  'webserver_password' : 'c0ntrail!23',
  'webserver_log_path' :  '/home/bhushana/Documents/technical/logs',
  'webroot' : 'Docs/logs',
  'mail_server' :  '10.204.216.49',
  'mail_port' : '25',
  'mail_sender': 'contrailbuild@juniper.net'
}

ha_setup = True

env.cluster_id='clusterc7c8g36i1i2i3'
minimum_diskGB=32
env.test_repo_dir='/root/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='dl-contrail-sw@juniper.net'
multi_tenancy=True
env.interface_rename = True
env.encap_priority =  "MPLSoUDP,MPLSoGRE,VXLAN"
env.enable_lbaas = True
do_parallel = True
env.xmpp_auth_enable=True
env.xmpp_dns_auth_enable=True
