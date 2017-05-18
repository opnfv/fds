#!/bin/bash
script_dir=$(dirname $0)
. $script_dir/lib.sh

NODE_TYPES="compute controller"
RESOURCE_TYPES="openstack opendaylight fdio"

display_arguments() {
    echo "Available arguments:"
    echo "  -n|--node-type with valid values $NODE_TYPES"
    echo "  -e|--exclude with valid values $RESOURCE_TYPES"
    echo "  -w|--whitelist with valid values $RESOURCE_TYPES"
    echo "  -e and -o may be repeated and are mutually exclusive"
    exit 1
}

build_final_resource_queue() {
    if [[ $WHITELIST ]]
    then
        for RESOURCE in $RESOURCE_QUEUE
        do
            in_array $RESOURCE $WHITELIST
            if [[ $? -eq 0 ]]
            then
                FINAL_QUEUE="$FINAL_QUEUE $RESOURCE"
            fi
        done
    elif [[ $EXCLUDE ]]
    then
        for RESOURCE in $RESOURCE_QUEUE
        do
            in_array $RESOURCE $EXCLUDE
            if [[ $? -ne 0 ]]
            then
                FINAL_QUEUE="$FINAL_QUEUE $RESOURCE"
            fi
        done
    else
        FINAL_QUEUE=$RESOURCE_QUEUE
    fi
}

prompt_manual_overcloud_node() {
    echo "It appears that we are on a $1 node. Do you wish to clean it up (y), run the script as if on jumphost (j) or \
abort the script (a)? (y/j/a):"
    read
    in_array $REPLY "y j a"
    while [[ $? -eq 1 ]]
    do
        echo "Invalid input. Valid inputs are y/j/a:"
        read
        in_array $REPLY "y j a"
    done
    case $REPLY in
        y)
            NODE_TYPE=$1
            ;;
        a)
            exit 0
            ;;
    esac
}

clean_resource() {
    case $1 in
        openstack)
            echo openstack
            ;;
        opendaylight)
            echo opendaylight
            ;;
        fdio)
            echo fdio
            ;;
    esac
}

NODE_TYPE=jumphost
while [[ $# -gt 1 ]]
do
    arg="$1"
    case $arg in
        -n|--node-type)
            in_array $2 $NODE_TYPES
            if [[ $? -eq 0 ]]
            then
                NODE_TYPE=$2
            else
                display_arguments
            fi
            shift
            ;;
        -e|--exclude)
            if [[ $WHITELIST ]]
            then
                display_arguments
            fi
            in_array $2 $RESOURCE_TYPES
            if [[ $? -eq 0 ]]
            then
                EXCLUDE="$EXCLUDE $2"
            else
                display_arguments
            fi
            shift
            ;;
        -w|--whitelist)
            if [[ $EXCLUDE ]]
            then
                display_arguments
                exit 1
            fi
            in_array $2 $RESOURCE_TYPES
            if [[ $? -eq 0 ]]
            then
                WHITELIST="$WHITELIST $2"
            else
                display_arguments
            fi
            shift
            ;;
        -h|--help)
            display_arguments
            ;;
        *)
            echo "Unknown argument $arg."
            display_arguments
            ;;
    esac
    shift
done

# figure out where this is run - jumphost, controller or compute
# then figure out if it's run manually on controller or compute
# need a function with two arguments - jumphost or overcloud node and what resources to clean
# if jumphost, locally openstack and execute on overcloud
#   check if it's not compute or controller based on $(hostname) and ask user
#   need to check what resources to clean and build a whitelist for compute and controllers
# if not jumphost, build list and execute
if [[ $NODE_TYPE == "jumphost" ]]
then
    # figure out if this is not an overcloud node
    if [[ $NODE_TYPE == "$NODE_PATTERN_controller"* ]]
    then
        prompt_manual_overcloud_node controller
    elif [[ $NODE_TYPE == "$NODE_PATTERN_novacompute"* ]]
    then
        prompt_manual_overcloud_node compute
    fi
fi

case $NODE_TYPE in
    controller)
        RESOURCE_QUEUE="fdio"
        ;;
    compute)
        RESOURCE_QUEUE="opendaylight fdio"
        ;;
    jumphost)
        RESOURCE_QUEUE="openstack opendaylight fdio"
        ;;
esac
build_final_resource_queue

for RESOURCE in $FINAL_QUEUE
do
    clean_resource $RESOURCE
done

exit 1
echo "NOTICE: this script doesn't install odl features; It assumes features are already configured in $ODL_ROOT/etc/org.apache.karaf.features.cfg"
echo "NOTICE: this script also doesn't configure logging; You can configure logging in $ODL_ROOT/etc/org.ops4j.pax.logging.cfg"
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
