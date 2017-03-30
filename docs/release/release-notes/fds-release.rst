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
OPNFV Danube1.0 release note for FastDataStacks
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
|            |          | (Cisco)          | release                   |
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

FastDataStacks Scenarios in Danube 1.0
======================================

In release Danube 1.0, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`:
  OpenStack (with Neutron networking-vpp mechanism driver), VPP
 * `os-odl_l2-fdio-ha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-ha/index.html>`
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l2-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l2-fdio-noha/index.html>`
  OpenStack, OpenDaylight (for Layer 2 networking control),
  HoneyComb, VPP
 * `os-odl_l3-fdio-noha <http://docs.opnfv.org/en/stable-danube/submodules/fds/docs/scenarios/os-odl_l3-fdio-noha/index.html>`
  OpenStack, OpenDaylight (for Layer 2 and Layer 3 networking control),
  HoneyComb, VPP

All of the scenarios are installed using the APEX installer.

Known Issues/Restrictions
=========================

Scenario os-nosdn-fdio-noha known issues
----------------------------------------

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


Scenario os-odl_l2-fdio-noha known issues
-----------------------------------------

* `FDS-264 <https://jira.opnfv.org/browse/FDS-264>`_:
  ODL sometimes creates vxlan on incorrect host
* `FDS-275 <https://jira.opnfv.org/browse/FDS-275>`_:
  Refstack testcase ImagesOneServerTestJSON.
  test_create_delete_image failure

Scenario os-odl_l2-fdio-ha known issues
---------------------------------------

* `FDS-264 <https://jira.opnfv.org/browse/FDS-264>`_:
  ODL sometimes creates vxlan on incorrect host
* `FDS-275 <https://jira.opnfv.org/browse/FDS-275>`_:
  Refstack testcase ImagesOneServerTestJSON.
  test_create_delete_image failure

Scenario os-odl_l3-fdio-noha known issues
-----------------------------------------

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

