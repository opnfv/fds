# == Class fdio::vpp::service
#
# Starts the VPP systemd or Upstart service.
#
class fdio::vpp::service {
  # TODO
  # bring interfaces down before service start
  # so vpp can bind
  service { 'vpp':
    ensure     => running,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
  # TODO
  #sudo vppctl set interface ip address TenGigabitEthernet7/0/0 192.168.21.21/24
  #sudo vppctl set interface state TenGigabitEthernet7/0/0 up


}
