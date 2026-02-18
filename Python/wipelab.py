import requests
import json

login_url = 'http://172.24.255.170/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"-1"}'
headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)
cookies = login.cookies

def wipe_all(total):
    for i in range(1, total+1):
        url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes/{i}/wipe'
        wipe_api = requests.get(url=url,cookies=cookies,headers=headers)
        response = wipe_api.json()
        print(f"Device with id {i} wiped." )
###### End Functions


total = int(input("Enter the amount of nodes in your setup: "))
wipe_all(total)