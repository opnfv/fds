.. This work is licensed under a Creative Commons
.. Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0

=======
License
=======

OPNFV Fraser release notes for FastDataStacks

OPNFV Fraser release notes for FastDataStacks
are licensed under a Creative Commons Attribution 4.0 International License.
You should have received a copy of the license along with this.
If not, see <http://creativecommons.org/licenses/by/4.0/>.

===================================================
OPNFV Fraser release notes for FastDataStacks
===================================================

Abstract
========

This document describes the release notes of FastDataStacks project.

OPNFV Fraser Release
=======================


Any NFV solution stack is only as good as its foundation: The networking
infrastructure. Key foundational assets for a NFV infrastructure are:

 * The virtual forwarder: The virtual forwarder needs to be a feature-rich, high
   performance, highly scale virtual switch-router. It needs to leverage hardware
   accelerators when available and run in user space. In addition, it should be
   modular and easily extensible.

 * Forwarder diversity: A solution stack should
   support a variety of forwarders, hardware forwarders (physical switches and
   routers) as well as software forwarders. This way virtual and physical
   forwarding domains can be seamlessly glued together.

 * Policy driven connectivity: Business policies should determine the network level
   connectivity, rather than the other way around. Historically this has often
   been the other way around which quite often resulted in operational
   challenges.

In order to meet these desired qualities of an NFV infrastructure, the OPNFV
FastDataStacks project was started in spring 2016, shortly after the FD.io
Linux Foundation collaborative project was launched. FastDataStacks set out to
compose a variety of scenarios using FD.io as a foundation to create an NFV
solution that is both fast and flexible. OPNFV runs NFV for real – which also
means that a virtual forwarder has to supply multi-million packet per second
forwarding capability – even, and especially when integrated into a full stack
solution. Simple software switches which are often found in cloud deployments
with forwarding rates in the tens of thousands packets per second don’t offer
appropriate performance for NFV deployments.

FastDataStacks scenarios are created with components from a set of open source
projects. While performing the integration, FastDataStacks had to integrate
and significantly evolve the functionality of different upstream components
used, and evolve the automated installation and testing tools in OPNFV.
FastDataStacks is a great example of OPNFV’s modus operandi: create, compose,
deploy, test, iterate.

The key ingredient for all these scenarios is the data-plane forwarding and
control infrastructure supplied by FD.io, i.e. VPP and networking-vpp along with
OpenStack as the VM manager.

Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | FastDataStacks                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | fds/opnfv-6.1.0                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | 6.1.0                                |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2018-05-25                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Fraser release                 |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

FastDataStacks Scenarios in Fraser
======================================

In release Fraser, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-fraser/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`_:
  OpenStack (with Neutron networking-vpp mechanism driver),
  VPP
 * `os-nosdn-fdio-ha <http://docs.opnfv.org/en/stable-fraser/submodules/fds/docs/scenarios/os-nosdn-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup, with Neutron networking-vpp mechanism driver),
  VPP

Both scenarios are installed using the APEX installer.

Known Issues/Restrictions
=========================

Scenario os-nosdn-fdio-noha known issues in Fraser
-----------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller
* `FDS-491 <https://jira.opnfv.org/browse/FDS-491>`_:
  neutron trunk port feature is not supported in networking-vpp
* `FDS-492 <https://jira.opnfv.org/browse/FDS-492>`_:
  VxLAN is not yet fully functional
* `FDS-493 <https://jira.opnfv.org/browse/FDS-493>`_:
  snaps_smoke has some failures around floating ip
* `FDS-494 <https://jira.opnfv.org/browse/FDS-494>`_:
  refstack has random failures
* `FDS-495 <https://jira.opnfv.org/browse/FDS-495>`_:
  tempest test cases test_network_basic_ops and test_server_basic_ops fail but
  pass when run standalone
* `FDS-496 <https://jira.opnfv.org/browse/FDS-496>`_:
  NAT does not work with VPP 18.04 in some scenarios
* `FUNCTEST-970 <https://jira.opnfv.org/browse/FUNCTEST-970>`_:
  vping_ssh/vping_userdata fail with fraser
* `APEX-593 <https://jira.opnfv.org/browse/APEX-593>`_:
  cirros instance stays stuck in boot for a very long time causing functest
  testcases to timeout

Scenario os-nosdn-fdio-ha known issues in Fraser
---------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller
* `FDS-399 <https://jira.opnfv.org/browse/FDS-399>`_:
  Neutron ports are not marked ACTIVE
* `FDS-400 <https://jira.opnfv.org/browse/FDS-400>`_:
  Race condition between VPP ML2 agent and tempest code
* `FDS-491 <https://jira.opnfv.org/browse/FDS-491>`_:
  neutron trunk port feature is not supported in networking-vpp
* `FDS-492 <https://jira.opnfv.org/browse/FDS-492>`_:
  VxLAN is not yet fully functional
* `FDS-493 <https://jira.opnfv.org/browse/FDS-493>`_:
  snaps_smoke has some failures around floating ip
* `FDS-494 <https://jira.opnfv.org/browse/FDS-494>`_:
  refstack has random failures
* `FDS-495 <https://jira.opnfv.org/browse/FDS-495>`_:
  tempest test cases test_network_basic_ops and test_server_basic_ops fail but
  pass when run standalone
* `FDS-496 <https://jira.opnfv.org/browse/FDS-496>`_:
  NAT does not work with VPP 18.04 in some scenarios
* `FUNCTEST-970 <https://jira.opnfv.org/browse/FUNCTEST-970>`_:
  vping_ssh/vping_userdata fail with fraser
* `APEX-593 <https://jira.opnfv.org/browse/APEX-593>`_:
  cirros instance stays stuck in boot for a very long time causing functest
  testcases to timeout
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
