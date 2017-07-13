##############################################################################
# Copyright (c) 2017 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import requests
import os.path
import time
import logging
import datetime
import threading
import xml.dom.minidom
import os
import paramiko
import yaml
from novaclient.exceptions import ClientException
from lib.FDSLibrary import FDSLibrary


class MyThread(threading.Thread):
    def run(self):
        try:
            self.err = None
            threading.Thread.run(self)
        except Exception as self.err:
            logger = logging.getLogger('StressTest.Verification')
            logger.exception('An exception occurred while verifying resources')
            logger.debug('self.err in MyThread: {}'.format(self.err))


def threaded(fn):
    def wrapper(*args, **kwargs):
        MyThread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class OpenstackNode(object):
    def __init__(self, host_ip, http_session, ssh_user, ssh_key_path, odl_creds=None,
                 wait_for_start=True):
        self.logger = logging.getLogger('StressTest.OpenstackNode')
        self.logger.info('Getting information about an Openstack node at ' + host_ip)
        self.logger.addHandler()
        self.host_ip = host_ip
        self.ssh_user = ssh_user
        self.ssh_key_path = ssh_key_path
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host_ip, username=self.ssh_user, key_filename=self.ssh_key_path)
        self.hostname = self.ssh_client.exec_command('hostname')[1].read()
        self.logger.propagate = False
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(self.hostname + '%(asctime)s: %(name)s: %(levelname)s: %(message)s'))
        self.logger.addHandler(stream)

        self.logger.debug('Found hostname')

        self.sftp_client = self.ssh_client.open_sftp()
        self.http_session = http_session

        self.odl_node = False
        self.odl_creds = odl_creds
        self._get_odl_data()
        self.wait_for_start = wait_for_start

        self._get_fdio_data()

        self.sftp_client.close()
        self.ssh_client.close()

    def _get_odl_data(self):
        self.logger.log('Getting ODL data')
        odl_running_output = self.ssh_client.exec_command(
            "ps aux | grep karaf | grep -v grep | grep -Eo '\-classpath ([^:]*)' | "
            "cut -d " " -f 2 | awk -F\"/lib\" '{print $1}'")[1].read()
        if odl_running_output != '':
            self.odl_node = True
            self.odl_dir = odl_running_output
            self.logger.debug('Found running odl')
            odl_systemd = self.ssh_client.exec_command('systemctl -p SubState show opendaylight | grep running')[
                1].read()
            if odl_systemd != '':
                self.odl_systemd = True
            else:
                self.odl_systemd = False

            # get rest username, password and ip
            remote_jetty_path = os.path.join(self.odl_dir, 'etc', 'jetty.xml')
            jetty_xml = self.sftp_client.file(remote_jetty_path).read()
            document_node = xml.dom.minidom.parseString(jetty_xml).documentElement
            set_nodes = document_node.getElementsByTagName('Set')
            ip_addresses = []
            ports = []
            for set_node in set_nodes:
                if set_node.hasAttribute('name'):
                    if set_node.getAttribute('name') == 'host':
                        text = ''.join([x.data for x in set_node.childNodes if x.TEXT_NODE == x.nodeType]).strip()
                        ip_addresses.append(text)
                    elif set_node.getAttribute('name') == 'port':
                        text = ''.join([x.data for x in set_node.childNodes if x.TEXT_NODE == x.nodeType]).strip()
                        ports.append(text)
            self.odl_routing_node = self.ssh_client.exec_command('grep ^routing-node {} | cut -d = -f 2'.format(
                os.path.join(self.odl_dir, 'etc', 'org.opendaylight.groupbasedpolicy.neutron.vpp.mapper.startup.cfg')))[
                1].read()

            if len(ip_addresses) > 0:
                self.odl_rest_ip = ip_addresses[0]
            else:
                self.odl_rest_ip = self.host_ip

            if len(ports) > 0:
                self.odl_rest_port = ports[0]
            else:
                raise Exception('No ports found in ' + remote_jetty_path)

            self.logger.debug('Found odl rest ip {} and rest port {}'.format(self.odl_rest_ip, self.odl_rest_port))
        else:
            self.odl_node = False
            self.odl_rest_ip = None
            self.odl_rest_port = None
            self.odl_routing_node = None
            self.logger.debug('ODL is not running on this node')

    def _get_fdio_data(self):
        self.logger.info('Gathering fdio data')
        response = self.ssh_client.exec_command("""ps aux | grep -o "\S*/vpp-integration-distribution" |
grep -v '\\S'""")[1].read()
        if response != '':
            self.fdio_node = True
            self.honeycomb_dir = os.path.dirname(response)
            honeycomb_config_dir = os.path.join(self.honeycomb_dir, 'config')
            # TODO clean this up
            self.honeycomb_rest_ip = self.ssh_client.exec_command("""grep restconf-binding-address -r
{} | grep -Eo '([0-9]{{1,3}}.){{3}}[0-9]{{1,3}}'""".format(honeycomb_config_dir))[1].read()
            if self.honeycomb_rest_ip == '127.0.0.1':
                self.honeycomb_rest_ip = self.host_ip
            self.honeycomb_rest_port = self.ssh_client.exec_command("""grep restconf-port -r {} |
grep -o '[0-9]*'""".format(honeycomb_config_dir))[1].read()
            self.honeycomb_rest_username = self.ssh_client.exec_command("""grep username -r {} |
grep -Eo ': "\w+.*$' | grep -Eo '\w+'""".format(honeycomb_config_dir))[1].read()
            self.honeycomb_rest_password = self.ssh_client.exec_command("""grep '"password"' -r {} |
grep -Eo ': "\w+.*$' | grep -Eo '\w+'""")[1].read()
            self.honeycomb_rest_creds = (self.honeycomb_rest_username, self.honeycomb_rest_password)
            self.logger.debug('Found Honeycomb rest ip {}, rest port {}, rest username {} and rest password {}'
                              .format(self.honeycomb_rest_ip,
                                      self.honeycomb_rest_port,
                                      self.honeycomb_rest_username,
                                      self.honeycomb_rest_password))
        else:
            self.fdio_node = False
            self.honeycomb_rest_ip = None
            self.honeycomb_rest_port = None
            self.honeycomb_rest_username = None
            self.honeycomb_rest_password = None
            self.honeycomb_rest_creds = None
            self.logger.debug('Honeycomb is not running on this node')

    def restart_odl(self):
        if self.odl_node:
            try:
                self.ssh_client.connect(self.host_ip, username=self.ssh_user, key_filename=self.ssh_key_path)
                if self.odl_systemd:
                    # execute service opendaylight restart &> /dev/null
                    self.ssh_client.exec_command('service opendaylight restart')
                else:
                    # TODO implement
                    # execute $ODL_DIR/bin/stop &> /dev/null
                    # poll ps aux | grep karaf | grep -c -v grep
                    # when odl is stopped, execute $ODL_DIR/bin/start &> /dev/null
                    pass
                if self.wait_for_start:
                    self._poll_odl_rest()
            finally:
                self.ssh_client.close()

        else:
            raise Exception('Node {} is not an ODL node, cannot restart ODL.'.format(self.hostname))

    def _poll_odl_rest(self):
        positive_response = False
        self.logger.info('Waiting for ODL to respond to rest calls.')
        while not positive_response:
            try:
                response = self.http_session.get('http://{}:{}/restconf/config/network-topology:network-topology'
                                                 '/topology/topology-netconf/'.format(self.odl_rest_ip,
                                                                                      self.odl_rest_port),
                                                 timeout=1,
                                                 auth=self.odl_creds)
                if response.status_code == requests.codes.ok:
                    positive_response = True
                time.sleep(1)
            except requests.exceptions.RequestException:
                # rest call was not yet successful
                pass

        self.logger.info('ODL is responding to rest calls.')


