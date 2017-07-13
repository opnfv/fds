.. This work is licensed under a Creative Commons
.. Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0

=======
License
=======

OPNFV Danube release note for Functest Docs

OPNFV Danube release note for Functest Docs
are licensed under a Creative Commons Attribution 4.0 International License.
You should have received a copy of the license along with this.
If not, see <http://creativecommons.org/licenses/by/4.0/>.

===============================================
OPNFV Danube3.0 release note for FastDataStacks
===============================================

Abstract
========

This document describes the release notes of FastDataStacks project.


Version history
===============

+------------+----------+------------------+---------------------------+
| **Date**   | **Ver.** | **Author**       | **Comment**               |
|            |          |                  |                           |
+------------+----------+------------------+---------------------------+
| 2017-03-30 | 1.0.0    | Frank Brockners  | FastDataStacks for Danube |
|            |          | (Cisco)          | 1.0 release               |
+------------+----------+------------------+---------------------------+
| 2017-05-02 | 2.0.0    | Frank Brockners  | FastDataStacks for Danube |
|            |          | (Cisco)          | 2.0 release               |
+------------+----------+------------------+---------------------------+
| 2017-13-07 | 3.0.0    | Juraj Linkes     | FastDataStacks for Danube |
|            |          | (Cisco)          | 3.0 release               |
+------------+----------+------------------+---------------------------+


OPNFV Danube Release
======================


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
control infrastructure supplied by FD.io, i.e. VPP and Honeycomb along with
OpenStack as the VM manager. In addition, OpenDaylight as a network controller
plays a key role in many of the scenarios built by FastDataStacks.

Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | FastDataStacks                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | danube.1.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube base release                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | March 31st 2017                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Danube base release                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

+--------------------------------------+--------------------------------------+
| **Project**                          | FastDataStacks                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | danube.2.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube enhancements release          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | May 4st    2017                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Danube enhancements release          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

+--------------------------------------+--------------------------------------+
| **Project**                          | FastDataStacks                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | danube.3.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube enhancements release          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | Jul 14th    2017                     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Danube enhancements release          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

FastDataStacks Scenarios in Danube 1.0
======================================

In release Danube 1.0, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`_:
  OpenStack (with Neutron networking-vpp mechanism driver), VPP
 * `os-odl_l2-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l2-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-noha/index.html>`_:
  OpenStack, OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-noha/index.html>`_:
  OpenStack, OpenDaylight (for Layer 2 and Layer 3 networking control),
  HoneyComb, VPP

All of the scenarios are installed using the APEX installer.


FastDataStacks Scenarios in Danube 2.0
======================================

In release Danube 2.0, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`_:
  OpenStack (with Neutron networking-vpp mechanism driver), VPP
 * `os-odl_l2-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l2-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-noha/index.html>`_:
  OpenStack, OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-noha/index.html>`_:
  OpenStack, OpenDaylight (for Layer 2 and Layer 3 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup), OpenDaylight (for Layer 2 and Layer 3 networking control in clustered mode),
  HoneyComb, VPP


All of the scenarios are installed using the APEX installer.


FastDataStacks Scenarios in Danube 3.0
======================================

In release Danube 3.0, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`_:
  OpenStack (with Neutron networking-vpp mechanism driver),
  VPP
 * `os-nosdn-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-nosdn-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup, with Neutron networking-vpp mechanism driver),
  VPP
 * `os-odl_l2-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 networking control in clustered mode),
  HoneyComb, VPP
 * `os-odl_l2-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-noha/index.html>`_:
  OpenStack,
  OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-noha/index.html>`_:
  OpenStack,
  OpenDaylight (for Layer 2 and Layer 3 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 and Layer 3 networking control in clustered mode),
  HoneyComb, VPP


All of the scenarios are installed using the APEX installer.


Known Issues/Restrictions
=========================

Scenario os-nosdn-fdio-noha known issues in Danube 1.0
------------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  os-nosdn-fdio-noha scenario:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  os-nosdn-fdio-noha scenario: Vlan fix on controller
* `FDS-269 <https://jira.opnfv.org/browse/FDS-269>`_:
  os-nosdn-fdio-noha scenario/refstack_devcore failure
  - tempest.api.volume.test_volumes_actions.
  VolumesV2ActionsTest.test_get_volume_attachment testcase
