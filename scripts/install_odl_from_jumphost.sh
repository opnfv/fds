#!/bin/bash
SCRIPT_DIR=$(dirname $0)
. $SCRIPT_DIR/lib.sh
REMOTE_ODL_LOC=/opt/$(basename "$1")
copy_to_controllers $1 $REMOTE_ODL_LOC
if [[ $(echo ${#NODES} | wc -w) -gt 1 ]]
then
    exec_on_controllers /root/fds/scripts/install_odl.sh $REMOTE_ODL_LOC -c
else
    exec_on_controllers /root/fds/scripts/install_odl.sh $REMOTE_ODL_LOC
fi

sleep 60
$SCRIPT_DIR/remount_vpp_into_odl.sh
