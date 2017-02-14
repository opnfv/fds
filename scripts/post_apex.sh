#!/bin/bash
#overcloud_file_name=overcloudrc # change this if needed
undercloud_ip=`arp -a | grep $(virsh domiflist undercloud | grep default | awk '{print $5}') | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"`
#echo $undercloud_ip
#
## copy rc file to jumphost
#scp -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$undercloud_ip:/home/stack/overcloudrc /root/$overcloud_file_name
#
## copy jumphost root key to undercloud vm - needs $undercloud_ip
#scp -oStrictHostKeyChecking=no /root/.ssh/id_rsa.pub root@$undercloud_ip:/home/stack/id_rsa_jumphost_root.pub

overcloud_dir="/root/.overcloud"
node_list_filename="$overcloud_dir/node_list"
mkdir -p $overcloud_dir
OIFS="$IFS"
IFS=$'\n'
nova_list=`ssh stack@$undercloud_ip ". stackrc && nova list | tail -n+4 | head -n-1 | sed 's/ //g'"`
node_list=($nova_list)
IFS="$OIFS"
first=false
for node in "${node_list[@]}"
do
  node_fields=`echo $node | cut -d "|" -f 3,7`
  node_name=`echo $node_fields | cut -d "|" -f 1`
  node_ip=`echo $node_fields | cut -d "=" -f 2`
  if [ "$first" = false ]
  then
    echo $node_name $node_ip > $node_list_filename
    first=true
  else
    echo $node_name $node_ip >> $node_list_filename
  fi
done
