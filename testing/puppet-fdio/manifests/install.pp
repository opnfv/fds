# == Class fdio::install
#
# Manages the installation of fdio.
#
class fdio::install (
  $install_method = $::fdio::params::install_method,
){
  if $install_method == 'rpm' {
    # Choose Yum URL based on OS (CentOS vs Fedora)
    # NB: Currently using the CentOS CBS for both Fedora and CentOS
    $base_url = $::operatingsystem ? {
      'CentOS' => 'https://nexus.fd.io/content/repositories/fd.io.master.centos7/',
      'Fedora' => 'https://nexus.fd.io/content/repositories/fd.io.master.centos7/',
    }

    # Add fdio's Yum repository
    yumrepo { 'fdio-master':
      # 'ensure' isn't supported with Puppet <3.5
      # Seems to default to present, but docs don't say
      # https://docs.puppetlabs.com/references/3.4.0/type.html#yumrepo
      # https://docs.puppetlabs.com/references/3.5.0/type.html#yumrepo
      baseurl  => $base_url,
      descr    => 'fd.io master branch latest merge',
      enabled  => 1,
      # NB: RPM signing is an active TODO, but is not done. We will enable
      #     this gpgcheck once the RPM supports it.
      gpgcheck => 0,
    }

  }
  else {
    fail("Unknown install method: ${fdio::install_method}")
  }
}
