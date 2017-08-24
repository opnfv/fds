.. OPNFV - Open Platform for Network Function Virtualization
.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Scenario: "OpenStack - OpenDaylight - FD.io DVR"
======================================================

Scenario: apex-os-odl-fdio-dvr-noha

"apex-os-odl-fdio-dvr-noha" is a scenario developed as part of the
FastDataStacks OPNFV project. The main components of the
"apex-os-odl-fdio-dvr-noha" scenario are:

 - APEX (TripleO) installer (please also see APEX installer documentation)
 - Openstack (in non-HA configuration)
 - OpenDaylight controller (non-clustered)
   controlling layer 2 and layer 3 networking
 - FD.io/VPP virtual forwarder for tenant networking

Introduction
============

NFV and virtualized high performance applications, such as video processing,
require a "fast data stack" solution that provides both carrier grade
forwarding performance, scalability and open extensibility, along with
functionality for realizing application policies and controlling a complex
network topology.

A solution stack is only as good as its foundation. Key foundational assets for
NFV infrastructure are

  * The virtual forwarder: The virtual forwarder needs to be a feature rich,
    high performance, highly scale virtual switch-router. It needs to leverage
    hardware accelerators when available and run in user space.
    In addition, it should be modular and easily extensible.
  * Forwarder diversity: A solution stack should support a variety of
    forwarders, hardware forwarders (physical switches and routers)
    as well as software forwarders. This way virtual and physical
    forwarding domains can be seamlessly glued together.
  * Policy driven connectivity: Connectivity should respect and
    reflect different business

In order to meet the desired qualities of an NFV infrastructure, the
following components were chosen for the "Openstack - OpenDaylight - FD.io"
scenario:

  * FD.io Vector Packet Processor (VPP) - a highly scalable,
    high performance, extensible virtual forwarder
  * OpenDaylight Controller - an extensible controller platform which
    offers the ability to separate business logic from networking
    constructs, supports a diverse set of network devices
    (virtual and physical) via the "group based policy (GBP)"
    component, and can be clustered to achieve a highly available
    deployment.

The "Openstack - OpenDaylight - FD.io DVR" scenario provides the capability to
realize a set of use-cases relevant to the deployment of NFV nodes instantiated
by means of an Openstack orchestration system on FD.io/VPP enabled compute
nodes. The role of the Opendaylight network controller in this integration is
twofold. It provides a network device configuration and topology abstraction
via the Openstack Neutron interface, while providing the capability to realize
more complex network policies by means of Group Based Policies. Furthermore it
also provides the capabilities to monitor as well as visualize the operation of
the virtual network devices and their topologies.  In supporting the general
use-case of instantiatiting an NFV instance, two specific types of network
transport use cases are realized:

  * NFV instances with VPP data-plane forwarding using a VLAN provider network
  * NFV instances with VPP data-plane forwarding using a VXLAN overlay
    transport network

A deployment of the "apex-os-odl-fdio-dvr-noha" scenario consists of 4 or more
servers:

  * 1 Jumphost hosting the APEX installer - running the Undercloud
  * 1 Controlhost, which runs the Overcloud as well as
      OpenDaylight as a network controller
  * 2 or more Computehosts. These Computehosts also serve as
      layer 3 gateways for tenant networks.

TODO: update the image:
    1. Compute 0..N are gateways
    2. NIC2 on controller is not in vpp

.. image:: FDS-odl_l3-noha-overview.png

Tenant and public networking leverages FD.io/VPP. On compute nodes,
VPP binds to both the tenant networking interface as well as the public
networking interface. This means that VPP is used for communication within
a tenant network, between tenant networks, as well as between a tenant network
and the Internet.

Note that this setup slightly differs from the usual
centralized L3 setup with qrouter on the control node. This setup was chosen
to limit the configuration changes for the introduction of FD.io/VPP.  The
OpenDaylight network controller is used to setup and manage layer 2 and
layer 3 networking for the scenario - with Group Based Policy (GBP) being the
key component. Tenant networking can either leverage VXLAN (in which case a
full mesh of VXLAN tunnels is created) or VLANs.

