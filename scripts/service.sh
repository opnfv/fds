#!/bin/bash
if [[ $# -ne 2 ]]
then
    echo "Must have at least two arguments. The first is name of the service and the second is the action to be done with the service."
    exit 1
fi
for odl_hostname in `grep -Eo 'overcloud-controller-[0-9]' /etc/hosts`
do
    echo "Executing service $1 $2 on $odl_hostname"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $odl_hostname service $1 $2 2> /dev/null
done
