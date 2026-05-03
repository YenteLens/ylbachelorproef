# Lab 3 - Setup 2

### S2S

```bash
#on ASA-S2S
tunnel-group 10.199.199.40 type ipsec-l2l
tunnel-group 10.199.199.40 ipsec-attributes
 ikev2 remote-authentication pre-shared-key cisco123
 ikev2 local-authentication pre-shared-key cisco123
```

```bash
#on ASA-Remote
tunnel-group 10.199.199.30 type ipsec-l2l
tunnel-group 10.199.199.30 ipsec-attributes
 ikev2 remote-authentication pre-shared-key cisco123
 ikev2 local-authentication pre-shared-key cisco123
```

### VRF

```bash
#on core-rt-B
interface vlan10
vrf member LAN
ip address 172.16.1.1/29
interface vlan20
vrf member LAN
ip address 172.16.1.9/29

interface Ethernet1/4
no switchport
vrf member DMZ
ip address 172.16.20.1/30
ip router ospf 1 area 0.0.0.0

#on core-rt-C
interface Ethernet1/1
no vrf member DMZ
vrf member LAN
ip address 10.0.1.14/30
interface Ethernet1/2
no vrf member DMZ
vrf member LAN
ip address 10.0.1.10/30
```

### Static Route

```bash
#on ASA-S2S
route inside 10.0.1.0 255.255.255.0 192.168.1.9 1
route inside 172.16.1.0 255.255.255.0 192.168.1.9 1
route inside 172.16.20.0 255.255.255.0 192.168.1.9 1

```
