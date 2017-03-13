##############################################################################
# Copyright (c) 2017 Tomas Cechvala (Cisco) and others.
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
Resource        lib/Keywords.robot
Suite Setup     Setup Suite
Suite Teardown  Teardown Suite

*** Variables ***

*** Test Cases ***

Create network for VMs
    Create tenant network

Create subnet with dhcp for VMs
    Create subnet with dhcp

Create sec groups
    ${result} =    Create security group no default rules    ${sg_server}
    Set Suite Variable  ${SEC_GR_SERVER}   ${result}
    ${result} =    Create security group no default rules    ${sg_client}
    Set Suite Variable  ${SEC_GR_CLIENT}   ${result}

Create sec rules
    Wait Until Keyword Succeeds  3x  3s  create security rule  ${SEC_GR_CLIENT}  egress  ipv4
    Wait Until Keyword Succeeds  3x  3s  create security rule  ${SEC_GR_CLIENT}  ingress  ipv4
    Wait Until Keyword Succeeds  3x  3s  create security rule  ${SEC_GR_SERVER}  egress  ipv4
    Wait Until Keyword Succeeds  3x  3s  create security rule  ${SEC_GR_SERVER}  ingress  ipv4  proto=icmp

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
    ${result} =     Create vm       ${vm2_name}     ${port_ids}    flavor=${flavor_to_use}     userdata=${userdata2}
    Set Suite Variable  ${vm2_id}   ${result}

Wait for VM2 to be active
    Should Be True  $vm2_id is not $None
    Poll vm     ${vm2_id}   active

Check VM2 userdata
    ${result} =     Check vm console    ${vm2_id}   PASSED
    Should Be True  ${result}

Modify policy
    Wait Until Keyword Succeeds  3x  3s  create security rule  ${SEC_GR_SERVER}  ingress  ipv4  proto=tcp  port_min=80  port_max=80

Check VM2 userdata again
    ${result} =     Check vm console    ${vm2_id}   curl_passed
    Should Be True  ${result}

*** Keywords ***
Setup Suite
    Set Suite Variable  ${network_id}   ${None}
    Set Suite Variable  ${subnet_id}    ${None}
    Set Suite Variable  ${port1_id}     ${None}
    Set Suite Variable  ${port2_id}     ${None}
    Set Suite Variable  ${vm1_id}       ${None}
    Set Suite Variable  ${vm2_id}       ${None}
    Set Suite Variable  ${SEC_GR_SERVER}       ${None}
    Set Suite Variable  ${SEC_GR_CLIENT}       ${None}
    Ensure Image
    Ensure Flavor

Teardown Suite
    Run Keyword If  $vm1_id is not $None        Delete vm       ${vm1_id}
    Run Keyword If  $vm2_id is not $None        Delete vm       ${vm2_id}
    Run Keyword If  $port1_id is not $None      Delete ports    ${port1_id}
    Run Keyword If  $port2_id is not $None      Delete ports    ${port2_id}
    Run Keyword If  $network_id is not $None    Delete network  ${network_id}
    Run Keyword If  $SEC_GR_SERVER is not $None      delete security group  ${SEC_GR_SERVER}
    Run Keyword If  $SEC_GR_CLIENT is not $None      delete security group  ${SEC_GR_CLIENT}
