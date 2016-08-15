# == Class fdio::honeycomb::service
#
# Starts the honeycomb systemd or Upstart service.
#
class fdio::honeycomb::service {
  service { 'honeycomb':
    ensure     => running,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
}
