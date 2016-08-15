# == Class fdio::params
#
# This class manages the default params for the ODL class.
#
class fdio::params {
  # NB: If you update the default values here, you'll also need to update:
  #   spec/spec_helper_acceptance.rb's install_odl helper fn
  #   spec/classes/fdio_spec.rb tests that use default Karaf features
  # Else, both the Beaker and RSpec tests will fail
  # TODO: Remove this possible source of bugs^^
  $install_method = 'rpm'
  $dpdk_pmd_type = 'uio_pci_generic'
  $dpdk_pci_devs = []
}
