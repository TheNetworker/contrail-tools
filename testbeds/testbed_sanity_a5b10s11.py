from fabric.api import env
import os

#Management ip addresses of hosts in the cluster
host1 = 'root@10.87.119.23'
host2 = 'root@10.87.119.24'
host3 = 'root@10.87.119.25'
host4 = 'root@10.87.67.171'
host5 = 'root@10.87.67.172'
host6 = 'root@10.87.67.173'
host7 = 'root@10.87.67.174'
host8 = 'root@10.87.67.176'

kvm_a5b7s11 = 'root@10.87.119.1'
kvm_a5b7s12 = 'root@10.87.119.2'
kvm_a5b7s13 = 'root@10.87.119.3'

reimage_param = os.getenv('REIMAGE_PARAM', 'ubuntu-14.04.2')

vm_node_details = {
    'default': {
                'image_dest' : '/mnt/disk1/images/',
                'ram' : '32768',
                'vcpus' : '4',
                'disk_format' : 'qcow2',
                'image_source' : 'http://10.84.5.120/images/node_vm_images/%s-256G.img.gz' % (reimage_param),
                },
    host1 : {
                'name' : '5b7s11-vm5',
                'server': kvm_a5b7s11,
                'network' : [{'bridge' : 'br0', 'mac':'62:53:55:11:00:01'},
                             {'bridge' : 'br1'}
                            ],
            },
    host2 : {
                'name' : '5b7s12-vm5',
                'server': kvm_a5b7s12,
                'network' : [{'bridge' : 'br0', 'mac':'62:53:55:21:00:02'},
                             {'bridge' : 'br1'}
                            ],
            },
    host3 : {
                'name' : '5b7s13-vm5',
                'server': kvm_a5b7s13,
                'network' : [{'bridge' : 'br0', 'mac':'62:53:55:31:00:03'},
                             {'bridge' : 'br1'}
                            ],
            }
}

#External routers if any
ext_routers = [('5b7-mx80-1', '10.87.123.244')]

#Autonomous system number
router_asn = 64522

#Host from which the fab commands are triggered to install and provision
host_build = 'root@10.84.24.64'

#Role definition of the hosts.
env.roledefs = {
    'all': [host1, host2, host3, host4, host5, host6, host7, host8],
    'openstack': [host1, host2, host3],
    'webui': [host1, host2, host3],
    'cfgm': [host1, host2, host3],
    'control': [host1, host2, host3],
    'collector': [host1, host2, host3],
    'database': [host1, host2, host3],
    'compute': [host4, host5, host6, host7, host8],
    'build': [host_build],
}

env.hostnames = {
    host1: '5b7s11-vm5',
    host2: '5b7s12-vm5',
    host3: '5b7s13-vm5',
    host4: '5b10s11',
    host5: '5b10s12',
    host6: '5b10s13',
    host7: '5b10s14',
    host8: '5b10s32',
}

if os.getenv('AUTH_PROTOCOL',None) == 'https':
    if os.getenv('KEYSTONE_VERSION',None) == 'v3':
        env.log_scenario='Multi-Interface Sanity[mgmt, ctrl=data, DPDK, Keystone=v3, https]'
        env.keystone = {
            'version': 'v3',
            'auth_protocol': 'https'
        }
    else:
        env.log_scenario='Multi-Interface Sanity[mgmt, ctrl=data, DPDK, Keystone=v2, https]'
        env.keystone = {
            'auth_protocol': 'https'
        }
    env.cfgm = {
        'auth_protocol': 'https'
    }
else:
    env.log_scenario='Multi-Interface Sanity[mgmt, ctrl=data, DPDK, Keystone=v2]'

# RBAC
if os.getenv('ENABLE_RBAC',None) == 'true':
    cloud_admin_role = 'admin'
    aaa_mode = 'rbac'

#Openstack admin password
env.openstack_admin_password = 'c0ntrail123'

env.password = 'c0ntrail123'
#Passwords of each host
env.passwords = {
    host1: 'c0ntrail123',
    host2: 'c0ntrail123',
    host3: 'c0ntrail123',
    host4: 'c0ntrail123',
    host5: 'c0ntrail123',
    host6: 'c0ntrail123',
    host7: 'c0ntrail123',
    host8: 'c0ntrail123',
    host_build: 'c0ntrail123',
}

#For reimage purpose
env.ostypes = {
    host1: 'ubuntu',
    host2: 'ubuntu',
    host3: 'ubuntu',
    host4: 'ubuntu',
    host5: 'ubuntu',
    host6: 'ubuntu',
    host7: 'ubuntu',
    host8: 'ubuntu',
}

