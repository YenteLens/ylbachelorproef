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


def login():
    response = session.post(
        login_url,
        json={"username": "admin", "password": "eve", "html5": "0"},
        verify=CA_CERT_PATH
    )
    # checks for errors in HTTP response, if it finds one execution is stopped
    response.raise_for_status()
    print("Logged in")


def create_nxos():

    url = "https://evepro.interligo.local/api/labs/Labs/test.unl/nodes"
    data = {"image": "nxosv9k-9500v-10.4.2.F", "name": "NXOS", "icon": "Switch-3D-L3-S.svg", "cpulimit": 0, "cpu": 2,
            "ram": 8192, "ethernet": 8, "qemu_version": "4.1.0", "qemu_arch": "x86_64",
            "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -enable-kvm -cpu host",
            "config": "0", "sat": "-1", "delay": 0, "console": "telnet", "left": 30, "top": 30, "count": 1,
            "template": "nxosv9k", "type": "qemu", "postfix": 0}

    login()
    create_api = session.post(url=url, json=data, headers=headers, verify=CA_CERT_PATH)
    response = create_api.json()

    device_id = response['data']['id']
    print(f"Created nxos.")
    return device_id

def start(node_id):
    url = f"https://evepro.interligo.local/api/labs/Labs/test.unl/nodes/{node_id}/start"
    response = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
    print(f"Device with id: {node_id} started")

def get_port(node_id):
    url = 'https://evepro.interligo.local/api/labs/Labs/test.unl/nodes'

    login()

    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    port_details = node_dict[f'{node_id}']['url']
    port_number = int(port_details[-5:])

    return port_number

def disable_poap(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    tn.write(b"yes\n")

def nxos_init(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    tn.write(b"no\r\n")
    tn.write(b"Root1234?\n")
    tn.write(b"Root1234?\n")
    tn.write(b"no\r\n")

    time.sleep(10)
def nxos_login(port_number):
    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    tn.write(b"admin\r\n")
    tn.write(b"Root1234?\r\n")
#######################################################################################

id = create_nxos()

start(id)

print("Letting devices boot, 540 seconds...")
time.sleep(300)
print("5 minutes have passed")
time.sleep(240)
print("Done")

port = get_port(id)
disable_poap(id)

print("Sleeping for 5 minutes...")
time.sleep(300)
print("Done")

nxos_init(port)
nxos_login(port)