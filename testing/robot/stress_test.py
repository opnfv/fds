##############################################################################
# Copyright (c) 2017 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import requests
import time
import logging
import datetime
import threading
import os
from novaclient.exceptions import ClientException
from lib.FDSLibrary import FDSLibrary


class OpenstackNode(object):
    def __init__(self, hostname):
        self.hostname = hostname
        self._get_host_ip()

    def _get_host_ip(self):
        self.host_ip = None

    def _get_odl_port(self):
        self.odl_port = None

    def _get_honeycomb_port(self):
        self.honeycomb_port = None

    def _get_openstack_services(self):
        self.openstack_services = None


class MyThread(threading.Thread):
    def run(self):
        try:
            threading.Thread.run(self)
        except Exception as self.err:
            logger = logging.getLogger('StressTest.Verification')
            logger.exception('An exception occurred while verifying resources')
        else:
            self.err = None


def threaded(fn):
    def wrapper(*args, **kwargs):
        MyThread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class StressTest(FDSLibrary):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')
        self.odl_ip = os.getenv('SDN_CONTROLLER_IP')
        if self.odl_ip is None:
            raise Exception('Odl ip not found among environment variables, please set SDN_CONTROLLER_IP')
        # TODO move these to yaml or such
        self.odl_port = 8081
        self.honeycomb_port = 8183
        self.routing_node = 'overcloud-novacompute-0.opnfv.org'
        self.scenario = 'odl_l3'
        self.odl_auth = ('admin', 'admin')
        self.honeycomb_auth = ('admin', 'admin')

        # TODO generically handle openstack resources that might not be there
        self.image = 'cirros-0.3.4'
        self.flavor = 'm1.tiny'

        self.logger = logging.getLogger('StressTest')
        self.logger_level = logging.DEBUG
        self.logger.setLevel(self.logger_level)
        self.resource_verify_timeout = 1200
        self.ports_per_vm = 27
        self.attached_ports = 0
        self.current_cidr_bin = 65793
        self.current_vm = None
        self.current_network_id = None
        self.current_subnet_id = None
        self.current_router_id = None
        self.current_port_id = None
        self.current_tenant_gateway_port_id = None
        self.current_compute_hypervisor = None  # hypervisor
        self.created_networks = 0
        self.created_vms = 0
        # hypervisors contains vcpus (max vms) and used_cpus(current vms)
        self.hypervisors = None
        self.routing_node_ip = None
        # self.nova_availability_zone = None
        self.cleanup = {'vms': [],
                        'ports': [],
                        'networks': [],
                        'routers': [],
                        'flavors': [],
                        'floating_ips': [],
                        'images': []}
        FDSLibrary.__init__(self)

    def _free_vm_space(self):
        self._update_hypervisors()
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
        logger = logging.getLogger('StressTest.GatewayCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking tenant gateway port in honeycomb')
        start = datetime.datetime.now()
        interface_list = self._get_honeycomb_json(self.routing_node_ip,
                                                  '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                  + self.current_tenant_gateway_port_id, 'interface')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        while datetime.datetime.now() - start < delta:
            if interface_list:
                logger.debug('Tenant gateway port {} created in honeycomb on node {}'
                             .format(self.current_tenant_gateway_port_id,
                                     self.routing_node))
                break
            else:
                port_json = interface_list[0]
                l2_json = port_json.get('v3po:l2')
                if l2_json:
                    self.logger.debug('L2 configuration {} on tenant gateway port {} created in honeycomb on node {}'
                                      .format(l2_json, self.current_tenant_gateway_port_id,
                                              self.routing_node))
                    break

            interface_list = self._get_honeycomb_json(self.routing_node_ip,
                                                      '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                      + self.current_tenant_gateway_port_id, 'interface')
        else:
            logger.error('Tenant gateway port {} has not been created in time'
                         .format(self.current_tenant_gateway_port_id))
            # raise Exception('Timed out when checking that tenant gateway port has been created')
            exit()
        logger.info('Tenant gateway port {} has been created on {} after {}'
                    .format(self.current_tenant_gateway_port_id,
                            self.routing_node,
                            datetime.datetime.now() - start))

    @threaded
    def verify_port_honeycomb(self):
        logger = logging.getLogger('StressTest.HCPortCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking port in honeycomb')
        start = datetime.datetime.now()
        interface_list = self._get_honeycomb_json(self.current_compute_hypervisor.host_ip,
                                                  '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                  + self.current_port_id, 'interface')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        interface_found = False
        while datetime.datetime.now() - start < delta:
            if interface_list:
                if not interface_found:
                    interface_found = True
                    logger.debug("Port {} created in honeycomb on node {}, "
                                 "checking whether it's been added to bridge domain {}"
                                 .format(self.current_port_id,
                                         self.current_compute_hypervisor.hypervisor_hostname,
                                         self.current_network_id))
                else:
                    port_json = interface_list[0]
                    l2_json = port_json.get('v3po:l2')
                    if l2_json:
                        ports_bridge_domain = l2_json.get('bridge-domain')
                        if ports_bridge_domain:
                            logger.debug('Port {} added to bridge domain {} honeycomb on node {}'
                                         .format(self.current_port_id, ports_bridge_domain,
                                                 self.current_compute_hypervisor.hypervisor_hostname))
                            break

            interface_list = self._get_honeycomb_json(self.current_compute_hypervisor.host_ip,
                                                      '/restconf/config/ietf-interfaces:interfaces/interface/neutron_port_'
                                                      + self.current_port_id, 'interface')
        else:
            logger.error('Port {} has not been created in honeycomb in time'.format(self.current_port_id))
            # raise Exception('Timed out when checking that port has been created')
            exit()
        logger.info('Port {} has been created on {} after {}'
                    .format(self.current_port_id,
                            self.current_compute_hypervisor.hypervisor_hostname,
                            datetime.datetime.now() - start))

    @threaded
    def verify_port_odl(self):
        logger = logging.getLogger('StressTest.ODLPortCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking port in odl')
        # TODO finish this
        start = datetime.datetime.now()
        port_list = self._get_odl_json('/restconf/config/neutron:neutron/ports/port/'
                                       + self.current_port_id, 'port')
        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        interface_found = False
        while datetime.datetime.now() - start < delta:
            if port_list:
                if not interface_found:
                    interface_found = True
                    logger.debug('Port {} created in odl neutron, checking vif-details'.format(self.current_port_id))
                else:
                    port_json = port_list[0]
                    l2_json = port_json.get('neutron-binding:vif-details')
                    if l2_json:
                        logger.debug('Vif-details on port {} created in odl neutron'.format(self.current_port_id))
                        break

            port_list = self._get_odl_json('/restconf/config/neutron:neutron/ports/port/'
                                           + self.current_port_id, 'port')
        else:
            logger.error('Port {} has not been created in time'.format(self.current_port_id))
            # raise Exception('Timed out when checking that port has been created')
            exit()
        logger.info('Port {} has been created on {} after {}'
                    .format(self.current_port_id,
                            self.current_compute_hypervisor.hypervisor_hostname,
                            datetime.datetime.now() - start))

    @threaded
    def verify_bridge_domains(self):
        logger = logging.getLogger('StressTest.BDCheck')
        logger.setLevel(self.logger_level)
        logger.info('Checking bridge domains on ' + self.current_compute_hypervisor.hypervisor_hostname)
        start = datetime.datetime.now()
        bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)

        delta = datetime.timedelta(seconds=self.resource_verify_timeout)
        while datetime.datetime.now() - start < delta:
            if self.current_network_id in bridge_domains:
                break
            time.sleep(1)
            bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)
        else:
            logger.debug('Bridge domains on node {} after timeout: {}'
                         .format(self.current_compute_hypervisor.hypervisor_hostname, bridge_domains))
            logger.error('Bridge domain {} has not been created in time'.format(self.current_network_id))
            # TODO: move this exception to ping testing when it's implemented
            raise Exception('Timed out when checking that bridge domain has been created')
        logger.info('Bridge domain has been created on {} after {}'
                    .format(self.current_compute_hypervisor.hypervisor_hostname,
                            datetime.datetime.now() - start))

    def _create_vm(self):
        self.created_vms += 1
        self._create_port()
        vm_name = 'stress-vm' + str(self.created_vms)
        self.logger.info('Creating VM ' + vm_name)
        self.current_vm = self.create_server(vm_name, self.image, self.flavor, [self.current_port_id])
        self.logger.debug('Created VM with id ' + self.current_vm.id)
        self.current_compute_hypervisor = None
        self.cleanup['vms'].append(self.current_vm)

        self.logger.debug('Waiting for VM to be bound to a host')
        # TODO also wait for it to be ACTIVE? Or wait for active, then just get where it's bound
        if self.current_compute_hypervisor is None:
            current_compute_hostname = None
            while current_compute_hostname is None:
                current_compute_hostname = getattr(self.nova_client.servers.get(self.current_vm),
                                                   'OS-EXT-SRV-ATTR:host', None)
            self.logger.info('VM found on host ' + current_compute_hostname)
            for hypervisor in self.hypervisors:
                if hypervisor.hypervisor_hostname == current_compute_hostname:
                    self.current_compute_hypervisor = hypervisor
                    break

            if self.current_compute_hypervisor is None:
                raise Exception('Hypervisor {} not found.'.format(current_compute_hostname))

    def _attach_port(self):
        self._create_port()
        self.logger.info('Attaching port to vm')
        start = datetime.datetime.now()
        try:
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
                    if len(exceptions) > 0:
                        raise Exception('Verification of resources failed')

            except Exception as e:
                self.logger.exception('Test failed')
        except Exception as e:
            self.logger.exception('Test setup failed')
            raise e
        finally:
            self.tear_down()

    def set_up(self):
        # attributes we're interested in: hypervisor_hostname and vcpus, host_ip
        # for availability_zone in self.nova_client.availability_zones.list():
        #     if availability_zone.zoneName == 'nova':
        #         self.nova_availability_zone = availability_zone.hosts.keys()
        #         break
        # self.current_compute_host = self.nova_availability_zone[0]
        # TODO create project with proper quotas and use that project
        self._update_hypervisors()
        self._get_routing_node_ip()
        # TODO check image
        # TODO check flavor

    def tear_down(self):
        # TODO delete all created resources
        pass

    def _get_routing_node_ip(self):
        for hypervisor in self.hypervisors:
            if self.routing_node == hypervisor.hypervisor_hostname:
                self.routing_node_ip = hypervisor.host_ip
                break

        if self.routing_node_ip is None:
            raise Exception('Routing node {} not found'.format(self.routing_node))

    def _update_hypervisors(self):
        self.hypervisors = self.nova_client.hypervisors.list()

    @staticmethod
    def rest_get(host_ip, port, url, auth, key):
        response_json = requests.get('http://{}:{}{}'.format(host_ip, port, url),
                                     auth=auth).json()
        response_key_json = response_json.get(key)
        return response_key_json

    def _get_odl_json(self, url, key):
        return self.rest_get(self.odl_ip, self.odl_port, url, self.odl_auth, key)

    def _get_honeycomb_json(self, hostname, url, key):
        return self.rest_get(hostname, self.honeycomb_port, url, self.honeycomb_auth, key)

    def _get_bridge_domains(self, hostname):
        bridge_domains_json = self._get_honeycomb_json(hostname,
                                                       '/restconf/config/v3po:bridge-domains/',
                                                       'bridge-domains')

        if bridge_domains_json:
            return [x['name'] for x in bridge_domains_json['bridge-domain']]
        else:
            return []


if __name__ == '__main__':
    StressTest().run_test()
