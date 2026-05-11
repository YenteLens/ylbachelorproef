import time
import requests
import json

from paramiko.auth_handler import GssapiWithMicAuthHandler
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
routers = {}
switches = {}
firewalls = {}
cloud = {}
vpcs = {}

all_devices = {}

links = [
    ("ASA", 1, "External-R", 0),
    ("ASA", 2, "R1", 0),
    ("ASA", 3, "DMZ-R", 0),
    ("R1", 1, "SW1", 3),
    ("R1", 2, "R2", 0),
    ("R2", 1, "SW2", 3),
    ("SW1", 0, "SW3", 1),
    ("SW1", 1, "SW2", 0),
    ("SW1", 2, "SW4", 2),
    ("SW2", 1, "SW4", 0),
    ("SW2", 2, "SW3", 2),
    ("SW3", 3, "PC1", 0),
    ("SW4", 3, "PC2", 0),
    ("External-R", 1, "PC3", 0),
    ("DMZ-R", 1, "DMZ-Server", 0),
]


# Start function declarations

def login():
    response = session.post(
        login_url,
        json={"username": "admin", "password": "eve", "html5": "0"},
        verify=CA_CERT_PATH
    )
    # checks for errors in HTTP response, if it finds one execution is stopped
    response.raise_for_status()
    print("Logged in")


def create_router():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes'
    base_data = {"image": "vios-adventerprisek9-m.spa.159-3.m9", "name": "vIOS", "icon": "Router.png", "cpulimit": 1,
                 "cpu": 1, "ram": 1024, "ethernet": 4, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 750, "top": 250, "count": 1,
                 "template": "vios", "type": "qemu", "postfix": 0}

    for i in range(4):
        data = base_data.copy()

        # Give each device a unique name and location
        data["name"] = f"R{i + 1}"

        match data["name"]:
            case "R2":
                data["top"] = 450
            case "R3":
                data["top"] = 450
                data["left"] = 350
                data["name"] = "External-R"
            case "R4":
                data["left"] = 350
                data["name"] = "DMZ-R"

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        routers[data["name"]] = device_id
        print(f"Created router with device id: {device_id}")


def create_switch():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes'
    base_data = {"image": "viosl2-adventerprisek9-m-15.2.4055", "name": "Switch", "icon": "Switch.png", "cpulimit": 1,
                 "cpu": 1, "ram": 1024, "ethernet": 8, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 900, "top": 250, "count": 4,
                 "template": "viosl2", "type": "qemu", "postfix": 0}

    for i in range(4):
        data = base_data.copy()

        # Give each device a unique name and location
        data["name"] = f"SW{i + 1}"

        match data["name"]:
            case "SW2":
                data["top"] = 450
            case "SW3":
                data["left"] = 1100
            case "SW4":
                data["top"] = 450
                data["left"] = 1100

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        switches[data["name"]] = device_id
        print(f"Created switch with device id: {device_id}")


def create_firewall():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes'
    base_data = {"image": "asav-9-20-2-22", "name": "ASA", "icon": "Firewall.png", "cpulimit": 1, "cpu": 1,
                 "ram": 2048, "ethernet": 8, "qemu_version": "2.12.0", "qemu_arch": "x86_64",
                 "qemu_nic": "virtio-net-pci",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -cpu host -nodefaults -display none -vga std -rtc base=utc",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 550, "top": 250, "count": 1,
                 "template": "asav", "type": "qemu", "postfix": 0}

    login()
    create_api = session.post(url=url, json=base_data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    firewalls[base_data["name"]] = device_id
    print(f"Created firewall with device id: {device_id}")


def create_vpc():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes'
    base_data = {"name": "VPC", "icon": "Desktop.png", "config": "0", "sat": "-1", "delay": 0, "left": 1250, "top": 250,
                 "count": 4, "template": "vpcs", "type": "vpcs", "postfix": 0}

    for i in range(4):
        data = base_data.copy()

        data["name"] = f"PC{i + 1}"

        match data["name"]:
            case "PC2":
                data["top"] = 450
            case "PC3":
                data["left"] = 200
                data["top"] = 450
            case "PC4":
                data["left"] = 200
                data["name"] = "DMZ-Server"
                data["icon"] = "Server.png"

        login()
        create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        vpcs[data["name"]] = device_id
        print(f"Created vpc with device id: {device_id}")

def create_cloud():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/networks'
    base_data = {"name": "Internet", "type": "pnet1", "icon": "01-Cloud-Default.svg", "left": 550, "top": 550,
                 "count": 1, "postfix": 0, "visibility": 1}

    login()
    create_api = session.post(url=create_url, json=base_data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    cloud[base_data["name"]] = device_id
    print(f"Created cloud with network id: {device_id}")

def create_network():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/networks'
    data = {"count":1,"name":"Net-R2iface0","type":"bridge","visibility":1,"left":0,"top":0,"postfix":0}

    login()
    response = session.post(url=url, json=data, verify=CA_CERT_PATH)
    network_id = response.json()['data']['id']
    #return the network device ID
    return network_id

def connect_interfaces(node_id,interface_id,network_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes/{node_id}/interfaces"

    data = {
        interface_id:network_id
    }

    response = session.put(url=url, json=data, verify=CA_CERT_PATH)
    print(response.json())

def hide_networks(network_id):
    hide_data = {"visibility": 0}
    hide_url = f'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/networks/{network_id}'
    response = session.put(url=hide_url, json=hide_data,verify=CA_CERT_PATH)

def start(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes/{node_id}/start"
    response = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
    print(f"Device with id: {node_id} started")

def get_port(node_id):
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab2.unl/nodes'

    login()

    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    port_details = node_dict[f'{node_id}']['url']
    port_number = int(port_details[-5:])

    return port_number

def telnet_init(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"no\n")

    tn.write(b"\r\n")

def upload_config(port_number, node_name):
    login()

    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    print(f"Uploading {node_name} config.")

    with open(f"./configs/Automation/{node_name}.txt", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r')
            time.sleep(1)
    print("Done.")

# End function definitions

create_router()
create_switch()
create_firewall()
create_vpc()
create_cloud()

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
#connect firewall to internet separately
connect_interfaces(firewalls["ASA"],4,cloud["Internet"])

for device in all_devices:
    start(all_devices[device])

print("Waiting 165 seconds to let all devices boot.")
time.sleep(165)
print("Sleep finished.")

for device in all_devices:
    tn_port = get_port(all_devices[device])
    if device != "ASA":
        telnet_init(tn_port)
        upload_config(tn_port,device)
    else:
        upload_config(tn_port,device)