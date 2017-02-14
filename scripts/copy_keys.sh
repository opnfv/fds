#!/bin/bash
if [[ $# -ne 1 ]]
then
    echo "Must have one argument which is the ip of the host to which the key will be copied"
    exit 1
fi
scp -oStrictHostKeyChecking=no /home/stack/id_rsa_jumphost_root.pub heat-admin@$1:/home/heat-admin
ssh -oStrictHostKeyChecking=no heat-admin@$1 'cat /home/heat-admin/id_rsa_jumphost_root.pub >> /home/heat-admin/.ssh/authorized_keys'
ssh -oStrictHostKeyChecking=no heat-admin@$1 'cat /home/heat-admin/id_rsa_jumphost_root.pub | sudo tee -a /root/.ssh/authorized_keys'
ssh -oStrictHostKeyChecking=no heat-admin@$1 'rm -f /home/heat-admin/id_rsa_jumphost_root.pub'
