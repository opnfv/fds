#!/bin/bash
script_dir=$(dirname $0)
. $script_dir/variables.sh

echo "WARNING: this script doesn't install odl features; It assumes features are already configured in $ODL_ROOT/etc/org.apache.karaf.features.cfg"
echo "WARNING: this script also doesn't configure logging; You can configure logging in $ODL_ROOT/etc/org.ops4j.pax.logging.cfg"
echo

echo "Stopping odl on all nodes"
$script_dir/service.sh opendaylight stop

echo "Waiting 10 seconds for odl to stop"
for i in {1..10}
do
    echo -n "."
    sleep 1
done

echo

odl_hostnames=$(grep -Eo 'overcloud-controller-[0-9]' /etc/hosts)

echo
for odl_hostname in $odl_hostnames
do
    echo "Removing data, journal, snapshots and instances on $odl_hostname"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $odl_hostname rm -rf $odl_dir/data $odl_dir/journal $odl_dir/snapshots $odl_dir/instances 2> /dev/null
done

echo

echo "Starting odl on all nodes"
$script_dir/service.sh opendaylight start

echo "Waiting 20 seconds for odl to start"
for i in {1..20}
do
    echo -n "."
    sleep 1
done

echo
echo
$script_dir/remount_vpp_into_odl.sh
