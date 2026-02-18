import requests
import time
import json

login_url = 'http://172.24.255.170/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"-1"}'
headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)
cookies = login.cookies

def stop_all(total):
    for i in range(1, total+1):
        url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes/{i}/stop'

        stop_api = requests.request("GET", url=url, headers=headers, cookies=cookies)
        print(f"Device with id {i} stopped")

def delete_all(total):
    for i in range(1, total+1):
        url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes/{i}'
        delete_api = requests.request("DELETE", url=url, headers=headers, cookies=cookies)
        print(f"Device with id {i} deleted")
###### End function declarations

total = int(input("Total number of devices: "))
stop_all(total)

print("All devices stopped, small delay before deletion")
time.sleep(10)

delete_all(total)
print("All devices deleted")