The picture below shows an example setup with two compute and one control
node. Note that the external network is connected via compute node 0 through
VPP. VPP provides all layer 3 services which are provided in a "vanilla"
OpenStack deployment, including SNAT and DNAT, as well as north-south
and east-west traffic filtering for security purposes ("security groups").

TODO: update the image:
    1. Add External network interface to Computenode-1

.. image:: FDS-L3-noha-sample-setup.png

Features of the scenario
------------------------

Main features of the "apex-os-odl-fdio-dvr-noha" scenario:

  * Automated installation using the APEX installer
  * Fast and scalable tenant networking using FD.io/VPP as forwarder
  * Layer 2 networking using VLANs or VXLAN, managed
    and controlled through OpenDaylight
  * Layer 3 connectivitiy for tenant networks supplied
    through FD.io/VPP. Layer 3 features, including security groups as well as
    floating IP addresses (i.e. NAT) are implemented by the FD.io/VPP forwarder
  * Manual and automatic (via DHCP) addressing on tenant networks

Scenario components and composition
===================================

The apex-os-odl-fdio-dvr-noha scenario combines components from three key open
source projects: OpenStack, OpenDaylight, and Fast Data (FD.io). The key
components that realize the apex-os-odl-fdio-dvr-noha scenario and which differ
from a regular, OVS-based scenario, are the OpenStack ML2 OpenDaylight plugin,
OpenDaylight Neutron Northbound, OpenDaylight Group Based Policy, OpenDaylight
Virtual Bridge Domain Manager, FD.io Honeycomb management agent and FD.io
Vector Packet Processor (VPP).

Note that the key components of the OpenDaylight based scenarios of
FastDataStacks are the same. The centrallized scenario "apex-os-odl-fdio-noha"
and the DVR scenario "apex-os-odl-fdio-dvr-noha" share the same components.

Here's a more detailed list of the individual software components involved:

**Openstack Neutron ML2 OpenDaylight Plugin**: Handles Neutron data base
synchronization and interaction with the southbound controller using a REST
interface.

**ODL GBP Neutron Mapper**: Maps neutron elements like networks, subnets,
security groups, etc. to GBP entities: Creates policy and configuration for
tenants (endpoints, resolved policies, forwarding rules).

**ODL GBP Neutron VPP Mapper**: Maps Neutron ports to VPP endpoints in GBP.

**ODL GBP Location Manager**: Provides real location for endpoints (i.e. Which
physical node an endpoint is connected to).

**GBP Renderer Manager**: Creates configuration for Renderers (like e.g.
VPP-Renderer or OVS-Renderer). The GBP Renderer Manager is the central point
for dispatching of data to specific device renderers.  It uses the information
derived from the GBP end-point and its topology entries to dispatch the task
of configuration to a specific device renderer by writing a renderer policy
configuration into the registered renderer's policy store. The renderer
manager also monitors, by being a data change listener on the VPP Renderer
Policy States, for any errors in the application of a rendered configuration.

**GBP VPP Renderer Interface Manager**: Listens to VPP endpoints in the
Config DataStore and configures associated interfaces on VPP via HoneyComb.

**GBP VPP Renderer Renderer Policy Manager**: Manages the creation of
bridge domains using VBD and assigns interfaces to bridge domains.

**Virtual Bridge Domain Manager (VBD)**: Creates bridge domains (i.e. in case
of VXLAN creates full mesh of VXLAN tunnels, configures split horizon on
tunnel endpoints etc.). VDB configures VXLAN tunnels always into a full-mesh
with split-horizon group forwarding applied on any domain facing tunnel
interface (i.e. forwarding behavior will be that used for VPLS).

