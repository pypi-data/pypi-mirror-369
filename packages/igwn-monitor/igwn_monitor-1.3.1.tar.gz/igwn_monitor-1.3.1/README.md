This project houses custom monitoring plugins designed to be executed
on the remote host (not the monitoring instance).

All plugins here must follow (as far as possible) the Monitoring Plugins
Development Guidelines as outlined here:

<https://www.monitoring-plugins.org/doc/guidelines.html>

#### Installation

Binary packages from this project are distributed for RHEL and Debian
distributions supported by the IGWN Computing and Software group.
For instructions on configuring your system package manager to
follow the IGWN repositories, please see

<https://computing.docs.ligo.org/guide/software/>

The `igwn-monitoring-plugins` packages follow the convention for Nagios plugin
packages for each platform and can be discovered on the relevant systems via

```shell
dnf search nagios-plugins-igwn*
```

for RHEL and derivatives, and

```shell
apt-cache search monitoring-plugins-igwn*
```

for Debian.