* `FDS-270 <https://jira.opnfv.org/browse/FDS-270>`_:
  os-nosdn-fdio-noha scenario/refstack_devcore failure -
  tearDownClass (tempest.api.volume.test_volumes_actions.
  VolumesV2ActionsTest)
* `FDS-271 <https://jira.opnfv.org/browse/FDS-271>`_:
  os-nosdn-fdio-noha scenario/snaps_smoke fails 1 test -
  VM not able to obtain IP from DHCP
* `FDS-272 <https://jira.opnfv.org/browse/FDS-272>`_:
  os-nosdn-fdio-noha scenario/domino fails because
  of https proxy issue


Scenario os-odl_l2-fdio-noha known issues in Danube 1.0
-------------------------------------------------------

* `FDS-264 <https://jira.opnfv.org/browse/FDS-264>`_:
  ODL sometimes creates vxlan on incorrect host
* `FDS-275 <https://jira.opnfv.org/browse/FDS-275>`_:
  Refstack testcase ImagesOneServerTestJSON.
  test_create_delete_image failure

Scenario os-odl_l2-fdio-ha known issues in Danube 1.0
-----------------------------------------------------

* `FDS-264 <https://jira.opnfv.org/browse/FDS-264>`_:
  ODL sometimes creates vxlan on incorrect host
* `FDS-275 <https://jira.opnfv.org/browse/FDS-275>`_:
  Refstack testcase ImagesOneServerTestJSON.
  test_create_delete_image failure

Scenario os-odl_l3-fdio-noha known issues in Danube 1,0
-------------------------------------------------------

Note that a set of manual configration steps need to be performed
post an automated deployment for the scenario to be fully functional.
Please refer to `APEX-420 <https://jira.opnfv.org/browse/APEX-420>`_
for details.

* `FDS-246 <https://jira.opnfv.org/browse/FDS-246>`_:
  Metadata service not reachable via dhcp namespace
* `FDS-251 <https://jira.opnfv.org/browse/FDS-251>`_:
  Nat outbound interface is not set correctly in all cases
* `FDS-252 <https://jira.opnfv.org/browse/FDS-252>`_:
  VPP renderer config is sometimes resolved after
  hundreds of configuration changes
* `FDS-264 <https://jira.opnfv.org/browse/FDS-264>`_:
  ODL sometimes creates vxlan on incorrect host
* `FDS-275 <https://jira.opnfv.org/browse/FDS-275>`_:
  Refstack testcase ImagesOneServerTestJSON.
  test_create_delete_image failure
* `APEX-420 <https://jira.opnfv.org/browse/APEX-420>`_:
  Public and tenant interface configuration in odl for
  fdio_l3 noha scenario

Scenario os-nosdn-fdio-noha known issues in Danube 2.0
------------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  os-nosdn-fdio-noha scenario:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  os-nosdn-fdio-noha scenario: Vlan fix on controller
* `FDS-272 <https://jira.opnfv.org/browse/FDS-272>`_:
  os-nosdn-fdio-noha scenario/domino fails because
  of https proxy issue


Scenario os-odl_l2-fdio-noha known issues in Danube 2.0
-------------------------------------------------------

* `FDS-324 <https://jira.opnfv.org/browse/FDS-324>`_:
  Clone of APEX-449 - Domino fails in ci
* `FDS-325 <https://jira.opnfv.org/browse/FDS-325>`_:
  4 Refstack testcases fail - qrouter tap port issue

Scenario os-odl_l2-fdio-ha known issues in Danube 2.0
-----------------------------------------------------

* `FDS-324 <https://jira.opnfv.org/browse/FDS-324>`_:
  Clone of APEX-449 - Domino fails in ci
* `FDS-325 <https://jira.opnfv.org/browse/FDS-325>`_:
  4 Refstack testcases fail - qrouter tap port issue

Scenario os-odl_l3-fdio-noha known issues in Danube 2.0
-------------------------------------------------------

Note that a set of manual configration steps need to be performed
post an automated deployment for the scenario to be fully functional.
Please refer to `APEX-420 <https://jira.opnfv.org/browse/APEX-420>`_
and `APEX 445 <https://jira.opnfv.org/browse/APEX-445>`_ for details.

