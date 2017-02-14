#!/bin/bash
#overcloud_file_name=overcloudrc # change this if needed
NODE_PATTERN=overcloud
undercloud_ip=`arp -a | grep $(virsh domiflist undercloud | grep default | awk '{print $5}') | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"`
#echo $undercloud_ip

# copy rc file to jumphost
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$undercloud_ip:/home/stack/overcloudrc /root/$overcloud_file_name

# copy jumphost root key to undercloud vm - needs $undercloud_ip
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /root/.ssh/id_rsa.pub root@$undercloud_ip:/home/stack/id_rsa_jumphost_root.pub

# copy key copying script to undercloud vm
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null `dirname $0`/copy_keys.sh root@$undercloud_ip:/home/stack

#overcloud_dir="/root/.overcloud"
#node_list_filename="$overcloud_dir/node_list"
#mkdir -p $overcloud_dir
sed -i "/$NODE_PATTERN/d" /etc/hosts
OIFS="$IFS"
IFS=$'\n'
nova_list=`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$undercloud_ip ". stackrc && nova list | tail -n+4 | head -n-1 | sed 's/ //g'"`
node_list=($nova_list)
IFS="$OIFS"
for node in "${node_list[@]}"
do
  node_fields=`echo $node | cut -d "|" -f 3,7`
  node_name=`echo $node_fields | cut -d "|" -f 1`
  node_ip=`echo $node_fields | cut -d "=" -f 2`
  echo "adding $node_name to /etc/hosts"
  echo $node_ip $node_name >> /etc/hosts
  echo "removing $node_ip from known hosts"
  sed -i "/$node_ip/d" /root/.ssh/known_hosts
  echo "setting up ssh keys on $node_name for root"
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$undercloud_ip "/home/stack/copy_keys.sh $node_ip &"
done
