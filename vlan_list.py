import netmiko

device = {
    "device_type": "cisco_nxos",
    "ip": "192.168.1.1",
    "username": "admin",
    "password": "secret",
    "secret": "secret",
}

connection = netmiko.ConnectHandler(**device)

vlan_list = connection.send_command("show vlan brief")
vlan_list = vlan_list.split("\n")
vlan_list = [vlan.split()[:2] for vlan in vlan_list[3:-1]]

with open("vlan_list.txt", "w") as f:
    for vlan in vlan_list:
        f.write(";".join(vlan) + "\n")

connection.disconnect()
