#!/bin/bash
SCRIPT_DIR=$(dirname $0)
. $SCRIPT_DIR/lib.sh
service opendaylight stop
sleep 10
INSTALL_DIR=/opt
ODL_DIR=$INSTALL_DIR/opendaylight
ODL_TGZ_NAME=$1
cp $ODL_DIR/etc/jetty.xml $INSTALL_DIR
cp $ODL_DIR/etc/org.opendaylight.groupbasedpolicy.neutron.vpp.mapper.startup.cfg $INSTALL_DIR
cp $ODL_DIR/etc/org.opendaylight.groupbasedpolicy.renderer.vpp.startup.cfg $INSTALL_DIR
rm -rf $ODL_DIR
#mv opendaylight orig_opendaylight
ODL_DEFAULT_DIR_NAME=$(tar tf $ODL_TGZ_NAME | head -n1 | cut -d "/" -f 1)
tar -C $INSTALL_DIR -xf $ODL_TGZ_NAME
mv $INSTALL_DIR/$ODL_DEFAULT_DIR_NAME $INSTALL_DIR/opendaylight

#CHANGE PORT:
cp $INSTALL_DIR/jetty.xml $ODL_DIR/etc/
cp $INSTALL_DIR/org.opendaylight.groupbasedpolicy.neutron.vpp.mapper.startup.cfg $ODL_DIR/etc/
cp $INSTALL_DIR/org.opendaylight.groupbasedpolicy.renderer.vpp.startup.cfg $ODL_DIR/etc/

#CONFIGURE LOGGING:
sed -i 's/log4j.appender.out.maxFileSize=.*/log4j.appender.out.maxFileSize=100MB/' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
sed -i 's/log4j.appender.out.maxBackupIndex=.*/log4j.appender.out.maxBackupIndex=10/' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.groupbasedpolicy.renderer.vpp = TRACE' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.groupbasedpolicy.neutron.mapper = TRACE' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.groupbasedpolicy.neutron.vpp.mapper = TRACE' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.vbd = TRACE' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.netconf.sal.connect.netconf = TRACE' $ODL_DIR/etc/org.ops4j.pax.logging.cfg
#sed -i '$alog4j.logger.org.opendaylight.netconf = DEBUG' $ODL_DIR/etc/org.ops4j.pax.logging.cfg

#ACL LOGGING
#sed -i '$alog4j.logger.org.opendaylight.groupbasedpolicy.renderer.vpp.policy.acl = INFO' $ODL_DIR/etc/org.ops4j.pax.logging.cfg

#INSTALL FEATURES
sed -i 's/featuresBoot=.*/featuresBoot=config,standard,region,package,kar,ssh,management,odl-restconf,odl-netconf-all,odl-groupbasedpolicy-neutron-vpp-mapper,odl-vbd/' $ODL_DIR/etc/org.apache.karaf.features.cfg

#CHANGE OWNER AND RESTART DAEMON
chown -R odl:odl $ODL_DIR
systemctl daemon-reload

#CONFIGURE CLUSTER
if [[ $2 == "-c" ]]
then
    NODE_NUMBER=$(hostname | grep -o [0-9])
    ((NODE_NUMBER++))
    ODL_IPS=$(grep -A 7 "listen opendaylight" /etc/haproxy/haproxy.cfg | grep server | grep -Eo "$IPV4_REGEX")
    $ODL_DIR/bin/configure_cluster.sh $NODE_NUMBER $ODL_IPS
fi

#START ODL
service opendaylight start

