from fabric.api import env

os_username = 'admin'
os_password = 'contrail123'
os_tenant_name = 'demo'
 
host1 = 'root@10.204.217.13'
host2 = 'root@10.204.217.77'
host3 = 'root@10.204.217.176'
host4 = 'root@10.204.217.129'
host5 = 'root@10.204.217.131' 
host6 = 'root@10.204.217.132' 


ext_routers = []
router_asn = 64512
database_dir = '/home/cassandra'

 
#Host from which the fab commands are triggered to install and provision
host_build = 'stack@10.204.216.49'
 
env.roledefs = {

    'all': [host1, host2, host3, host4, host5, host6],
    'cfgm': [host1, host2, host3],
    'openstack': [host1, host2, host3],
    'control': [host1, host2, host3],
    'compute': [host4, host5, host6],
    'collector': [host1, host2, host3],
    'webui': [host1, host2, host3],
    'database': [host1, host2, host3],
    'build': [host_build],


}
 
env.hostnames ={
    'all': ['nodec28', 'nodeg37', 'nodec10', 'nodei17', 'nodei19', 'nodei20']
}

#Openstack admin password
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

bond= {
    host6 : { 'name': 'bond0', 'member': ['eth1','eth2','eth3'],'mode':'802.3ad' },
}

control_data = {
    host1 : { 'ip': '192.168.100.11/24', 'gw' : '', 'device':'eth1' },
    host2 : { 'ip': '192.168.100.12/24', 'gw' : '', 'device':'eth1' },
    host3 : { 'ip': '192.168.100.13/24', 'gw' : '', 'device':'eth1' },
    host4 : { 'ip': '192.168.100.14/24', 'gw' : '', 'device':'eth1' },
    host5 : { 'ip': '192.168.100.15/24', 'gw' : '', 'device':'eth1' },
    host6 : { 'ip': '192.168.100.16/24', 'gw' : '', 'device':'bond0' },
}

# VIP
env.ha = {
    'internal_vip' : '192.168.100.10',
}

#To enable multi-tenancy feature
multi_tenancy = True
env.xmpp_auth_enable=True
env.xmpp_dns_auth_enable=True
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"
env.enable_lbaas = True
do_parallel = True
enable_ceilometer = True
ceilometer_polling_interval = 60
minimum_diskGB=32
env.test_repo_dir='/home/stack/smgr_github_ubuntu_multi_node/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='dl-contrail-sw@juniper.net'
env.log_scenario='Server Manager Multi-Interface HA Sanity'
env.rsyslog_params = {'port':19876, 'proto':'tcp', 'collector':'dynamic', 'status':'enable'}
