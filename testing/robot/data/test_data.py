##############################################################################
# Copyright (c) 2016 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import uuid

run_uuid = str(uuid.uuid4())
network_name = 'fds_smoke_network_' + run_uuid
subnet_name = 'fds_smoke_subnet_' + run_uuid
sg_client = 'client'
sg_server = 'server'
vm1_name = 'fds_smoke_vm1_' + run_uuid
vm1_address = '192.168.10.5'
vm2_name = 'fds_smoke_vm2_' + run_uuid
vm2_address = '192.168.10.6'
port1_name = 'fds_smoke_port1_' + run_uuid
port2_name = 'fds_smoke_port2_' + run_uuid
subnet_cidr = '192.168.10.0/24'
vm_flavor = 'nfv-fds'
vm_image = 'cirros-0.3.5'
image_path = '/home/opnfv/functest/data/cirros-0.3.5-x86_64-disk.img'
userdata1 = "#!/bin/sh\n\nsudo ip a add {}/24 dev eth0\n while true; do echo curl_passed | nc -l -p 80; done\n".format(vm1_address)
userdata2 = "#!/bin/sh\n\nsudo ip a add {}/24 dev eth0\nwhile true; do\n ping -c 1 {} 2>&1 >/dev/null\n " \
            "RES=$?\n if [ \"Z$RES\" = \"Z0\" ] ; then\n  echo 'ping PASSED'\n break\n else\n  echo " \
            "'ping FAILED'\n fi\n sleep 1\ndone\n\nwhile true; do curl {} --retry-delay 1 -m 1; sleep 3; done\n".format(vm2_address, vm1_address, vm1_address)
