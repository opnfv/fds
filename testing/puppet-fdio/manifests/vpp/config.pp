# == Class fdio::vpp::config
#
# This class handles vpp config changes.
#
class fdio::vpp::config (
  $dpdk_pmd_type = $::fdio::params::dpdk_pmd_type,
  $dpdk_pci_devs = $::fdio::params::dpdk_pci_devs,
){
  file { '/etc/vpp/startup.conf':
    content => template('fdio/startup.conf.erb'),
  }

  # ensure that uio-pci-generic is loaded
  exec { 'modprobe uio-pci-generic':
    unless => 'lsmod | grep uio-pci-generic',
    path   => '/bin:/sbin',
  }
}
