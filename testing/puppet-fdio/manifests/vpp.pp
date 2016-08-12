# == Class: fdio::vpp
#
# fd.io::vpp
#
# === Parameters
# [* vpp_port *]
#   Port for VPP to listen on.
# [* dpdk_pmd_driver *]
#   Sets VPP's uio-driver value
class fdio::vpp (
  $install_method = $::fdio::params::install_method,
  $dpdk_pmd_type = $::fdio::params::dpdk_pmd_type,
  $dpdk_pci_devs = $::fdio::params::dpdk_pci_devs,
) inherits ::fdio {

  class { '::fdio::vpp::install':
    install_method => $install_method,
  } ->
  class { '::fdio::vpp::config':
    dpdk_pmd_type => $dpdk_pmd_type,
    dpdk_pci_devs => $dpdk_pci_devs,
  } ~>
  class { '::fdio::vpp::service': } ->
  Class['::fdio::vpp']
}
