import time
import requests
import json

#from paramiko.auth_handler import GssapiWithMicAuthHandler
from telnetlib3 import Telnet
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

login_url = 'https://evepro.interligo.local/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"0"}'
headers = {'Accept': 'application/json'}

# global session and certificate
session = requests.session()
CA_CERT_PATH = "./eveng.crt"

# device_ids
nxos = {}
routers = {}
switches = {}
firewalls = {}
cloud = {}
vpcs = {}

all_devices = {}

# Topology
links = [
    ("Core-RT-A", 0, "Core-RT-C", 2),
    ("Core-RT-A", 1, "Core-RT-B", 1),
    ("Core-RT-A", 2, "Core-RT-B", 3),
    ("Core-RT-A", 3, "ASA-Edge", 1),
    ("Core-RT-A", 4, "ASA-Edge", 2),
    ("Core-RT-A", 5, "DMZ-Router", 0),
    ("Core-RT-B", 2, "Core-RT-C", 1),
    ("Core-RT-B", 4, "ASA-DMZ", 1),
    ("Core-RT-B", 5, "Access-SW", 0),
    ("Core-RT-B", 6, "Access-SW", 1),
    ("Core-RT-B", 7, "SW-B", 0),
    ("Core-RT-B", 8, "SW-B", 1),
    ("Core-RT-C", 3, "SW-C", 0),
    ("Core-RT-C", 4, "SW-C", 1),
    ("SW-C", 2, "C-Host", 0),
    ("SW-B", 2, "B-PC2", 0),
    ("Access-SW", 2, "Printer", 0),
    ("Access-SW", 3, "B-PC1", 0),
    ("ASA-DMZ", 2, "DMZ-SW", 0),
    ("DMZ-SW", 1, "DMZ-Host-B", 0),
    ("DMZ-Router", 1, "DMZ-Host-A", 0),
    ("ASA-Edge", 3, "ASA-S2S", 1),
    ("ASA-Edge", 4, "WAN-SW", 0),
    ("ASA-S2S", 2, "WAN-SW", 1),
    ("Remote-ASA", 2, "Remote-SW", 0),
    ("Remote-SW", 1, "Remote-Host", 0),
]


# Functions

def login():
    response = session.post(
        login_url,
        json={"username": "admin", "password": "eve", "html5": "0"},
        verify=CA_CERT_PATH
    )
    # checks for errors in HTTP response, if it finds one execution is stopped
    response.raise_for_status()
    #print("Logged in")

def create_folder(folder_name):
    if folder_check(folder_name):
        print(f"Folder '{folder_name}' already exists")
        return

    url = "https://evepro.interligo.local/api/folders"
    data = {"path": "/", "name": f"{folder_name}"}

    create_api = session.post(url=url, headers=headers, json=data, verify=CA_CERT_PATH)
    response = create_api.json()

    print(response)


def folder_check(folder_name):
    url = "https://evepro.interligo.local/api/folders//"

    response = session.get(url=url, headers=headers, verify=CA_CERT_PATH)
    response.raise_for_status()

    data = response.json()

    folders = data.get("data", {}).get("folders", [])

    for folder in folders:
        if folder.get("name") == folder_name:
            return True

    return False


def create_lab(lab_name, folder_name):
    if lab_check(lab_name, folder_name):
        print(f"Lab '{lab_name}' already exists")
        return

    url = "https://evepro.interligo.local/api/labs"
    data = {"path": f"/{folder_name}", "author": "", "body": "", "countdown": 0, "description": "", "grid": 1, "linkwidth": 1,
            "name": f"{lab_name}", "sat": "-1", "scripttimeout": 600, "shared": [], "version": 0}

    create_api = session.post(url=url, headers=headers, json=data, verify=CA_CERT_PATH)
    response = create_api.json()

    print(response)

    activate_url = f"https://evepro.interligo.local/api/labs/{folder_name}/{lab_name}.unl/filter/activate"
    activate_api = session.post(activate_url, headers=headers, verify=CA_CERT_PATH)

    activation = activate_api.json()

    print(activation)

