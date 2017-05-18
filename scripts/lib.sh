overcloud_file_name=overcloudrc # change this if needed
odl_username=admin
odl_password=admin
odl_port=8081
odl_dir=/opt/opendaylight
vpp_username=admin
vpp_password=admin
vpp_port=2831
NODE_PATTERN=overcloud
overcloudrc_path=/root/$overcloud_file_name
overcloud_fds_repo_loc=/root
overcloud_script_loc=$overcloud_fds_repo_loc/fds/scripts

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
