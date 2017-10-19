.. This work is licensed under a Creative Commons
.. Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0

=======
License
=======

OPNFV Euphrates release notes for FastDataStacks

OPNFV Euphrates release notes for FastDataStacks
are licensed under a Creative Commons Attribution 4.0 International License.
You should have received a copy of the license along with this.
If not, see <http://creativecommons.org/licenses/by/4.0/>.

===================================================
OPNFV Euphrates release notes for FastDataStacks
===================================================

Abstract
========

This document describes the release notes of FastDataStacks project.

OPNFV Euphrates Release
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
control infrastructure supplied by FD.io, i.e. VPP and Honeycomb along with
OpenStack as the VM manager. In addition, OpenDaylight as a network controller
plays a key role in many of the scenarios built by FastDataStacks.

Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | FastDataStacks                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | fds/euphrates.1.0                    |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | 5.0.0                                |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2017-10-20                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Euphrates release              |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

FastDataStacks Scenarios in Euphrates
======================================

In release Euphrates, FastDataStacks releases the following scenarios:

 * `os-nosdn-fdio-noha <http://docs.opnfv.org/en/stable-euphrates/submodules/fds/docs/scenarios/os-nosdn-fdio-noha/index.html>`_:
  OpenStack (with Neutron networking-vpp mechanism driver),
  VPP
 * `os-nosdn-fdio-ha <http://docs.opnfv.org/en/stable-euphrates/submodules/fds/docs/scenarios/os-nosdn-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup, with Neutron networking-vpp mechanism driver),
  VPP
 * `os-odl-fdio-noha <http://docs.opnfv.org/en/stable-euphrates/submodules/fds/docs/scenarios/os-odl-fdio-noha/index.html>`_:
  OpenStack,
  OpenDaylight (for Layer 2 and Layer 3 networking control),
  HoneyComb, VPP
 * `os-odl-fdio-ha <http://docs.opnfv.org/en/stable-euphrates/submodules/fds/docs/scenarios/os-odl-fdio-ha/index.html>`_:
  OpenStack (in a high-availability setup),
  OpenDaylight (for Layer 2 and Layer 3 networking control in clustered mode),
  HoneyComb, VPP
 * `os-odl-fdio_dvr-noha <http://docs.opnfv.org/en/stable-euphrates/submodules/fds/docs/scenarios/os-odl-fdio-dvr-noha/index.html>`_:
  OpenStack,
  OpenDaylight (for Layer 3 networking control; there is not Layer 2 configuration),
  HoneyComb, VPP


All of the scenarios are installed using the APEX installer.

Known Issues/Restrictions
=========================

Scenario os-nosdn-fdio-noha known issues in Euphrates
-----------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller
* `FDS-401 <https://jira.opnfv.org/browse/FDS-401>`_:
  SimpleHealthCheck fails in snaps_smoke
* `FDS-483 <https://jira.opnfv.org/browse/FDS-483>`_:
  Live migration not supported

Scenario os-nosdn-fdio-ha known issues in Euphrates
---------------------------------------------------

* `FDS-156 <https://jira.opnfv.org/browse/FDS-156>`_:
  Race conditions for network-vif-plugged notification
* `FDS-160 <https://jira.opnfv.org/browse/FDS-160>`_:
  Vlan fix on controller
* `FDS-371 <https://jira.opnfv.org/browse/FDS-371>`_:
  Tempest_full_parallel failures due to DBDeadlock error
* `FDS-399 <https://jira.opnfv.org/browse/FDS-399>`_:
  Neutron ports are not marked ACTIVE
* `FDS-400 <https://jira.opnfv.org/browse/FDS-400>`_:
  Race condition between VPP ML2 agent and tempest code
* `FDS-401 <https://jira.opnfv.org/browse/FDS-401>`_:
  SimpleHealthCheck fails in snaps_smoke
* `FDS-483 <https://jira.opnfv.org/browse/FDS-483>`_:
  Live migration not supported
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
* `APEX-469 <https://jira.opnfv.org/browse/APEX-469>`_:
  Undercloud iptables rules are messed up post a power outage
* `FUNCTEST-841 <https://jira.opnfv.org/browse/FUNCTEST-841>`_:
  Cloudify_ims testcase keeps timing out
* `ORCEHSTRA-13 <https://jira.opnfv.org/browse/ORCEHSTRA-13>`_:
  Internal Server Error/java.lang.OutOfMemoryError: Java heap space

Scenario os-odl-fdio-noha known issues in Euphrates
---------------------------------------------------

* `FDS-476 <https://jira.opnfv.org/browse/FDS-476>`_:
  Race conditions in GBP
* `FDS-481 <https://jira.opnfv.org/browse/FDS-481>`_:
  VPP hangs on blocking read from vhost user interface
* `FDS-482 <https://jira.opnfv.org/browse/FDS-482>`_:
  Live migration not supported
* `FDS-484 <https://jira.opnfv.org/browse/FDS-484>`_:
  snaps_smoke failures
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
* `APEX-469 <https://jira.opnfv.org/browse/APEX-469>`_:
  Undercloud iptables rules are messed up post a power outage
* `APEX-532 <https://jira.opnfv.org/browse/APEX-532>`_:
  Add nat undercloud configuration for fdio scenarios

Scenario os-odl-fdio-ha known issues in Euphrates
-------------------------------------------------

* `FDS-476 <https://jira.opnfv.org/browse/FDS-476>`_:
  Race conditions in GBP
* `FDS-481 <https://jira.opnfv.org/browse/FDS-481>`_:
  VPP hangs on blocking read from vhost user interface
* `FDS-482 <https://jira.opnfv.org/browse/FDS-482>`_:
  Live migration not supported
* `FDS-484 <https://jira.opnfv.org/browse/FDS-484>`_:
  snaps_smoke failures
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
* `APEX-469 <https://jira.opnfv.org/browse/APEX-469>`_:
  Undercloud iptables rules are messed up post a power outage
* `APEX-532 <https://jira.opnfv.org/browse/APEX-532>`_:
  Add nat undercloud configuration for fdio scenarios

Scenario os-odl-fdio_dvr-noha known issues in Euphrates
-------------------------------------------------

* `FDS-481 <https://jira.opnfv.org/browse/FDS-481>`_:
  VPP hangs on blocking read from vhost user interface
* `FDS-482 <https://jira.opnfv.org/browse/FDS-482>`_:
  Live migration not supported
* `FDS-484 <https://jira.opnfv.org/browse/FDS-484>`_:
  snaps_smoke failures
* `FDS-485 <https://jira.opnfv.org/browse/FDS-485>`_:
  LISP errors, improvements and cleanup in GBP
* `APEX-468 <https://jira.opnfv.org/browse/APEX-468>`_:
  Mariadb/mysqld fails to start post a reboot
* `APEX-469 <https://jira.opnfv.org/browse/APEX-469>`_:
  Undercloud iptables rules are messed up post a power outage
* `APEX-532 <https://jira.opnfv.org/browse/APEX-532>`_:
  Add nat undercloud configuration for fdio scenarios
* `HC2VPP-249 <https://jira.fd.io/browse/HC2VPP-249>`_:
  Route can be created even if output interface does not exist
* `HC2VPP-250 <https://jira.fd.io/browse/HC2VPP-250>`_:
  Cannot add EID if it's already present in oprational DS