#OPTIONAL BONDING CONFIGURATION
#==============================
#Inferface Bonding
#OPTIONAL BONDING CONFIGURATION
#==============================
#Inferface Bonding
bond= {
    host4 : { 'name': 'bond0', 'member': ['p514p1','p514p2'], 'mode':'802.3ad' },
    host5 : { 'name': 'bond0', 'member': ['p514p1','p514p2'], 'mode':'802.3ad' },
    host6 : { 'name': 'bond0', 'member': ['p514p1','p514p2'], 'mode':'802.3ad' },
    host7 : { 'name': 'bond0', 'member': ['p514p1','p514p2'], 'mode':'802.3ad' },
    host8 : { 'name': 'bond0', 'member': ['p514p1','p514p2','p414p1','p414p2'], 'mode':'802.3ad' },
}

#env.sriov = {
#    host16 :[ {'interface' : 'p514p2', 'VF' : 31, 'physnets' : ['physnet1', 'physnet2']} ]
#    #host7 :[ {'interface' : 'p514p1', 'VF' : 7, 'physnets' : ['physnet1', 'physnet3']},{'interface' : 'p514p2', 'VF' : 31, 'physnets' : ['physnet2', 'physnet4']} ]
#}

#OPTIONAL SEPARATION OF MANAGEMENT AND CONTROL + DATA
#====================================================
#Control Interface
#control = {
#    host1 : { 'ip': '10.87.140.197/22', 'gw' : '10.87.159.254', 'device':'eth0' },
#    host2 : { 'ip': '10.87.140.198/22', 'gw' : '10.87.159.254', 'device':'eth0' },
#    host3 : { 'ip': '10.87.140.199/22', 'gw' : '10.87.159.254', 'device':'eth0' },
#}

#Data Interface
control_data = {
   host1 : { 'ip': '192.16.7.31/24', 'gw' : '192.16.7.100', 'device':'eth1', 'vlan':'150' },
   host2 : { 'ip': '192.16.7.32/24', 'gw' : '192.16.7.100', 'device':'eth1', 'vlan':'150' },
   host3 : { 'ip': '192.16.7.33/24', 'gw' : '192.16.7.100', 'device':'eth1', 'vlan':'150' },
   host4 : { 'ip': '192.16.7.34/24', 'gw' : '192.16.7.100', 'device':'bond0', 'vlan':'150' },
   host5 : { 'ip': '192.16.7.35/24', 'gw' : '192.16.7.100', 'device':'bond0', 'vlan':'150' },
   host6 : { 'ip': '192.16.7.36/24', 'gw' : '192.16.7.100', 'device':'bond0', 'vlan':'150' },
   host7 : { 'ip': '192.16.7.37/24', 'gw' : '192.16.7.100', 'device':'bond0', 'vlan':'150' },
   host8 : { 'ip': '192.16.7.38/24', 'gw' : '192.16.7.100', 'device':'bond0', 'vlan':'150' },

}

#To disable installing contrail interface rename package
env.interface_rename = False

#To use existing service_token
#service_token = 'your_token'

#Specify keystone IP
#keystone_ip = '1.1.1.1'

#Specify Keystone admin user if not same as  admin
#keystone_admin_user = 'nonadmin'

#Specify Keystone admin password if not same as env.openstack_admin_password
#keystone_admin_password = 'contrail123'

#Specify Region Name
#region_name = 'RegionName'

#To enable multi-tenancy feature
#multi_tenancy = True

#To enable haproxy feature
#haproxy = True

#To Enable prallel execution of task in multiple nodes
#do_parallel = True

# To configure the encapsulation priority. Default: MPLSoGRE
#env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"

#Ceph related

#storage_node_config = {
#    host2 : { 'disks' : ['/dev/sdc', '/dev/sdd'] , 'journal' : ['/dev/sdb'] },
#    host3 : { 'disks' : ['/dev/sdb'] , 'journal' : ['/dev/sdb'] },
#}
#if os.getenv('HA_TEST',None) == 'True':
env.ha = {
    'external_vip' : '10.87.119.26',
    'external_virtual_router_id' : 115
    #'contrail_external_vip' : '10.87.119.27',
    #'contrail_external_virtual_router_id' : 112
}
#if os.getenv('AUTH_PROTOCOL',None) != 'https':
#    env.ha['internal_vip'] = '192.16.7.28'
#    env.ha['contrail_internal_vip'] = '192.16.7.27'
env.ha['internal_vip'] = '192.16.7.26'
env.ha['internal_virtual_router_id'] = 116
#env.ha['contrail_internal_vip'] = '192.16.7.27'
#env.ha['contrail_internal_virtual_router_id'] = 114

# HA Test configuration
ha_setup = 'True'
minimum_diskGB=32
env.mail_from='jebap@juniper.net'
env.mail_to='jebap@juniper.net'
multi_tenancy=True
env.encap_priority="'MPLSoUDP','MPLSoGRE','VXLAN'"
env.mail_server='10.84.24.64'
env.mail_port='4000'
env.mx_gw_test=False
env.testbed_location='US'
env.interface_rename = False
env.image_web_server = '10.84.5.120'
#env.log_scenario='Multi-Interface Sanity[mgmt, ctrl=data, CEPH]'


#storage_replica_size = 2

env.test = {
'mail_to' :'jebap@juniper.net',
}
env.test_repo_dir='/root/contrail-test'
