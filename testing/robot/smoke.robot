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
Library         lib/FDSLibrary.py
Variables       data/test_data.py
Suite Setup     Setup Suite
Suite Teardown  Teardown Suite

*** Variables ***

*** Test Cases ***
Create network for VMs
    Create tenant network

Create subnet without dhcp for VMs
    Create subnet without dhcp

Create port for VM1
    ${result} =     Create port with ip     ${port1_name}   ${vm1_address}
    Set Suite Variable  ${port1_id}     ${result}

Create port for VM2
    ${result} =     Create port with ip     ${port2_name}   ${vm2_address}
    Set Suite Variable  ${port2_id}     ${result}

Create VM1
    ${port_ids} =   Create List     ${port1_id}
    ${result} =     Create vm       ${vm1_name}     ${port_ids}     userdata=${userdata1}
    Set Suite Variable  ${vm1_id}   ${result}

Wait for VM1 to be active
    Should Be True  $vm1_id is not $None
    Poll vm     ${vm1_id}   active

Create VM2
    ${port_ids} =   Create List     ${port2_id}
    ${result} =     Create vm       ${vm2_name}     ${port_ids}     userdata=${userdata2}
    Set Suite Variable  ${vm2_id}   ${result}

Wait for VM2 to be active
    Should Be True  $vm2_id is not $None
    Poll vm     ${vm2_id}   active

Check VM2 userdata
    ${result} =     Check vm console    ${vm2_id}   PASSED
    Should Be True  ${result}

*** Keywords ***
Setup Suite
    Set Suite Variable  ${network_id}   ${None}
    Set Suite Variable  ${subnet_id}    ${None}
    Set Suite Variable  ${port1_id}     ${None}
    Set Suite Variable  ${port2_id}     ${None}
    Set Suite Variable  ${vm1_id}       ${None}
    Set Suite Variable  ${vm2_id}       ${None}
    Ensure Image
    Ensure Flavor

Teardown Suite
    Run Keyword If  $vm1_id is not $None        Delete vm       ${vm1_id}
    Run Keyword If  $vm2_id is not $None        Delete vm       ${vm2_id}
    Run Keyword If  $port1_id is not $None      Delete ports    ${port1_id}
    Run Keyword If  $port2_id is not $None      Delete ports    ${port2_id}
    Run Keyword If  $network_id is not $None    Delete network  ${network_id}

Ensure Flavor
    ${result} =     Check Flavor Exists     ${vm_flavor}
    Return From Keyword If ${result} == 'True'
    Create Flavor  ${vm_flavor}  ram=768
    ${result} =     Check Flavor Exists     ${vm_flavor}
    Should be True      ${result}

Ensure Image
    ${result} =     Check Image Exists  ${vm_image}
    Return From Keyword If ${result} == 'True'
    Create Image  ${vm_image}  /home/opnfv/functest/data/cirros-0.3.5-x86_64-disk.img
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

Create port with ip
    [Arguments]     ${port_name}    ${ip_address}
    &{response} =   create port     ${port_name}    ${network_id}   ${subnet_id}    ${ip_address}
    log many    &{response}
    log         ${response.port['id']}
    [Return]    ${response.port['id']}

Create vm
    [Arguments]     ${vm_name}     ${port_ids}  ${security_groups}=${None}  ${userdata}=${None}
    Log Many    ${vm_name}  ${vm_image}     ${vm_flavor}    ${port_ids}     ${userdata}
    ${response} =   create server   ${vm_name}     ${vm_image}     ${vm_flavor}    ${port_ids}  ${security_groups}
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
