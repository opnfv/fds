#!/bin/bash
script_dir=$(dirname $0)
. $script_dir/lib.sh

NODE_TYPES="compute controller"
RESOURCE_TYPES="openstack opendaylight fdio"
HOSTNAME=$(hostname)

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
    echo -n "It appears that we are on a $1 node. Do you wish to clean it up (y), run the script as if on jumphost (j) or \
abort the script (a)? (y/j/a): "
    read -en 1
    in_array $REPLY "y j a"
    while [[ $? -eq 1 ]]
    do
        echo -n "Invalid input. Valid inputs are y/j/a: "
        read -en 1
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

clean_from_jumphost() {
    for RESOURCE in $@
    do
        case $RESOURCE in
            openstack)
                # check that a docker container with functest in name exists
                # if more than one exists, give choice or exit?
                # choice should include what env vars are configured in that container
                echo "Cleaning openstack"
                FUNCTEST_CONTAINER=$(docker ps | grep functest | cut -d " " -f 1)
                if [[ $(echo $FUNCTEST_CONTAINER | wc -w) -gt 1 ]]
                then
                    echo "Found more than one functest container, skipping cleanup"
                else
                    docker exec $FUNCTEST_CONTAINER ls /home/opnfv/functest/conf/orig_openstack_snapshot.yaml
                    if [[ $? -eq 0 ]]
                    then
                        docker exec $FUNCTEST_CONTAINER cp /home/opnfv/functest/conf/orig_openstack_snapshot.yaml \
                            /home/opnfv/functest/conf/openstack_snapshot.yaml
                    fi
                    docker exec $FUNCTEST_CONTAINER \
                        sh -c ". /home/opnfv/functest/conf/openstack.creds && functest openstack clean"
                fi
                ;;
            opendaylight)
                CONTROLLER_QUEUE="$CONTROLLER_QUEUE -w opendaylight"
                REMOUNT=True
                ;;
            fdio)
                CONTROLLER_QUEUE="$CONTROLLER_QUEUE -w fdio"
                COMPUTE_QUEUE="-w fdio"
                ;;
        esac
    done

    # get list of nodes with ips
    NODES=$(grep -Eo "$NODE_PATTERN[^ ]*" /etc/hosts)
    # iterate over the list
    for NODE in $NODES
    do
        if [[ $NODE == *"controller"* && $CONTROLLER_QUEUE ]]
        then
            # if controller node and controller queue exist, execute on that node
            echo "Cleaning $NODE"
            ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$NODE \
                "$overcloud_script_loc/$0 -n controller $CONTROLLER_QUEUE" &
        fi
        if [[ $NODE == *"compute"* && $COMPUTE_QUEUE ]]
        then
            # if compute node and compute queue exist, execute on that node
            echo "Cleaning $NODE"
            ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$NODE \
                "$overcloud_script_loc/$0 -n compute $COMPUTE_QUEUE" &
        fi
    done

    # then check for running scripts
    echo "Waiting for cleanup to finish"
    JOBS=$(jobs -r)
    while [[ $JOBS ]]
    do
        sleep 1
        echo -n .
        JOBS=$(jobs -r)
    done
    echo
    echo "Cleanup finished"
    if [[ $REMOUNT ]]
    then
        $script_dir/remount_vpp_into_odl.sh
    fi
}

