#!/bin/bash
. $(dirname "$0")/lib.sh
if [[ $# -ne 2 ]]
then
    echo "Must have at least two arguments. The first is name of the service and the second is the action to be done with the service."
    exit 1
fi
exec_on_controllers service $1 $2
