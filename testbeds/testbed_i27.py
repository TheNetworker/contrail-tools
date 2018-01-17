from fabric.api import env
import os

host1 = 'root@10.204.217.139'
host2 = 'root@10.204.217.140'
host3 = 'root@10.204.217.144'
host4 = 'root@10.204.217.204'
host5 = 'root@10.204.217.229'
host6 = 'root@10.204.217.181'
esx1 = 'root@10.204.217.147'
esx2 = 'root@10.204.217.148'
esx3 = 'root@10.204.217.123'
host_build = 'stack@10.204.216.49'

if os.getenv('HA_TEST',None) == 'True':
    env.roledefs = {
        'all': [host1, host2,host3, host4, host5, host6],
        'cfgm': [host1, host2,host3],
        'webui': [host1, host2,host3],
        'control': [host1, host2,host3],
        'collector': [host1,host2,host3],
        'database': [host1,host2,host3],
        'compute': [host4, host5, host6],
        'build': [host_build]
    }
else:
    env.roledefs = {
        'all': [host1, host2,host3, host4, host5, host6],
        'cfgm': [host1, host2,host3],
        'webui': [host1, host2,host3],
        'control': [host1, host2,host3],
        'collector': [host1,host2,host3],
        'database': [host1,host2,host3],
        'compute': [host4, host5, host6],
        'build': [host_build]
    }
env.hostnames = {
    'all': ['nodei27', 'nodei28' ,'nodei32', 'nodei35-compute-vm', 'nodei36-compute-vm', 'nodei11-compute-vm']
}

env.password = 'c0ntrail123'
env.passwords = {
    host1: 'c0ntrail123',
    host2: 'c0ntrail123',
    host3: 'c0ntrail123',
    host4: 'c0ntrail123',
    host5: 'c0ntrail123',
    host6: 'c0ntrail123',
    esx1: 'c0ntrail123',
    esx2: 'c0ntrail123',
    esx3: 'c0ntrail123',
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

env.orchestrator = 'vcenter'

env.vcenter_servers = {
     'server1':{
        'server':'10.204.217.246',
        'port': '443',
        'username': 'administrator@vsphere.local',
        'password': 'Contrail123!',
        'auth': 'https',
         'datacenters' : {
             'i27_datacenter11' : {
                 'datacenter_mtu': '1500',
                 'dv_switches': {
                     'vm_dvs2': {
                         'dv_switch_version': '6.5.0',
                         'dv_port_group': { 
                             'dv_portgroup_name': 'vm_dvs_pg2', 
                             'number_of_ports': '3', },
                     'clusters': ['i27_cluster11','i27_cluster12'],
                   },
               },

        'dv_switch-fab': { 
            'dv_switch_name': 'fab_dvs', 
            'dv_port_group_fab': { 'dv_portgroup_name': 'fab-pg', 'number_of_ports': '3', },
            },  
          },
         },
        },
    }


esxi_hosts = {
    'nodei35' : {
        'ip' : '10.204.217.147',
        'vcenter_server':'server1',
        'username' : 'root',
        'password' : 'c0ntrail123',
        'datastore' : '/vmfs/volumes/nodei35-ds',
        'datacenter': 'i27_datacenter11',
        'cluster': 'i27_cluster11',
        'skip_reimage'  : 'true',
        'contrail_vm' : {
            'name' : 'nodei35-compute-vm',
            'mac' : '00:77:56:cd:bc:ba',
            'host' : host4,
            'mode': 'vcenter',
            'vmdk' : '/cs-shared/images/vcenter-vmdk/ContrailVM-disk1.vmdk',
        }
    },
    'nodei36' : {
        'vcenter_server':'server1',
        'ip' : '10.204.217.148',
        'username' : 'root',
        'password' : 'c0ntrail123',
        'datacenter': 'i27_datacenter11',
        'cluster' : 'i27_cluster11',
        'datastore' : '/vmfs/volumes/nodei36-ds',
        'skip_reimage'  : 'true',
        'contrail_vm' : {
            'name' : 'nodei36-compute-vm',
            'mac' : '00:77:56:aa:ba:ba',
            'host' : host5,
            'mode': 'vcenter',
            'vmdk' : '/cs-shared/images/vcenter-vmdk/ContrailVM-disk1.vmdk',
        }
    },
    'nodei11' : {
        'vcenter_server':'server1',
        'ip' : '10.204.217.123',
        'username' : 'root',
        'password' : 'c0ntrail123',
        'datacenter': 'i27_datacenter11',
        'cluster' : 'i27_cluster11',
        'datastore' : '/vmfs/volumes/nodei11-ds',
        'skip_reimage'  : 'true',
        'contrail_vm' : {
            'name' : 'nodei11-compute-vm',
            'mac' : '00:50:56:a6:25:04',
            'host' : host6,
            'mode': 'vcenter',
            'vmdk' : '/cs-shared/images/vcenter-vmdk/ContrailVM-disk1.vmdk',
        }
    },


}
# HA configuration:

env.test = {
     'mail_to': 'dl-contrail-sw@juniper.net',
           }

env.cluster_id='cluster-esxi-new'
minimum_diskGB=32
env.test_repo_dir='/home/stack/multi_interface_parallel/centos65/icehouse/contrail-test'
env.mail_from='contrail-build@juniper.net'
env.mail_to='dl-contrail-sw@juniper.net'
env.interface_rename = False
env.encap_priority =  "'MPLSoUDP','MPLSoGRE','VXLAN'"
env.log_scenario='Vcenter MultiNode Single Intf Sanity'
#do_parallel = True
env.ntp_server = '10.204.217.158'
env.optional_services = {
    'cfgm' : ['device-manager'],
}