def lab_check(lab_name, folder_name):
    url = f"https://evepro.interligo.local/api/folders/{folder_name}/"

    response = session.get(url=url, headers=headers, verify=CA_CERT_PATH)
    response.raise_for_status()

    data = response.json()

    labs = data.get("data", {}).get("labs", [])


    for lab in labs:
        # EVE-NG stores labs as .unl files
        existing_lab = lab.get("file", "").replace(".unl", "")

        if existing_lab == lab_name:
            return True

    return False

def create_nxos():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'
    base_data = {"image": "nxosv9k-9300v-10.4.2.F", "name": "NXOS", "icon": "Switch-3D-L3-S.svg", "cpulimit": 0,
                 "cpu": 4, "ram": 8192, "ethernet": 9, "qemu_version": "4.1.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -enable-kvm -cpu host",
                 "config": "0", "sat": "3", "delay": 0, "console": "telnet", "left": 600, "top": 500, "count": 1,
                 "template": "nxosv9k", "type": "qemu", "postfix": 0}

    for i in range(2):
        data = base_data.copy()

        data["name"] = f"NXOS{i + 1}"

        match data["name"]:
            case "NXOS1":
                data["name"] = "Core-RT-B"
            case "NXOS2":
                data["name"] = "Core-RT-C"
                data["left"] = 850

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        nxos[data["name"]] = device_id
        print(f"Created nxos with device id: {device_id}")


def create_router():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'
    base_data = {"image": "vios-adventerprisek9-m.spa.159-3.m9", "name": "vIOS", "icon": "Router.png", "cpulimit": 1,
                 "cpu": 1, "ram": 1024, "ethernet": 6, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 725, "top": 350, "count": 1,
                 "template": "vios", "type": "qemu", "postfix": 0}

    for i in range(2):
        data = base_data.copy()

        data["name"] = f"R{i + 1}"

        match data["name"]:
            case "R1":
                data["name"] = "Core-RT-A"
            case "R2":
                data["name"] = "DMZ-Router"
                data["left"] = 400

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        routers[data["name"]] = device_id
        print(f"Created router with device id: {device_id}")


def create_switch():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'
    base_data = {"image": "viosl2-adventerprisek9-m-15.2.4055", "name": "Switch", "icon": "Switch.png", "cpulimit": 1,
                 "cpu": 1, "ram": 1024, "ethernet": 8, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 525, "top": 700, "count": 1,
                 "template": "viosl2", "type": "qemu", "postfix": 0}

    for i in range(6):
        data = base_data.copy()

        data["name"] = f"SW{i + 1}"

        match data["name"]:
            case "SW1":
                data["name"] = "Access-SW"
            case "SW2":
                data["name"] = "SW-B"
                data["left"] = 650
            case "SW3":
                data["name"] = "SW-C"
                data["left"] = 850
            case "SW4":
                data["name"] = "DMZ-SW"
                data["left"] = 250
                data["top"] = 500
            case "SW5":
                data["name"] = "WAN-SW"
                data["left"] = 725
                data["top"] = 125
            case "SW6":
                data["name"] = "Remote-SW"
                data["left"] = 1075
                data["top"] = 250

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        switches[data["name"]] = device_id
        print(f"Created switch with device id: {device_id}")


