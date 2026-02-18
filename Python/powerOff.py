import json
import requests

login_url = 'http://172.24.255.170/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"-1"}'
headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)
cookies = login.cookies

device_ids = input("Enter device ID to power off: ").split(',')

def stop(device_ids):
    for device_id in device_ids:
        stop_url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes/{device_id}/stop'
        stop_api = requests.request("GET", url=stop_url, headers=headers, cookies=cookies)
        print(stop_api.json())

stop(device_ids)