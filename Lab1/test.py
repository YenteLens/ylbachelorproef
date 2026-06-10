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

firewalls = {}
all_devices = {}

def login():
    response = session.post(
        login_url,
        json={"username": "admin", "password": "eve", "html5": "0"},
        verify=CA_CERT_PATH
    )
    # checks for errors in HTTP response, if it finds one execution is stopped
    response.raise_for_status()
    print("Logged in")

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

def start(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes/{node_id}/start"
    response = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
    print(f"Device with id: {node_id} started")

def get_port(node_id):
    url = 'https://evepro.interligo.local/api/labs/Labs/Lab1.unl/nodes'

    login()

    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    port_details = node_dict[f'{node_id}']['url']
    port_number = int(port_details[-5:])

    return port_number

def upload_config(port_number, node_name, node_id):
    login()

    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    print(f"Uploading {node_name} config.")

    with open(f"./configs/Automation/{node_name}.txt", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r')
            time.sleep(1)
    print("Done.")
    time.sleep(5)

def export_config(node_id, port_number):
    url = f"https://evepro.interligo.local/api/labs/Labs//Lab1.unl/nodes/{node_id}/export"

    # tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    # for _ in range (3):
    #     tn.write(b"\r\n")

    login()
    response = session.put(url=url, verify=CA_CERT_PATH)
    print(f"Config of node {node_id} exported.")
    print(response.json())

def enable_startup(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs//Lab1.unl/nodes/{node_id}"
    data = {"config":"1"}

    response = session.put(url=url, json=data, verify=CA_CERT_PATH)
    print(f"Node {node_id} startup config enabled.")

##############################################

login()
create_firewall()

all_devices.update(firewalls)

for device in all_devices:
    start(all_devices[device])

print("Waiting 300 seconds to let all devices boot.")
time.sleep(300)
print("Sleep finished.")

for device in all_devices:
    tn_port = get_port(all_devices[device])
    upload_config(tn_port, device, all_devices[device])
    export_config(all_devices[device], tn_port)