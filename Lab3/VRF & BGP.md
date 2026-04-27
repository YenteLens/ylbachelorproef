### VRF & BGP

##### 1. VRF

- create and list vrf's

- ```bash
  ip vrf <name>
  
  show ip vrf #shows all existing VRF's
  #on nexusv9k
  vrf context <name>
  int g0/0
  no switchport
  vrf member <name>
  ```

- assign interfaces to a vrf

```bash
interface g0/0
ip vrf forwarding <name>
```

- show vrf routing table

- ```bash
  show ip route vrf <name>
  ```

- ping ips in a vrf

- ```bash
  ping vrf <name> <ip-address>
  ```

##### 2. BGP

- enable BGP

- ```bash
  router bgp <as-number>
  ```

- specify a neighbor

- ```bash
  neighbor <ip-address> remote-as <as-number>
  ```

- when advertising a route over bgp the exact network and subnet mask must be entered and a corresponding route must exist in the routing table

- ```bash
  network 1.1.1.1 mask 255.255.255.255
  ```

- to create a route to share on bgp that isnt in the routing table yet 

- ```bash
  ip route 10.0.0.0 255.255.0.0 null0
  #creates a summary route for various smaller networks but discard incoming traffic
  ```
