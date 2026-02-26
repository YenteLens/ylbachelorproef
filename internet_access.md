# Internet access for lab's in eve-ng

### Step 1: Add a second NIC to your VM in proxmox

### Step 2: Add an IP to the 2nd interface

```bash
nano /etc/network/interfaces


#look for this part of the file
# Cloud devices
iface eth1 inet manual
auto pnet1
iface pnet1 inet static     # this will say manual, change it to static
    bridge_ports eth1
    bridge_stp off
    address 10.199.199.1    # <-- Create an address
    netmask 255.255.255.0   # <-- Create a subnet mask


#Save & exit after making changes
```

### Step 3: Restart networking

```bash
systemctl restart networking

#if you get an error like: "ifup failed to bring up natmac"
    #run the following commands
ip link set natmac down
ip link delete natmac type bridge
stystemctl restart networking

#more troubleshooting at the bottom
```

### Step 4: Turn op IPv4 Forwarding

```bash
nano /etc/sysctl.conf
#uncomment the following line
net.ipv4.ip_forward=1


#save & exit and run
sysctl -p /etc/sysctl.conf
```

### Step 5: Configure iptables to NAT outbound connections

```bash
iptables -t nat -A POSTROUTING -s 10.199.199.0/24 -o pnet0 -j MASQUERADE
```

### Step 6: Make iptables changes persistent

```bash
iptables-save > /etc/iptables.rules
nano /etc/network/if-pre-up.d/iptables


#enter this content into the file:

#!/bin/sh
iptables-restore < /etc/iptables.rules
exit 0


#save changes then edit/create next iptables file:
nano /etc/network/if-post-down.d/iptables

#enter the following content in this file:

#!/bin/sh
iptables-save -c > /etc/iptables.rules
if [ -f /etc/iptables.rules ]; then
    iptables-restore < /etc/iptables.rules
fi
exit 0

#save changes and make both files executable
sudo chmod +x /etc/network/if-post-down.d/iptables
sudo chmod +x /etc/network/if-pre-up.d/iptables
```

### Step 7: Create a test lab

- in this lab add a VPC and configure with the following settings
  
  - IP Address: 10.199.199.10/24
  
  - Default Gateway: 10.199.199.1
  
  - The ip must be in the same subnet as the default gateway/pnet1 

- Then add Cloud1 and  connect the VPC to it

- From the VPC try to ping the default gateway

- if this doesn't work save the VPC's config and turn it off and on again, then try to ping again.

- if it works then try pinging 8.8.8.8


