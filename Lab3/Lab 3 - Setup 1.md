# Lab 3 - Setup 1

### LACP

```bash
#on core-rt-B
int e1/5
channel-group 1 mode active
int e1/6
channel-group 1 mode active
#wait around 30 seconds
```

### BGP

```bash
#on core-rt-B
router bgp 65002
vrf LAN
neighbor 10.0.1.1
    remote-as 65001
    address-family ipv4 unicast
neighbor 10.0.1.14
    remote-as 65003
    address-family ipv4 unicast
vrf DMZ
neighbor 10.0.1.1
    remote-as 65001
    address-family ipv4 unicast
```

```bash
#on core-rt-A
router bgp 65001
address-family ipv4 vrf DMZ
neighbor 10.0.1.2 remote-as 65002
neighbor 10.0.1.2 activate

address-family ipv4 vrf LAN
neighbor 10.0.1.2 remote-as 65002
neighvor 10.0.1.2 activate
neighbor 10.0.1.10 remote-as 65003
neighbor 10.0.1.10 activate
```

```bash
#on core-rt-C
router bgp 65003
vrf LAN
address-family ipv4 unicast
network 200.0.1.0/30
```

### Subnet mismatch

```bash
#on remote-host
ip 100.0.0.2/30 100.0.0.1
```
