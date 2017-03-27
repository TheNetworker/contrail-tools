import sys
import json
from fabric.api import *
import paramiko
import os
import subprocess
import ast
import uuid
import random
import string
import time

# with open("floating_ip_test_multiple.json") as json_data:
if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print '''
	THE CORRECT FORMAT OF USING THIS SCRIPT IS:
		python inp_to_yaml.py <input_json_file> <function_to_perform>
	EXAMPLE :
		python inp_to_yaml.py input.json create_network_yaml > network.yaml
	'''
    sys.exit()

inp_file = sys.argv[1]
with open(inp_file) as json_data:
    parsed_json = json.load(json_data)


description = parsed_json["inp_params"]["description"]["msg"]
total_servers = parsed_json["inp_params"]["params"]["no_of_servers"]
total_networks = parsed_json["inp_params"]["params"]["no_of_networks"]

network_name_list = []
# parse all the data from the json file into a dict so that it an be used
# in the script

# Creating all The Dictionaries from the input json file that are required
# for all the functions to work properly in a scalable manner

#server_dict = parsed_json["inp_params"]["servers"]
server_dict = {}
network_dict = parsed_json["inp_params"]["networks"]
#cluster_dict = parsed_json["inp_params"]["cluster_json_params"]
cluster_dict = {}
floating_ip_network_dict = parsed_json["inp_params"]["floating_ip_network"]
general_params_dict = parsed_json["inp_params"]["params"]
#testbed_py_dict = parsed_json["inp_params"]["testbed_py_params"]
testbed_py_dict = {}
all_cluster_dict = parsed_json["inp_params"]["cluster"]

for clus in all_cluster_dict:
    server_dict[clus] = all_cluster_dict[clus]["servers"]
    cluster_dict[clus] = all_cluster_dict[clus]["cluster_json_params"]
    testbed_py_dict[clus] = all_cluster_dict[clus]["testbed_py_params"]

for i in network_dict:
    network_name_list.append(network_dict[i]["name"])
    # A list to maintain all the network names


def add_sm_os_to_openstack():
    a = subprocess.Popen(
        "openstack image list -f json",
        shell=True,
        stdout=subprocess.PIPE)
    a_tmp = a.stdout.read()
    a_tmp_dict = eval(a_tmp)
    a_tmp = ""
    for i in a_tmp_dict:
        if i["Name"] == "ubuntu-14-04":
            a_tmp = "ubuntu-14-04"
    if len(a_tmp) == 0:
        print "The Requested Image is not present in the cluster, Downloading it ----->>\n"
        ab = subprocess.Popen(
            "wget http://10.84.5.120/images/soumilk/vm_images/ubuntu14-04-5.qcow2",
            shell=True,
            stdout=subprocess.PIPE)
        ab_tmp = a.stdout.read()
        print a_tmp
        time.sleep(10)
        a = subprocess.Popen(
            "openstack image create --disk-format qcow2 --container-format bare --public --file ubuntu14-04-5.qcow2 ubuntu-14-04",
            shell=True,
            stdout=subprocess.PIPE)
        a_tmp = a.stdout.read()
        print a_tmp
        time.sleep(5)
        a = subprocess.Popen(
            "openstack image list | grep ubuntu-14-04",
            shell=True,
            stdout=subprocess.PIPE)
        a_tmp = a.stdout.read()
        print a_tmp
    else:
        print "Requested Image already exists in the cluster "


def check_if_sm_has_correct_image():
    for clus in server_dict:
        for server in server_dict[clus]:
            if server_dict[clus][server]["server_manager"] == "true":
                # First change the image_val in input.json
                server_dict[clus][server]["image"] = "ubuntu-14-04"
                print server_dict[clus][server]
                a = subprocess.Popen(
                    "openstack image list -f json",
                    shell=True,
                    stdout=subprocess.PIPE)
                a_tmp = a.stdout.read()
                a_tmp_dict = eval(a_tmp)
                a_tmp = ""
                for i in a_tmp_dict:
                    if i["Name"] == "ubuntu-14-04":
                        a_tmp = "ubuntu-14-04"
                if len(a_tmp) == 0:
                    b = subprocess.Popen(
                        "wget http://10.84.5.120/images/soumilk/vm_images/ubuntu14-04-5.qcow2",
                        shell=True,
                        stdout=subprocess.PIPE)
                    b_tmp = b.stdout.read()
                    print b_tmp
                    print "Image for server manager downloaded"
                    a = subprocess.Popen(
                        "openstack image create --disk-format qcow2 --container-format bare --public --file ubuntu14-04-5.qcow2 ubuntu-14-04",
                        shell=True,
                        stdout=subprocess.PIPE)
                    a_tmp = a.stdout.read()
                    print a_tmp

                else:
                    print "Server Image already exists in the cluster"

# A method for checking if the required falvor exists in the openstack, if
# not creating it.


def check_and_create_required_flavor():
    chk_flavor = subprocess.Popen(
        "openstack flavor list  | grep m1.xxlarge",
        shell=True,
        stdout=subprocess.PIPE)
    chk_flavor_tmp = chk_flavor.stdout.read()
    if len(chk_flavor_tmp) == 0:
        print "The Recommended Flavor is not present on the base cluster, Adding it :-\n"
        add_flavor = subprocess.Popen(
            "openstack flavor create m1.xxlarge --id 100 --ram 32768 --disk 300 --vcpus 10 --public",
            shell=True,
            stdout=subprocess.PIPE)
        add_flavor_tmp = add_flavor.stdout.read()
        print add_flavor_tmp
        print "Printing all the Flavors Present on the base cluster:-"
        chk_flavor = subprocess.Popen(
            "openstack flavor list",
            shell=True,
            stdout=subprocess.PIPE)
        chk_flavor_tmp = chk_flavor.stdout.read()
        print chk_flavor_tmp
    else:
        print "The Recommended Flavor is Present in the Base Cluster"
        chk_flavor = subprocess.Popen(
            "openstack flavor list",
            shell=True,
            stdout=subprocess.PIPE)
        chk_flavor_tmp = chk_flavor.stdout.read()
        print chk_flavor_tmp


# A method for adding the project UUID in the names of the of all the
# networks so that they won't create duplicates


def change_network_dict():
    project_uuid = general_params_dict["project_uuid"]
    # print project_uuid
    for k in network_dict:
        if project_uuid not in k:
            new_key = k + "_" + project_uuid
            network_dict[new_key] = network_dict.pop(k)
    # print network_dict
    for i in network_dict:
        name = network_dict[i]["name"]
        if project_uuid not in name:
            new_name = name + "_" + project_uuid
            network_dict[i]["name"] = new_name
    # print network_dict

# A Method for chnaginf the network and the server stack names


def change_stack_names():
    project_uuid = general_params_dict["project_uuid"]
    general_params_dict["network_stack_name"] = general_params_dict["network_stack_name"] + project_uuid
    general_params_dict["server_stack_name"] = general_params_dict["server_stack_name"] + project_uuid

# A method to create a yaml file to create networks using the heat
# component of the openstack


def create_network_yaml():
    change_network_dict()
    project_uuid = general_params_dict["project_uuid"]
    network_string = ""
    network_string = network_string + "heat_template_version: 2015-04-30\n\ndescription: " + \
        description + "\n\n" + "resources:\n"
    for i in network_dict:
        num = 1
        if "name" in network_dict[i]:
            name = network_dict[i]["name"]
        else:
            name = i
        network_name_list.append(name)
        network_string = network_string + "  " + name + ":\n"
        network_string = network_string + "    type: OS::Neutron::Net\n"
        network_string = network_string + "    properties:\n      name: " + name + "\n"
        network_string = network_string + "      tenant_id: %s\n\n" % project_uuid
        subnet_name = name + "_subnet_" + str(num)
        network_string = network_string + "  " + subnet_name + ":\n"
        network_string = network_string + "    type: OS::Neutron::Subnet\n"
        network_string = network_string + "    properties:\n"
        network_string = network_string + "      tenant_id: %s\n" % project_uuid
        network_string = network_string + \
            "      network_id: { get_resource: %s }\n" % name
        ip_block_with_mask = network_dict[i]["ip_block_with_mask"]
        network_string = network_string + "      cidr: %s\n" % ip_block_with_mask
        network_string = network_string + "      ip_version: 4\n"
        network_string = network_string + "      name: %s\n\n" % subnet_name
        num = num + 1
    print network_string


# A Method for changing the server_dict according to the given
# 'project_uuid' given in the 'input.json' file so that naming
# complications can be avoided.
def change_server_dict():
    for clus in all_cluster_dict:
        server_dict = parsed_json["inp_params"]["cluster"][clus]["servers"]
        project_uuid = general_params_dict["project_uuid"]
        # print server_dict
        for i in server_dict:
            if project_uuid not in i:
                new_key = i + "_" + project_uuid
                server_dict[new_key] = server_dict.pop(i)

        # print server_dict
        for i in server_dict:
            a = server_dict[i]['ip_address']
            for j in a:
                if project_uuid not in j:
                    new_key = j + "_" + project_uuid
                    a[new_key] = a.pop(j)
    # print server_dict

# A Method for changing the floatingIP pool parameters from the input.json


def change_floatingip_pool_params():
    project_uuid = general_params_dict["project_uuid"]
    name = floating_ip_network_dict["param"]["name"]
    if project_uuid not in name:
        new_name = name + "_" + project_uuid
        floating_ip_network_dict["param"]["name"] = new_name
    return floating_ip_network_dict

# A Method to create a yaml file to create servers using the heat
# component of the openstack


