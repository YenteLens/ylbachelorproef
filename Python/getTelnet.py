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

def get_port():
    url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes'
    nodes = requests.get(url=url, headers=headers, cookies=cookies)
    data = nodes.json()
    node_dict = data['data']

    ###### Here the node ID is statically provided, make sure to dynamically provide this
    ###### The port number should be the return value of a function
    port_details = node_dict[f'5']['url']
    port_number = int(port_details[-5:])

    return port_number

def device_config(port_number):
    tn = Telnet(host='172.24.255.170', port=port_number, timeout=10)
    print("Uploading config...")
    with open(f"testconfig.conf", 'r') as cmd_file:
        for cmd in cmd_file.readlines():
            cmd = cmd.strip('\r\n')
            tn.write(cmd.encode()+  b'\r')
            time.sleep(1)
    #print("Finished uploading config")

def telnet_init(port_number):
    print(f"Port number is {port_number}")
    print("Waiting for device to boot.")
    time.sleep(100)
    print("Device has booted, Connecting...")
    tn = Telnet(host='172.24.255.170',port=port_number, timeout=10)
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"no\n")

    tn.read_until(b"Press RETURN to get started!", timeout=120)
    tn.write(b"\r\n")

    print("Device is ready to use.")
    device_config(port_number)
    print("Finished uploading config")

port = get_port()
telnet_init(port)

