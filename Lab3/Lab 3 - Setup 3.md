# Lab 3 - Setup 3

### Native VLAN mismatch

```bash
#on core-rt-B
int port-channel 1
switchport trunk native vlan 1

#on access-sw
int port-channel 1
switchport trunk native vlan 1
```

### NAT

```bash
#on ASA-EDGE
object network SITE-B-DMZ
 subnet 172.16.20.0 255.255.255.0
```

### ACL

```bash
#on DMZ-router
remove acl on g0/0 or permit IP instead of udp
```
