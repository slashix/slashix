import re
import sys
import json
import yaml

from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from paramiko.ssh_exception import SSHException
import netmiko
import getpass


dictionary = {}
device_ip = {
    'smi': {
        'acc1': {'ip': '1.1.1.1'},
        'acc2': {'ip': '1.1.1.2'}
    },
    'str': {
        'acc1': {'ip': '2.2.2.1'},
        'acc2': {'ip': '2.2.2.2'}
    },
    'gzn': {
        'acc1': {'ip': '3.3.3.1'},
        'acc2': {'ip': '3.3.3.2'}
    }
}

location = ''

def input_contour():
    while True:
        contour = input('Enter DPK\DC contour:').lower()
        if contour in ['dpk', 'dc']: break
        else:
            print('Enter a valid contour "DPK" or "DC"')
    if 'dpk' in contour:
        with open('vlan_dpk_list.yaml') as file:
            vlan_data = yaml.safe_load(file)
    elif 'dc' in contour:
        with open('vlan-list.yaml') as file:
            vlan_data = yaml.safe_load(file)
    return vlan_data


def input_location():
    global location
    while True:
        location = input('Enter location (SMI/STR/GZN): ').lower()
        if location in ['smi', 'str', 'gzn']:
            return location
        else:
            print('Enter correct location, please.')

def input_device():
    while True:
        device = input('Введите название устройства (ACC1/ACC2) или введите \'done\' для завершения: ').lower()
        if device == 'done' or device in ['acc1', 'acc2']:
            return device
        else:
            print('Введите корректное название устройства или \'done\' для завершения.')

def parse_blocks(blocks, data, net_connect, result, device):
    print(blocks)
    blocks = blocks.split('version')[-1].split('interface')[1:]  
    
    for block in blocks:
        lines = block.strip().split('\n')  

        

        if 'channel-group' in block:
            interface_dict = {'interface': [lines[0].strip()], 'int_dict_trunk': {}}
            trunk_dict = interface_dict['int_dict_trunk']
            word_list = block.split()
            num_list = [int(num) for num in filter(lambda num: num.isnumeric(), word_list)]
            vpc = net_connect.send_command_timing("sh run int po" + str(num_list[-1]))
            trunk_dict['device'] = device
            if 'vpc' in vpc:
                trunk_dict['vpc'] = 'yes|'+str(num_list[-1])
            else:
                trunk_dict['vpc'] = 'no'
            if 'description' in vpc:
                vpc_desc = vpc.split('description')[1].split(('\n'))[0].strip()
                print(vpc_desc)
                trunk_dict['vpc_description'] = vpc_desc
            if 'mode active' in block or 'mode passive' in block:
                trunk_dict['lacp'] = 'active'
            else:
                trunk_dict['lacp'] = 'static'

            trunk_dict['trunk_ports'] = [data['leaf_port']]
        else:

            interface_dict = {'interface': [lines[0].strip()], 'int_dict_physical': {}}
            physical_dict = interface_dict['int_dict_physical']
            physical_dict['device'] = device
            physical_dict['phys_int'] = [data['leaf_port']]

        trunk = False
        vlan_list = []
        for line in lines:
            line = line.strip()
            

            if line.startswith('description'):
                if 'int_dict_trunk' in interface_dict:
                    trunk_dict['description'] = [line.split('description')[1].strip()]
                else:
                    physical_dict['description'] = [line.split('description')[1].strip()]
            elif line.startswith('mtu'):
                if 'int_dict_trunk' in interface_dict:
                    trunk_dict['mtu'] = line.split('mtu')[1].strip()
                else:
                    physical_dict['mtu'] = line.split('mtu')[1].strip()
            elif line.startswith('spanning-tree port type edge'):
                if 'int_dict_trunk' in interface_dict:
                    trunk_dict['stp'] = "yes"
                else:
                    physical_dict['stp'] = "yes"
            elif line.startswith('switchport mode trunk'):
                trunk = True
                if 'int_dict_trunk' in interface_dict:
                    trunk_dict['switchport mode'] = line.split('switchport mode')[1].strip()
                else:
                    physical_dict['switchport mode'] = line.split('switchport mode')[1].strip()
            elif line.startswith('switchport trunk allowed vlan'):
                vlan_values = line.split('switchport trunk allowed vlan')[1].strip().split(',')
                for vlan in vlan_values:
                    vlan = vlan.strip()
                    if vlan.startswith('add'):
                        vlan = vlan.replace('add', '').strip()
                    if vlan.isdigit():
                        vlan_list.append(int(vlan))
                    elif '-' in vlan:
                        start, end = vlan.split('-')
                        vlan_list.extend(range(int(start), int(end) + 1))
            elif line.startswith('switchport access vlan'):
                if trunk == True: continue
                else:
                    vlan_list = line.split('switchport access vlan')[1].strip()



        if 'int_dict_trunk' in interface_dict:
            trunk_dict['vlan_list'] = vlan_list
        else:
            physical_dict['vlan_list'] = vlan_list

        result.append(interface_dict)
    return result