* `FDS-324 <https://jira.opnfv.org/browse/FDS-324>`_:
  Clone of APEX-449 - Domino fails in ci
* `FDS-325 <https://jira.opnfv.org/browse/FDS-325>`_:
  4 Refstack testcases fail - qrouter tap port issue
* `FDS-333 <https://jira.opnfv.org/browse/FDS-333>`_:
  Tempest failures in l3 scenarios
* `FDS-334 <https://jira.opnfv.org/browse/FDS-334>`_:
  Refstack failures in l3 scenarios

Scenario os-odl_l3-fdio-ha known issues in Danube 2.0
-----------------------------------------------------

Note that a set of manual configration steps need to be performed
post an automated deployment for the scenario to be fully functional.
Please refer to `APEX-420 <https://jira.opnfv.org/browse/APEX-420>`_
and `APEX 445 <https://jira.opnfv.org/browse/APEX-445>`_ for details.

* `FDS-324 <https://jira.opnfv.org/browse/FDS-324>`_:
  Clone of APEX-449 - Domino fails in ci
* `FDS-325 <https://jira.opnfv.org/browse/FDS-325>`_:
  4 Refstack testcases fail - qrouter tap port issue
* `FDS-333 <https://jira.opnfv.org/browse/FDS-333>`_:
  Tempest failures in l3 scenarios
* `FDS-334 <https://jira.opnfv.org/browse/FDS-334>`_:
  Refstack failures in l3 scenarios

Scenario os-nosdn-fdio-noha known issues in Danube 3.0
------------------------------------------------------

* `FDS-405 <https://jira.opnfv.org/browse/FDS-405>`_:
  vlan-strip-offload parameter needs to be set to off
* `FDS-401 <https://jira.opnfv.org/browse/FDS-401>`_:
  SimpleHealthCheck fails in snaps_smoke
* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller

Scenario os-nosdn-fdio-ha known issues in Danube 3.0
------------------------------------------------------

* `FDS-405 <https://jira.opnfv.org/browse/FDS-405>`_:
  vlan-strip-offload parameter needs to be set to off
* `FDS-401 <https://jira.opnfv.org/browse/FDS-401>`_:
  SimpleHealthCheck fails in snaps_smoke
* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller
* `FDS-400 <https://jira.opnfv.org/browse/FDS-400>`_:
  RACE condition between VPP ML2 agent and tempest code
* `FDS-399 <https://jira.opnfv.org/browse/FDS-399>`_:
  Neutron ports are not marked ACTIVE
* `FDS-371 <https://jira.opnfv.org/browse/FDS-371>`_:
  Tempest_full_parallel failures due to DBDeadlock error
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
* `APEX-469 <https://jira.opnfv.org/browse/APEX-469>`_:
  Undercloud iptables rules are messed up post a power outage
* `FUNCTEST-841 <https://jira.opnfv.org/browse/FUNCTEST-841>`_:
  Cloudify_ims testcase keeps timing out
* `ORCEHSTRA-13 <https://jira.opnfv.org/browse/ORCEHSTRA-13>`_:
  Internal Server Error/java.lang.OutOfMemoryError: Java heap space

Scenario os-odl_l2-fdio-noha known issues in Danube 3.0
-------------------------------------------------------

* `FDS-397 <https://jira.opnfv.org/browse/FDS-397>`_:
  Metadata rules are not configured

Scenario os-odl_l2-fdio-ha known issues in Danube 3.0
-----------------------------------------------------

* `FDS-397 <https://jira.opnfv.org/browse/FDS-397>`_:
  Metadata rules are not configured
* `FDS-404 <https://jira.opnfv.org/browse/FDS-404>`_:
  Cluster in HA scenarios sometimes breaks down

Scenario os-odl_l3-fdio-noha known issues in Danube 3.0
-------------------------------------------------------

* `FDS-397 <https://jira.opnfv.org/browse/FDS-397>`_:
  Metadata rules are not configured

Scenario os-odl_l3-fdio-ha known issues in Danube 3.0
-----------------------------------------------------

* `FDS-397 <https://jira.opnfv.org/browse/FDS-397>`_:
  Metadata rules are not configured
* `FDS-404 <https://jira.opnfv.org/browse/FDS-404>`_:
  Cluster in HA scenarios sometimes breaks down

