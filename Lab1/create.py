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


#topology connections
links = [
    ("R1", 0, "R3", 1),
    ("R1", 1, "R2", 0),
    ("R1", 2, "SW1", 0),
    ("R1", 3, "ASA", 1),
    ("R2", 1, "R3", 0),
    ("R2", 2, "SW2", 0),
    ("R3", 2, "SW3", 0),
    ("SW2", 1, "HR", 0),
    ("SW3", 1, "IT", 0),
    ("SW1", 1, "Reception", 0),
    ("ASA", 2, "External", 0),
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
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes'
    base_data = {"image": "vios-adventerprisek9-m.spa.159-3.m9", "name": "vIOS", "icon": "Router.png",
                 "cpulimit": 1, "cpu": 1, "ram": 1024, "ethernet": 4, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 700, "top": 240, "count": 1,
                 "template": "vios", "type": "qemu", "postfix": 0}

    for i in range(3):
        data = base_data.copy()

        # give the devices a unique name and location
        data["name"] = f"R{i + 1}"
        match data["name"]:
            case "R2":
                data["left"] = 550
                data["top"] = 400
            case "R3":
                data["left"] = 850
                data["top"] = 400
            case _:
                pass  # does nothing

        # turn data into JSON
        # create the devices and store the response to extract the device_id
        login()
        create_api = session.post(url=create_url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        routers[data["name"]] = device_id
        print(f"Created router with device id: {device_id}")


def create_switch():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes'
    base_data = {"image": "viosl2-adventerprisek9-m-15.2.4055", "name": "Switch", "icon": "Switch.png", "cpulimit": 1,
                 "cpu": 1, "ram": 1024, "ethernet": 8, "qemu_version": "2.4.0", "qemu_arch": "x86_64",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 550, "top": 240, "count": 1,
                 "template": "viosl2", "type": "qemu", "postfix": 0}

    for i in range(3):
        data = base_data.copy()

        # give the devices a unique name and location
        data["name"] = f"SW{i + 1}"
        match data["name"]:
            case "SW2":
                data["top"] = 550
            case "SW3":
                data["top"] = 550
                data["left"] = 850


        login()
        create_api = session.post(url=create_url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        switches[data["name"]] = device_id
        print(f"Created switch with device id: {device_id}")


def create_firewall():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes'
    base_data = {"image": "asav-9-20-2-22", "name": "ASA", "icon": "Firewall.png", "cpulimit": 1, "cpu": 1,
                 "ram": 2048, "ethernet": 8, "qemu_version": "2.12.0", "qemu_arch": "x86_64",
                 "qemu_nic": "virtio-net-pci",
                 "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -cpu host -nodefaults -display none -vga std -rtc base=utc",
                 "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 850, "top": 240, "count": 1,
                 "template": "asav", "type": "qemu", "postfix": 0}


    login()
    create_api = session.post(url=create_url, json=base_data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    firewalls[base_data["name"]] = device_id
    print(f"Created firewall with device id: {device_id}")


def create_cloud():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/networks'
    base_data = {"name": "Internet", "type": "pnet1", "icon": "01-Cloud-Default.svg", "left": 850, "top": 100,
                 "count": 1, "postfix": 0, "visibility": 1}

    login()
    create_api = session.post(url=create_url, json=base_data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    cloud[base_data["name"]] = device_id
    print(f"Created cloud with network id: {device_id}")


def create_vpc():
    create_url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes'
    base_data = {"name": "VPC", "icon": "Desktop.png", "config": "0", "sat": "-1", "delay": 0, "left": 400,
                 "top": 240, "count": 1, "template": "vpcs", "type": "vpcs", "postfix": 0}

    for i in range(4):
        data = base_data.copy()

        # give the devices a unique name and location
        data["name"] = f"VPC{i + 1}"
        match data["name"]:
            case "VPC1":
                data["left"] = 550
                data["top"] = 700
                data["name"] = "HR"
            case "VPC2":
                data["left"] = 850
                data["top"] = 700
                data["name"] = "IT"
            case "VPC3":
                data["left"] = 1000
                data["top"] = 240
                data["name"] = "External"
            case "VPC4":
                data["name"] = "Reception"


        login()
        create_api = session.post(url=create_url, json=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        vpcs[data["name"]] = device_id
        print(f"Created vpc with device id: {device_id}")

def create_network():
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/networks'
    data = {"count":1,"name":"Net-R2iface0","type":"bridge","visibility":1,"left":0,"top":0,"postfix":0}

    login()
    response = session.post(url=url, json=data, verify=CA_CERT_PATH)
    network_id = response.json()['data']['id']
    #return the network device ID
    return network_id

def connect_interfaces(node_id,interface_id,network_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes/{node_id}/interfaces"

    data = {
        interface_id:network_id
    }

    response = session.put(url=url, json=data, verify=CA_CERT_PATH)
    print(response.json())

def hide_networks(network_id):
    hide_data = {"visibility": 0}
    hide_url = f'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/networks/{network_id}'
    response = session.put(url=hide_url, json=hide_data,verify=CA_CERT_PATH)

def start(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes/{node_id}/start"
    response = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
    print(f"Device with id: {node_id} started")

# End function declarations

create_router()
create_switch()
create_firewall()
create_cloud()
create_vpc()

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
#connect firewall to internet separately
connect_interfaces(firewalls["ASA"],3,cloud["Internet"])

for device in all_devices:
    start(all_devices[device])

print("Waiting 165 seconds to let all devices boot.")
time.sleep(165)
print("Sleep finished.")