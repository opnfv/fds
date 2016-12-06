#!/bin/bash
# NETWORK AND SUBNET
echo "Creating network with subnet"
neutron net-create test-net
neutron subnet-create --name test-subnet test-net 192.168.20.0/24

# ATTACH NETWORK TO ROUTER
echo "Attaching external and tenant networks to reouter"
neutron router-create test-router
neutron router-interface-add test-router test-subnet
neutron router-gateway-set test-router external

# FIRST VM
echo "Creating port and first VM"
neutron port-create --name test-port1 test-net
nova boot --image cirros-0.3.4 --flavor nfv --nic port-id=`neutron port-list | grep test-port1 | cut -f 2 -d " "` test-vm1

# SECOND VM
echo "Creating port and second VM"
neutron port-create --name test-port2 test-net
nova boot --image cirros-0.3.4 --flavor nfv --nic port-id=`neutron port-list | grep test-port2 | cut -f 2 -d " "` test-vm2

# FLOATING IP
echo "Creating floating IP for the first VM"
neutron floatingip-create external --port-id `neutron port-list | grep test-port1 | cut -f 2 -d " "`
