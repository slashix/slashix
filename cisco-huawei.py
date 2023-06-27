import yaml

def load_vlan_database():
    with open('vlan_database.yaml') as file:
        vlan_database = yaml.safe_load(file)
    return vlan_database

def load_vlan_dpk_database():
    with open('vlan_dpk_database.yaml') as file:
        vlan_dpk_database = yaml.safe_load(file)
    return vlan_dpk_database

def load_cisco_config(file_path):
    with open(file_path) as file:
        cisco_config = yaml.safe_load(file)
    return cisco_config

def convert_config(cisco_config, huawei_interfaces):
    vlan_database = load_vlan_database()
    vlan_dpk_database = load_vlan_dpk_database()

    huawei_config = ''

    trunk_ports = input("Введите номера физических интерфейсов, разделенные запятой: ").split(", ")

    huawei_config += f"interface Eth-Trunk{min(huawei_interfaces)}\n"
    huawei_config += f" description {cisco_config['interface']['description']}\n"
    huawei_config += " stp edged-port enable\n"
    huawei_config += " mode lacp-dynamic\n"

    if 'vpc' in cisco_config:
        huawei_config += f" dfs-group 1 m-lag {min(huawei_interfaces)}\n"

    for port in trunk_ports:
        huawei_config += f" trunkport {port}\n"

    huawei_config += "\n"

    for interface, vlans in huawei_interfaces.items():
        for vlan in vlans:
            if vlan in vlan_dpk_database:
                huawei_config += "########DPK_VLAN##########\n"

            huawei_config += f" interface Eth-Trunk{interface}.{vlan} mode l2\n"
            huawei_config += f"  description {vlan_database.get(vlan, 'Unknown VLAN')}\n"
            huawei_config += f"  encapsulation dot1q vid {vlan}\n"
            huawei_config += f"  bridge-domain {vlan}\n"
            huawei_config += " #\n\n"

            if vlan in vlan_dpk_database:
                huawei_config += "##########################\n\n"

    return huawei_config

cisco_config_path = 'cisco.cfg'
huawei_interfaces = {
    3: [200, 991, 999, 1000]
    # остальная часть конфигурации Huawei
}

cisco_config = load_cisco_config(cisco_config_path)
huawei_config = convert_config(cisco_config, huawei_interfaces)
print(huawei_config)
