import time
import requests
import json
from telnetlib3 import Telnet
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

login_url = 'https://evepro.interligo.local/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"0"}'
headers = {'Accept': 'application/json'}

session = requests.session()
CA_CERT_PATH = "./eveng.crt"


# login = session.post(url=login_url, data=cred,verify=CA_CERT_PATH)
# cookies = login.cookies
# print(cookies)

router_ids = []
network_ids = []
vpc_net_ids = []
vpc_ids = []
device_names = []

def login():
    response = session.post(
        login_url,
        json={"username": "admin", "password": "eve", "html5":"0"},
        verify=CA_CERT_PATH
    )
    response.raise_for_status()
    print("Logged in")


def create_router(total):
    for i in range(0, total):
        ios_data = {"template": "vios", "type": "qemu", "count": "1", "image": "vios-adventerprisek9-m.spa.159-3.m9",
                    "name": f"vIOS_{i}", "icon": "Router-2D-Gen-White-S.svg", "uuid": "", "cpulimit": "undefined",
                    "cpu": "1", "ram": "1024", "ethernet": "4", "qemu_version": "", "qemu_arch": "", "qemu_nic": "",
                    "qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                    "ro_qemu_options": "-machine type=pc,accel=kvm -serial mon:stdio -nographic -no-user-config -nodefaults -rtc base=utc -cpu host",
                    "config": "0", "delay": "0", "console": "telnet", "left": "760", "top": "252", "postfix": 0}
        ios_data = json.dumps(ios_data)
        create_url = 'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'

        create_api = session.post(url=create_url, data=ios_data, headers=headers,verify=CA_CERT_PATH)

        if create_api.status_code in (401,412):
            print("session expired, reauthenticating")
            login()
            create_api = session.post(url=create_url, data=ios_data, headers=headers, verify=CA_CERT_PATH)
            response = create_api.json()

        response = create_api.json()
        device_id = response['data']['id']
        router_ids.append(device_id)

        url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'
        nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)
        data = nodes.json()
        node_dict = data['data']

        node_name = node_dict[f'{device_id}']['name']
        device_names.append(node_name)

        print(f"Created Instance ID is: {device_id}")

    for i in range(total):
        network_id = create_network()
        print(f"Created network ID is: {network_id}")
        network_ids.append(network_id)

    for i in range(total):
        # print(len(router_ids))
        # print(len(network_ids))
        connect_devices(router_ids[i], 0, network_ids[i])
        if i == 0:
            connect_devices(router_ids[i], 1, network_ids[-1])
        else:
            connect_devices(router_ids[i], 1, network_ids[i-1])
        hide_network(network_ids[i])



def create_vpc(total):
    for i in range(0, total):
        ios_data = {"template": "vpcs", "type": "vpcs", "count": "1", "name": f"VPC_{i}",
                    "icon": "PC-2D-Desktop-Generic-S.svg", "config": "0", "delay": "0", "left": "614", "top": "376",
                    "postfix": 0}
        ios_data = json.dumps(ios_data)
        create_url = 'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'
        create_api = session.post(url=create_url, data=ios_data, headers=headers,verify=CA_CERT_PATH)
        response = create_api.json()
        device_id = response['data']['id']
        vpc_ids.append(device_id)
        print(f"Created VPC ID is: {device_id}")
    for i in range(total):
        vpc_net_id = create_network()
        print(f"Created network ID is: {vpc_net_id}")
        vpc_net_ids.append(vpc_net_id)
    for i in range(total):
        # print(len(router_ids))
        # print(len(network_ids))
        connect_devices(vpc_ids[i], 0, vpc_net_ids[i])
        connect_devices(router_ids[i], 2, vpc_net_ids[i])
        hide_network(vpc_net_ids[i])

def create_network():
    network_url = 'https://evepro.interligo.local/api/labs/test/testlab.unl/networks'
    network_data = {"count": 1, "name": "Net-vIOS_2iface_0", "type": "bridge", "left": 669, "top": 322, "visibility": 1,
                    "postfix": 0}
    response = session.post(
        network_url,
        json=network_data,
        verify=CA_CERT_PATH
    )

    network_id = response.json()['data']['id']
    #print("Network ID:", network_id)
    return network_id

def create_vpc_net():
    net_url = 'https://evepro.interligo.local/api/labs/test/testlab.unl/networks'
    net_data = {"count":1,"name":"Net-VPCiface_0","type":"bridge","left":696,"top":482.70001220703125,"visibility":1,"postfix":0}
    response = session.post(
        net_url,
        json=net_data,
        verify=CA_CERT_PATH
    )
    net_id = response.json()['data']['id']
    return net_id

def connect_devices(node_id, interface_id, network_id):
    url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes/{node_id}/interfaces'

    data = {
        str(interface_id): network_id
    }

    r = session.put(url, json=data,verify=CA_CERT_PATH)

def hide_network(network_id):
    hide_data = {"visibility": 0}
    hide_url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/networks/{network_id}'
    response = session.put(url=hide_url, json=hide_data,verify=CA_CERT_PATH)

def start(routers, vpcs):
    for router in routers:
        start_url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes/{router}/start'
        start_api = session.request("GET", url=start_url, headers=headers,verify=CA_CERT_PATH)
        print(f"Router {router} started.")
    for vpc in vpcs:
        start_url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes/{vpc}/start'
        start_api = session.request("GET", url=start_url, headers=headers,verify=CA_CERT_PATH)
        print(f"VPC {vpc} started.")
    print("Waiting for devices to start (100 seconds)")
    time.sleep(100)

def get_port(node_id):
    url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'
    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    if nodes.status_code in (401,412):
        print("session expired, reauthenticating")
        login()
        nodes = session.get(url=url, headers=headers, verify=CA_CERT_PATH)

    data = nodes.json()
#    print(data)
    node_dict = data['data']

    port_details = node_dict[f'{node_id}']['url']
    port_number = int(port_details[-5:])

    return port_number


def telnet_init(port_number):
    tn = Telnet(host='evepro.interligo.local',port=port_number, timeout=10)
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"no\n")

    tn.write(b"\r\n")

def device_config(port_number, device_id):
    url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'
    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    if nodes.status_code in (401,412):
        print("session expired, reauthenticating")
        login()
        nodes = session.get(url=url, headers=headers, verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    device = node_dict[f'{device_id}']['name']


    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    print("Uploading Router config...")
    with open(f"{device}.conf", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r')
            time.sleep(1)

def vpc_config(port_number, device_id):
    url = f'https://evepro.interligo.local/api/labs/test/testlab.unl/nodes'
    nodes = session.get(url=url, headers=headers,verify=CA_CERT_PATH)

    if nodes.status_code in (401,412):
        print("session expired, reauthenticating")
        login()
        nodes = session.get(url=url, headers=headers, verify=CA_CERT_PATH)

    data = nodes.json()
    node_dict = data['data']

    device = node_dict[f'{device_id}']['name']


    tn = Telnet(host='evepro.interligo.local', port=port_number, timeout=10)
    tn.read_until(b'VPCS>', timeout=5)
    print("Uploading VPC config...")
    with open(f"{device}.conf", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r\n')
            time.sleep(1)


###### End of function definitions
login()
total = int(input("How many routers and VPC's should be created: "))

create_router(total)
create_vpc(total)
start(router_ids,vpc_ids)

for router in router_ids:
    tn_port = get_port(router)
    telnet_init(tn_port)
    device_config(tn_port,router)

for vpc in vpc_ids:
    tn_port = get_port(vpc)
    vpc_config(tn_port,vpc)
print("All processes are finished")
