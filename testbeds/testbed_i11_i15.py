from fabric.api import env

host1 = 'root@10.204.217.123'
host2 = 'root@10.204.217.124'
host3 = 'root@10.204.217.125'
host4 = 'root@10.204.217.126'
host5 = 'root@10.204.217.127'
host6 = 'root@10.204.217.138'

ext_routers = [('hooper','10.204.217.240')]
router_asn = 64512
public_vn_rtgt = 2225
public_vn_subnet = '10.204.221.160/28'

host_build = 'stack@10.204.216.49'

env.roledefs = {
    'all': [host1, host2, host3, host4, host5, host6],
    'cfgm': [host1, host2],
    'webui': [host1],
    'openstack': [host1],
    'control': [host2, host3],
    'collector': [host1],
    'database': [host1],
    'compute': [host4, host5, host6],
    'build': [host_build]
}

env.hostnames = {
    'all': ['nodei11', 'nodei12', 'nodei13', 'nodei14', 'nodei15', 'nodei26']
}
env.interface_rename = True

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
    host1:'centos65',
    host2:'centos65',
    host3:'centos65',
    host4:'centos65',
    host5:'centos65',
    host6:'centos65',
}
minimum_diskGB=32
env.test_repo_dir='/home/stack/multi_interface_parallel/centos65/icehouse/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='dl-contrail-sw@juniper.net'
multi_tenancy=True
env.interface_rename = True
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"
env.log_scenario='MultiNode Single Intf Sanity'
env.enable_lbaas = True
do_parallel = True