def merge_dicts_by_vpc(dicts_list):
    vpc_dict = {}
    merged_dicts = []

    
    for interface_dict in dicts_list:
        vpc_value = interface_dict.get("int_dict_trunk", {}).get("vpc")
        device_value = interface_dict.get("int_dict_trunk", {}).get("device")
        if vpc_value is not None and device_value is not None:
            key = (vpc_value, device_value)
            if key not in vpc_dict:
                vpc_dict[key] = []
            vpc_dict[key].append(interface_dict)

    
    for key, dicts_group in vpc_dict.items():
        if len(dicts_group) > 1:
            merged_dict = dicts_group[0].copy()
            trunk_ports_list = []
            description_list = []
            interface_list = []
            for interface_dict in dicts_group:
                interface_list.extend(interface_dict.get("interface", []))
                trunk_ports_list.extend(interface_dict.get("int_dict_trunk", {}).get("trunk_ports", []))
                description_list.extend(interface_dict.get("int_dict_trunk", {}).get("description", []))
            merged_dict["interface"] = interface_list
            merged_dict["int_dict_trunk"]["trunk_ports"] = trunk_ports_list
            merged_dict["int_dict_trunk"]["description"] = description_list
            merged_dicts.append(merged_dict)
        else:
            merged_dicts.extend(dicts_group)

    
    for interface_dict in dicts_list:
        if "int_dict_physical" in interface_dict:
            merged_dicts.append(interface_dict)

    return merged_dicts

def netmiko_config_collector(dictionary):
    login = input('Login: ')
    passwd = getpass.getpass('Password: ')
    result = []
    for location, devices in dictionary.items():
        
        if location in device_ip:
            for device, data_list in devices.items():
                if device in device_ip[location]:
                    data_list = dictionary[location][device]
                    ip = device_ip[location][device]['ip']
                    ios = {
                        'device_type': 'cisco_ios',
                        'ip': ip,
                        'username': login,
                        'password': passwd,
                    }
                    try:
                        with netmiko.ConnectHandler(**ios) as net_connect:
                            for data in data_list:
                                blocks = net_connect.send_command_timing("sh run int eth" + data['port'])
                                parse_blocks(blocks, data, net_connect, result, device)
                    except (NetmikoTimeoutException, NetmikoAuthenticationException, SSHException) as e:
                        print(f"An error occurred while connecting to {device} at {location}: {str(e)}")
        else:
            print(f"No IP address found for devices in {location}.")
    with open("cisco.cfg", "w") as file:
        file.write(json.dumps(result))
    return result

