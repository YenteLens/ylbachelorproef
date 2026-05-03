### ASA-S2S VPN config

```bash
#objects
object-group network LOCAL-LAN
    network-object 172.16.1.0 255.255.255.248
    network-object 172.16.1.8 255.255.255.248
object network REMOTE-LAN
    subnet 100.0.0.0 255.255.255.252

#NAT exemption
nat (inside,outside) source static LOCAL-LAN LOCAL-LAN destination static REMOTE-LAN REMOTE-LAN no-proxy-arp route-lookup

#ACL
access-list VPN-ACL extended permit ip object-group LOCAL-LAN object REMOTE-LAN

#IKEv2
crypto ikev2 policy 10
     encryption aes-256
     integrity sha256
     prf sha256
     group 14
     lifetime seconds 86400
crypto ikev2 enable outside

#Tunnel group
tunnel-group 100.0.0.0 type ipsec-l2l
tunnel-group 100.0.0.0 ipsec-attributes
    ikev2 local-authentication pre-shared-key cisco123
    ikev2 remote-authentication pre-shared-key cisco123

#Crypto map
crypto ipsec ikev2 ipsec-proposal IPSEC-PROP
    protocol esp encryption aes-256
    protocol esp integrity sha-256

crypto map VPN-MAP 10 match address VPN-ACL
crypto map VPN-MAP 10 set peer 10.199.199.40
crypto map VPN-MAP 10 set ikev2 ipsec-proposal IPSEC-PROP
crypto map VPN-MAP interface outside
```

### ASA-REMOTE S2S-VPN config

```bash
#objects
object network LOCAL-LAN
    subnet 100.0.0.0 255.255.255.248
object-group network REMOTE-LAN
    network-object 172.16.1.0 255.255.255.248
    network-object 172.16.1.8 255.255.255.248

#NAT exemption
nat (inside,outside) source static LOCAL-LAN LOCAL-LAN destination static REMOTE-LAN REMOTE-LAN no-proxy-arp route-lookup

#ACL
access-list VPN-ACL extended permit ip object LOCAL-LAN object-group REMOTE-LAN

#IKEv2
crypto ikev2 policy 10
     encryption aes-256
     integrity sha256
     prf sha256
     group 14
     lifetime seconds 86400
crypto ikev2 enable outside

#Tunnel group
tunnel-group 10.199.199.30 type ipsec-l2l
tunnel-group 10.199.199.30 ipsec-attributes
    ikev2 local-authentication pre-shared-key cisco123
    ikev2 remote-authentication pre-shared-key cisco123

#Crypto map
crypto ipsec ikev2 ipsec-proposal IPSEC-PROP
    protocol esp encryption aes-256
    protocol esp integrity sha-256

crypto map VPN-MAP 10 match address VPN-ACL
crypto map VPN-MAP 10 set peer 10.199.199.30
crypto map VPN-MAP 10 set ikev2 ipsec-proposal IPSEC-PROP
crypto map VPN-MAP interface outside
```