clean_overcloud_resource() {
    case $1 in
        opendaylight)
            # TODO modify the check so that it works if odl wasn't started using systemctl
            if [[ $(systemctl -p SubState show opendaylight | grep running) ]]
            then
                echo "$HOSTNAME: found running odl, cleaning up"
                rm -rf /opt/opendaylight/data/ /opt/opendaylight/journal/ /opt/opendaylight/snapshots/ \
                    /opt/opendaylight/instances/ /opt/opendaylight/cache/
                service opendaylight restart
                ODL_RESTARTED=True
            else
                echo "$HOSTNAME: odl is not running, no cleanup will be done"
            fi
            ;;
        fdio)
            if [[ -e /etc/vpp/vpp-exec ]]
            then
                # TODO check that /etc/vpp/startup.conf contains vpp-exec
                # if not, insert
                AUTOCONFIG=TRUE
            fi
            INTERFACE1=$(vppctl show int | grep GigabitEthernet | sed -n 1p | cut -d " " -f 1)
            INTERFACE2=$(vppctl show int | grep GigabitEthernet | sed -n 2p | cut -d " " -f 1)
            if [[ ! $AUTOCONFIG ]]
            then
                INTERFACE1_IP=$(vppctl show int $interface1 addr | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+")
                INTERFACE2_IP=$(vppctl show int $interface2 addr | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+")
            fi
            service honeycomb stop
            sudo rm -rf /var/lib/honeycomb/persist/config/*
            sudo rm -rf /var/lib/honeycomb/persist/context/*
            sudo rm -f /var/log/honeycomb/honeycomb.log
            service vpp stop

            if [[ $HOSTNAME == *"compute"* ]]; then
                sysctl -w vm.nr_hugepages=2048 > /dev/null
                sysctl -w vm.max_map_count=4506 > /dev/null
                sysctl -w vm.hugetlb_shm_group=0 > /dev/null
                sysctl -w kernel.shmmax=4294967296 > /dev/null
            fi

            service vpp start
            if [[ ! $AUTOCONFIG ]]
            then
                vppctl set interface state $INTERFACE1 up
                vppctl set interface ip address $INTERFACE1 $INTERFACE1_IP
                if [[ -n $INTERFACE2 ]]; then
                    vppctl set interface state $INTERFACE2 up
                    vppctl set interface ip address $INTERFACE2 $INTERFACE2_IP
                fi
            fi
            service honeycomb start
            #TODO change sleep to more sensible check
            HC_IP=$(grep restconf-binding-address /opt/honeycomb/config/honeycomb.json | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
            HC_PORT=$(grep restconf-port /opt/honeycomb/config/honeycomb.json | grep -Eo [0-9]+)
        for i in $(seq 1 30)
        do
            sleep 1
            HC_RESPONSE=$(curl -s -XGET -u $odl_username:$odl_password \
                http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces \
                | python -m json.tool 2> /dev/null)
            if [[ $? -ne 0 && $(echo $HC_RESPONSE | grep -c error) -eq 0 ]]
            then
                if [[ $i == 30 ]]
                then
                    echo "$HOSTNAME: honecomb didn't respond to rest calls after $i seconds, stopping trying"
                elif [[ $i == *"0" ]]
                then
                    echo "$HOSTNAME: honeycomb didn't respond to rest calls after $i seconds, waiting up to 30 seconds"
                fi
            else
                echo "$HOSTNAME: honeycomb is responding to rest calls"
                break
            fi
        done
            INTERFACE1_HC=$(echo $INTERFACE1 | sed 's/\//%2F/g')
            curl -s -XPOST -H 'Content-Type: application/json' -v -u $hc_username:$hc_password \
                http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces/interface/$INTERFACE1_HC \
                -d '{"description": "tenant-interface"}' 2> /dev/null
            echo "$HOSTNAME: configured tenant-interface on $INTERFACE1"
            if [[ -n $interface2 ]]; then
                INTERFACE2_HC=$(echo $INTERFACE2 | sed 's/\//%2F/g')
                curl -s -XPOST -H 'Content-Type: application/json' -v -u $hc_username:$hc_password \
                    http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces/interface/$INTERFACE2_HC \
                    -d '{"description": "public-interface"}' 2> /dev/null
                echo "$HOSTNAME: configured public-interface on $INTERFACE2"
            fi
            ;;
    esac
}

NODE_TYPE=jumphost
while [[ $# -gt 0 ]]
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
    if [[ $(hostname) == "$NODE_PATTERN-controller"* ]]
    then
        prompt_manual_overcloud_node controller
    elif [[ $(hostname) == "$NODE_PATTERN-novacompute"* ]]
    then
        prompt_manual_overcloud_node compute
    fi
fi

case $NODE_TYPE in
    controller)
        RESOURCE_QUEUE="opendaylight fdio"
        ;;
    compute)
        RESOURCE_QUEUE="fdio"
        ;;
    jumphost)
        RESOURCE_QUEUE="openstack opendaylight fdio"
        ;;
esac
build_final_resource_queue

if [[ $NODE_TYPE == "jumphost" ]]
then
    clean_from_jumphost $FINAL_QUEUE
else
    for RESOURCE in $FINAL_QUEUE
    do
        clean_overcloud_resource $RESOURCE
    done
    if [[ $ODL_RESTARTED ]]
    then
        ODL_IP=$(awk '/<Call/{f=1} f{print; if (/<\/Call>/) exit}' /opt/opendaylight/etc/jetty.xml | \
            grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
        ODL_PORT=$(awk '/<Call/{f=1} f{print; if (/<\/Call>/) exit}' /opt/opendaylight/etc/jetty.xml | \
            grep jetty.port | grep -Eo [0-9]+)
        echo "$HOSTNAME: waiting for odl to start"
        for i in $(seq 1 60)
        do
            sleep 1
            ODL_RESPONSE=$(curl -s -XGET -u $odl_username:$odl_password \
                http://$ODL_IP:$ODL_PORT/restconf/config/network-topology:network-topology/topology/topology-netconf/ \
                | python -m json.tool 2> /dev/null)
            if [[ $? -ne 0 && $(echo $ODL_RESPONSE | grep -c error) -eq 0 ]]
            then
                if [[ $i == 60 ]]
                then
                    echo "$HOSTNAME: odl didn't respond to rest calls after $i seconds, stopping trying"
                elif [[ $i == *"0" ]]
                then
                    echo "$HOSTNAME: odl didn't respond to rest calls after $i seconds, waiting up to 60 seconds"
                fi
            else
                echo "$HOSTNAME: odl is responding to rest calls"
                break
            fi
        done
    fi
fi

