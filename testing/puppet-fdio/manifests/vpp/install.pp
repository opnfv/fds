# == Class fdio::vpp::install
#
# Manages the installation of vpp.
#
class fdio::vpp::install (
  $install_method = $::fdio::params::install_method,
) inherits fdio::install {
  if $install_method == 'rpm' {
    # Install the VPP RPM
    package { 'vpp':
      ensure  => present,
      require => Yumrepo['fdio-master'],
    }
  }
  else {
    fail("Unknown install method: ${fdio::install_method}")
  }
}
