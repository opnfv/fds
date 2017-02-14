#!/bin/bash
overcloud_file_name=overcloudrc # change this if needed
NODE_PATTERN=overcloud
overcloudrc_path=/root/$overcloud_file_name
undercloud_ip=`arp -a | grep $(virsh domiflist undercloud | grep default | awk '{print $5}') | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"`
#echo $undercloud_ip

# copy rc file to jumphost
echo "Copying overcloud rc to jumphost to $overcloudrc_path"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$undercloud_ip:/home/stack/overcloudrc $overcloudrc_path 2> /dev/null

# copy jumphost root key to undercloud vm - needs $undercloud_ip
echo "Copying root's public ssh key to undercloud vm"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /root/.ssh/id_rsa.pub root@$undercloud_ip:/home/stack/id_rsa_jumphost_root.pub 2> /dev/null

# copy key copying script to undercloud vm
echo "Copying ssh setup script to undercloud vm"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null `dirname $0`/copy_keys.sh root@$undercloud_ip:/home/stack 2> /dev/null

#overcloud_dir="/root/.overcloud"
#node_list_filename="$overcloud_dir/node_list"
#mkdir -p $overcloud_dir
sed -i "/$NODE_PATTERN/d" /etc/hosts
OIFS="$IFS"
IFS=$'\n'
nova_list=`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$undercloud_ip ". stackrc && nova list | tail -n+4 | head -n-1 | sed 's/ //g'" 2> /dev/null`
node_list=($nova_list)
IFS="$OIFS"
echo
for node in "${node_list[@]}"
do
  node_fields=`echo $node | cut -d "|" -f 3,7`
  node_name=`echo $node_fields | cut -d "|" -f 1`
  node_ip=`echo $node_fields | cut -d "=" -f 2`
  echo "adding $node_name to /etc/hosts"
  echo $node_ip $node_name >> /etc/hosts
  echo "removing $node_ip from known hosts"
  sed -i "/$node_ip/d" /root/.ssh/known_hosts
  echo "Setting up ssh keys on $node_name for root"
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$undercloud_ip "/home/stack/copy_keys.sh $node_ip &" 2> /dev/null
  echo "Copying overcloudrc to $node_name"
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $overcloudrc_path heat-admin@$node_ip:. 2> /dev/null
  ssh -oStrictHostKeyChecking=no heat-admin@$ip 'sudo cp /home/heat-admin/overcloudrc /root' 2> /dev/null
  echo "Cloning fds repo on $node_name to /root/fds"
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $node_name 'git clone https://gerrit.opnfv.org/gerrit/p/fds.git /root/fds' 2> /dev/null
  if [[ $node_name = *'controller'* ]]
  then
      echo "Setting debugs for nova and neutron on $node_name"
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?debug *=.*$/debug=True/" /etc/nova/nova.conf' 2> /dev/null
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?verbose *=.*$/verbose=True/" /etc/nova/nova.conf' 2> /dev/null
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?debug *=.*$/debug=True/" /etc/neutron/neutron.conf' 2> /dev/null
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?verbose *=.*$/verbose=True/" /etc/neutron/neutron.conf' 2> /dev/null
  else
      echo "Setting debugs for nova on $node_name"
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?debug *=.*$/debug=True/" /etc/nova/nova.conf' 2> /dev/null
      ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null heat-admin@$node_name 'sudo sed -i "s/^\(# *\)\?verbose *=.*$/verbose=True/" /etc/nova/nova.conf' 2> /dev/null
  fi
  echo
done
echo "Post-apex script is finished. If you want the nova and neutron debug configurations to take effect, you'll need to restart the services manually."