def int_dict_trunk(element, vlan_data):
    config = ''
    int_dict_trunk = element['int_dict_trunk']
    vpc = int_dict_trunk.get('vpc')
    lacp = int_dict_trunk.get('lacp')
    trunk_ports = int_dict_trunk.get('trunk_ports')
    vpc_description = int_dict_trunk.get('vpc_description')
    description = int_dict_trunk.get('description')
    switchport_mode = int_dict_trunk.get('switchport mode')
    vlan_list = int_dict_trunk.get('vlan_list')
    if 'mtu' in element.get('int_dict_trunk'):
        mtu = int_dict_trunk.get('mtu')
    else:
        mtu = 1500
    if 'stp' in element.get('int_dict_trunk'):
        stp = int_dict_trunk.get('stp')
    else:
        stp = 'None'
    eth = int_dict_trunk.get('trunk_ports')
    eth_trunk_list = []
    port = ''
    for trunk in eth:
        eth_trunk_list.append(int(trunk.split('/')[-1]))
        port += f'trunkport 25GE{trunk}\n'
    eth_port = min(eth_trunk_list)
    config += f'interface Eth-Trunk{eth_port}\n'
    config += f'description {vpc_description}\n'
    if 'active' in lacp:
        config += 'mode lacp-static\n'
    elif 'static' in lacp:
        pass
    if int(mtu) != 1500:
        config += f'mtu {mtu}\n'
    if 'yes' in stp:
        config += 'stp edged-port enable\n'
    if 'yes' in vpc:
        config += f'dfs-group 1 m-lag {eth_port}\n'
    config += port
    config += '#\n'
    for int_port, desc in zip(eth, description):
        config += f'interface 25GE{int_port}\ndescription {desc}\n#\n'
    for vlan in vlan_list:
        found = False
        for sublist in vlan_data:
            if sublist[0] == int(vlan):
                vlan_name = sublist[1]
                found = True
                break
        if not found: 
            continue
        config += f'interface Eth-Trunk{eth_port}.{vlan} mode l2\n'
        config += f'description {vpc_description}.{vlan_name}\n'
        config += f'encapsulation dot1q vid {vlan}\n'
        config += f'bridge-domain {vlan}\n'
        config += '#\n'
    config += '#\n'
    return (config)

def int_dict_physical(element, vlan_data):
    config = ''
    int_dict_physical = element['int_dict_physical']
    phys_int = int_dict_physical.get('phys_int')
    if 'description' in element.get('int_dict_physical'):
        description = (int_dict_physical.get('description'))[0]
    else: description = 'None'
    switchport_mode = int_dict_physical.get('switchport mode')
    vlan_list = int_dict_physical.get('vlan_list')
    if 'mtu' in element.get('int_dict_physical'):
        mtu = int_dict_physical.get('mtu')
    else:
        mtu = 1500
    if 'stp' in element.get('int_dict_physical'):
        stp = int_dict_physical.get('stp')
    else:
        stp = 'None'
    config += f'interface 25GE{phys_int[-1]}\n'
    config += f'description {description}\n'
    if int(mtu) != 1500:
        config += f'mtu {mtu}\n'
    if 'yes' in stp:
        config += 'stp edged-port enable\n'

    config += '#\n'
    for vlan in vlan_list:
        found = False
        for sublist in vlan_data:
            if sublist[0] == int(vlan):
                vlan_name = sublist[1]
                found = True
                break
        if not found:  
            continue
        config += f'interface 25GE{phys_int[-1]}.{vlan} mode l2\n'
        config += f'description {description}.{vlan_name}\n'
        config += f'encapsulation dot1q vid {vlan}\n'
        config += f'bridge-domain {vlan}\n'
        config += '#\n'
    config += '#\n'
    return(config)

def conf(output_dicts, vlan_data):
    conf_list = ''
    for element in output_dicts:
        interface = element['interface']

        if 'int_dict_trunk' in element:
            conf_list += int_dict_trunk(element, vlan_data)

        elif 'int_dict_physical' in element:
            conf_list += int_dict_physical(element, vlan_data)
    return (conf_list)


