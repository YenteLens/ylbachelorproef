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

        #give the devices a unique name and location
        data["name"] = f"R{i+1}"
        match data["name"]:
            case "R2":
                data["left"] = 600
                data["top"] = 400
            case "R3":
                data["left"] = 800
                data["top"] = 400
            case _:
                pass #does nothing

        #turn data into JSON
        data = json.dumps(data)
        #create the devices and store the response to extract the device_id
        login()
        create_api = session.post(url=create_url, data=data, headers=headers, verify=CA_CERT_PATH)
        response = create_api.json()

        device_id = response['data']['id']
        print(f"Created router: {device_id}")

# End function declarations

login()
create_router()
