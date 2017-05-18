#!/bin/bash
display_usage() {
  echo "Add VPP Mount into ODL."
  echo "Usage:$0 [ODL Hostname or IP] [Mount Name of VPP in ODL] [VPP IP] \n"
  exit 85
}

. $(dirname $0)/lib.sh

if [  $# -lt 3 ]
then
  display_usage
exit 1
fi

odl_ip=$1
hc_host=$2
hc_ip=$3

post_data='{"node" : [
{"node-id":"'$hc_host'",
"netconf-node-topology:host":"'$hc_ip'",
"netconf-node-topology:port":"'$hc_netconf_port'",
"netconf-node-topology:tcp-only":false,
"netconf-node-topology:keepalive-delay":0,
"netconf-node-topology:username":"'$hc_username'",
"netconf-node-topology:password":"'$hc_password'",
"netconf-node-topology:connection-timeout-millis":10000,
"netconf-node-topology:default-request-timeout-millis":10000,
"netconf-node-topology:max-connection-attempts":10,
"netconf-node-topology:between-attempts-timeout-millis":10000}
]
}
'

curl -u $odl_username:$odl_password -X POST -d "$post_data" -H 'Content-Type: application/json' http://$odl_ip:$odl_port/restconf/config/network-topology:network-topology/network-topology:topology/topology-netconf/
