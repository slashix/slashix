from netmiko import ConnectHandler

device = {
    'device_type': 'huawei',
    'ip': 'YOUR_DEVICE_IP',
    'username': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
}

with open('vlan_list.txt', 'r') as f:
    vlans = f.readlines()

connection = ConnectHandler(**device)
connection.enable()

for vlan in vlans:
    vlan_info = vlan.strip().split(';')
    vlan_id = vlan_info[0]
    vlan_name = vlan_info[1]
    config_commands = [
        'system-view',
        f'vlan {vlan_id}',
        f'name {vlan_name}'
    ]
    connection.send_config_set(config_commands)

connection.send_command('commit')
connection.disconnect()
