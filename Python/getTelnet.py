import requests
import json
from pprint import pprint

login_url = 'http://172.24.255.170/api/auth/login'
cred = '{"username":"admin","password":"eve","html5":"-1"}'
headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)
cookies = login.cookies

url = f'http://172.24.255.170/api/labs/test/testlabtwo.unl/nodes'
nodes = requests.get(url=url, headers=headers, cookies=cookies)
data = nodes.json()
node_dict = data['data']
port_details = node_dict[f'4']['url']
port_number = int(port_details[-5:])

pprint(port_number)