def create_firewall():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'
    base_data = {"image": "asav-9-20-2-22", "name": "ASAv", "icon": "Firewall.png", "cpulimit": 1, "cpu": 1,
                 "ram": 2048, "ethernet": 8, "qemu_version": "2.12.0", "qemu_arch": "x86_64",
                 "qemu_nic": "virtio-net-pci",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -cpu host -nodefaults -display none -vga std -rtc base=utc",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 425, "top": 500, "count": 1,
                 "template": "asav", "type": "qemu", "postfix": 0}

    for i in range(4):
        data = base_data.copy()

        data["name"] = f"ASA{i + 1}"

        match data["name"]:
            case "ASA1":
                data["name"] = "ASA-DMZ"
            case "ASA2":
                data["name"] = "ASA-Edge"
                data["left"] = 625
                data["top"] = 250
            case "ASA3":
                data["name"] = "ASA-S2S"
                data["left"] = 825
                data["top"] = 250
            case "ASA4":
                data["name"] = "Remote-ASA"
                data["left"] = 1075
                data["top"] = 125
        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        firewalls[data["name"]] = device_id
        print(f"Created firewall with device id: {device_id}")


def create_vpc():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'
    base_data = {"name": "VPC", "icon": "Desktop.png", "config": "0", "sat": "-1", "delay": 0,
                 "left": 250, "top": 350, "count": 1, "template": "vpcs", "type": "vpcs", "postfix": 0}

    for i in range(7):
        data = base_data.copy()

        data["name"] = f"VPC{i + 1}"

        match data["name"]:
            case "VPC1":
                data["name"] = "DMZ-Host-A"
            case "VPC2":
                data["name"] = "DMZ-Host-B"
                data["left"] = 125
                data["top"] = 500
            case "VPC3":
                data["name"] = "Printer"
                data["icon"] = "Server.png"
                data["left"] = 450
                data["top"] = 850
            case "VPC4":
                data["name"] = "B-PC1"
                data["left"] = 550
                data["top"] = 850
            case "VPC5":
                data["name"] = "B-PC2"
                data["left"] = 650
                data["top"] = 850
            case "VPC6":
                data["name"] = "C-Host"
                data["left"] = 850
                data["top"] = 850
            case "VPC7":
                data["name"] = "Remote-Host"
                data["left"] = 1225
                data["top"] = 250

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        vpcs[data["name"]] = device_id
        print(f"Created vpc with device id: {device_id}")

