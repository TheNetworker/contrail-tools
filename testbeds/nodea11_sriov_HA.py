from fabric.api import env

a11 = '10.204.216.7'
a18 = '10.204.216.14'
a19 = '10.204.216.15'
#g25 = '10.204.217.65'
#g26 = '10.204.217.66'
#g27 = '10.204.217.67'
#k9 =  '10.204.216.229'
l5 = '10.204.217.212'
l6 = '10.204.217.215'
l3 =  '10.204.217.209'

#nodeg25_vm = '10.204.217.26'
#nodeg26_vm = '10.204.217.27'
#nodeg27_vm = '10.204.217.28'

nodel5_vm = '10.204.217.26'
nodel6_vm = '10.204.217.27'
#nodel7_vm = '10.204.217.28'

host1 = 'root@10.204.216.7'
host2 = 'root@10.204.216.14'
host3 = 'root@10.204.216.15'
host4 = 'root@10.204.217.26'
host5 = 'root@10.204.217.27'
host6 = 'root@10.204.217.209'
host7 = 'root@10.204.216.10'
esx2 = 'root@10.204.217.212'
esx3 = 'root@10.204.217.215'
#esx4 = 'root@' + l7


ext_routers = [('blr-mx1', '10.204.216.253')]
router_asn = 64510
public_vn_rtgt = 19006
public_vn_subnet = "10.204.219.80/29"

host_build = 'stack@10.204.216.49'
#host_build = 'root@10.204.216.7'

env.roledefs = {
    #'all': [host1, host2, host3, host4,host5, host6, host7, host10],
    #'all': [host1, host2, host3, host4,host5,host6],
    'all': [host1, host2, host3, host4,host5,host6,host7],
    'cfgm': [host1,host2,host3],
    'openstack': [host7],
    'vcenter_compute': [host7],
    'webui': [host1],
    'control': [host2, host3],
    'collector': [host2,host3],
    'database': [host1,host2,host3],
    'compute': [host4,host5,host6],
    'build': [host_build]
}

env.hostnames = {
    #'all': ['nodea11', 'nodea18', 'nodea19', 'nodek9','nodel5-compute-vm','nodel7-compute-vm','nodel7-compute-vm']
    'all': ['nodea11', 'nodea18', 'nodea19', 'nodel5-compute-vm','nodel6-compute-vm', 'nodel3','nodea14']
}

env.password = 'c0ntrail123'
env.passwords = {
    host1: 'c0ntrail123',
    host2: 'c0ntrail123',
    host3: 'c0ntrail123',
    host4: 'c0ntrail123',
    host5: 'c0ntrail123',
    host6: 'c0ntrail123',
    host7: 'c0ntrail123',
    #host10: 'c0ntrail123',
    esx2: 'c0ntrail123',
    esx3: 'c0ntrail123',
    #esx4: 'c0ntrail123',
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
    #host10:'ubuntu',
}

#env.orchestrator = 'vcenter'
control_data = {
    host1 : { 'ip': '192.168.250.2/24', 'gw' : '192.168.250.254', 'device':'em1' },
    host2 : { 'ip': '192.168.250.3/24', 'gw' : '192.168.250.254', 'device':'em1' },
    host3 : { 'ip': '192.168.250.4/24', 'gw' : '192.168.250.254', 'device':'em1' },
    host7 : { 'ip': '192.168.250.5/24', 'gw' : '192.168.250.254', 'device':'em1' },
    host4 : { 'ip': '192.168.250.6/24', 'gw' : '192.168.250.254', 'device':'eth20' },
    host5 : { 'ip': '192.168.250.7/24', 'gw' : '192.168.250.254', 'device':'eth20' },
    host6 : { 'ip': '192.168.250.8/24', 'gw' : '192.168.250.254', 'device':'em2' },
}
env.vcenter_servers = {
     'vcenter1':{   
        'server':'10.204.217.189',
        'port': '443',
        'username': 'administrator@vsphere.local',
        'password': 'Contrail123!',
        'auth': 'https',
        'datacenter': 'a11a29',
        'cluster': ['a11a29_blr'],
        'vcenter_compute':'10.204.216.10',
        'dv_switch': { 'dv_switch_name': 'a11a29_dvs',},
        'dv_port_group': { 'dv_portgroup_name': 'a11a29_dvpg', 'number_of_ports': '3', },
        'dv_switch_sr_iov': {
            'dv_switch_name': 'dvs-sriov',
        },
        'dv_port_group_sr_iov': {
            'dv_portgroup_name': 'dvs-sriov-pg',
            'number_of_ports': '2',
        },
 
    }
}

esxi_hosts = {
    'nodel5' : {
        'ip' : l5,
        'vcenter_server' : 'vcenter1', 
        'username' : 'root',
        'password' : 'c0ntrail123',
        'cluster' : 'a11a29_blr',
        'datastore' : '/vmfs/volumes/l5-ds',
        'contrail_vm' : {
            'name' : 'nodel5-compute-vm',
            'mac' : '52:54:00:29:26:b9',
            'host' : 'root@10.204.217.26',
            'pci_devices':{
                'nic':["02:00.1"]
                },
            'mode': "vcenter",
            'vmdk' : '/cs-shared-test/images/Ubuntu-precise-14.04-LTS.vmdk',
        }
    },
    'nodel6' : {
        'ip' : l6,
        'vcenter_server' : 'vcenter1', 
        'username' : 'root',
        'password' : 'c0ntrail123',
        'cluster' : 'a11a29_blr',
        'datastore' : '/vmfs/volumes/l6-ds',
        'contrail_vm' : {
            'name' : 'nodel6-compute-vm',
            'mac' : '52:54:00:cd:ff:b9',
            'host' : 'root@10.204.217.27',
            'sr_iov_nics': ['vmnic3'],
            'mode': "vcenter",
            'vmdk' : '/cs-shared-test/images/Ubuntu-precise-14.04-LTS.vmdk',
        }
    },
}

# VIP
env.ha = {
    'contrail_internal_vip' : '192.168.250.10',
    'contrail_external_vip' : '10.204.216.125',
}

minimum_diskGB=32
env.test_repo_dir='/root/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='sandipd@juniper.net'
multi_tenancy=True
env.interface_rename = False
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"
env.log_scenario='Vcenter as Compute MultiNode Single Intf Sanity'
env.enable_lbaas = True
do_parallel = True
env.ntp_server = 'ntp.juniper.net'

#enable ceilometer
#enable_ceilometer = True
#ceilometer_polling_interval = 60
