##############################################################################
# Copyright (c) 2016 Juraj Linkes (Cisco) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

*** Settings ***
Library         OperatingSystem
Library         FDSLibrary.py
Variables       ../data/test_data.py

*** Keywords ***

Ensure Flavor
    ${result} =     Check Flavor Exists     ${vm_flavor}
    Set Suite Variable  ${flavor_to_use}    ${result}
    Return From Keyword If  '${result}' == '${EMPTY}'
    Create Flavor  ${vm_flavor}  ram=768
    ${result} =     Check Flavor Exists
    Set Suite Variable  ${flavor_to_use}    ${result}
    Should Not Be Empty    ${result}

Ensure Image
    ${result} =     Check Image Exists  ${vm_image}
    Return From Keyword If  '${result}' == 'True'
    Create Image  ${vm_image}  /home/opnfv/functest/data/cirros-0.3.4-x86_64-disk.img
    ${result} =     Check Image Exists  ${vm_image}
    Should be True      ${result}

Create tenant network
    &{response} =   create network  ${network_name}
    log many    &{response}
    Set Suite Variable  ${network_id}   ${response.network['id']}
    log     ${network_id}

Create subnet without dhcp
    &{response} =   create subnet  ${subnet_name}   ${network_id}   ${subnet_cidr}  dhcp=False
    log many    &{response}
    Set Suite Variable  ${subnet_id}    ${response.subnet['id']}
    log     ${subnet_id}

Create subnet with dhcp
    &{response} =   create subnet  ${subnet_name}   ${network_id}   ${subnet_cidr}  dhcp=True
    log many    &{response}
    Set Suite Variable  ${subnet_id}    ${response.subnet['id']}
    log     ${subnet_id}

Create security group no default rules
    [Arguments]     ${name}
    &{response} =   create security group  ${name}
    log many     &{response}
    : FOR    ${rule}    IN    @{response.security_group['security_group_rules']}
    \    log    ${rule}
    \    log    ${rule['id']}
    \    delete security rule  ${rule['id']}
    [Return]    ${response.security_group['id']}

Create security group rules
    #def create_security_rule(self, sg_id, dir, eth, desc=None, proto=None, port_min=None, port_max=None, r_sg_id=None, r_prefix=None):
    &{response} =   create security rule  ${sg_client}  ingress  ipv4
    log many    &{response}
    &{response} =   create security rule  ${sg_client}  egress'  ipv4
    log many    &{response}
    &{response} =   create security rule  ${sg_server}  egress   ipv4
    log many    &{response}
    &{response} =   create security rule  ${sg_server}  ingress  ipv4  icmp
    log many    &{response}

Create port with ip
    [Arguments]     ${port_name}    ${ip_address}
    &{response} =   create port     ${port_name}    ${network_id}   ${subnet_id}    ${ip_address}
    log many    &{response}
    log         ${response.port['id']}
    [Return]    ${response.port['id']}

Create vm
    [Arguments]     ${vm_name}     ${port_ids}    ${flavor}=${vm_flavor}    ${security_groups}=${None}  ${userdata}=${None}
    Log Many    ${vm_name}  ${vm_image}     ${flavor}    ${port_ids}     ${userdata}
    ${response} =   create server   ${vm_name}     ${vm_image}     ${flavor}    ${port_ids}  ${security_groups}
    ...                             ${userdata}
    log many    ${response}
    log         ${response.id}
    [Return]    ${response.id}

Check vm console
    [Arguments]     ${vm_id}    ${string}
    ${response} =   check server console    ${vm_id}    ${string}
    [Return]    ${response}

Poll vm
    [Arguments]     ${id}   ${state}
    poll server     ${id}   ${state}

Delete vm
    [Arguments]     ${id}
    ${response} =   delete server   ${id}
    log     ${response}
    Poll vm     ${id}   ${None}

Delete ports
    [Arguments]     ${id}
    ${response} =   delete port     ${id}
    log     ${response}

Delete network
    [Arguments]     ${id}
    ${response} =   delete net      ${id}
    log     ${response}
