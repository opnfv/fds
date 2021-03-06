##############################################################################
# Copyright (c) 2017 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#!/bin/bash
# NETWORK AND SUBNET
echo "Creating network with subnet"
neutron net-create test-net
neutron subnet-create --name test-subnet test-net 192.168.20.0/24
net_id=$(neutron net-list | grep test-net | cut -f 2 -d " ")

# ATTACH NETWORK TO ROUTER
echo "Attaching external and tenant networks to router"
neutron router-create test-router
neutron router-interface-add test-router test-subnet
neutron router-gateway-set test-router external

# CREATE SECURITY GROUP
echo "Creating security groups with ICMP and SSH allow rules"
nova secgroup-create test-secgroup test
nova secgroup-add-rule test-secgroup icmp -1 -1 0.0.0.0/0
nova secgroup-add-rule test-secgroup tcp 22 22 0.0.0.0/0

# FIRST VM
echo "Creating first VM in the network and adding the security group to it"
nova boot --image cirros-0.3.4 --flavor nfv --nic net-id=$net_id test-vm1
nova add-secgroup test-vm1 test-secgroup

echo "Waiting 7 seconds for the VM to come up"
sleep 7

# SECOND VM
echo "Creating second VM in the network and adding the security group to it"
nova boot --image cirros-0.3.4 --flavor nfv --nic net-id=$net_id test-vm2
nova add-secgroup test-vm2 test-secgroup

# FLOATING IP
echo "Creating and associating floating IP for the first VM"
floatingip_id=$(neutron floatingip-create external | grep " id " |
    tr -s " " | cut -f 4 -d " ")
neutron floatingip-associate $floatingip_id $(neutron port-list |
    grep $(nova show test-vm1 | grep "test-net network" |
    grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+") | cut -d " " -f 2)
