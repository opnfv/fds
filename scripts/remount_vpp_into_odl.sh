#!/bin/bash
SCRIPT_DIR=$(dirname $0)
. $SCRIPT_DIR/lib.sh

overcloud_node_ips=$(grep -E "$NODE_PATTERN-[^-]+-[0-9]" /etc/hosts | grep -Eo "$IPV4_REGEX")
for overcloud_node_ip in $overcloud_node_ips
do
    overcloud_node_hostname=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $overcloud_node_ip hostname 2> /dev/null)
    # TODO get node names from nova service list and neutron agent-list
    echo "Mounting $overcloud_node_hostname:$overcloud_node_ip on $NODE_PATTERN-controller-0"
    $SCRIPT_DIR/mount_vpp_into_odl.sh $NODE_PATTERN-controller-0 $overcloud_node_hostname $overcloud_node_ip
done
