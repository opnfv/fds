#!/bin/bash
script_dir=$(dirname $0)
. $script_dir/variables.sh

overcloud_node_ips=$(grep -E "$NODE_PATTERN-[^-]+-[0-9]" /etc/hosts | grep -Eo '([0-9]{1,3}.){3}[0-9]{1,3}')
for overcloud_node_ip in $overcloud_node_ips
do
    overcloud_node_hostname=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $overcloud_node_ip hostname)
    $script_dir/mount_vpp_into_odl.sh $NODE_PATTERN-controller-0 $overcloud_node_hostname $overcloud_node_ip
done