class StressTest(FDSLibrary):
    """
    Assumptions: The whole setup is up and running and ready to use - openstack is running, cluster is running,
                 hc/vpp are running and nothing on these needs to be configured.
                 The test will in fact use configuration of the above components.
                 Openstack credentials are sourced.
                 The host on which this test runs has access to all openstack nodes via ssh.
                 ODL, honeycomb and vpp are running on nodes where neutron or nova services are running.
                 The versions of ODL, honeycomb and vpp are the same across all nodes.
                 The whole setup as well as the node where the test is executed is linux-based.
    """

    def __init__(self):
        logging.basicConfig(format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')
        with open(os.path.join(os.path.dirname(__file__), 'data', 'stress_test.yaml')) as yaml_file:
            yaml_config = yaml.load(yaml_file)

        self.scenario = self._get_yaml_field(yaml_config, 'scenario', 'DEPLOY_SCENARIO')

        self.odl_rest_creds = None
        if 'odl' in self.scenario:
            odl_yaml_config = yaml_config.get('odl')
            if odl_yaml_config:
                self.odl_cluster_rest_ip = self._get_yaml_field(odl_yaml_config, 'cluster_rest_ip', 'SDN_CONTROLLER_IP')
                self.odl_cluster_rest_port = self._get_yaml_field(odl_yaml_config, 'cluster_rest_port')

                username = self._get_yaml_field(odl_yaml_config, 'rest_username')
                password = self._get_yaml_field(odl_yaml_config, 'rest_password')
                self.odl_rest_creds = (username, password)
            else:
                raise Exception('ODL configuration missing in data/stress_test.yaml for scenario ' + self.scenario)

        self.logger_level = self._get_yaml_field(yaml_config, 'log_level', mandatory=False)
        if not self.logger_level:
            self.logger_level = logging.INFO
        elif self.logger_level == 'DEBUG':
            self.logger_level = logging.DEBUG
        elif self.logger_level == 'INFO':
            self.logger_level = logging.INFO
        elif self.logger_level == 'WARNING':
            self.logger_level = logging.WARNING
        elif self.logger_level == 'ERROR':
            self.logger_level = logging.ERROR
        elif self.logger_level == 'CRITICAL':
            self.logger_level = logging.CRITICAL
        else:
            self.logger.warning('Unknown log level {}, setting to INFO'.format(self.logger_level))
            self.logger_level = logging.INFO

        openstack_yaml_config = yaml_config.get('openstack')
        if openstack_yaml_config:
            self.ssh_user = self._get_yaml_field(openstack_yaml_config, 'ssh_user')
            self.ssh_key_path = self._get_yaml_field(openstack_yaml_config, 'ssh_key_path')
            self.openstack_node_ips = self._get_yaml_field(openstack_yaml_config, 'node_ips')
        else:
            raise Exception('Openstack configuration missing in data/stress_test.yaml for scenario ' + self.scenario)

        # TODO generically handle openstack resources that might not be there
        self.image = self._get_yaml_field(yaml_config, 'image')
        self.flavor = self._get_yaml_field(yaml_config, 'flavor')

        self.logger = logging.getLogger('StressTest')
        self.logger.setLevel(self.logger_level)
        self.http_session = requests.Session()

        self.resource_verify_timeout = 300
        self.bridge_domain_verify_timeout = 1200
        self.ports_per_vm = 27
        self.attached_ports = 0
        self.current_cidr_bin = 65793
        self.current_vm = None
        self.current_network_id = None
        self.current_subnet_id = None
        self.current_router_id = None
        self.current_port_id = None
        self.current_tenant_gateway_port_id = None
        self.current_compute_node = None
        self.routing_node = None
        self.created_networks = 0
        self.created_vms = 0
        self.compute_nodes = []
        self.odl_nodes = []
        self.controller_nodes = []
        self.openstack_nodes = []
        self.hypervisors = []
        self.cleanup = {'vms': [],
                        'ports': [],
                        'networks': [],
                        'routers': [],
                        'flavors': [],
                        'floating_ips': [],
                        'images': []}
        FDSLibrary.__init__(self)

    def _get_yaml_field(self, yaml_config, key, env_var=None, mandatory=True):
        yaml_field = yaml_config.get(key)
        if not yaml_field and env_var:
            self.scenario = os.getenv(env_var)
        if not yaml_field and mandatory:
            if env_var:
                raise Exception('Cannot get {}, either configure it in data/stress_test.yaml '
                                'or set {}.'.format(key, env_var))
            else:
                raise Exception(key + ' is missing in data/stress_test.yaml')
        return yaml_field

    def restart_odls(self):
        # ips of nodes where odl runs are in yaml file
        # need to maintain connections to all these nodes
        # find odl, could be running as a service or not
        # kill odl, then start odl
        # when that odl starts responding to rest calls, move to some other odl and repeat
        # need to do in thread and then signal the thread when to stop
        pass

    def restart_openstack_services(self):
        # get ips of nodes where openstack services run
        # we're interested in networking services, but maybe also compute?
        # neutron-server, neutron-dhcp-agent, neutron-metadata-agent, neutron-l3-agent (in odl_l2), networking-vpp
        # nova-api, nova-conductor, nova-scheduler, nova-conductor
        # need to do in thread and then signal the thread when to stop
        pass

    def _update_hypervisors(self):
        self.hypervisors = self.nova_client.hypervisors.list()

    def _gather_openstack_nodes_data(self):
        # construct hostname: OpenstackNode dictionary
        for openstack_node_ip in self.openstack_node_ips:
            openstack_node = OpenstackNode(openstack_node_ip, self.http_session, self.ssh_key_path, self.odl_rest_creds)
            self.openstack_nodes[openstack_node.hostname] = openstack_node
            if openstack_node.odl_node:
                self.odl_nodes.append(openstack_node)

    def rest_get(self, host_ip, port, url, auth, key):
        response_json = self.http_session.get('http://{}:{}{}'.format(host_ip, port, url),
                                              auth=auth).json()
        response_key_json = response_json.get(key)
        return response_key_json

    def _get_odl_json(self, url, key):
        response = self.rest_get(self.odl_cluster_rest_ip, self.odl_cluster_rest_port, url, self.odl_rest_creds, key)
        return response

    def _get_honeycomb_json(self, node, url, key):
        response = self.rest_get(node.honeycomb_rest_ip, node.honeycomb_rest_port, url, node.honeycomb_rest_creds, key)
        return response

    def _get_bridge_domains(self, node):
        bridge_domains_json = self._get_honeycomb_json(node,
                                                       '/restconf/config/v3po:bridge-domains/',
                                                       'bridge-domains')

        if bridge_domains_json:
            return [x['name'] for x in bridge_domains_json['bridge-domain']]
        else:
            return []

    def _free_vm_space(self):
        self._update_hypervisors()
        # hypervisors contains vcpus (max vms) and vcpus_used (current vms)
        for hypervisor in self.hypervisors:
            if hypervisor.vcpus > hypervisor.vcpus_used:
                return True

        return False

    def _create_port(self):
        self.attached_ports += 1
        port_name = 'stress-port-vm{}-{}'.format(self.created_vms, self.attached_ports)
        self.logger.info('Creating port ' + port_name)
        self.current_port_id = self.create_port(port_name, self.current_network_id)['port']['id']
        self.logger.debug('Created port with id ' + self.current_port_id)
        self.cleanup['ports'].append(self.current_port_id)

    @threaded
    def verify_tenant_gateway_honeycomb(self):
        logger = logging.getLogger('StressTest.HCGatewayCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking tenant gateway port in honeycomb')
        start = datetime.datetime.now()
        interface_list = self._get_honeycomb_json(self.routing_node,
                                                  '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                  + self.current_tenant_gateway_port_id, 'interface')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        interface_found = None
        while datetime.datetime.now() - start < delta:
            if interface_list:
                if not interface_found:
                    interface_found = datetime.datetime.now()
                    logger.debug('Tenant gateway port {} created in honeycomb on node {} after {}'
                                 .format(self.current_tenant_gateway_port_id,
                                         self.routing_node.hostname,
                                         interface_found - start))
                port_json = interface_list[0]
                l2_json = port_json.get('v3po:l2')
                if l2_json:
                    logger.debug('L2 configuration {} on tenant gateway port {} created '
                                 'in honeycomb on node {} after {}'
                                 .format(l2_json,
                                         self.current_tenant_gateway_port_id,
                                         self.routing_node.hostname,
                                         datetime.datetime.now() - interface_found))
                    break
            elif interface_found:
                logger.warning('Tenant gateway port {} has been deleted in honeycomb on node {} after {}'
                               .format(self.current_tenant_gateway_port_id,
                                       self.routing_node.hostname,
                                       interface_found - start))
                interface_found = None

            time.sleep(1)
            interface_list = self._get_honeycomb_json(self.routing_node,
                                                      '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                      + self.current_tenant_gateway_port_id, 'interface')
        else:
            if interface_found:
                logger.error("Tenant gateway port {} hasn't been added to bridge domain in honeycomb in time"
                             .format(self.current_tenant_gateway_port_id))
            else:
                logger.error("Tenant gateway port {} has not been created in honeycomb in time"
                             .format(self.current_tenant_gateway_port_id))
            # raise Exception('Timed out when checking that tenant gateway port has been created')
            exit()
        logger.info('Tenant gateway port has been created and added to bridge domain in honeycomb on {} after {}'
                    .format(self.routing_node.hostname,
                            datetime.datetime.now() - start))

    @threaded
    def verify_port_honeycomb(self):
        logger = logging.getLogger('StressTest.HCPortCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking port in honeycomb')
        start = datetime.datetime.now()
        interface_list = self._get_honeycomb_json(self.current_compute_node,
                                                  '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                  + self.current_port_id, 'interface')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        interface_found = None
        while datetime.datetime.now() - start < delta:
            if interface_list:
                if not interface_found:
                    interface_found = datetime.datetime.now()
                    logger.debug("Port {} created in honeycomb on node {} after {}, "
                                 "checking whether it's been added to bridge domain {}"
                                 .format(self.current_port_id,
                                         self.current_compute_node.hostname,
                                         interface_found - start,
                                         self.current_network_id))
                port_json = interface_list[0]
                l2_json = port_json.get('v3po:l2')
                if l2_json:
                    ports_bridge_domain = l2_json.get('bridge-domain')
                    if ports_bridge_domain:
                        logger.debug('Port {} added to bridge domain {} in honeycomb on node {} after {}'
                                     .format(self.current_port_id,
                                             ports_bridge_domain,
                                             self.current_compute_node.hostname,
                                             datetime.datetime.now() - interface_found))
                        break
            elif interface_found:
                logger.warning('Port {} has been deleted in honeycomb on node {} after {}'
                               .format(self.current_port_id,
                                       self.current_compute_node.hostname,
                                       interface_found - start))
                interface_found = None

            time.sleep(1)
            interface_list = self._get_honeycomb_json(self.current_compute_node,
                                                      '/restconf/config/ietf-interfaces:interfaces/interface/'
                                                      'neutron_port_' + self.current_port_id, 'interface')
        else:
            if interface_found:
                logger.error("Port {} hasn't been added to bridge domain in honeycomb in time"
                             .format(self.current_port_id))
            else:
                logger.error("Port {} has not been created in honeycomb in time"
                             .format(self.current_port_id))
            # raise Exception('Timed out when checking that port has been created')
            exit()
        logger.info('Port has been created and added to bridge domain in honeycomb on {} after {}'
                    .format(self.current_compute_node.hostname,
                            datetime.datetime.now() - start))

    @threaded
    def verify_port_odl(self):
        logger = logging.getLogger('StressTest.ODLPortCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking port in odl neutron')
        # TODO finish this
        start = datetime.datetime.now()
        port_list = self._get_odl_json('/restconf/config/neutron:neutron/ports/port/'
                                       + self.current_port_id, 'port')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        interface_found = None
        while datetime.datetime.now() - start < delta:
            if port_list:
                if not interface_found:
                    interface_found = datetime.datetime.now()
                    logger.debug('Port {} created in odl neutron after {}, checking vif-details'
                                 .format(self.current_port_id,
                                         interface_found - start))
                port_json = port_list[0]
                l2_json = port_json.get('neutron-binding:vif-details')
                if l2_json:
                    logger.debug('Vif-details on port {} created in odl neutron after {}'
                                 .format(self.current_port_id,
                                         datetime.datetime.now() - interface_found))
                    break

            time.sleep(1)
            port_list = self._get_odl_json('/restconf/config/neutron:neutron/ports/port/'
                                           + self.current_port_id, 'port')
        else:
            if interface_found:
                logger.error("Port {} hasn't had vif-details in time in odl neutron"
                             .format(self.current_port_id))
            else:
                logger.error("Port {} has not been created in time in odl neutron"
                             .format(self.current_port_id))
            # raise Exception('Timed out when checking that port has been created')
            exit()
        logger.info('Port has been created and has vif-details in odl neutron after {}'
                    .format(datetime.datetime.now() - start))

    @threaded
    def verify_bridge_domains(self):
        logger = logging.getLogger('StressTest.BDCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking bridge domains on ' + self.current_compute_node.hostname)
        start = datetime.datetime.now()
        bridge_domains = self._get_bridge_domains(self.current_compute_node)

        # TODO remove specific timeout when we fix the issue
        delta = datetime.timedelta(seconds=self.bridge_domain_verify_timeout)
        while datetime.datetime.now() - start < delta:
            if self.current_network_id in bridge_domains:
                break
            time.sleep(1)
            bridge_domains = self._get_bridge_domains(self.current_compute_node)
        else:
            logger.debug('Bridge domains on node {} after timeout: {}'
                         .format(self.current_compute_node.hostname, bridge_domains))
            logger.error('Bridge domain {} has not been created in time'.format(self.current_network_id))
            # TODO: move this exception to ping testing when it's implemented
            raise Exception('Timed out when checking that bridge domain has been created')
        logger.info('Bridge domain has been created on {} after {}'
                    .format(self.current_compute_node.hostname,
                            datetime.datetime.now() - start))

    def _create_vm(self):
        self.created_vms += 1
        self._create_port()
        vm_name = 'stress-vm' + str(self.created_vms)
        self.logger.info('Creating VM ' + vm_name)
        self.current_vm = self.create_server(vm_name, self.image, self.flavor, [self.current_port_id])
        self.logger.debug('Created VM with id ' + self.current_vm.id)
        self.cleanup['vms'].append(self.current_vm)

        self.logger.debug('Waiting for VM to be bound to a host')
        # TODO also wait for it to be ACTIVE? Or wait for active, then just get where it's bound
        current_compute_hostname = None
        while current_compute_hostname is None:
            current_compute_hostname = getattr(self.nova_client.servers.get(self.current_vm),
                                               'OS-EXT-SRV-ATTR:host', None)
        self.logger.info('VM found on host ' + current_compute_hostname)
        self.current_compute_node = self.openstack_nodes[current_compute_hostname]

    def _attach_port(self):
        self._create_port()
        self.logger.info('Attaching port to vm')
        start = datetime.datetime.now()
        try:
            # TODO do this in thread?
            self.nova_client.servers.interface_attach(self.current_vm, port_id=self.current_port_id,
                                                      net_id=None, fixed_ip=None)
        except ClientException as e:
            self.logger.warning('Encountered ClientException during interface adding. '
                                'The port was not most likely not created in time (60s). '
                                'More details: {}'.format(e))
        delta = datetime.datetime.now() - start
        self.logger.debug('Attached port {} to vm {} after {}'.format(self.current_port_id,
                                                                      self.current_vm.id,
                                                                      delta))
        if self.attached_ports == self.ports_per_vm:
            self.attached_ports = 0

    def _decode_cidr(self):
        return '{}.{}.{}.0/24'.format(self.current_cidr_bin / 65536 % 256,
                                      self.current_cidr_bin / 256 % 256,
                                      self.current_cidr_bin % 256)

    def _create_network(self):
        self.created_networks += 1
        net_name = 'stress-net-' + str(self.created_networks)
        self.logger.info('Creating network ' + net_name)
        self.current_network_id = self.create_network(net_name)['network']['id']
        self.logger.debug('Created network with id ' + self.current_network_id)
        self.cleanup['networks'].append(self.current_network_id)
        subnet_name = 'stress-subnet-' + str(self.created_networks)
        self.logger.info('Creating subnet ' + subnet_name)
        self.current_subnet_id = self.create_subnet(subnet_name, self.current_network_id,
                                                    self._decode_cidr())['subnet']['id']
        self.logger.debug('Created subnet with id ' + self.current_subnet_id)
        self.current_cidr_bin += 1

    def _create_router(self):
        router_name = 'stress-router-' + str(self.created_networks)
        self.logger.info('Creating router ' + router_name)
        body = {'router': {
            'name': router_name
        }}
        self.current_router_id = self.neutron_client.create_router(body=body)['router']['id']
        self.logger.debug('Created router with id ' + self.current_router_id)
        self.cleanup['routers'].append(self.current_router_id)

    def _attach_subnet_to_router(self):
        self.logger.info('Attaching subnet to router')
        body = {'subnet_id': self.current_subnet_id}
        self.current_tenant_gateway_port_id = self.neutron_client.add_interface_router(self.current_router_id,
                                                                                       body=body)['port_id']

    def set_up(self):
        # attributes we're interested in: hypervisor_hostname and vcpus, host_ip
        # for availability_zone in self.nova_client.availability_zones.list():
        #     if availability_zone.zoneName == 'nova':
        #         self.nova_availability_zone = availability_zone.hosts.keys()
        #         break
        # self.current_compute_host = self.nova_availability_zone[0]
        # TODO create project with proper quotas and use that project
        self._update_hypervisors()
        self._gather_openstack_nodes_data()
        if self.scenario == 'odl_l3':
            self.routing_node = self.openstack_nodes[self.controller_nodes[0].routing_node]
        else:
            self.routing_node = None
        # TODO check image
        # TODO check flavor

    def run_test(self):
        try:
            self.set_up()
            try:
                while self._free_vm_space():
                    # create network
                    # if attached ports = 0, create port in that network and create vm with that port
                    # otherwise attach port in that network to vm
                    self.logger.info('=========================================='
                                     '==========================================')
                    iteration_start = datetime.datetime.now()
                    self._create_network()
                    self._create_router()
                    self._attach_subnet_to_router()
                    self.verify_tenant_gateway_honeycomb()
                    if self.attached_ports == 0:
                        # create vm
                        self._create_vm()
                    else:
                        # attach port
                        self._attach_port()
                    if 'odl' in self.scenario:
                        self.verify_port_odl()
                    self.verify_port_honeycomb()
                    self.verify_bridge_domains()

                    other_threads = threading.enumerate()
                    other_threads.remove(threading.currentThread())
                    for t in other_threads:
                        t.join()

                    self.logger.info('Iteration for network {} done after {}'
                                     .format(self.current_network_id, datetime.datetime.now() - iteration_start))
                    self.logger.info('=========================================='
                                     '==========================================')

                    exceptions = [t.err for t in other_threads if t.err is not None]
                    self.logger.debug('Exceptions from threads: {}'.format(exceptions))
                    if len(exceptions) > 0:
                        raise Exception('Verification of resources failed')

            except Exception as e:
                self.logger.exception('Test failed')
        except Exception as e:
            self.logger.exception('Test setup failed')
            raise e
        finally:
            self.tear_down()

    def tear_down(self):
        # TODO delete all created resources
        pass


if __name__ == '__main__':
    StressTest().run_test()