def create_server_yaml():
    for clus in server_dict:
        port_string = ""
        server_string = ""
        server_string = server_string + "heat_template_version: 2015-04-30\n\ndescription: " + \
            description + "\n\n" + "resources:\n"
        ip_port_dict = {}
        # Change the contents of the Server_dict
        change_server_dict()
        # Change the contets of the Network_dict
        change_network_dict()
        # Change the contents Cluster Names
        change_stack_names()
        # Change the contents of the floating_ip_network_dict
        floating_ip_network_dict = change_floatingip_pool_params()
        # Create required ports for all the VMs

        for i in server_dict[clus]:
            # print server_dict[i]
            name = server_dict[clus][i]["name"]
            # The internal dictionary that contains the mapping of the network
            # name to the fixed ip should also be chnaged. The next 5 lines are
            # doing that
            ip_address_dict = server_dict[clus][i]["ip_address"]
            project_uuid = general_params_dict["project_uuid"]
            for k in ip_address_dict:
                new_key = k + "_" + project_uuid
                #ip_address_dict[new_key] = ip_address_dict.pop(k)
            # print ip_address_dict
            #ip_num = 0
            for j in network_dict:
                if network_dict[j]["role"] == "management":
                    ip_num = 0
                else:
                    ip_num = 1
                net_name = network_dict[j]["name"]
                port_name = name + "_port_" + str(ip_num)
                server_string = server_string + "  " + port_name + ":\n"
                server_string = server_string + "    type: OS::Neutron::Port\n"
                server_string = server_string + "    properties:\n"
                server_string = server_string + "      network: %s\n" % net_name
                server_string = server_string + "      name: %s\n" % port_name
                if "mac_address" in server_dict[clus][i]:
                    server_string = server_string + \
                        "      mac_address: %s\n" % (server_dict[clus][i]["mac_address"][net_name])
                server_string = server_string + "      fixed_ips:\n"
                server_string = server_string + \
                    "        - ip_address: %s\n" % ip_address_dict[net_name]
                if network_dict[j]["role"] == "management":
                    if ("external_vip" in cluster_dict[clus]
                            ["parameters"]["provision"]["openstack"]):
                        server_string = server_string + "      allowed_address_pairs:\n"
                        server_string = server_string + \
                            "        - ip_address: %s\n" % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
                    if ("contrail_external_vip" in cluster_dict[clus]
                            ["parameters"]["provision"]["contrail"]):
                        server_string = server_string + "      allowed_address_pairs:\n"
                        server_string = server_string + \
                            "        - ip_address: %s\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
                if network_dict[j]["role"] == "control-data":
                    if ("internal_vip" in cluster_dict[clus]
                            ["parameters"]["provision"]["openstack"]):
                        server_string = server_string + "      allowed_address_pairs:\n"
                        server_string = server_string + \
                            "        - ip_address: %s\n" % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
                    if ("contrail_internal_vip" in cluster_dict[clus]
                            ["parameters"]["provision"]["contrail"]):
                        server_string = server_string + "      allowed_address_pairs:\n"
                        server_string = server_string + \
                            "        - ip_address: %s\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_vip"]
                ip_port_dict[(ip_address_dict[net_name])] = port_name
            #ip_num += 1
    # Launch the VMs
    ip_association_floating = []
    for i in server_dict[clus]:
        name = server_dict[clus][i]["name"]
        server_string = server_string + "  " + name + ":\n"
        server_string = server_string + "    type: OS::Nova::Server\n"
        server_string = server_string + "    properties:\n      name: " + name + "\n"
        server_string = server_string + \
            "      flavor: %s\n" % server_dict[clus][i]["flavor"]
        server_string = server_string + \
            "      image: %s\n" % server_dict[clus][i]["image"]
        if "user_data_file_name" in server_dict[clus][i]:
            server_string = server_string + "      user_data:\n"
            server_string = server_string + \
                "        get_file: %s\n" % server_dict[clus][i]["user_data_file_name"]
        server_string = server_string + "      networks:\n"
        port_for_floating_ip = []
        ip_address_dict = server_dict[clus][i]["ip_address"]
        ip_list = ip_address_dict.values()
        # print ip_list[1]
        for key, value in ip_address_dict.items():
            if value in ip_list:
                if network_dict[key]["role"] == "management":
                    ip_association_floating.append(value)
                    server_string = server_string + \
                        "        - port: { get_resource:  %s}\n" % ip_port_dict[value]
                    ip_list.remove(value)
        if len(ip_list) > 0:
            # print ip_association_floating
            for j in ip_list:
                # print ip_list
                server_string = server_string + \
                    "        - port: { get_resource:  %s}\n" % ip_port_dict[j]
                if len(port_for_floating_ip) == 0:
                    port_for_floating_ip.append(ip_port_dict[j])
            server_string = server_string + "\n"
    # If Floating IP Pool present in the given Json tanslate it into the yaml
    # file
    if "floating_ip_network" in parsed_json["inp_params"]:
        # Change the name of the floatingip pool. Add the porject uuid to the
        # name.
        change_floatingip_pool_params()
        name = floating_ip_network_dict["param"]["name"]
        server_string = server_string + "  " + name + ":\n"
        server_string = server_string + "    type: OS::ContrailV2::FloatingIpPool\n"
        server_string = server_string + "    properties:\n"
        server_string = server_string + "      name: %s\n" % name
        server_string = server_string + \
            "      virtual_network: %s\n\n" % floating_ip_network_dict["param"]["floating_ip_network_uuid"]
        #server_string = server_string + "      virtual_network: public\n\n"
    # creating floating IP from the above created pool for the VMs
    for i in server_dict[clus]:
        if server_dict[clus][i]["floating_ip"] == "true":
            name = server_dict[clus][i]["name"] + "_floating_ip"
            server_string = server_string + "  " + name + ":\n"
            server_string = server_string + "    type: OS::ContrailV2::FloatingIp\n"
            server_string = server_string + "    properties:\n"
            #floating_ip = server_dict[i]["floating_ip"]
            #server_string = server_string + "      floating_ip_address: %s\n"%floating_ip
            abc = ip_association_floating[0]
            port_to_associate = ip_port_dict[abc]
            # print ip_port_dict
            # print port_to_associate
            ip_association_floating.pop(0)
            #server_string = server_string + "      virtual_machine_interface_refs: [{ get_resource : %s}]\n"%port_for_floating_ip[0]
            server_string = server_string + \
                "      virtual_machine_interface_refs: [{ get_resource : %s}]\n" % port_to_associate
            floating_ip_network_dict = parsed_json["inp_params"]["floating_ip_network"]["param"]
            server_string = server_string + \
                "      floating_ip_pool: { get_resource: %s }\n" % floating_ip_network_dict["name"]
            server_string = server_string + "      floating_ip_fixed_ip_address: %s \n" % abc
            server_string = server_string + \
                "      project_refs: [ %s ]\n\n" % general_params_dict["project_uuid"]
        else:
            pass

    print server_string
    # print ip_association_floating


# Method for Parsing Openstack Resource output
fixed_ip_mac_mapping = {}
# Dict for storing fixed IP to Mac mapping
# floating_ip_mac_mapping is for the mapping of the floating ip to the
# server manager VM so that it can be used in the provisioning of the
# server manager vm
floating_ip_mac_mapping = {}


def parse_output():
    project_uuid = general_params_dict["project_uuid"]
    # Change the contents of the Server_dict
    change_server_dict()
    # Change the contets of the Network_dict
    change_network_dict()
    # Change the contents of the floating_ip_network_dict
    floating_ip_network_dict = change_floatingip_pool_params()
    # Change both the stack names
    change_stack_names()
    network_stack_name = general_params_dict["network_stack_name"]
    server_stack_name = general_params_dict["server_stack_name"]
    # print network_stack_name
    # print server_stack_name
    all_server_names = []
    for clus in server_dict:
        for i in server_dict[clus]:
            name = server_dict[clus][i]["name"]
            all_server_names.append(name)
    # print all_server_names
    # print server_stack_name
    for i in all_server_names:
        #a = os.system("openstack stack resource show %s %s"%(server_stack_name,i))
        a = subprocess.Popen(
            "openstack stack resource show %s %s" %
            (server_stack_name, i), shell=True, stdout=subprocess.PIPE)
        a_tmp = a.stdout.read()
        a_tmp = str(a_tmp)
        # print a_tmp
        split_list_1 = a_tmp.split("attributes")
        # print split_list_1
        split_string_1 = split_list_1[1]
        # print split_string_1
        split_list_2 = split_string_1.split("creation_time")
        # print split_list_2[0]
        split_string_2 = split_list_2[0]
        split_list_3 = split_string_2.split("|")
        # print split_list_3
        final_string = split_list_3[1]
        final_string.replace(" ", "")
        # print final_string
        # Convert the above string 'final_string' into a valid dictionary
        final_resource_params_dict = eval(final_string)
        # print final_resource_params_dict["addresses"]
        for j in final_resource_params_dict["addresses"]:
            # print j
            for k in range(len(final_resource_params_dict["addresses"][j])):
                # print k
                # print final_resource_params_dict["addresses"][j]
                if final_resource_params_dict["addresses"][j][k]["OS-EXT-IPS:type"] == "fixed":
                    fixed_ip_mac_mapping[final_resource_params_dict["addresses"][j][k]["addr"]
                                         ] = final_resource_params_dict["addresses"][j][k]["OS-EXT-IPS-MAC:mac_addr"]
                    # print "Yes"
                elif final_resource_params_dict["addresses"][j][k]["OS-EXT-IPS:type"] == "floating":
                    floating_ip_mac_mapping[final_resource_params_dict["addresses"][j][k][
                        "OS-EXT-IPS-MAC:mac_addr"]] = final_resource_params_dict["addresses"][j][k]["addr"]
    # print fixed_ip_mac_mapping
    # print floating_ip_mac_mapping


