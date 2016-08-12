# == Class fdio::honeycomb::install
#
# Manages the installation of fdio.
#
class fdio::honeycomb::install (
  $install_method = $::fdio::params::install_method,
) inherits fdio::install {
  if $fdio::install_method == 'rpm' {
    # Install the HC RPM
    package { 'honeycomb':
      ensure  => present,
      require => Yumrepo['fdio-master'],
    }
  }
  else {
    fail("Unknown install method: ${fdio::install_method}")
  }
}
