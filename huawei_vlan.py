from netmiko import ConnectHandler
import csv

device = {
    'device_type': 'huawei',
    'ip': '<ip_address>',
    'username': '<username>',
    'password': '<password>',
    'port': 22,
    'secret': '<secret>',
    'verbose': False
}

def configure_vlan(connection, vlan_id, vlan_name):
    connection.enable()
    connection.send_command("system-view")
    connection.send_command("vlan " + str(vlan_id))
    connection.send_command("name " + vlan_name)

with open("vlan_list.txt", "r") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        vlan_id = row[0]
        vlan_name = row[1]
        connection = ConnectHandler(**device)
        configure_vlan(connection, vlan_id, vlan_name)
        connection.disconnect()
