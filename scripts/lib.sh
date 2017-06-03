overcloud_file_name=overcloudrc # change this if needed
odl_username=admin
odl_password=admin
odl_port=8081
odl_dir=/opt/opendaylight
hc_username=admin
hc_password=admin
hc_netconf_port=2831
NODE_PATTERN=overcloud
CONTROLLER_PATTERN=controller
overcloudrc_path=/root/$overcloud_file_name
overcloud_fds_repo_loc=/root
overcloud_script_loc=$overcloud_fds_repo_loc/fds/scripts
IPV4_REGEX='([0-9]{1,3}.){3}[0-9]{1,3}'

get_nodes() {
    if [[ $1 ]]
    then
        NODES=$(grep -o "$NODE_PATTERN-$1-[0-9]" /etc/hosts)
    else
        NODES=$(grep -Eo "$NODE_PATTERN-[^-]+-[0-9]" /etc/hosts)
    fi
}

copy_to_controllers () {
    get_nodes $CONTROLLER_PATTERN
    LOCAL_FILE=$1
    REMOTE_LOC=$2
    for NODE in $NODES
    do
        scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $LOCAL_FILE $NODE:$REMOTE_LOC
    done
}

exec_on_controllers() {
    get_nodes $CONTROLLER_PATTERN
    for NODE in $NODES
    do
        ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $NODE $@
    done
}

in_array() {
    key=$1
    shift
    items=$@
    for item in $items
    do
        if [ $item == $key ]
        then
            return 0
            break
        fi
    done
    return 1
}