# A Method for gettinf the server manager ip
def get_sm_ip():
    a = subprocess.Popen(
        'neutron floatingip-list -f json',
        shell=True,
        stdout=subprocess.PIPE)
    a_tmp = a.stdout.read()
    a_tmp = str(a_tmp)
    fip_neutron_dict = eval(a_tmp)
    floating_ip_list = []
    change_network_dict()
    net_name = []
    for i in network_dict:
        net_name.append(network_dict[i]["name"])
    for clus in server_dict:
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] == "true":
                for j in server_dict[clus][i]["ip_address"]:
                    for k in range(len(fip_neutron_dict)):
                        if fip_neutron_dict[k]["fixed_ip_address"] == server_dict[clus][i]["ip_address"][j]:
                            b = subprocess.Popen(
                                'neutron port-show %s -f json' %
                                fip_neutron_dict[k]["port_id"],
                                shell=True,
                                stdout=subprocess.PIPE)
                            b_tmp = b.stdout.read()
                            b_tmp = str(b_tmp)
                            current_port_dict = json.loads(b_tmp)
                            current_network_id = current_port_dict["network_id"]
                            c = subprocess.Popen(
                                'neutron net-list -f json', shell=True, stdout=subprocess.PIPE)
                            c_tmp = c.stdout.read()
                            c_tmp = str(c_tmp)
                            all_net_dict = json.loads(c_tmp)
                            for net in all_net_dict:
                                if current_network_id == net["id"] and net["name"] in net_name:
                                    floating_ip_list.append(
                                        fip_neutron_dict[k]["floating_ip_address"])

    for fip in floating_ip_list:
        print fip

# Method for getting the floating ip od the config node in the mainline build


def get_config_node_ip_mainline():
    a = subprocess.Popen(
        'neutron floatingip-list -f json',
        shell=True,
        stdout=subprocess.PIPE)
    a_tmp = a.stdout.read()
    a_tmp = str(a_tmp)
    fip_neutron_dict = eval(a_tmp)
    project_uuid = general_params_dict["project_uuid"]
    config_node_ip_dict = {}
    change_network_dict()
    net_name = []
    for i in network_dict:
        net_name.append(network_dict[i]["name"])
    for clus in server_dict:
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                if "contrail-controller" in server_dict[clus][i]["roles"]:
                    for j in server_dict[clus][i]["ip_address"]:
                        for k in range(len(fip_neutron_dict)):
                            if fip_neutron_dict[k]["fixed_ip_address"] == server_dict[clus][i]["ip_address"][j]:
                                b = subprocess.Popen(
                                    'neutron port-show %s -f json' %
                                    fip_neutron_dict[k]["port_id"],
                                    shell=True,
                                    stdout=subprocess.PIPE)
                                b_tmp = b.stdout.read()
                                b_tmp = str(b_tmp)
                                current_port_dict = json.loads(b_tmp)
                                current_network_id = current_port_dict["network_id"]
                                c = subprocess.Popen(
                                    'neutron net-list -f json', shell=True, stdout=subprocess.PIPE)
                                c_tmp = c.stdout.read()
                                c_tmp = str(c_tmp)
                                all_net_dict = json.loads(c_tmp)
                                for net in all_net_dict:
                                    if current_network_id == net["id"] and net["name"] in net_name:
                                        config_node_ip_dict[clus] = (
                                            fip_neutron_dict[k]["floating_ip_address"])
    for cfgmip in config_node_ip_dict:
        print config_node_ip_dict[cfgmip]


# Method for getting the floating ip of the config node so that the
# testbed.py can be transferred to this server and the tests can run from
# here.
def get_config_node_ip():
    a = subprocess.Popen(
        'neutron floatingip-list -f json',
        shell=True,
        stdout=subprocess.PIPE)
    a_tmp = a.stdout.read()
    a_tmp = str(a_tmp)
    fip_neutron_dict = eval(a_tmp)
    project_uuid = general_params_dict["project_uuid"]
    config_node_ip_dict = {}
    change_network_dict()
    net_name = []
    for i in network_dict:
        net_name.append(network_dict[i]["name"])
    for clus in server_dict:
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                if "config" in server_dict[clus][i]["roles"]:
                    for j in server_dict[clus][i]["ip_address"]:
                        for k in range(len(fip_neutron_dict)):
                            if fip_neutron_dict[k]["fixed_ip_address"] == server_dict[clus][i]["ip_address"][j]:
                                b = subprocess.Popen(
                                    'neutron port-show %s -f json' %
                                    fip_neutron_dict[k]["port_id"],
                                    shell=True,
                                    stdout=subprocess.PIPE)
                                b_tmp = b.stdout.read()
                                b_tmp = str(b_tmp)
                                current_port_dict = json.loads(b_tmp)
                                current_network_id = current_port_dict["network_id"]
                                c = subprocess.Popen(
                                    'neutron net-list -f json', shell=True, stdout=subprocess.PIPE)
                                c_tmp = c.stdout.read()
                                c_tmp = str(c_tmp)
                                all_net_dict = json.loads(c_tmp)
                                for net in all_net_dict:
                                    if current_network_id == net["id"] and net["name"] in net_name:
                                        config_node_ip_dict[clus] = (
                                            fip_neutron_dict[k]["floating_ip_address"])
    for cfgmip in config_node_ip_dict:
        print config_node_ip_dict[cfgmip]


