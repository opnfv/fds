# FD.IO

#### Table of Contents 
1. [Overview](#overview)
1. [Module Description](#module-description)
1. [Setup](#setup)
1. [Usage](#usage)
1. [Reference ](#reference)
1. [Limitations](#limitations)
1. [Development](#development)
1. [Release Notes/Contributors](#release-notescontributors)

## Overview

Puppet module that installs and configures [FD.IO][7].

## Module Description

Deploys FD.IO to various OSs via package.

All configuration should be handled through the Puppet
module's [params](#parameters).

## Setup

* Installs VPP and Honeycomb
* Assumes pre-exiting DPDK bindings
* Configures VPP's startup.conf
* Ensures services are running


## Usage

The most basic usage, passing no parameters to the fdio class, will
install and start vpp and honeycomb with a default configuration.

```puppet
class { 'fdio':
}
```

### Ports

To change the port vpp listens use the `vpp_port` param.


```puppet
class { 'fdio':
  vpp_port => '5002',
}
```

### Set uio-driver

To set the uio-driver use the `dpdk_pmd_driver` param.

```puppet
class { 'fdio':
  dpdk_pmd_driver => 'vfio_pci',
}
```

## Reference

### Classes

#### Public classes

* `::fdio`: Main entry point to the module.

#### Private classes

* `::fdio::params`: Contains default class param values.
* `::fdio::install`: Installs VPP and Honeycomb from packages.
* `::fdio::config`: Manages vpp config
* `::fdio::service`: Starts the services.

### `::fdio`

#### Parameters

##### `vpp_port`

Sets the VPP port.

Default: `8080`

Valid options: A valid port number for VPP to listen on.

##### `dpdk_pmd_driver`

Sets the uio-driver for vpp 

Default: `uio_pci_generic`

Valid options: Driver names are specifed as strings.


## Limitations

* Tested on CentOS 7.

## Development

We welcome contributions and work to make them easy!

TODO

## Release Notes/Contributors

TODO

[1]: <link to fd.io website>
