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
from lib.FDSLibrary import FDSLibrary


class StressTest(FDSLibrary):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')
        self.logger = logging.getLogger('StressTest')
        self.logger.setLevel(logging.DEBUG)
        self.bridge_domain_verify_timeout = 1200
        self.ports_per_vm = 27
        self.image = 'cirros-0.3.4'
        self.flavor = 'm1.tiny'
        self.bd_check_timeout = 1800
        self.attached_ports = 0
        self.current_cidr_bin = 65793
        self.current_vm_id = None
        self.current_network_id = None
        self.current_subnet_id = None
        self.current_router_id = None
        self.current_port_id = None
        self.current_compute_hypervisor = None # hypervisor
        self.created_networks = 0
        self.created_vms = 0
        # hypervisors contains vcpus (max vms) and used_cpus(current vms)
        self.hypervisors = None
        # self.nova_availability_zone = None
        self.cleanup = {'vms': [],
                        'ports': [],
                        'networks': [],
                        'routers': []}
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

    def _verify_bridge_domains(self):
        if self.current_compute_hypervisor is None:
            current_compute_hostname = None
            while current_compute_hostname is None:
                current_compute_hostname = getattr(self.nova_client.servers.get(self.current_vm_id),
                                                   'OS-EXT-SRV-ATTR:host', None)
            self.logger.info('VM found on host ' + current_compute_hostname)
            for hypervisor in self.hypervisors:
                if hypervisor.hypervisor_hostname == current_compute_hostname:
                    self.current_compute_hypervisor = hypervisor
                    break

            if self.current_compute_hypervisor is None:
                raise Exception('Hypervisor {} not found.'.format(current_compute_hostname))

        self.logger.info('Checking bridge domains on ' + self.current_compute_hypervisor.hypervisor_hostname)
        bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)

        start = datetime.datetime.now()
        delta = datetime.timedelta(seconds=self.bridge_domain_verify_timeout)
        while datetime.datetime.now() - start < delta:
            if self.current_network_id in bridge_domains:
                break
            else:
                time.sleep(1)
                bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)
        else:
            self.logger.debug('Bridge domains on node {}: {}'
                              .format(self.current_compute_hypervisor.hypervisor_hostname, bridge_domains))
            raise Exception('Timed out when checking that bridge domain has been created')
        self.logger.info('Bridge domain has been created on ' + self.current_compute_hypervisor.hypervisor_hostname)

    def _create_vm(self):
        self.created_vms += 1
        self._create_port()
        vm_name = 'stress-vm' + str(self.created_vms)
        self.logger.info('Creating VM ' + vm_name)
        self.current_vm_id = self.create_server(vm_name, self.image, self.flavor, [self.current_port_id])
        self.logger.debug('Created VM with id ' + self.current_vm_id)
        self.current_compute_hypervisor = None
        self.cleanup['vms'].append(self.current_vm_id)

    def _attach_port(self):
        self._create_port()
        self.logger.info('Attaching port to vm')
        self.nova_client.servers.interface_attach(self.current_vm_id, port_id=self.current_port_id,
                                                  net_id=None, fixed_ip=None)
        if self.attached_ports == self.ports_per_vm:
            self.attached_ports = 0

    def _decode_cidr(self):
        return '{}.{}.{}.0/24'.format(self.current_cidr_bin/65536 % 256,
                                      self.current_cidr_bin/256 % 256,
                                      self.current_cidr_bin % 256)

    def _create_network(self):
        self.created_networks += 1
        net_name = 'stress-net-' + str(self.created_networks)
        self.logger.info('==============================================================================')
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
        self.neutron_client.add_interface_router(self.current_router_id, body=body)

    def run_test(self):
        try:
            self.set_up()
            try:
                while self._free_vm_space():
                    # create network
                    # if attached ports = 0, create port in that network and create vm with that port
                    # otherwise attach port in that network to vm
                    self._create_network()
                    self._create_router()
                    self._attach_subnet_to_router()
                    if self.attached_ports == 0:
                        # create vm
                        self._create_vm()
                    else:
                        # attach port
                        self._attach_port()
                    self._verify_bridge_domains()
            except Exception:
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
        # TODO check image
        # TODO check flavor

    def tear_down(self):
        pass

    def _update_hypervisors(self):
        self.hypervisors = self.nova_client.hypervisors.list()

    def _get_bridge_domains(self, hostname):
        bridge_domains_json = requests.get('http://{}:8183/restconf/config/v3po:bridge-domains/'
                                           .format(hostname),
                                           auth=('admin', 'admin')).json()
        try:
            bridge_domains = bridge_domains_json['bridge-domains']
        except KeyError:
            bridge_domains = {}

        if len(bridge_domains) > 0:
            return [x['name'] for x in bridge_domains['bridge-domain']]
        else:
            return []


if __name__ == '__main__':
    StressTest().run_test()
