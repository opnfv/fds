# == Class: fdio::honeycomb
#
# fd.io::honeycomb
#
class fdio::honeycomb (
  $install_method = $::fdio::params::install_method,
) inherits ::fdio {

  class { '::fdio::honeycomb::install':
    install_method => $install_method,
  } ->
  class { '::fdio::honeycomb::service': } ->
  Class['::fdio']
}
