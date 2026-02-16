import time
import requests
import json
from pprint import pprint
from telnetlib3 import Telnet

login_url = 'http://172.24.255.170/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"-1"}'
headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)
cookies = login.cookies


def create_router(total):
    for i in range(0, total):
        ios_data = {"template": "vios", "type": "qemu", "count": "1", "image": "vios-adventerprisek9-m.spa.159-3.m9",
                    "name": f"vIOS_{i}", "icon": "Router-2D-Gen-White-S.svg", "uuid": "", "cpulimit": "undefined",
                    "cpu": "1", "ram": "1024", "ethernet": "4", "qemu_version": "", "qemu_arch": "", "qemu_nic": "",
                    "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                    "ro_qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                    "config": "0", "delay": "0", "console": "telnet", "left": "760", "top": "252", "postfix": 0}
        ios_data = json.dumps(ios_data)
        create_url = 'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes'

        create_api = requests.post(url=create_url, data=ios_data, cookies=cookies, headers=headers)
        response = create_api.json()
        # print(response)
        device_id = response['data']['id']
        print(f"Created Instance ID is: {device_id}")
        network_id = create_network()


def create_vpc(total):
    for i in range(0, total):
        ios_data = {"template": "vpcs", "type": "vpcs", "count": "1", "name": "VPC",
                    "icon": "PC-2D-Desktop-Generic-S.svg", "config": "0", "delay": "0", "left": "614", "top": "376",
                    "postfix": 0}
        ios_data = json.dumps(ios_data)
        create_url = 'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes'
        create_api = requests.post(url=create_url, data=ios_data, cookies=cookies, headers=headers)
        response = create_api.json()
        device_id = response['data']['id']
        print(f"Created VPC ID is: {device_id}")

def create_network():
    network_url = 'http://172.24.255.170/api/labs/test/testlabtwo.unl/networks'
    network_data = {"count": 1, "name": "Net-vIOS_2iface_0", "type": "bridge", "left": 669, "top": 322, "visibility": 1,
                    "postfix": 0}
    response = requests.post(
        network_url,
        json=network_data,
        cookies=cookies
    )

    network_id = response.json()['data']['id']
    print("Network ID:", network_id)
    return network_id

def connect_devices(node_id, interface_id, network_id):
    url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes/{node_id}/interfaces'

    data = {
        str(interface_id): network_id
    }

    r = requests.put(url, json=data, cookies=cookies)

def hide_network(network_id):
    hide_data = {"visibility": 0}
    hide_url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/networks/{network_id}'
    response = requests.put(url=hide_url, json=hide_data, cookies=cookies)

###### End of function definitions

total_routers = int(input("How many routers should be created: "))
total_VPC = int(input("How mant VPCs should be created: "))

create_router(total_routers)
create_vpc(total_VPC)
