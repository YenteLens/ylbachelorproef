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
apt install iptables-persistent netfilter-persistent -y

nft add rule ip nat POSTROUTING ip saddr 10.199.199.0/24 oif "pnet0" masquerade

#verify if rule was added with next command:
nft list ruleset


#save ruleset
nft list ruleset > /etc/nftables.conf
systemctl enable nftables

#then the nftables.conf file needs to be edited to prevent some errors
#make sure the following line does not have "oif pnet0" after the address
nano /etc/nftables.conf
ip saddr 10.199.199.0/24 masquerade

#save
nft -f /etc/nftables.conf

#reboot and verify if your rule exists with 
nft list ruleset
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



### Troubleshooting

- When adding an IP to pnet1 and restarting networking you may encounter some errors. We can prevent this by verifying that pnet1 has eth1 actually assigned to it and that they're both up

```bash
#verify eth1 exists and is up
ip addr show eth1
ip link set eth1 up

#verify pnet1 exists
#make sure your eve vm has a second NIC!!
ip addr show pnet1

#verify eth1 is attached to pnet1
brctl show

#verify both are up
ip link show eth1
ip link show pnet1

#if eth1 is not attached to pnet1 run the following
brctl addif pnet1 eth1
ip link set eth1 up
ip link set pnet1 up
```