def bd_generator(bd_list, vlan_data, location):
    if location == 'smi':
        asn = '4200102194'
    elif location == 'str':
        asn = '4200102195'
    elif location == 'gzn':
        asn = '4200102196'
    else: asn = '4200102194'
    unique_vlan_list = []
    for dictionary in bd_list:
        if 'vlan_list' in dictionary.get('int_dict_trunk', {}):
            vlan_list = dictionary['int_dict_trunk']['vlan_list']
            if isinstance(vlan_list, list):
                unique_vlan_list.extend(vlan_list)
            else:
                unique_vlan_list.append(vlan_list)

    unique_vlan_list = list(set(unique_vlan_list))
    check_list = [item[0] for item in vlan_data]

    bridge_domain = list(set(check_list) & set(unique_vlan_list))
    with open("hua_conf_dmz.txt", "a") as file:
        file.write('==========BRIDGE DOMAIN COMMON CONFIG==========\n')
    for vlan in vlan_data:
        vlan_id = vlan[0]
        if vlan_id not in bridge_domain:
            continue
        vlan_name = vlan[-1]
        commands = []
        data = """bridge-domain {}
     description {}
     vxlan vni 102{:04}
     #
     evpn
      route-distinguisher auto
      vpn-target {}:{:04} export-extcommunity
      vpn-target 4200102194:{:04} import-extcommunity
      vpn-target 4200102195:{:04} import-extcommunity
      vpn-target 4200102196:{:04} import-extcommunity
    interface Nve1
     vni 102{:04} head-end peer-list protocol bgp
    """.format(vlan_id, vlan_name, int(vlan_id), int(asn), int(vlan_id),int(vlan_id), int(vlan_id), int(vlan_id), int(vlan_id), int(vlan_id))
        with open("hua_conf_dmz.txt", "a") as file:
            file.write(data + "\n")
    with open("hua_conf_dmz.txt", "a") as file:
        file.write('==========BRIDGE DOMAIN BGW CONFIG==========\n')
    for vlan in vlan_data:
        vlan_id = vlan[0]
        if vlan_id not in bridge_domain:
            continue
        vlan_name = vlan[-1]
        commands = []
        data = """bridge-domain {}
     description {}
     vxlan vni 102{:04}
     vxlan vni 1102{:04} split-group dci
     #
     evpn
      route-distinguisher auto
      vpn-target {}:{:04} export-extcommunity
      vpn-target 4200102194:{:04} import-extcommunity
      vpn-target 4200102195:{:04} import-extcommunity
      vpn-target 4200102196:{:04} import-extcommunity
    interface Nve1
     vni 102{:04} head-end peer-list protocol bgp
     vni 1102{:04} head-end peer-list protocol bgp
    """.format(vlan_id, vlan_name, int(vlan_id), int(vlan_id), int(asn), int(vlan_id), int(vlan_id), int(vlan_id), int(vlan_id), int(vlan_id), int(vlan_id))
        with open("hua_conf_dmz.txt", "a") as file:
            file.write(data + "\n")

    with open("hua_conf_dmz.txt", "a") as file:
        file.write('==========REMOVE '+location.upper()+' ACC1/ACC2 VLAN==========\n')
        data = [str(a) for a in bridge_domain]
        data = ', '.join(data)
        file.write(f'interface port-channel7\nswitchport trunk allowed vlan remove {data}\n')
        file.write(f'interface port-channel8\nswitchport trunk allowed vlan remove {data}\n')
        file.write('==========ADD ' + location.upper() + ' ACC1/ACC2 VLAN==========\n')
        file.write(f'interface port-channel7\nswitchport trunk allowed vlan add {data}\n')
        file.write(f'interface port-channel8\nswitchport trunk allowed vlan add {data}\n')

def main():
    vlan_data = input_contour()
    location = input_location()

    while True:
        device = input_device()
        if device == 'done':
            loc = 'break'
            break

        port = input('Enter port number: ')
        leaf = input('Enter Destination Leaf number: ')
        leaf_port = input(f'Enter Leaf{leaf} port number: ')

        if location not in dictionary:
            dictionary[location] = {}

        if device not in dictionary[location]:
            dictionary[location][device] = []

        dictionary[location][device].append({
            'port': port,
            'leaf': leaf,
            'leaf_port': leaf_port
        })

    merge_result = netmiko_config_collector(dictionary)
    output_dicts = merge_dicts_by_vpc(merge_result)
    print('+'*15+'FINAL RESULT'+'+'*15)
    print(output_dicts)
    print('=' * 15 + 'CONFIGURE' + '=' * 15)

    with open("hua_conf_dmz.txt", "w") as file:
        file.write(conf(output_dicts, vlan_data))
    bd_generator(output_dicts, vlan_data, location)
    sys.exit()


if __name__ == "__main__":
    main()
