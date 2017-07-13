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
from lib.FDSLibrary import FDSLibrary


class StressTest(FDSLibrary):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')
        self.logger = logging.getLogger('StressTest')
        self.logger.setLevel(logging.DEBUG)
        self.ports_per_vm = 27
        self.image = 'cirros-0.3.4'
        self.flavor = 'm1.tiny'
        self.bd_check_timeout = 1800
        self.attached_ports = 0
        self.current_cidr_bin = 65793
        self.bridge_domains = {}
        self.current_vm_id = None
        self.current_network_id = None
        self.current_subnet_id = None
        self.current_router_id = None
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
        port_name = 'stress-port-vm{}-{}'.format(self.created_vms, self.attached_ports)
        self.logger.info("Creating port " + port_name)
        port_id = self.create_port(port_name, self.current_network_id)['port']['id']
        self.cleanup['ports'].append(port_id)
        return port_id

    def _verify_bridge_domains(self):
        if self.current_compute_hypervisor is None:
            current_compute_hostname = getattr(self.nova_client.servers.get(self.current_vm_id),
                                               'OS-EXT-SRV-ATTR:host', None)
            for hypervisor in self.hypervisors:
                if hypervisor.hypervisor_hostname == current_compute_hostname:
                    self.current_compute_hypervisor = hypervisor
                    break

            if self.current_compute_hypervisor is None:
                raise Exception('Hypervisor {} not found.'.format(current_compute_hostname))

        self.logger.info("Checking bridge domains on " + self.current_compute_hypervisor.hypervisor_hostname)
        bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)

        while len(self.bridge_domains[self.current_compute_hypervisor.hypervisor_hostname]) == len(bridge_domains):
            time.sleep(1)
            bridge_domains = self._get_bridge_domains(self.current_compute_hypervisor.host_ip)
        self.bridge_domains[self.current_compute_hypervisor.hypervisor_hostname] = bridge_domains

    def _create_vm(self):
        vm_name = 'stress-vm-' + str(self.created_vms)
        self.logger.info("Creating vm " + vm_name)
        self.created_vms += 1
        self.attached_ports += 1
        port_id = self._create_port()
        self.current_vm_id = self.create_server(vm_name, self.image, self.flavor, [port_id])
        self.current_compute_hypervisor = None
        self.cleanup['vms'].append(self.current_vm_id)

    def _attach_port(self):
        self.attached_ports += 1
        port_id = self._create_port()
        self.nova_client.servers.interface_attach(self.current_vm_id, port_id=port_id,
                                                  net_id=None, fixed_ip=None)

    def _decode_cidr(self):
        return '{}.{}.{}.0/24'.format(self.current_cidr_bin/65536 % 256,
                                      self.current_cidr_bin/256 % 256,
                                      self.current_cidr_bin % 256)

    def _create_network(self):
        net_name = 'stress-net-' + str(self.created_networks)
        self.logger.info("Creating network " + net_name)
        self.created_networks += 1
        self.current_network_id = self.create_network(net_name)['network']['id']
        self.cleanup['networks'].append(self.current_network_id)
        subnet_name = 'stress-subnet-' + str(self.created_networks)
        self.logger.info("Creating subnet " + subnet_name)
        self.current_subnet_id = self.create_subnet(subnet_name, self.current_network_id,
                                                    self._decode_cidr())['subnet']['id']
        self.current_cidr_bin += 1

    def _create_router(self):
        router_name = 'stress-router-' + str(self.created_networks)
        self.logger.info("Creating router " + router_name)
        body = {"router": {
            "name": router_name
        }}
        self.current_router_id = self.neutron_client.create_router(body=body)['router']['id']
        self.cleanup['routers'].append(self.current_router_id)

    def _attach_subnet_to_router(self):
        self.logger.info("Attaching subnet to router")
        body = {"subnet_id": self.current_subnet_id}
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
        for hypervisor in self.hypervisors:
            self.bridge_domains[hypervisor.hypervisor_hostname] = self._get_bridge_domains(hypervisor.host_ip)
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
