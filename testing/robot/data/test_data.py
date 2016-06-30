import uuid

run_uuid = str(uuid.uuid4())
network_name = 'fds_smoke_network_' + run_uuid
subnet_name = 'fds_smoke_subnet_' + run_uuid
vm1_name = 'fds_smoke_vm1_' + run_uuid
vm1_address = '192.168.10.5'
vm2_name = 'fds_smoke_vm2_' + run_uuid
vm2_address = '192.168.10.6'
port1_name = 'fds_smoke_port1_' + run_uuid
port2_name = 'fds_smoke_port2_' + run_uuid
subnet_cidr = '192.168.10.0/24'
vm_flavor = 'm1.small'
vm_image = 'cirros-0.3.3'