**Virtual Packet Processor (VPP) and Honeycomb server**: The VPP is the
accelerated data plane forwarding engine relying on vhost user interfaces
towards Virtual Machines created by the Nova Agent. The Honeycomb NETCONF
configuration server is responsible for driving the configuration of the VPP,
and collecting the operational data.

**Nova Agent**: The Nova Agent, a sub-component of the overall Openstack
architecture, is responsible for interacting with the compute node's host
Libvirt API to drive the life-cycle of Virtual Machines. It, along with the
compute node software, are assumed to be capable of supporting vhost user
interfaces.

The picture below shows the key components.

.. image:: FDS-basic-components.jpg

To provide a better understanding how the above mentioned components interact
with each other, the following diagram shows how the example of creating a
vhost-user port on VPP through Openstack Neutron:

To create or update a port, Neutron will send a request to ODL Neutron
Northbound which contains the UUID, along with the host-id as "vpp" and
vif-type as "vhost-user". The GBP Neutron mapper turns the "Neutron speak" of
"ports" into the generic connectivity model that GroupBasedPolicy uses.
Neutron "ports" become generic "GBP Endpoints" which can be consumed by the
GBP Renderer Manager. The GBP Renderer Manager resolves the policy for the
endpoint, i.e. it determines which communication relationships apply to the
specific endpoint, and hands the resolution to a device specific renderer,
which is the VPP renderer in the given case here. VPP renderer turns the
generic policy into VPP specific configuration. Note that in case the policy
would need to be applied to a different device, e.g. an OpenVSwitch (OVS),
then an "OVS Renderer" would be used. VPP Renderer and the topology manager
("Virtual Bridge Domain" manager - i.e. VBD) cooperate to create the actual
network configuration. VPP Renderer configures the interfaces to the virtual
machines (VM), i.e. the vhost-user interface in the given case here and
attaches them to a bridge domain on VPP. VBD handles the setup of connectivity
between bridge domains on individual VPPs, i.e. it maintains the VXLAN tunnels
in the given case here. Both VPP Renderer as well as VBD communicate with the
device through Netconf/YANG. All compute and control nodes run an instance of
VPP and the VPP-configuration agent "Honeycomb". Honeycomb serves as a
Netconf/YANG server, receives the configuration commands from VBD and VPP
Renderer and drives VPP configuration using VPP's local Java APIs.

.. image:: FDS-simple-callflow.png

Scenario Configuration
======================

To enable the "apex-os-odl-fdio-dvr-noha" scenario check the appropriate
settings in the APEX configuration files. Those are typically found in
/etc/opnfv-apex.

File "deploy_settings.yaml": Choose Opendaylight as controller with version
"oxygen" and enable vpp as forwarder. "odl_routing_node" chooses the dvr
setup for l3 forwarding::

  deploy_options:
    sdn_controller: opendaylight
    odl_version: oxygen
    odl_routing_node: dvr
    tacker: true
    congress: true
    sfc: false
    vpn: false
    vpp: true
    dataplane: fdio
    performance:
      Controller:
        kernel:
          hugepages: 1024
          hugepagesz: 2M
          intel_iommu: 'on'
          iommu: pt
          isolcpus: 1,2
        vpp:
          main-core: 1
          corelist-workers: 2
          uio-driver: uio_pci_generic
      Compute:
        kernel:
          hugepagesz: 2M
          hugepages: 2048
          intel_iommu: 'on'
          iommu: pt
          isolcpus: 1,2
        vpp:
          main-core: 1
          corelist-workers: 2
          uio-driver: uio_pci_generic

Limitations, Issues and Workarounds
===================================

For specific information on limitations and issues, please refer to the APEX
installer release notes.

References
==========


  * FastDataStacks OPNFV project wiki: https://wiki.opnfv.org/display/fds
  * Fast Data (FD.io): https://fd.io/
  * FD.io Vector Packet Processor (VPP): https://wiki.fd.io/view/VPP
  * OpenDaylight Controller: https://www.opendaylight.org/
  * OPNFV Danube release - more information: http://www.opnfv.org/danube