def create_cloud():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/networks'
    base_data = {"name": "Internet", "type": "pnet1", "icon": "01-Cloud-Default.svg", "left": 900, "top": 50,
                 "count": 1, "postfix": 0, "visibility": 1}

    login()
    create_api = session.post(url=create_url, json=base_data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    cloud[base_data["name"]] = device_id
    print(f"Created cloud with network id: {device_id}")

def create_network():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/networks'
    data = {"count":1,"name":"Net-R2iface0","type":"bridge","visibility":1,"left":0,"top":0,"postfix":0}

    login()
    response = session.post(url=url, json=data, verify=CA_CERT_PATH)
    network_id = response.json()['data']['id']
    #return the network device ID
    return network_id

def connect_interfaces(node_id,interface_id,network_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes/{node_id}/interfaces"

    data = {
        interface_id:network_id
    }

    response = session.put(url=url, json=data, verify=CA_CERT_PATH)
    #print(response.json())

def hide_networks(network_id):
    hide_data = {"visibility": 0}
    hide_url = f'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/networks/{network_id}'
    response = session.put(url=hide_url, json=hide_data,verify=CA_CERT_PATH)

def start(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes/{node_id}/start"
    response = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
    print(f"Device with id: {node_id} started")

def get_port(node_id):
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab3.unl/nodes'

    login()

    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    port_details = node_dict[f'{node_id}']['url']
    port_number = int(port_details[-5:])

    return port_number

def telnet_init(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    for _ in range (3):
        tn.write(b"\r\n")

    tn.write(b"no\n")

    tn.write(b"\r\n")
    tn.read_until(b">", timeout=120)

def upload_config(port_number, node_name, node_id):
    login()

    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    print(f"Uploading {node_name} config.")

    if node_name == "Core-RT-B":
        tn.write(b"\n")
        tn.write(b"admin\n")
        time.sleep(10)
        tn.write(b"Root1234?\n")
        time.sleep(10)
    elif node_name == "Core-RT-C":
        tn.write(b"\n")
        tn.write(b"admin\n")
        time.sleep(10)
        tn.write(b"Root1234?\n")
        time.sleep(10)

    with open(f"./configs/Automation/{node_name}.txt", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r')
            time.sleep(1)
    print("Config uploaded.")
    tn.read_until(b"#", timeout=180)

    if node_name == "Core-RT-B" or node_name == "Core-RT-C":
        time.sleep(60)
        pass
    else:
        login()
        export_config(node_id)

def disable_poap(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)

    for i in range (3):
        tn.write(b"\r\n")

    tn.write(b"yes\r\n")

    time.sleep(5)

def nxos_init(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)

    for i in range (3):
        tn.write(b"\r\n")

    tn.write(b"no\r\n")
    time.sleep(5)
    tn.write(b"Root1234?\n")
    time.sleep(5)
    tn.write(b"Root1234?\n")

    time.sleep(10)

    tn.write(b"no\r\n")

    time.sleep(10)

def export_config(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs//Lab3.unl/nodes/{node_id}/export"

    response = session.put(url=url, verify=CA_CERT_PATH)
    print(f"Config of node {node_id} exported.")
    print(response.json())

def enable_startup(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs//Lab3.unl/nodes/{node_id}"
    data = {"config":"1"}

    response = session.put(url=url, json=data, verify=CA_CERT_PATH)
    print(f"Node {node_id} startup config enabled.")

def upload_vpc_conf(port_number, node_name, node_id):
    login()
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)

    time.sleep(2)

    with open(f"./configs/Automation/{node_name}.txt", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip()

            print(f"SENDING: {cmd}")
            tn.write(cmd.encode() + b"\r")
            tn.read_until(b">", timeout=10)

    print("Config uploaded.")
    tn.read_until(b">", timeout=120)
    login()
    export_config(node_id)
# End functions

login()
create_folder("Labs")
create_lab("Lab3", "Labs")

create_nxos()
create_router()
create_switch()
create_firewall()
create_vpc()
create_cloud()

all_devices.update(nxos)
all_devices.update(routers)
all_devices.update(switches)
all_devices.update(firewalls)
all_devices.update(vpcs)


#uses the links declared at the top to connect the devices on the correct interfaces
for device1, int1, device2, int2 in links:

    network_id = create_network()

    connect_interfaces(all_devices[device1], int1, network_id)
    connect_interfaces(all_devices[device2], int2, network_id)
    hide_networks(network_id)
    print(f"{device1}:{int1} <--> {device2}:{int2}")

for device in all_devices:
    login()

    start(all_devices[device])
    time.sleep(2)

print("Letting devices boot, 600 seconds...")
time.sleep(300)
print("5 minutes have passed")
time.sleep(300)
print("Sleep Done")

for switch in nxos:
    tn_port = get_port(nxos[switch])
    disable_poap(tn_port)

print("Sleeping until POAP is disabled")
time.sleep(120)
print("Done")

for n in nxos:
    tn_port = get_port(all_devices[n])
    nxos_init(tn_port)
    upload_config(tn_port,n,nxos[n])
    login()
    export_config(nxos[n])

for r in routers:
    tn_port = get_port(routers[r])
    telnet_init(tn_port)
    upload_config(tn_port, r, routers[r])

for s in switches:
    tn_port = get_port(switches[s])
    telnet_init(tn_port)
    upload_config(tn_port, s, switches[s])

for f in firewalls:
    tn_port = get_port(firewalls[f])
    telnet_init(tn_port)
    upload_config(tn_port, f, firewalls[f])

for v in vpcs:
    tn_port = get_port(vpcs[v])
    upload_vpc_conf(tn_port, v, vpcs[v])

for device in all_devices:
    enable_startup(all_devices[device])


for device in all_devices:
    enable_startup(all_devices[device])


connect_interfaces(switches["WAN-SW"],2,cloud["Internet"])
connect_interfaces(firewalls["Remote-ASA"],1,cloud["Internet"])