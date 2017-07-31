#!/bin/bash
SCRIPT_DIR=$(dirname $0)
. $SCRIPT_DIR/lib.sh

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
    read -e
    if [[ ${#REPLY} -gt 1 ]]
    then
        INPUT_OK=1
    else
        in_array $REPLY "y j a"
        INPUT_OK=$?
    fi
    while [[ ! $INPUT_OK ]]
    do
        echo -n "Invalid input. Valid inputs are y/j/a: "
        read -e
        if [[ ${#REPLY} -gt 1 ]]
        then
            INPUT_OK=1
        else
            in_array $REPLY "y j a"
            INPUT_OK=$?
        fi
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
                # TODO if more than one exists, give choice or exit?
                # choice should include what env vars are configured in that container
                echo "Cleaning openstack"
                FUNCTEST_CONTAINER=$(docker ps | grep functest | cut -d " " -f 1)
                if [[ $(echo $FUNCTEST_CONTAINER | wc -w) -gt 1 ]]
                then
                    echo "Found more than one functest container, skipping cleanup"
                else
                    docker exec $FUNCTEST_CONTAINER ls /home/opnfv/functest/conf/orig_openstack_snapshot.yaml > /dev/null
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
                "$overcloud_script_loc/$(basename $0) -n controller $CONTROLLER_QUEUE" &
        fi
        if [[ $NODE == *"compute"* && $COMPUTE_QUEUE ]]
        then
            # if compute node and compute queue exist, execute on that node
            echo "Cleaning $NODE"
            ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$NODE \
                "$overcloud_script_loc/$(basename $0) -n compute $COMPUTE_QUEUE" &
        fi
    done

    # then check for running scripts
    JOBS=$(jobs -r)
    while [[ $JOBS ]]
    do
        sleep 1
        JOBS=$(jobs -r)
    done
    echo
    echo "Cleanup finished"
    if [[ $REMOUNT ]]
    then
        $SCRIPT_DIR/remount_vpp_into_odl.sh
    fi
}

clean_overcloud_resource() {
    case $1 in
        opendaylight)
            # TODO modify the check so that it works if odl wasn't started using systemctl
            if [[ $(systemctl -p SubState show opendaylight | grep running) ]]
            then
                echo "$HOSTNAME: found running odl, cleaning up"
                ODL_DIR=/opt/opendaylight
                rm -rf $ODL_DIR/data/ $ODL_DIR/journal/ $ODL_DIR/snapshots/ \
                    $ODL_DIR/instances/ $ODL_DIR/cache/
                echo "$HOSTNAME: restarting odl"
                service opendaylight restart &> /dev/null
                ODL_RESTARTED=True
            else
                case $(ps aux | grep karaf | grep -c -v grep) in
                    0)
                        echo "$HOSTNAME: odl is not running, no cleanup will be done"
                        ;;
                    1)
                        ODL_DIR=$(ps aux | grep karaf | grep -v grep | grep -Eo '\-classpath ([^:]*)' | cut -d " " -f 2 | awk -F"/lib" '{print $1}')
                        echo "$HOSTNAME: restarting odl"
                        $ODL_DIR/bin/stop &> /dev/null
                        while [[ $(ps aux | grep karaf | grep -c -v grep) -ne 0 ]]
                        do
                            sleep 1
                        done
                        rm -rf $ODL_DIR/data/ $ODL_DIR/journal/ $ODL_DIR/snapshots/ \
                            $ODL_DIR/instances/ $ODL_DIR/cache/
                        $ODL_DIR/bin/start &> /dev/null
                        ODL_RESTARTED=True
                        ;;
                    *)
                        echo "$HOSTNAME: found more than one karaf container running, no cleanup will be done"
                        ;;
                esac
            fi
            ;;
        fdio)
            if [[ -e /etc/vpp/vpp-exec ]]
            then
                if [[ $(grep -c vpp-exec /etc/vpp/startup.conf) -eq 0 ]]
                then
                    sed '/unix {/ a \ \ exec /etc/vpp/vpp-exec' /etc/vpp/startup.conf
                fi
                INTERFACES=$(grep -Eo "[^ ]*GigabitEthernet[^ ]+" /etc/vpp/vpp-exec | uniq | sort)
            else
                MANUAL_CONFIG=TRUE
                INTERFACES=$(vppctl show int | grep -Eo "[^ ]*GigabitEthernet[^ ]+")
            fi

            TENANT_INTERFACE=$(echo $INTERFACES | cut -d " " -f 1)
            PUBLIC_INTERFACE=$(echo $INTERFACES | cut -s -d " " -f 2)

            if [[ $MANUAL_CONFIG ]]
            then
                TENANT_INTERFACE_IP=$(vppctl show int $TENANT_INTERFACE addr \
                    | grep -Eo "$IPV4_REGEX")
                if [[ -n $PUBLIC_INTERFACE ]]
                then
                    PUBLIC_INTERFACE_IP=$(vppctl show int $PUBLIC_INTERFACE addr \
                        n| grep -Eo "$IPV4_REGEX")
                fi
            fi

            service honeycomb stop &> /dev/null
            echo "$HOSTNAME: stopping honeycomb"
            sudo rm -rf /var/lib/honeycomb/persist/config/*
            sudo rm -rf /var/lib/honeycomb/persist/context/*
            sudo rm -f /var/log/honeycomb/honeycomb.log
            service vpp stop &> /dev/null
            echo "$HOSTNAME: stopping vpp"

            if [[ $HOSTNAME == *"compute"* ]]; then
                sysctl -w vm.nr_hugepages=2048 > /dev/null
                sysctl -w vm.max_map_count=4506 > /dev/null
                sysctl -w vm.hugetlb_shm_group=0 > /dev/null
                sysctl -w kernel.shmmax=4294967296 > /dev/null
            fi

            service vpp start &> /dev/null
            echo "$HOSTNAME: starting vpp"
            if [[ $MANUAL_CONFIG ]]
            then
                vppctl set interface state $TENANT_INTERFACE up
                vppctl set interface ip address $TENANT_INTERFACE $TENANT_INTERFACE_IP
                if [[ -n $PUBLIC_INTERFACE ]]
                then
                    vppctl set interface state $PUBLIC_INTERFACE up
                    vppctl set interface ip address $PUBLIC_INTERFACE $PUBLIC_INTERFACE_IP
                fi
            fi
            sleep 1
            service honeycomb start &> /dev/null
            echo "$HOSTNAME: starting honeycomb"
            HC_IP=$(grep restconf-binding-address /opt/honeycomb/config/honeycomb.json | grep -Eo "$IPV4_REGEX")
            HC_PORT=$(grep restconf-port /opt/honeycomb/config/honeycomb.json | grep -Eo [0-9]+)
            for i in $(seq 1 30)
            do
                sleep 1
                HC_RESPONSE=$(curl -s -XGET -u $hc_username:$hc_password \
                    http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces \
                    | python -m json.tool 2> /dev/null)
                if [[ $? -ne 0 || $(echo $HC_RESPONSE | grep -c error) -ne 0 ]]
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
            echo "$HOSTNAME: configuring interface roles"
            sleep 1
            TENANT_INTERFACE_HC=$(echo $TENANT_INTERFACE | sed 's/\//%2F/g')
            curl -s -XPOST -H 'Content-Type: application/json' -v -u $hc_username:$hc_password \
                http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces/interface/$TENANT_INTERFACE_HC \
                -d '{"description": "tenant-interface"}' 2> /dev/null
            echo "$HOSTNAME: configured tenant-interface on $TENANT_INTERFACE"
            if [[ -n $PUBLIC_INTERFACE ]]
            then
                PUBLIC_INTERFACE_HC=$(echo $PUBLIC_INTERFACE | sed 's/\//%2F/g')
                curl -s -XPOST -H 'Content-Type: application/json' -v -u $hc_username:$hc_password \
                    http://$HC_IP:$HC_PORT/restconf/config/ietf-interfaces:interfaces/interface/$PUBLIC_INTERFACE_HC \
                    -d '{"description": "public-interface"}' 2> /dev/null
                echo "$HOSTNAME: configured public-interface on $PUBLIC_INTERFACE"
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
        ODL_IP=$(awk '/<Call/{f=1} f{print; if (/<\/Call>/) exit}' $ODL_DIR/etc/jetty.xml | \
            grep -Eo "$IPV4_REGEX")
        ODL_PORT=$(awk '/<Call/{f=1} f{print; if (/<\/Call>/) exit}' $ODL_DIR/etc/jetty.xml | \
            grep jetty.port | grep -Eo [0-9]+)
        echo "$HOSTNAME: waiting for odl to start"
        for i in $(seq 1 120)
        do
            sleep 1
            ODL_RESPONSE=$(curl -s -XGET -u $odl_username:$odl_password \
                http://$ODL_IP:$ODL_PORT/restconf/config/network-topology:network-topology/topology/topology-netconf/ \
                | python -m json.tool 2> /dev/null)
            if [[ $? -ne 0 || $(echo $ODL_RESPONSE | grep -c error) -ne 0 ]]
            then
                if [[ $i == 120 ]]
                then
                    echo "$HOSTNAME: odl didn't respond to rest calls after $i seconds, stopping trying"
                elif [[ $i == *"0" ]]
                then
                    echo "$HOSTNAME: odl didn't respond to rest calls after $i seconds, waiting up to 120 seconds"
                fi
            else
                echo "$HOSTNAME: odl is responding to rest calls"
                break
            fi
        done
    fi
fi

