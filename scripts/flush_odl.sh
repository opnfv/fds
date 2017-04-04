#!/bin/bash
script_dir=$(dirname $0)
. $script_dir/variables.sh

echo "WARNING: this script doesn't install odl features; It assumes features are already configured in $ODL_ROOT/etc/org.apache.karaf.features.cfg"

odl_hostnames=$(grep -Eo 'overcloud-controller-[0-9]' /etc/hosts)
for odl_hostname in $odl_hostnames
do
    echo "Stopping odl on $odl_hostname"
    $script_dir/service.sh opendaylight stop
done

echo "Waiting 10 seconds for odl to stop"
for i in {1..10}
do
    echo -n "."
    sleep 1
done
echo

for odl_hostname in $odl_hostnames
do
    echo "Removing data, journal, snapshots and instances"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $odl_hostname rm -rf $odl_dir/data $odl_dir/journal $odl_dir/snapshots $odl_dir/instances
done

for odl_hostname in $odl_hostnames
do
    echo "Starting odl on $odl_hostname"
    $script_dir/service.sh opendaylight start
done

echo "Waiting 20 seconds for odl to start"
for i in {1..20}
do
    echo -n "."
    sleep 1
done

$script_dir/remount_vpp_into_odl.sh
