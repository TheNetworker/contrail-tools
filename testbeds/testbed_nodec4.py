from fabric.api import env

os_username = 'admin'
os_password = 'contrail123'
os_tenant_name = 'demo'

host1 = 'root@10.204.216.61'
host2 = 'root@10.204.216.62'
host3 = 'root@10.204.217.11'
host4 = 'root@10.204.217.139'
host5 = 'root@10.204.217.140'


ext_routers = [('blr-mx2', '10.204.216.245')]
router_asn = 64512
public_vn_rtgt = 19005
public_vn_subnet = "10.204.219.96/29"

host_build = 'stack@10.204.216.49'

env.roledefs = {
    'all': [host1, host2, host3, host4, host5],
    'cfgm': [host1],
    'control': [host2, host3],
    'compute': [host4, host5],
    'collector': [host1],
    'openstack': [host1],
    'webui': [host1],
    'database': [host1],
    'build': [host_build],
}

env.hostnames = {
     'all': ['nodec4', 'nodec5', 'nodec26', 'nodei27', 'nodei28']
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
    host1: 'ubuntu',
    host2: 'ubuntu',
    host3: 'ubuntu',
    host4: 'ubuntu',
    host5: 'ubuntu'
    }
env.test_repo_dir='/home/stack/multi_interface_parallel/centos65/icehouse/contrail-test'                                                                                                                                                                                      
env.mail_from='contrail-build@juniper.net'                                                                                                                                                                                                                                    
env.mail_to='ganeshahv@juniper.net'                                                                                                                                                                                                                                      
multi_tenancy=True                                                                                                                                                                                                                                                            
env.interface_rename = True                                                                                                                                                                                                                                                   
minimum_diskGB=32
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"                                                                                                                                                                                                                         
env.log_scenario='ECMP Regression'