# Method for creatng server.json required for the mainline build
def create_server_json_mainline():
    parse_output()
    change_network_dict()
    floating_ip_network_dict = change_floatingip_pool_params()
    change_stack_names()
    server_json_string = '''{
        "server":[
        '''
    mac_address_list = []
    for i in fixed_ip_mac_mapping:
        mac_address_list.append(fixed_ip_mac_mapping[i])
    total_server_number = 0
    for clus in server_dict:
        total_server_number = total_server_number + len(server_dict[clus])
    total_server_number = total_server_number - 1
    for clus in server_dict:
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                single_server_string = '\t{\n'
                if "cluster_id" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t"cluster_id": "%s",\n' % cluster_dict[clus]["cluster_id"]
                single_server_string = single_server_string + \
                    '\t\t"id": "%s",\n' % server_dict[clus][i]["name"]
                if "domain" in cluster_dict[clus]["parameters"]:
                    single_server_string = single_server_string + \
                        '\t\t"domain": "%s",\n' % cluster_dict[clus]["parameters"]["domain"]
                if "ipmi_address" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t"ipmi_address": "%s",\n' % cluster_dict[clus]["ipmi_address"]
                else:
                    single_server_string = single_server_string + '\t\t"ipmi_address": null,\n'
                if "ipmi_username" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t"ipmi_username": "%s",\n' % cluster_dict[clus]["ipmi_username"]
                else:
                    single_server_string = single_server_string + '\t\t"ipmi_username": null,\n'
                if "ipmi_password" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t"ipmi_password": "%s",\n' % cluster_dict[clus]["ipmi_password"]
                else:
                    single_server_string = single_server_string + '\t\t"ipmi_password": null,\n'
                if "control_data_iterface" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t"contrail": {\n'
                    single_server_string = single_server_string + \
                        '\t\t\t"control_data_interface": "%s"\n' % cluster_dict[clus]["control_data_iterface"]
                    single_server_string = single_server_string + '\t\t},\n'
                # Now lets get all the network interface parameters and add
                # them to the server.json
                single_server_string = single_server_string + \
                    '\t\t"network": {\n'
                single_server_string = single_server_string + \
                    '\t\t\t"interfaces": [\n'
                total_server_interfaces = len(
                    server_dict[clus][i]["ip_address"])
                for j in (server_dict[clus][i]["ip_address"]):
                    current_network = j
                    gateway = network_dict[j]["default_gateway"]
                    ip_add = server_dict[clus][i]["ip_address"][j]
                    mask = network_dict[j]["ip_block_with_mask"]
                    mask_list = mask.split("/")
                    mask = mask_list[1]
                    ip_add_with_mask = ip_add + '/' + mask
                    mac_address = fixed_ip_mac_mapping[ip_add]
                    role = network_dict[j]["role"]
                    if role == "management":
                        int_name = cluster_dict[clus]["management_interface"]
                    else:
                        int_name = cluster_dict[clus]["control_data_iterface"]
                    single_server_string = single_server_string + '\t\t\t\t{\n'
                    single_server_string = single_server_string + \
                        '\t\t\t\t\t"default_gateway": "%s",\n' % gateway
                    single_server_string = single_server_string + \
                        '\t\t\t\t\t"ip_address": "%s",\n' % ip_add_with_mask
                    single_server_string = single_server_string + \
                        '\t\t\t\t\t"mac_address": "%s",\n' % mac_address
                    if "server_json_dhcp" in cluster_dict[clus]:
                        single_server_string = single_server_string + \
                            '\t\t\t\t\t"dhcp": %s,\n' % cluster_dict[clus]["server_json_dhcp"]
                    else:
                        single_server_string = single_server_string + '\t\t\t\t\t"dhcp": false,\n'
                    single_server_string = single_server_string + \
                        '\t\t\t\t\t"name": "%s"\n' % int_name
                    if total_server_interfaces > 1:
                        single_server_string = single_server_string + '\t\t\t\t},\n'
                    else:
                        single_server_string = single_server_string + '\t\t\t\t}\n'
                    total_server_interfaces = total_server_interfaces - 1
                single_server_string = single_server_string + "\t\t\t],\n"
                if "provisioning_type" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t\t"provisioning_type": "%s",\n' % cluster_dict[clus]["provisioning_type"]
                if "management_interface" in cluster_dict[clus]:
                    single_server_string = single_server_string + \
                        '\t\t\t"management_interface": "%s"\n' % cluster_dict[clus]["management_interface"]
                single_server_string = single_server_string + '\t\t},\n'
                single_server_string = single_server_string + \
                    '\t\t"password": "%s",\n' % cluster_dict[clus]["server_password"]
                role_string = '['
                no_of_roles = len(server_dict[clus][i]["roles"])
                for r in server_dict[clus][i]["roles"]:
                    if no_of_roles == 1:
                        role_string = role_string + ' "%s"' % r
                    else:
                        role_string = role_string + ' "%s",' % r
                        no_of_roles = no_of_roles - 1
                role_string = role_string + ' ]'
                single_server_string = single_server_string + '\t\t"roles": %s,\n' % role_string
                if "partition" in server_dict[clus][i]:
                    single_server_string = single_server_string + \
                        '\t\t"parameters": {\n'
                    single_server_string = single_server_string + \
                        '\t\t\t"partition": "%s"\n' % server_dict[clus][i]["partition"]
                    single_server_string = single_server_string + '\t\t}\n'
                else:
                    single_server_string = single_server_string + \
                        '\t\t"parameters": {\n'
                    single_server_string = single_server_string + '\t\t}\n'
                if total_server_number > 1:
                    single_server_string = single_server_string + '\t\t},\n'
                    total_server_number = total_server_number - 1
                else:
                    single_server_string = single_server_string + '\t\t}\n'
                server_json_string = server_json_string + single_server_string
    server_json_string = server_json_string + '\t]\n'
    server_json_string = server_json_string + '}\n'
    print server_json_string


# Method for creating the server json required for adding the servers to
# the server manager
def create_server_json():
    parse_output()
    # Change the contents of the Server_dict
    # change_server_dict()
    # Change the contets of the Network_dict
    change_network_dict()
    # Change the contents of the floating_ip_network_dict
    floating_ip_network_dict = change_floatingip_pool_params()
    # Change the Cluster Names
    change_stack_names()
    server_json_string = '''{
	"server":[
	'''
    # Call the parse_output function os that we can use the IP-Mac Mapping provided by the function
    # parse_output()
    mac_address_list = []
    for i in fixed_ip_mac_mapping:
        mac_address_list.append(fixed_ip_mac_mapping[i])
    # print mac_address_list
    """
	for i in mac_address_list:
		if i in floating_ip_mac_mapping:
			ipmi_ip = floating_ip_mac_mapping[i]
	"""
    #total_server_number = len(parsed_json["inp_params"]["servers"]) -1
    total_server_number = 0
    for clus in server_dict:
        total_server_number = total_server_number + len(server_dict[clus])
    total_server_number = total_server_number - 1

    for clus in server_dict:
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                single_server_string = '''
				{
				"cluster_id": "%s",
				"contrail": {
					"control_data_interface": "%s"
				},
				"host_name": "%s",
				"id": "%s",
				"domain": "%s",
				"network": {
				''' % (cluster_dict[clus]["cluster_id"], cluster_dict[clus]["control_data_iterface"], server_dict[clus][i]["name"], server_dict[clus][i]["name"], cluster_dict[clus]["parameters"]["domain"])
                single_server_string = single_server_string + \
                    '''       "interfaces": ['''
                total_server_interfaces = len(
                    server_dict[clus][i]["ip_address"])
                for j in (server_dict[clus][i]["ip_address"]):
                    current_network = j
                    gateway = network_dict[j]["default_gateway"]
                    ip_add = server_dict[clus][i]["ip_address"][j]
                    mask = network_dict[j]["ip_block_with_mask"]
                    mask_list = mask.split("/")
                    mask = mask_list[1]
                    mac_address = fixed_ip_mac_mapping[ip_add]
                    role = network_dict[j]["role"]
                    if role == "management":
                        int_name = cluster_dict[clus]["management_interface"]
                    else:
                        int_name = cluster_dict[clus]["control_data_iterface"]
                    if total_server_interfaces > 1:
                        single_server_string = single_server_string + '''
						{
							"default_gateway": "%s",
							"dhcp": false,
							"ip_address": "%s/%s",
							"mac_address": "%s",
							"name": "%s"
						},
						''' % (gateway, ip_add, mask, mac_address, int_name)
                    else:
                        single_server_string = single_server_string + '''
	                                	{
	                                        	"default_gateway": "%s",
	                                        	"dhcp": false,
	                                        	"ip_address": "%s/%s",
	                                        	"mac_address": "%s",
	                                        	"name": "%s"
	                                	}
	                                	''' % (gateway, ip_add, mask, mac_address, int_name)
                    total_server_interfaces = total_server_interfaces - 1
                single_server_string = single_server_string + "],"
                single_server_string = single_server_string + \
                    '\n			"management_interface": "%s"\n' % (cluster_dict[clus]["management_interface"])
                server_json_string = server_json_string + single_server_string
                server_json_string_contd = '''
				},
				"password": "%s",
				"roles": [
				''' % (cluster_dict[clus]["server_password"])
                roles_string = ''
                total_number_of_roles = len(server_dict[clus][i]["roles"])
                for j in server_dict[clus][i]["roles"]:
                    if total_number_of_roles > 1:
                        roles_string = roles_string + '	"%s",\n' % j
                    else:
                        roles_string = roles_string + ' "%s"\n' % j
                    total_number_of_roles = total_number_of_roles - 1
                server_json_string = server_json_string + server_json_string_contd
                server_json_string = server_json_string + roles_string
                # print single_server_string
                # Is the number of servers in the input.json is more than one
                # then we need commas in the json after every server dict.
                if total_server_number > 1:
                    server_json_string_contd = '''
					]
					},
					'''
                    total_server_number = total_server_number - 1
                else:
                    server_json_string_contd = '''
	                        	]
	                        	}
	                        	'''
                # Reduce the number of the total servers by one so that when we
                # insert the last server dict in the json file, it will not
                # include the comma (,) at the end
                server_json_string = server_json_string + server_json_string_contd
        closing_string = '''
		]
	}
		'''
        server_json_string = server_json_string + closing_string
        print server_json_string

# Method for Creating Cluster.json for the Server Manager Mainline Build


def create_cluster_json_mainline():
    change_stack_names()
    clus_json_string = '{\n\t"cluster":[\n'
    no_of_clusters = len(cluster_dict)
    for clus in cluster_dict:
        individual_clus_string = '\t\t{\n'
        if "cluster_id" in cluster_dict[clus]:
            individual_clus_string = individual_clus_string + \
                '\t\t"id": "%s",\n' % cluster_dict[clus]["cluster_id"]
        individual_clus_string = individual_clus_string + \
            '\t\t"parameters":{\n'
        if "domain" in cluster_dict[clus]["parameters"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t"domain": "%s",\n' % cluster_dict[clus]["parameters"]["domain"]
        for net in network_dict:
            if network_dict[net]["role"] == "management":
                individual_clus_string = individual_clus_string + \
                    '\t\t\t"gateway": "%s",\n' % network_dict[net]["default_gateway"]
        individual_clus_string = individual_clus_string + \
            '\t\t\t"provision":{\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t"containers":{\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t"inventory":{\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t"[all:vars]":{\n'
        for server in server_dict[clus]:
            if "contrail-lb" in server_dict[clus][server]["roles"]:
                lb_external = ''
                lb_internal = ''
                for n in server_dict[clus][server]["ip_address"]:
                    if network_dict[n]["role"] == "management":
                        lb_external = server_dict[clus][server]["ip_address"][n]
                    if network_dict[n]["role"] == "control-data":
                        lb_internal = server_dict[clus][server]["ip_address"][n]
                individual_clus_string = individual_clus_string + \
                    '\t\t\t\t\t\t\t"config_ip": "%s",\n' % lb_external
                individual_clus_string = individual_clus_string + \
                    '\t\t\t\t\t\t\t"controller_ip": "%s",\n' % lb_external
                individual_clus_string = individual_clus_string + \
                    '\t\t\t\t\t\t\t"analytics_ip": "%s",\n' % lb_external
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t"api_config":{\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t\t"listen_port": "9100"\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t"},\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t"keystone_config":{\n'
        openstack_control_data_ip_list = []
        for server in server_dict[clus]:
            if "openstack" in server_dict[clus][server]["roles"]:
                if len(server_dict[clus][server]["ip_address"]) == 1:
                    for temp in server_dict[clus][server]["ip_address"]:
                        openstack_control_data_ip_list.append(
                            str(server_dict[clus][server]["ip_address"][temp]))
                else:
                    for temp in server_dict[clus][server]["ip_address"]:
                        if network_dict[temp]["role"] == "control-data":
                            openstack_control_data_ip_list.append(
                                str(server_dict[clus][server]["ip_address"][temp]))
        if "internal_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t\t"ip": "%s",\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
        else:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t\t"ip": "%s",\n' % openstack_control_data_ip_list[0]
        if "keystone_admin_password" in cluster_dict[clus]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t\t"admin_password": "%s",\n' % cluster_dict[clus]["keystone_admin_password"]
        else:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t\t"admin_password": "c0ntrail123",\n'
        # if "keystone_admin_token" in cluster_dict[clus]:
        #    individual_clus_string = individual_clus_string + \
        #        '\t\t\t\t\t\t\t\t"admin_token": "%s",\n' % cluster_dict[clus]["keystone_admin_token"]
        # else:
        #    individual_clus_string = individual_clus_string + \
        #        '\t\t\t\t\t\t\t\t"admin_token": "c0ntrail123",\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t\t"admin_tenant": "admin"\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t\t\t\t},\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t\t"global_config":{\n'
        # individual_clus_string = individual_clus_string + \
        #    '\t\t\t\t\t\t\t\t"config_username": "root",\n'
        # if "config_password" in cluster_dict[clus]:
        #    individual_clus_string = individual_clus_string + \
        #        '\t\t\t\t\t\t\t\t"config_password": "%s",\n' % cluster_dict[clus]["config_password"]
        # else:
        #    individual_clus_string = individual_clus_string + \
        #        '\t\t\t\t\t\t\t\t"config_password": "c0ntrail123",\n'
        # individual_clus_string = individual_clus_string + \
        #    '\t\t\t\t\t\t\t\t"service_tenant_name": "services",\n'
        individual_clus_string = individual_clus_string + \
            '''\t\t\t\t\t\t\t\t"external_rabbitmq_servers": "%s" \n''' % openstack_control_data_ip_list
        individual_clus_string = individual_clus_string + '\t\t\t\t\t\t\t},\n'
        if "contrail_compute_mode" in cluster_dict[clus]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t"contrail_compute_mode": "%s"\n' % cluster_dict[clus]["contrail_compute_mode"]
        else:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t\t"contrail_compute_mode": "bare_metal"\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t},\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t"contrail": {\n'
        if "kernel_upgrade" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"kernel_upgrade": %s,\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["kernel_upgrade"]
        """
	if "minimum_disk_database" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"database": {\n'
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"minimum_diskGB": %d\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["minimum_disk_database"]
            individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
        """
        for server in server_dict[clus]:
            if "contrail-lb" in server_dict[clus][server]["roles"]:
                if len(lb_external) != 0:
                    individual_clus_string = individual_clus_string + \
                        '\t\t\t\t\t"ha": {\n'
                    if len(lb_internal) != 0:
                        individual_clus_string = individual_clus_string + \
                            '\t\t\t\t\t\t"contrail_external_vip": "%s",\n' % lb_external
                        individual_clus_string = individual_clus_string + \
                            '\t\t\t\t\t\t"contrail_internal_vip": "%s"\n' % lb_internal
                        individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
                    else:
                        individual_clus_string = individual_clus_string + \
                            '\t\t\t\t\t\t"contrail_external_vip": "%s"\n' % lb_external
                        individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
        '''
		if "contrail_external_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
			if "contrail_internal_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
				individual_clus_string = individual_clus_string + '\t\t\t\t\t"ha": {\n'
				individual_clus_string = individual_clus_string + '\t\t\t\t\t\t"contrail_external_vip": "%s",\n'%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
				individual_clus_string = individual_clus_string + '\t\t\t\t\t\t"contrail_internal_vip": "%s"\n'%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_vip"]
				individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
			else:
				individual_clus_string = individual_clus_string + '\t\t\t\t\t"ha": {\n'
				individual_clus_string = individual_clus_string + '\t\t\t\t\t\t"contrail_external_vip": "%s",\n'%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
				individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
		'''
        config_node_control_data_ip_list = []
        for server in server_dict[clus]:
            if "contrail-controller" in server_dict[clus][server]["roles"]:
                if len(server_dict[clus][server]["ip_address"]) == 1:
                    for temp in server_dict[clus][server]["ip_address"]:
                        config_node_control_data_ip_list.append(
                            str(server_dict[clus][server]["ip_address"][temp]))
                else:
                    for temp in server_dict[clus][server]["ip_address"]:
                        if network_dict[temp]["role"] == "control-data":
                            config_node_control_data_ip_list.append(
                                str(server_dict[clus][server]["ip_address"][temp]))
        config_ip_list_string = '[ '
        ip_tot = len(config_node_control_data_ip_list)
        for ip in config_node_control_data_ip_list:
            if ip_tot > 1:
                config_ip_list_string = config_ip_list_string + '"%s", ' % ip
            else:
                config_ip_list_string = config_ip_list_string + '"%s" ' % ip
            ip_tot = ip_tot - 1
        config_ip_list_string = config_ip_list_string + ']'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t"config": {\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t\t"config_ip_list": %s,\n' % config_ip_list_string
        if "manage_neutron" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"manage_neutron": %s\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["manage_neutron"]
        individual_clus_string = individual_clus_string + '\t\t\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t},\n'
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t"openstack": {\n'
        if "external_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            if "internal_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
                openstack_ha_string = '\t\t\t\t\t"ha": {\n'
                openstack_ha_string = openstack_ha_string + \
                    '\t\t\t\t\t\t"external_vip": "%s",\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
                openstack_ha_string = openstack_ha_string + \
                    '\t\t\t\t\t\t"internal_vip": "%s"\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
                openstack_ha_string = openstack_ha_string + "\t\t\t\t\t},\n"
            else:
                openstack_ha_string = '\t\t\t\t\t"ha": {\n'
                openstack_ha_string = openstack_ha_string + \
                    '\t\t\t\t\t\t"external_vip": "%s"\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
                openstack_ha_string = openstack_ha_string + "\t\t\t\t\t},\n"
            individual_clus_string = individual_clus_string + openstack_ha_string
        if "openstack_manage_amqp" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"openstack_manage_amqp": %s,\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["openstack_manage_amqp"]
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t\t"keystone": {\n'
        if "keystone_admin_token" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"admin_token": "%s",\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["keystone_admin_token"]
        else:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"admin_token": "c0ntrail123",\n'
        if "keystone_admin_password" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"admin_password": "%s"\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["keystone_admin_password"]
        else:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"admin_password": "c0ntrail123"\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t\t}\n'
        individual_clus_string = individual_clus_string + '\t\t}\n'
        individual_clus_string = individual_clus_string + '\t}\n'
    clus_json_string = clus_json_string + individual_clus_string
    clus_json_string = clus_json_string + '\t]\n'
    clus_json_string = clus_json_string + '}\n'
    print clus_json_string

# Method for creating cluster json for the server manager


def create_cluster_json():
    change_stack_names()
    clus_json_string = '{\n\t"cluster":[\n'
    no_of_clusters = len(cluster_dict)
    for clus in cluster_dict:
        individual_clus_string = '\t\t{\n'
        if "cluster_id" in cluster_dict[clus]:
            individual_clus_string = individual_clus_string + \
                '\t\t"id": "%s",\n' % cluster_dict[clus]["cluster_id"]
        individual_clus_string = individual_clus_string + \
            '\t\t"parameters":{\n'
        if "domain" in cluster_dict[clus]["parameters"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t"domain": "%s",\n' % cluster_dict[clus]["parameters"]["domain"]
        individual_clus_string = individual_clus_string + \
            '\t\t\t"provision":{\n'
        # Lets start the contrail Part
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t"contrail":{\n'
        if "minimum_disk_database" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"database":{\n'
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"minimum_diskGB": %d\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["minimum_disk_database"]
            individual_clus_string = individual_clus_string + '\t\t\t\t\t},\n'
        if "enable_rabbitmq_ssl" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"amqp_ssl":"%s",\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["enable_rabbitmq_ssl"]
        if "kernel_version" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"kernel_version":"%s",\n' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["kernel_version"]
        if "kernel_upgrade" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"kernel_upgrade": %s' % cluster_dict[clus]["parameters"]["provision"]["contrail"]["kernel_upgrade"]
        # Contrail Part Ends here
        individual_clus_string = individual_clus_string + '\t\t\t\t},\n'

        # Now Lets start the openstack part
        individual_clus_string = individual_clus_string + \
            '\t\t\t\t"openstack":{\n'
        if "keystone_admin_password" in cluster_dict[clus]["parameters"]["provision"]["openstack"]:
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t"keystone":{\n'
            individual_clus_string = individual_clus_string + \
                '\t\t\t\t\t\t"admin_password": "%s"\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["keystone_admin_password"]
            #individual_clus_string = individual_clus_string + '					},\n'
        if (("external_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]) and (
                "internal_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"])):
            vip_string = ""
            individual_clus_string = individual_clus_string + '\t\t\t\t},\n'
            vip_string = vip_string + '\t\t\t\t"ha":{\n'
            vip_string = vip_string + \
                '\t\t\t\t\t"external_vip": "%s",\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
            vip_string = vip_string + \
                '\t\t\t\t\t"internal_vip": "%s",\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
            vip_string = vip_string + \
                '\t\t\t\t\t"external_virtual_router_id" : %d,\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_virtual_router_id"]
            vip_string = vip_string + \
                '\t\t\t\t\t"internal_virtual_router_id" : %d\n' % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_virtual_router_id"]
            vip_string = vip_string + '\t\t\t\t}\n'
            vip_string = vip_string + '\t\t\t}\n'
            vip_string = vip_string + '\t\t}\n'
            vip_string = vip_string + '\t}\n'
            no_of_clusters = no_of_clusters - 1
            if no_of_clusters == 0:
                vip_string = vip_string + '}\n'
            else:
                vip_string = vip_string + '},\n'
            individual_clus_string = individual_clus_string + vip_string
        else:
            individual_clus_string = individual_clus_string + '\t\t\t\t}\n'
            individual_clus_string = individual_clus_string + '\t\t\t}\n'
            individual_clus_string = individual_clus_string + '\t\t}\n'
            individual_clus_string = individual_clus_string + '\t}\n'
            no_of_clusters = no_of_clusters - 1
            if no_of_clusters == 0:
                individual_clus_string = individual_clus_string + '}\n'
            else:
                individual_clus_string = individual_clus_string + '},\n'
        clus_json_string = clus_json_string + individual_clus_string
    clus_json_string = clus_json_string + '\t]\n'
    clus_json_string = clus_json_string + '}'
    print clus_json_string


def create_testbedpy_file():
    dict_of_testbed_files = {}
    for clus in testbed_py_dict:
        file_str = ""
        file_str = file_str + "from fabric.api import env \nimport os\n\nnext_routers = []\n"
        if "router_asn" in testbed_py_dict[clus]:
            file_str = file_str + \
                "router_asn = %s\n\n" % testbed_py_dict[clus]["router_asn"]
        else:
            file_str = file_str + "router_asn = 64512\n\n"
        itr = 1
        if "public_vn_rtgt" in testbed_py_dict[clus]:
            file_str = file_str + \
                "public_vn_rtgt = %s\n\n" % testbed_py_dict[clus]["public_vn_rtgt"]
        if "public_vn_subnet" in testbed_py_dict[clus]:
            file_str = file_str + \
                'public_vn_subnet = "%s"\n\n' % testbed_py_dict[clus]["public_vn_subnet"]
        # hostname_string contains the hostanme of all the servers. This would
        # be added to the main string after wards
        hostname_string = "     'all' : [ "
        build_ip = ""
        control_data_string = "control_data = {\n"
        name_mapping = {}
        if "env_password" in testbed_py_dict[clus]:
            env_password_string = "\nenv.passwords = {\n"
        if "env_ostypes" in testbed_py_dict[clus]:
            env_ostypes_string = "env.ostypes = {\n"
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                for j in server_dict[clus][i]["ip_address"]:
                    if network_dict[j]["role"] == "management":
                        if "config" in server_dict[clus][i]["roles"]:
                            # Build Ip that will be used in the testbed.py file
                            if "host_build" in testbed_py_dict[clus]:
                                build_ip = testbed_py_dict[clus]["host_build"]
                            else:
                                build_ip = server_dict[clus][i]["ip_address"][j]
                        manag_ip = server_dict[clus][i]["ip_address"][j]
                    else:
                        if network_dict[j]["role"] == "control-data":
                            # control data ip that will be used in the
                            # control-data section of the testbed.py file
                            control_ip = server_dict[clus][i]["ip_address"][j]
                            gateway = network_dict[j]["default_gateway"]
                        else:
                            continue
                for net in network_dict:
                    if network_dict[net]["role"] == 'control-data':
                        if "control_data_vlan" in testbed_py_dict[clus]:
                            control_data_string = control_data_string + "   host%s : { 'ip': '%s', 'gw' : '%s', 'device': 'eth1', 'vlan': '%s'},\n" % (
                                str(itr), control_ip, gateway, testbed_py_dict[clus]["control_data_vlan"])
                        else:
                            control_data_string = control_data_string + \
                                "   host%s : { 'ip': '%s', 'gw' : '%s', 'device': 'eth1'},\n" % (str(itr), control_ip, gateway)
                file_str = file_str + \
                    "host%s = 'root@%s'\n" % (str(itr), manag_ip)
                if "env_password" in testbed_py_dict[clus]:
                    env_password_string = env_password_string + \
                        "   host%s: '%s',\n" % (str(itr), testbed_py_dict[clus]["env_password"])
                if "env_ostypes" in testbed_py_dict[clus]:
                    env_ostypes_string = env_ostypes_string + \
                        "     host%s: '%s',\n" % (str(itr), testbed_py_dict[clus]["env_ostypes"])
                # logic for not adding ',' (comma) after the last hostname in
                # the env.hostname field of the testbed.py being created.
                if itr == len(server_dict[clus]) - 1:
                    hostname_string = hostname_string + "'" + \
                        (server_dict[clus][i]["name"]) + "' "
                    testbed_py_name = "host%s" % str(itr)
                    name_mapping[server_dict[clus][i]
                                 ["name"]] = testbed_py_name
                else:
                    hostname_string = hostname_string + "'" + \
                        (server_dict[clus][i]["name"]) + "', "
                    testbed_py_name = "host%s" % str(itr)
                    name_mapping[server_dict[clus][i]
                                 ["name"]] = testbed_py_name
                itr += 1
        hostname_string = hostname_string + "]\n"
        control_data_string = control_data_string + "}\n\n"
        role_per_server_mapping = {
            "all": [],
            "cfgm": [],
            "openstack": [],
            "webui": [],
            "control": [],
            "collector": [],
            "database": [],
            "compute": [],
            "build": ["host_build"]}
        if "env_ostypes" in testbed_py_dict[clus]:
            env_ostypes_string = env_ostypes_string + "}\n\n"
        if "env_password" in testbed_py_dict[clus]:
            env_password_string = env_password_string + \
                "   host_build: '%s',\n}\n\n" % testbed_py_dict[clus]["env_password"]
            file_str = file_str + \
                "\nenv.password = '%s'\n" % testbed_py_dict[clus]["env_password"]
        file_str = file_str + "host_build = 'root@%s'\n\n" % build_ip
        # Lets Get the role definitions for all the servers in the input file
        # All the hostnames for env.roles section in testbed.py file
        all_host_list = name_mapping.values()
        for i in all_host_list:
            role_per_server_mapping["all"].append(i)
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                if "config" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["cfgm"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "openstack" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["openstack"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "webui" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["webui"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "control" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["control"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "collector" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["collector"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "database" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["database"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "compute" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["compute"].append(
                        name_mapping[server_dict[clus][i]["name"]])
        file_str = file_str + "env.hostnames = {\n"
        file_str = file_str + hostname_string + "}\n\n"
        file_str = file_str + "env.interface_rename = False\n\n"
        for net in network_dict:
            if network_dict[net]["role"] == "control-data":
                file_str = file_str + control_data_string
        # Print all the role defs referenced from the 'role_per_server_mapping'
        # dict mention above
        file_str = file_str + "env.roledefs = {\n"
        #itr = len(role_per_server_mapping)
        itr = 1
        for i in role_per_server_mapping:
            #inner_iter = len(role_per_server_mapping[i])
            inner_iter = 1
            file_str = file_str + "	'%s' : [ " % i
            for j in role_per_server_mapping[i]:
                if inner_iter == len(role_per_server_mapping[i]):
                    file_str = file_str + j + " ]"
                else:
                    file_str = file_str + "%s, " % j
                inner_iter += 1
            if itr == len(role_per_server_mapping):
                file_str = file_str + "\n"
            else:
                file_str = file_str + ",\n"
            itr += 1
        file_str = file_str + "}\n\n"
        if "openstack_admin_password" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.openstack_admin_password = '%s'\n" % testbed_py_dict[clus]["openstack_admin_password"]
        if "env.log_scenario" in testbed_py_dict[clus]:
            log_scenario_str = ''
            if "auth_protocol" in testbed_py_dict[clus]["env.log_scenario"]:
                if testbed_py_dict[clus]["env.log_scenario"]["auth_protocol"] == "https":
                    if "keystone_version" in testbed_py_dict[clus]["env.log_scenario"]:
                        if testbed_py_dict[clus]["env.log_scenario"]["keystone_version"] == "v3":
                            if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                                log_scenario_str = log_scenario_str + \
                                    "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                            log_scenario_str = log_scenario_str + \
                                "env.keystone = {\n"
                            log_scenario_str = log_scenario_str + "	'version': 'v3',\n"
                            log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                            log_scenario_str = log_scenario_str + "}\n"
                    else:
                        if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                            log_scenario_str = log_scenario_str + \
                                "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                        log_scenario_str = log_scenario_str + \
                            "env.keystone = {\n"
                        log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                        log_scenario_str = log_scenario_str + "}\n"
                    log_scenario_str = log_scenario_str + "env.cfgm = {\n"
                    log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                    log_scenario_str = log_scenario_str + "}\n"
                else:
                    if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                        log_scenario_str = log_scenario_str + \
                            "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                    else:
                        pass
                file_str = file_str + log_scenario_str
        if "enable_rbac" in testbed_py_dict[clus]:
            if testbed_py_dict[clus]["enable_rbac"] == "true":
                file_str = file_str + "cloud_admin_role = 'admin'\n"
                file_str = file_str + "aaa_mode = 'rbac'\n"
        if "env_password" in testbed_py_dict[clus]:
            file_str = file_str + env_password_string
        if "env_ostypes" in testbed_py_dict[clus]:
            file_str = file_str + env_ostypes_string
        if (("external_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]) and (
                "internal_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"])):
            file_str = file_str + "ha_setup = True\n"
            file_str = file_str + "env.ha = {\n"
            file_str = file_str + \
                "	'internal_vip' : '%s',\n" % cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
            if "contrail_internal_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "	'contrail_internal_vip' : '%s',\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_vip"]
            if "contrail_internal_virtual_router_id" in cluster_dict[
                    clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "	'contrail_internal_virtual_router_id' : %s,\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_virtual_router_id"]
            if "contrail_external_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "	'contrail_external_vip' : '%s',\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
            if "contrail_external_virtual_router_id" in cluster_dict[
                    clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "	'contrail_external_virtual_router_id' : %s,\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_virtual_router_id"]
            file_str = file_str + \
                "	'external_vip' : '%s'\n}\n\n" % cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
        if "ipmi_username" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ipmi_username = '%s'\n" % testbed_py_dict[clus]["ipmi_username"]
        if "ipmi_password" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ipmi_password = '%s'\n\n" % testbed_py_dict[clus]["ipmi_password"]
        file_str = file_str + \
            "env.cluster_id='%s'\n" % cluster_dict[clus]["cluster_id"]
        if "minimum_diskGB" in testbed_py_dict[clus]:
            file_str = file_str + \
                "minimum_diskGB = %d\n" % testbed_py_dict[clus]["minimum_diskGB"]
        if "env.test_repo_dir" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.test_repo_dir= '%s'\n" % testbed_py_dict[clus]["env.test_repo_dir"]
        if "env.mail_from" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_from= '%s'\n" % testbed_py_dict[clus]["env.mail_from"]
        if "env.mail_to" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_to= '%s'\n" % testbed_py_dict[clus]["env.mail_to"]
        if "env.mail_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_server = '%s'\n" % testbed_py_dict[clus]["env.mail_server"]
        if "env.mail_port" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_port = '%s'\n" % testbed_py_dict[clus]["env.mail_port"]
        if "multi_tenancy" in testbed_py_dict[clus]:
            file_str = file_str + \
                "multi_tenancy= %s\n" % testbed_py_dict[clus]["multi_tenancy"]
        if "env.interface_rename" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.interface_rename = %s\n" % testbed_py_dict[clus]["env.interface_rename"]
        if "env.encap_priority" in testbed_py_dict[clus]:
            file_str = file_str + \
                'env.encap_priority = "%s"\n' % testbed_py_dict[clus]["env.encap_priority"]
        if "env.enable_lbaas" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.enable_lbaas = %s\n" % testbed_py_dict[clus]["env.enable_lbaas"]
        if "enable_ceilometer" in testbed_py_dict[clus]:
            file_str = file_str + \
                "enable_ceilometer = %s\n" % testbed_py_dict[clus]["enable_ceilometer"]
        if "ceilometer_polling_interval" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ceilometer_polling_interval = %d\n" % testbed_py_dict[clus]["ceilometer_polling_interval"]
        if "do_parallel" in testbed_py_dict[clus]:
            file_str = file_str + \
                "do_parallel = %s\n" % testbed_py_dict[clus]["do_parallel"]
        if "env.image_web_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.image_web_server = '%s'\n" % testbed_py_dict[clus]["env.image_web_server"]
        if "env.testbed_location" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.testbed_location = '%s'\n" % testbed_py_dict[clus]["env.testbed_location"]
        if "env.mx_gw_test" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mx_gw_test = %s\n" % testbed_py_dict[clus]["env.mx_gw_test"]
        if "env.ntp_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.ntp_server = '%s'\n" % testbed_py_dict[clus]["env.ntp_server"]
        if "env.rsyslog_params" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.rsyslog_params = %s\n" % testbed_py_dict[clus]["env.rsyslog_params"]
        if "storage_replica_size" in testbed_py_dict[clus]:
            file_str = file_str + \
                "storage_replica_size = %s\n" % testbed_py_dict[clus]["storage_replica_size"]

        dict_of_testbed_files[clus] = file_str
    for testbed in dict_of_testbed_files:
        print dict_of_testbed_files[testbed]

# Method to create testbed.py file for the mainline build


def create_testbedpy_file_mainline():
    dict_of_testbed_files = {}
    for clus in testbed_py_dict:
        file_str = ""
        file_str = file_str + "from fabric.api import env \nimport os\n\nnext_routers = []\n"
        if "router_asn" in testbed_py_dict[clus]:
            file_str = file_str + \
                "router_asn = %s\n\n" % testbed_py_dict[clus]["router_asn"]
        else:
            file_str = file_str + "router_asn = 64512\n\n"
        itr = 1
        if "public_vn_rtgt" in testbed_py_dict[clus]:
            file_str = file_str + \
                "public_vn_rtgt = %s\n\n" % testbed_py_dict[clus]["public_vn_rtgt"]
        if "public_vn_subnet" in testbed_py_dict[clus]:
            file_str = file_str + \
                'public_vn_subnet = "%s"\n\n' % testbed_py_dict[clus]["public_vn_subnet"]
        # hostname_string contains the hostanme of all the servers. This would
        # be added to the main string after wards
        hostname_string = "     'all' : [ "
        build_ip = ""
        control_data_string = "control_data = {\n"
        name_mapping = {}
        if "env_password" in testbed_py_dict[clus]:
            env_password_string = "\nenv.passwords = {\n"
        if "env_ostypes" in testbed_py_dict[clus]:
            env_ostypes_string = "env.ostypes = {\n"
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                for j in server_dict[clus][i]["ip_address"]:
                    if network_dict[j]["role"] == "management":
                        if "contrail-controller" in server_dict[clus][i]["roles"]:
                            # Build Ip that will be used in the testbed.py file
                            if "host_build" in testbed_py_dict[clus]:
                                build_ip = testbed_py_dict[clus]["host_build"]
                            else:
                                build_ip = server_dict[clus][i]["ip_address"][j]
                        manag_ip = server_dict[clus][i]["ip_address"][j]
                    else:
                        if network_dict[j]["role"] == "control-data":
                            # control data ip that will be used in the
                            # control-data section of the testbed.py file
                            control_ip = server_dict[clus][i]["ip_address"][j]
                            gateway = network_dict[j]["default_gateway"]
                        else:
                            continue
                for net in network_dict:
                    if network_dict[net]["role"] == 'control-data':
                        if "control_data_vlan" in testbed_py_dict[clus]:
                            control_data_string = control_data_string + "   host%s : { 'ip': '%s', 'gw' : '%s', 'device': 'eth1', 'vlan': '%s'},\n" % (
                                str(itr), control_ip, gateway, testbed_py_dict[clus]["control_data_vlan"])
                        else:
                            control_data_string = control_data_string + \
                                "   host%s : { 'ip': '%s', 'gw' : '%s', 'device': 'eth1'},\n" % (str(itr), control_ip, gateway)
                file_str = file_str + \
                    "host%s = 'root@%s'\n" % (str(itr), manag_ip)
                if "env_password" in testbed_py_dict[clus]:
                    env_password_string = env_password_string + \
                        "   host%s: '%s',\n" % (str(itr), testbed_py_dict[clus]["env_password"])
                if "env_ostypes" in testbed_py_dict[clus]:
                    env_ostypes_string = env_ostypes_string + \
                        "     host%s: '%s',\n" % (str(itr), testbed_py_dict[clus]["env_ostypes"])
                # logic for not adding ',' (comma) after the last hostname in
                # the env.hostname field of the testbed.py being created.
                if itr == len(server_dict[clus]) - 1:
                    hostname_string = hostname_string + "'" + \
                        (server_dict[clus][i]["name"]) + "' "
                    testbed_py_name = "host%s" % str(itr)
                    name_mapping[server_dict[clus][i]
                                 ["name"]] = testbed_py_name
                else:
                    hostname_string = hostname_string + "'" + \
                        (server_dict[clus][i]["name"]) + "', "
                    testbed_py_name = "host%s" % str(itr)
                    name_mapping[server_dict[clus][i]
                                 ["name"]] = testbed_py_name
                itr += 1
        hostname_string = hostname_string + "]\n"
        control_data_string = control_data_string + "}\n\n"

        testbedfile_serverjson_role_mapping = {
            "openstack": "openstack",
            "contrail-controller": "controller",
            "contrail-analytics": "analytics",
            "contrail-analyticsdb": "analyticsdb",
            "contrail-compute": "compute",
            "contrail-lb": "lb"}
        role_per_server_mapping = {
            "all": [],
            "openstack": [],
            "contrail-controller": [],
            "contrail-analytics": [],
            "contrail-analyticsdb": [],
            "contrail-compute": [],
            "build": ["host_build"]}
        if "env_ostypes" in testbed_py_dict[clus]:
            env_ostypes_string = env_ostypes_string + "}\n\n"
        if "env_password" in testbed_py_dict[clus]:
            env_password_string = env_password_string + \
                "   host_build: '%s',\n}\n\n" % testbed_py_dict[clus]["env_password"]
            file_str = file_str + \
                "\nenv.password = '%s'\n" % testbed_py_dict[clus]["env_password"]
        file_str = file_str + "host_build = 'root@%s'\n\n" % build_ip
        # Lets Get the role definitions for all the servers in the input file
        # All the hostnames for env.roles section in testbed.py file
        all_host_list = name_mapping.values()
        for i in all_host_list:
            role_per_server_mapping["all"].append(i)
        for i in server_dict[clus]:
            if server_dict[clus][i]["server_manager"] != "true":
                if "openstack" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["openstack"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "contrail-controller" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["contrail-controller"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "contrail-analytics" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["contrail-analytics"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "contrail-analyticsdb" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["contrail-analyticsdb"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "contrail-compute" in server_dict[clus][i]["roles"]:
                    role_per_server_mapping["contrail-compute"].append(
                        name_mapping[server_dict[clus][i]["name"]])
                if "contrail-lb" in server_dict[clus][i]["roles"]:
                    if "contrail-lb" in role_per_server_mapping:
                        role_per_server_mapping["contrail-lb"].append(
                            name_mapping[server_dict[clus][i]["name"]])
                    else:
                        role_per_server_mapping["contrail-lb"] = []
                        role_per_server_mapping["contrail-lb"].append(
                            name_mapping[server_dict[clus][i]["name"]])
        file_str = file_str + "env.hostnames = {\n"
        file_str = file_str + hostname_string + "}\n\n"
        file_str = file_str + "env.interface_rename = False\n\n"
        for net in network_dict:
            if network_dict[net]["role"] == "control-data":
                file_str = file_str + control_data_string
        # Print all the role defs referenced from the 'role_per_server_mapping'
        # dict mention above
        file_str = file_str + "env.roledefs = {\n"
        #itr = len(role_per_server_mapping)
        itr = 1
        for i in role_per_server_mapping:
            #inner_iter = len(role_per_server_mapping[i])
            inner_iter = 1
            if i not in testbedfile_serverjson_role_mapping:
                file_str = file_str + "\t'%s' : [ " % i
            else:
                file_str = file_str + \
                    "\t'%s' : [ " % testbedfile_serverjson_role_mapping[i]
            for j in role_per_server_mapping[i]:
                if inner_iter == len(role_per_server_mapping[i]):
                    file_str = file_str + j + " ]"
                else:
                    file_str = file_str + "%s, " % j
                inner_iter += 1
            if itr == len(role_per_server_mapping):
                file_str = file_str + "\n"
            else:
                file_str = file_str + ",\n"
            itr += 1
        file_str = file_str + "}\n\n"
        if "openstack_admin_password" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.openstack_admin_password = '%s'\n" % testbed_py_dict[clus]["openstack_admin_password"]
        if "env.log_scenario" in testbed_py_dict[clus]:
            log_scenario_str = ''
            if "auth_protocol" in testbed_py_dict[clus]["env.log_scenario"]:
                if testbed_py_dict[clus]["env.log_scenario"]["auth_protocol"] == "https":
                    if "keystone_version" in testbed_py_dict[clus]["env.log_scenario"]:
                        if testbed_py_dict[clus]["env.log_scenario"]["keystone_version"] == "v3":
                            if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                                log_scenario_str = log_scenario_str + \
                                    "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                            log_scenario_str = log_scenario_str + \
                                "env.keystone = {\n"
                            log_scenario_str = log_scenario_str + "	'version': 'v3',\n"
                            log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                            log_scenario_str = log_scenario_str + "}\n"
                    else:
                        if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                            log_scenario_str = log_scenario_str + \
                                "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                        log_scenario_str = log_scenario_str + \
                            "env.keystone = {\n"
                        log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                        log_scenario_str = log_scenario_str + "}\n"
                    log_scenario_str = log_scenario_str + "env.cfgm = {\n"
                    log_scenario_str = log_scenario_str + "	'auth_protocol': 'https'\n"
                    log_scenario_str = log_scenario_str + "}\n"
                else:
                    if "description" in testbed_py_dict[clus]["env.log_scenario"]:
                        log_scenario_str = log_scenario_str + \
                            "env.log_scenario= %s\n" % testbed_py_dict[clus]["env.log_scenario"]["description"]
                    else:
                        pass
                file_str = file_str + log_scenario_str
        if "enable_rbac" in testbed_py_dict[clus]:
            if testbed_py_dict[clus]["enable_rbac"] == "true":
                file_str = file_str + "cloud_admin_role = 'admin'\n"
                file_str = file_str + "aaa_mode = 'rbac'\n"
        if "env_password" in testbed_py_dict[clus]:
            file_str = file_str + env_password_string
        if "env_ostypes" in testbed_py_dict[clus]:
            file_str = file_str + env_ostypes_string
        if (("contrail_external_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]) and (
                "contrail_internal_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"])):
            file_str = file_str + "ha_setup = True\n"
            file_str = file_str + "env.ha = {\n"
            if "contrail_internal_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "   'contrail_internal_vip' : '%s',\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_vip"]
            if "contrail_external_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
                file_str = file_str + \
                    "   'contrail_external_vip' : '%s'\n}\n\n" % cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
        '''
		if (("external_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"]) and ("internal_vip" in cluster_dict[clus]["parameters"]["provision"]["openstack"])):
			file_str = file_str+"ha_setup = True\n"
			file_str = file_str + "env.ha = {\n"
			file_str = file_str+"	'internal_vip' : '%s',\n"%cluster_dict[clus]["parameters"]["provision"]["openstack"]["internal_vip"]
			if "contrail_internal_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
				file_str = file_str+"	'contrail_internal_vip' : '%s',\n"%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_vip"]
			if "contrail_internal_virtual_router_id" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
				file_str = file_str+"	'contrail_internal_virtual_router_id' : %s,\n"%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_internal_virtual_router_id"]
			if "contrail_external_vip" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
				file_str = file_str+"	'contrail_external_vip' : '%s',\n"%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_vip"]
			if "contrail_external_virtual_router_id" in cluster_dict[clus]["parameters"]["provision"]["contrail"]:
				file_str = file_str+"	'contrail_external_virtual_router_id' : %s,\n"%cluster_dict[clus]["parameters"]["provision"]["contrail"]["contrail_external_virtual_router_id"]
			file_str = file_str+"	'external_vip' : '%s'\n}\n\n"%cluster_dict[clus]["parameters"]["provision"]["openstack"]["external_vip"]
		'''
        if "ipmi_username" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ipmi_username = '%s'\n" % testbed_py_dict[clus]["ipmi_username"]
        if "ipmi_password" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ipmi_password = '%s'\n\n" % testbed_py_dict[clus]["ipmi_password"]
        file_str = file_str + \
            "env.cluster_id='%s'\n" % cluster_dict[clus]["cluster_id"]
        if "minimum_diskGB" in testbed_py_dict[clus]:
            file_str = file_str + \
                "minimum_diskGB = %d\n" % testbed_py_dict[clus]["minimum_diskGB"]
        if "env.test_repo_dir" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.test_repo_dir= '%s'\n" % testbed_py_dict[clus]["env.test_repo_dir"]
        if "env.mail_from" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_from= '%s'\n" % testbed_py_dict[clus]["env.mail_from"]
        if "env.mail_to" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_to= '%s'\n" % testbed_py_dict[clus]["env.mail_to"]
        if "env.mail_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_server = '%s'\n" % testbed_py_dict[clus]["env.mail_server"]
        if "env.mail_port" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mail_port = '%s'\n" % testbed_py_dict[clus]["env.mail_port"]
        if "multi_tenancy" in testbed_py_dict[clus]:
            file_str = file_str + \
                "multi_tenancy= %s\n" % testbed_py_dict[clus]["multi_tenancy"]
        if "env.interface_rename" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.interface_rename = %s\n" % testbed_py_dict[clus]["env.interface_rename"]
        if "env.encap_priority" in testbed_py_dict[clus]:
            file_str = file_str + \
                'env.encap_priority = "%s"\n' % testbed_py_dict[clus]["env.encap_priority"]
        if "env.enable_lbaas" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.enable_lbaas = %s\n" % testbed_py_dict[clus]["env.enable_lbaas"]
        if "enable_ceilometer" in testbed_py_dict[clus]:
            file_str = file_str + \
                "enable_ceilometer = %s\n" % testbed_py_dict[clus]["enable_ceilometer"]
        if "ceilometer_polling_interval" in testbed_py_dict[clus]:
            file_str = file_str + \
                "ceilometer_polling_interval = %d\n" % testbed_py_dict[clus]["ceilometer_polling_interval"]
        if "do_parallel" in testbed_py_dict[clus]:
            file_str = file_str + \
                "do_parallel = %s\n" % testbed_py_dict[clus]["do_parallel"]
        if "env.image_web_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.image_web_server = '%s'\n" % testbed_py_dict[clus]["env.image_web_server"]
        if "env.testbed_location" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.testbed_location = '%s'\n" % testbed_py_dict[clus]["env.testbed_location"]
        if "env.mx_gw_test" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.mx_gw_test = %s\n" % testbed_py_dict[clus]["env.mx_gw_test"]
        if "env.ntp_server" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.ntp_server = '%s'\n" % testbed_py_dict[clus]["env.ntp_server"]
        if "env.rsyslog_params" in testbed_py_dict[clus]:
            file_str = file_str + \
                "env.rsyslog_params = %s\n" % testbed_py_dict[clus]["env.rsyslog_params"]
        if "storage_replica_size" in testbed_py_dict[clus]:
            file_str = file_str + \
                "storage_replica_size = %s\n" % testbed_py_dict[clus]["storage_replica_size"]

        dict_of_testbed_files[clus] = file_str
    for testbed in dict_of_testbed_files:
        print dict_of_testbed_files[testbed]

# Method to get the control data ip with mask so that it can be used in
# server.json required for the mainline build(contrail 4.0 onwards)


def get_control_data_ip_sm():
    ret_ip = ''
    for clus in server_dict:
        for server in server_dict[clus]:
            if server_dict[clus][server]["server_manager"] == "true":
                for i in server_dict[clus][server]["ip_address"]:
                    if len(server_dict[clus][server]["ip_address"]) == 1:
                        ret_ip = server_dict[clus][server]["ip_address"][i]
                        mask_list = network_dict[i]["ip_block_with_mask"].split(
                            '/')
                        ret_ip = ret_ip + '/' + mask_list[1]
                    else:
                        if network_dict[i]["role"] == "control-data":
                            ret_ip = server_dict[clus][server]["ip_address"][i]
                            mask_list = network_dict[i]["ip_block_with_mask"].split(
                                '/')
                            ret_ip = ret_ip + '/' + mask_list[1]
    print ret_ip


if __name__ == '__main__':
    globals()[sys.argv[2]]()
