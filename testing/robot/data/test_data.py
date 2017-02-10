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
vm_flavor = 'm1.small'
vm_image = 'cirros-0.3.3'
userdata1 = "#!/bin/sh\n\nsudo ip a add {}/24 dev eth0\n echo 'success' > f1\n sudo nc -l -p 80 < 'f1'\n".format(vm1_address)
userdata2 = "#!/bin/sh\n\nsudo ip a add {}/24 dev eth0\nwhile true; do\n ping -c 1 {} 2>&1 >/dev/null\n " \
            "RES=$?\n if [ \"Z$RES\" = \"Z0\" ] ; then\n  echo 'ping PASSED'\n break\n else\n  echo " \
            "'ping FAILED'\n fi\n sleep 1\ndone\n\nwhile true; do\n curl -m 5 {} 2>&1 >/dev/null\n " \
            "RES=$?\n if [ \"Z$RES\" = \"Z0\" ] ; then\n  echo 'CURLPASS'\n else\n  echo " \
            "'CURLFAIL'\n fi\n sleep 1\ndone\n".format(vm2_address, vm1_address, vm1_address)