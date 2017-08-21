#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
. $SCRIPT_DIR/lib.sh
UNDERCLOUD_IP=$(arp -a | grep $(virsh domiflist undercloud | grep default | awk '{print $5}') \
    | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
#echo $UNDERCLOUD_IP

# copy rc file to jumphost
echo "Copying overcloud rc to jumphost to $overcloudrc_path"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$UNDERCLOUD_IP:/home/stack/overcloudrc.v3 \
    $overcloudrc_path &> /dev/null

# copy jumphost root key to undercloud vm - needs $UNDERCLOUD_IP
echo "Copying root's public ssh key to undercloud vm"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /root/.ssh/id_rsa.pub \
    root@$UNDERCLOUD_IP:/home/stack/id_rsa_jumphost_root.pub &> /dev/null

# copy key copying script to undercloud vm
echo "Copying ssh setup script to undercloud vm"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $SCRIPT_DIR/copy_keys.sh \
    root@$UNDERCLOUD_IP:/home/stack &> /dev/null

#overcloud_dir="/root/.overcloud"
#node_list_filename="$overcloud_dir/node_list"
#mkdir -p $overcloud_dir
sed -i "/$NODE_PATTERN/d" /etc/hosts
OIFS="$IFS"
IFS=$'\n'
nova_list=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$UNDERCLOUD_IP \
    ". stackrc && nova list | tail -n+4 | head -n-1 | sed 's/ //g'" 2> /dev/null)
node_list=($nova_list)
IFS="$OIFS"
for node in "${node_list[@]}"
do
    echo
    node_fields=$(echo $node | cut -d "|" -f 3,7)
    node_name=$(echo $node_fields | cut -d "|" -f 1)
    node_ip=$(echo $node_fields | cut -d "=" -f 2)
    echo "Adding $node_name to /etc/hosts"
    echo $node_ip $node_name >> /etc/hosts
    echo "Removing $node_ip from known hosts"
    sed -i "/$node_ip/d" /root/.ssh/known_hosts
    echo "Removing $node_name from known hosts"
    sed -i "/$node_name/d" /root/.ssh/known_hosts
    echo "Setting up ssh keys on $node_name for root"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@$UNDERCLOUD_IP \
        "/home/stack/copy_keys.sh $node_ip &" &> /dev/null
    echo "Copying overcloudrc to $node_name"
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $overcloudrc_path heat-admin@$node_ip:. &> /dev/null
    ssh -oStrictHostKeyChecking=no heat-admin@$node_ip 'sudo cp /home/heat-admin/overcloudrc /root' &> /dev/null
    echo "Cloning fds repo on $node_name to $overcloud_fds_repo_loc"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $node_name \
        'git clone https://gerrit.opnfv.org/gerrit/p/fds.git $overcloud_fds_repo_loc' &> /dev/null
    if [[ $(ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$node_ip \
        'grep -c ". /root/overcloudrc" /root/.bashrc' 2> /dev/null) -eq 0 ]]
    then
        echo "Setting up . /root/overcloudrc in .bashrc on $node_name"
        ssh -oStrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$node_ip \
        'echo ". /root/overcloudrc" >> /root/.bashrc' &> /dev/null
    fi
done
. $overcloudrc_path
echo
openstack flavor list | grep nfv > /dev/null
if [[ ! $? -eq 0 ]]
then
    echo "Configuring flavor nfv"
    openstack flavor create nfv --ram 768 --property hw:mem_page_size=large
else
    echo "Flavor nfv is already configured"
fi

echo
openstack image list | grep cirros-0.3.4 > /dev/null
if [[ ! $? -eq 0 ]]
then
    echo "Configuring image cirros-0.3.4"
    image_loc=/root/cirros-0.3.4-x86_64-disk.img
    if [[ ! -f $image_loc ]]
    then
        echo "Downloading cirros image to $image_loc"
        wget https://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img -O $image_loc
    fi
    openstack image create --disk-format qcow2 --container-format bare --public --property hw_mem_page_size=large \
        --file $image_loc cirros-0.3.4
else
    echo "Image cirros-0.3.4 is already configured"
fi

echo
echo "Post-apex script is done."
