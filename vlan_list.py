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
vlan_data = []
for vlan in vlan_list[3:-1]:
    if vlan.startswith(" "):
        continue
    if "active" in vlan:
        vlan_data.append(vlan.split()[:2])

with open("vlan_list.txt", "w") as f:
    for vlan in vlan_data:
        f.write(";".join(vlan) + "\n")

connection.disconnect()
