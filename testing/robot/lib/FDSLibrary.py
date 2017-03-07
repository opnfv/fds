##############################################################################
# Copyright (c) 2016 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from keystoneauth1 import loading
from keystoneauth1 import session
from glanceclient import client as glance
from neutronclient.v2_0 import client as neutron
from novaclient import client as nova
from novaclient.exceptions import NotFound
import time
import datetime
import os
import subprocess

class FDSLibrary():
    def __init__(self):
        self.glance_client = glance.Client()
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=os.getenv('OS_AUTH_URL'), username=os.getenv('OS_USERNAME'), password=os.getenv('OS_PASSWORD'), project_id=os.getenv('OS_TENANT_NAME'))
        session = session.Session(auth=auth)
        self.glance_client = glance.Client('2', session=session)

        self.neutron_client = neutron.Client(username=os.getenv('OS_USERNAME'),
                                             password=os.getenv('OS_PASSWORD'),
                                             tenant_name=os.getenv('OS_TENANT_NAME'),
                                             auth_url=os.getenv('OS_AUTH_URL'))

        self.nova_client = nova.Client('2',
                                       os.getenv('OS_USERNAME'),
                                       os.getenv('OS_PASSWORD'),
                                       os.getenv('OS_TENANT_NAME'),
                                       os.getenv('OS_AUTH_URL'))

    def check_flavor_exists(self, flavor):
        flavor_list_names = [x.name for x in self.nova_client.flavors.list()]
        return flavor in flavor_list_names

    def create_flavor(self, name, ram, vcpus="1", disk="0"):
        response = self.nova_client.flavors.create(name, ram, vcpus, disk)
        return response

    def check_image_exists(self, image):
        image_list_names = [x.name for x in self.glance_client.images.list()]
        return image in image_list_names

    def create_image(self, image_name, file_path, disk="qcow2",
                        container="bare", public="public", property="hw_mem_page_size=large"):
        # openstack image create --disk-format qcow2 --container-format bare --public --property hw_mem_page_size=large --file ./cirros-0.3.4-x86_64-disk.img cirros-0.3.4
        image = self.glance_client.images.create(name=image_name,
                                                 visibility=public,
                                                 disk_format=disk,
                                                 container_format=container,
                                                 property=property)]
        return image.id

    def create_network(self, name):
        body = {'network': {'name': name}}
        response = self.neutron_client.create_network(body=body)
        return response

    def create_subnet(self, name, network_id, cidr, dhcp=True, ip_version=4):
        body = {'subnet': {
            'name': name,
            'enable_dhcp': dhcp,
            'network_id': network_id,
            'ip_version': ip_version,
            'cidr': cidr
        }}
        response = self.neutron_client.create_subnet(body=body)
        return response

    def create_port(self, name, net_id, subnet_id, ip_address, security_groups=None):
        body = {'port': {
            'name': name,
            'network_id': net_id,
            'fixed_ips': [
                {
                    'subnet_id': subnet_id,
                    'ip_address': ip_address
                }
            ]
        }}
        if security_groups is not None:
            # this is a list
            body['port']['security_groups'] = security_groups
        response = self.neutron_client.create_port(body=body)
        return response

    def create_server(self, name, image, flavor, port_ids, security_groups=None, userdata=None):
        image = self.nova_client.images.find(name=image)
        flavor = self.nova_client.flavors.find(name=flavor)
        nics = [{'port-id': port_id} for port_id in port_ids]
        response = self.nova_client.servers.create(name=name, image=image.id, flavor=flavor.id,
                                                   security_groups=security_groups, nics=nics,
                                                   userdata=userdata)
        for key in dir(response):
            print key, getattr(response, key)
        return response

    def format_string(self, string, substitute):
        return string.format(substitute)

    def check_server_console(self, vm_id, string):
        vm_obj = self.nova_client.servers.get(vm_id)
        timeout = 0
        while timeout < 100:
            console_out = vm_obj.get_console_output()
            print "console output is: '{}'".format(console_out[-200:])
            failed_to_read_metadata = 'failed to read iid from metadata'
            if string in console_out:
                return True
            elif 'request failed' in console_out:
                print 'retrying'
            elif failed_to_read_metadata in console_out:
                print failed_to_read_metadata
                return False
            timeout += 1
            time.sleep(5)
        return False

    def create_security_group(self):
        pass

    def create_security_rule(self):
        pass

    def poll_server(self, vm_id, status, timeout=300):
        try:
            start = datetime.datetime.now()
            delta = datetime.timedelta(seconds=timeout)
            vm_obj = self.nova_client.servers.get(vm_id)
            current_state = getattr(vm_obj, 'OS-EXT-STS:vm_state', None)
            print "Found state '{}' while looking for state '{}'".format(current_state, status)
            while datetime.datetime.now() - start < delta and self._states_are_not_equal(current_state, status):
                time.sleep(1)
                vm_obj = self.nova_client.servers.get(vm_id)
                current_state = getattr(vm_obj, 'OS-EXT-STS:vm_state', None)
                print "Found state '{}' while looking for state '{}'".format(current_state, status)

            if self._states_are_not_equal(current_state, status):
                raise Exception("Vm with id '{}' is in state '{}' after timeout of {} seconds"
                                "".format(vm_id, getattr(vm_obj, 'OS-EXT-STS:vm_state'), timeout))
        except NotFound as e:
            if status is not None:
                raise e
            else:
                print "VM not found, which means it's been deleted"

    def _states_are_not_equal(self, current_state, expected_state):
        return current_state.lower() != expected_state

    def delete_server(self, vm_id):
        response = self.nova_client.servers.delete(vm_id)
        return response

    def delete_port(self, port_id):
        response = self.neutron_client.delete_port(port_id)
        return response

    def delete_net(self, net_id):
        response = self.neutron_client.delete_network(net_id)
        return response

    def ping_vm(self, ip_address):
        try:
            output = subprocess.check_output(['ping', '-c', '4', ip_address])
            print output
        except subprocess.CalledProcessError as e:
            print e.output
            raise Exception('Ping on ip {} failed'.format(ip_address))
