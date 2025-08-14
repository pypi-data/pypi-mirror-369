%global srcname igwn-monitor
%global distname %{lua:name = string.gsub(rpm.expand("%{srcname}"), "[.-]", "_"); print(name)}
%global pkgname nagios-plugins-igwn
%global version 1.3.1
%global release 1
%global _plugindir %{_libdir}/nagios/plugins

# this build doesn't have a debug package
%global debug_package %{nil}

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   Nagios (Icinga) monitoring plugins for IGWN

License:   MIT
Url:       https://git.ligo.org/computing/monitoring/igwn-monitoring-plugins
Source0:   %pypi_source %distname

Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>

Prefix:    %{_prefix}

BuildRequires: python3-devel
BuildRequires: python3dist(pip)
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(setuptools-scm)
BuildRequires: python3dist(wheel)

%description
The igwn-monitoring-plugins project defines a Python library and set of
dependent monitoring plugin scripts developed for the International
Gravitational-Wave Observatory Network (IGWN).

# -- packages

# python3-igwn-monitor
%package -n python3-igwn-monitor
Summary: Python library for IGWN monitoring plugins
BuildArch: noarch
Requires: python3dist(ciecplib)
Requires: python3dist(gpstime)
Requires: python3dist(gssapi)
Requires: python3dist(igwn-auth-utils) >= 1.0.0
%if 0%{?rhel} != 0 && 0%{?rhel} < 9
Requires: python3dist(importlib-metadata)
%endif
Requires: python3dist(requests)
Requires: python3dist(requests-gssapi) >= 1.2.2
%description -n python3-igwn-monitor
The igwn-monitor library provides Python routines to support
custom Nagios (Icinga) monitoring plugins for IGWN.
%files -n python3-igwn-monitor
%doc README.md
%license LICENSE
%{python3_sitelib}/*

# nagios-plugins-igwn metapackage
%package -n %{pkgname}
Summary: Nagios (Icinga) monitoring plugins for IGWN (metapackage)
BuildArch: noarch
Requires: %{pkgname}-common = %{version}-%{release}
Requires: %{pkgname}-cvmfs = %{version}-%{release}
Requires: %{pkgname}-dqsegdb = %{version}-%{release}
Requires: %{pkgname}-docdb = %{version}-%{release}
%if 0%{?rhel} && 0%{?rhel} < 9
Requires: %{pkgname}-gds = %{version}-%{release}
%endif
Requires: %{pkgname}-gitlab = %{version}-%{release}
Requires: %{pkgname}-gracedb = %{version}-%{release}
Requires: %{pkgname}-grafana = %{version}-%{release}
Requires: %{pkgname}-gwdatafind = %{version}-%{release}
Requires: %{pkgname}-gwosc = %{version}-%{release}
Requires: %{pkgname}-htcondor = %{version}-%{release}
Requires: %{pkgname}-json = %{version}-%{release}
Requires: %{pkgname}-kerberos = %{version}-%{release}
Requires: %{pkgname}-koji = %{version}-%{release}
Requires: %{pkgname}-mattermost = %{version}-%{release}
%if 0%{?rhel} && 0%{?rhel} < 9
Requires: %{pkgname}-nds = %{version}-%{release}
%endif
Requires: %{pkgname}-pelican = %{version}-%{release}
Requires: %{pkgname}-scitoken = %{version}-%{release}
Requires: %{pkgname}-vault = %{version}-%{release}
Requires: %{pkgname}-xrootd = %{version}-%{release}
%description -n %{pkgname}
Extra Nagios (Icinga) monitoring plugins for IGWN.
This metapackage installs all of the IGWN monitoring plugins.
%files -n %{pkgname}
%doc README.md
%license LICENSE

# nagios-plugins-igwn-common
%package -n %{pkgname}-common
Requires: nagios-plugins
Requires: python3dist(gwdatafind)
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) common monitoring plugins
%description -n %{pkgname}-common
Common Nagios (Icinga) monitoring plugins for IGWN.
%files -n %{pkgname}-common
%doc README.md
%license LICENSE
%{_plugindir}/check_command
%{_plugindir}/check_file_latency
%{_plugindir}/check_nmap
%{_plugindir}/check_rsync
%{_plugindir}/check_url

# nagios-plugins-igwn-cvmfs
%package -n %{pkgname}-cvmfs
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Requires: python3dist(requests)
Summary: IGWN Nagios (Icinga) monitoring plugins for CVMFS
%description -n %{pkgname}-cvmfs
Nagios (Icinga) monitoring plugins to check CVMFS.
%files -n %{pkgname}-cvmfs
%doc README.md
%license LICENSE
%{_plugindir}/check_cvmfs*

# nagios-plugins-igwn-docdb
%package -n %{pkgname}-docdb
Requires: nagios-plugins
Requires: python3dist(beautifulsoup4)
Requires: python3-%{srcname} = %{version}-%{release}
Requires: python3dist(requests)
Summary: IGWN Nagios (Icinga) monitoring plugins for DocDB
%description -n %{pkgname}-docdb
Nagios (Icinga) monitoring plugins to check a DocDB instance.
%files -n %{pkgname}-docdb
%doc README.md
%license LICENSE
%{_plugindir}/check_docdb*

# nagios-plugins-igwn-dqsegdb
%package -n %{pkgname}-dqsegdb
Requires: nagios-plugins
Requires: python3dist(dqsegdb2) >= 1.2.1
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for DQSegDB
%description -n %{pkgname}-dqsegdb
Nagios (Icinga) monitoring plugins to check a DQSegDB server.
%files -n %{pkgname}-dqsegdb
%doc README.md
%license LICENSE
%{_plugindir}/check_dqsegdb*

# nagios-plugins-igwn-gds
%if 0%{?rhel} && 0%{?rhel} < 9
%package -n %{pkgname}-gds
Requires: gds-lsmp
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GDS
%description -n %{pkgname}-gds
Nagios (Icinga) monitoring plugins to check a GDS
%files -n %{pkgname}-gds
%doc README.md
%license LICENSE
%{_plugindir}/check_partitions
%endif

# nagios-plugins-igwn-gitlab
%package -n %{pkgname}-gitlab
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GitLab
%description -n %{pkgname}-gitlab
Nagios (Icinga) monitoring plugins to check a GitLab
%files -n %{pkgname}-gitlab
%doc README.md
%license LICENSE
%{_plugindir}/check_gitlab*

# nagios-plugins-igwn-gracedb
%package -n %{pkgname}-gracedb
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GraCEDB
%description -n %{pkgname}-gracedb
Nagios (Icinga) monitoring plugins to check a GraCEDB server.
%files -n %{pkgname}-gracedb
%doc README.md
%license LICENSE
%{_plugindir}/check_gracedb*

# nagios-plugins-igwn-grafana
%package -n %{pkgname}-grafana
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Grafana
%description -n %{pkgname}-grafana
Nagios (Icinga) monitoring plugins to check a Grafana server.
%files -n %{pkgname}-grafana
%doc README.md
%license LICENSE
%{_plugindir}/check_grafana*

# nagios-plugins-igwn-gwdatafind
%package -n %{pkgname}-gwdatafind
Requires: nagios-plugins
Requires: python3dist(dqsegdb2) >= 1.2.1
Requires: python3dist(gwdatafind) >= 2.1
Requires: python3dist(igwn-segments)
Requires: python3-%{srcname} = %{version}-%{release}
Requires: %{pkgname}-common = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GWDataFind
%description -n %{pkgname}-gwdatafind
Nagios (Icinga) monitoring plugins to check a GWDataFind server.
%files -n %{pkgname}-gwdatafind
%doc README.md
%license LICENSE
%{_plugindir}/check_data_availability*
%{_plugindir}/check_gwdatafind*

# nagios-plugins-igwn-gwosc
%package -n %{pkgname}-gwosc
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GWOSC
%description -n %{pkgname}-gwosc
Nagios (Icinga) monitoring plugins to check a GWOSC server.
%files -n %{pkgname}-gwosc
%doc README.md
%license LICENSE
%{_plugindir}/check_gwosc*

# nagios-plugins-igwn-htcondor
%package -n %{pkgname}-htcondor
Summary: IGWN Nagios (Icinga) monitoring plugins to check an HTCondor Pool
Requires: nagios-plugins
Requires: python3-condor
Requires: python3-%{srcname} = %{version}-%{release}
%description -n %{pkgname}-htcondor
Nagios (Icinga) monitoring plugin to check the status of an HTCondor Pool.
%files -n %{pkgname}-htcondor
%doc README.md
%license LICENSE
%{_plugindir}/check_htcondor*

# nagios-plugins-igwn-json
%package -n %{pkgname}-json
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
%if 0%{?rhel} != 0 && 0%{?rhel} < 9
Requires: python3dist(importlib-resources)
%endif
Requires: python3dist(jsonschema)
Summary: IGWN Nagios (Icinga) monitoring plugin to parse JSON
%description -n %{pkgname}-json
Nagios (Icinga) monitoring plugins to parse remote JSON output
and format as a monitoring plugin.
%files -n %{pkgname}-json
%doc README.md
%license LICENSE
%{_plugindir}/check_json

# nagios-plugins-igwn-kerberos
%package -n %{pkgname}-kerberos
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Requires: python3dist(ldap3)
Summary: IGWN Nagios (Icinga) monitoring plugins for Kerberos
%description -n %{pkgname}-kerberos
Nagios (Icinga) monitoring plugins for Kerberos.
%files -n %{pkgname}-kerberos
%doc README.md
%license LICENSE
%{_plugindir}/check_kdc*
%{_plugindir}/check_kerberos*

# nagios-plugins-igwn-koji
%package -n %{pkgname}-koji
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Koji
%description -n %{pkgname}-koji
Nagios (Icinga) monitoring plugins to check a Koji server.
%files -n %{pkgname}-koji
%doc README.md
%license LICENSE
%{_plugindir}/check_koji*

# nagios-plugins-igwn-mattermost
%package -n %{pkgname}-mattermost
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Mattermost
%description -n %{pkgname}-mattermost
Nagios (Icinga) monitoring plugins to check a Mattermost server.
%files -n %{pkgname}-mattermost
%doc README.md
%license LICENSE
%{_plugindir}/check_mattermost*

# nagios-plugins-igwn-nds
%if 0%{?rhel} && 0%{?rhel} < 9
%package -n %{pkgname}-nds
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
# https://git.ligo.org/nds/nds2-client/-/issues/166
Requires: nds2-client
Requires: python3-nds2-client
Summary: IGWN Nagios (Icinga) monitoring plugins for NDS
%description -n %{pkgname}-nds
Nagios (Icinga) monitoring plugins to check an NDS(2) server.
%files -n %{pkgname}-nds
%doc README.md
%license LICENSE
%{_plugindir}/check_nds*
%endif

# nagios-plugins-igwn-pelican
%package -n %{pkgname}-pelican
Requires: nagios-plugins
Requires: pelican
Requires: python3-%{srcname} = %{version}-%{release}
Requires: %{pkgname}-common = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Pelican
%description -n %{pkgname}-pelican
Nagios (Icinga) monitoring plugins to check a Pelican federation.
%files -n %{pkgname}-pelican
%doc README.md
%license LICENSE
%{_plugindir}/check_pelican*

# nagios-plugins-igwn-scitoken
%package -n %{pkgname}-scitoken
Summary: IGWN Nagios (Icinga) monitoring plugins to check tokens
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Requires: python3dist(python-dateutil)
Requires: python3dist(scitokens)
%description -n %{pkgname}-scitoken
Nagios (Icinga) monitoring plugin to check for a SciToken and validate
its claims (aud, scope, and exp).
%files -n %{pkgname}-scitoken
%doc README.md
%license LICENSE
%{_plugindir}/check_gettoken
%{_plugindir}/check_scitoken*
%{_plugindir}/check_vault_token

# nagios-plugins-igwn-vault
%package -n %{pkgname}-vault
Summary: IGWN Nagios (Icinga) plugin to check a Hashicorp Vault
Requires: nagios-plugins
Requires: python3
Requires: python3dist(requests)
%description -n %{pkgname}-vault
Nagios (Icinga) monitoring plugin to check a Hashicorp Vault instance.
%files -n %{pkgname}-vault
%doc README.md
%license LICENSE
%{_plugindir}/check_vault

# nagios-plugins-igwn-xrootd
%package -n %{pkgname}-xrootd
Requires: nagios-plugins
Requires: python3-%{srcname} = %{version}-%{release}
Requires: python3dist(xrootd)
Requires: %{pkgname}-common = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for XRootD
%description -n %{pkgname}-xrootd
Nagios (Icinga) monitoring plugins to check a XRootD server.
%files -n %{pkgname}-xrootd
%doc README.md
%license LICENSE
%{_plugindir}/check_xrd*
%{_plugindir}/check_xrootd*

# -- build steps

%prep
%autosetup -n %{distname}-%{version}
# for RHEL < 9 hack together setup.{cfg,py} for old setuptools
%if 0%{?rhel} && 0%{?rhel} < 10
cat > setup.cfg << SETUP_CFG
[metadata]
name = %{srcname}
version = %{version}
author-email = %{packager}
description = %{summary}
license = %{license}
license_files = LICENSE
url = %{url}
[options]
packages = find:
python_requires = >=3.6
install_requires =
  ciecplib
  gssapi
  igwn-auth-utils >= 1.0.0
  importlib-metadata ; python_version < "3.7"
  requests
  requests-gssapi >= 1.2.2
[options.entry_points]
console_scripts =
  check_command = igwn_monitor.plugins.check_command:main
  check_cvmfs_age = igwn_monitor.plugins.check_cvmfs_age:main
  check_data_availability = igwn_monitor.plugins.check_data_availability:main
  check_docdb = igwn_monitor.plugins.check_docdb:main
  check_dqsegdb_latency = igwn_monitor.plugins.check_dqsegdb_latency:main
  check_dqsegdb = igwn_monitor.plugins.check_dqsegdb:main
  check_file_latency = igwn_monitor.plugins.check_file_latency:main
  check_gettoken = igwn_monitor.plugins.check_gettoken:main
  check_gitlab = igwn_monitor.plugins.check_gitlab:main
  check_gracedb = igwn_monitor.plugins.check_gracedb:main
  check_grafana = igwn_monitor.plugins.check_grafana:main
  check_gwdatafind_latency = igwn_monitor.plugins.check_gwdatafind_latency:main
  check_gwdatafind = igwn_monitor.plugins.check_gwdatafind:main
  check_gwosc = igwn_monitor.plugins.check_gwosc:main
  check_htcondor = igwn_monitor.plugins.check_htcondor:main
  check_json = igwn_monitor.plugins.check_json:main
  check_kdc = igwn_monitor.plugins.check_kdc:main
  check_kerberos_principal_expiry = igwn_monitor.plugins.check_kerberos_principal_expiry:main
  check_koji = igwn_monitor.plugins.check_koji:main
  check_mattermost = igwn_monitor.plugins.check_mattermost:main
%if 0%{?rhel} && 0%{?rhel} < 9
  check_nds2 = igwn_monitor.plugins.check_nds2:main
%endif
  check_nmap = igwn_monitor.plugins.check_nmap:main
%if 0%{?rhel} && 0%{?rhel} < 9
  check_partitions = igwn_monitor.plugins.check_partitions:main
%endif
  check_pelican_latency = igwn_monitor.plugins.check_pelican_latency:main
  check_rsync = igwn_monitor.plugins.check_rsync:main
  check_scitoken_issuer = igwn_monitor.plugins.check_scitoken_issuer:main
  check_scitoken = igwn_monitor.plugins.check_scitoken:main
  check_url = igwn_monitor.plugins.check_url:main
  check_vault = igwn_monitor.plugins.check_vault:main
  check_vault_token = igwn_monitor.plugins.check_vault_token:main
  check_xrdcp = igwn_monitor.plugins.check_xrdcp:main
  check_xrootd_latency = igwn_monitor.plugins.check_xrootd_latency:main
  check_xrootd_ping = igwn_monitor.plugins.check_xrootd_ping:main
[options.package_data]
igwn_monitor.plugins = *.json
SETUP_CFG
%endif

%if %{undefined pyproject_wheel}
cat > setup.py << SETUP_PY
from setuptools import setup
setup()
SETUP_PY
%endif

%build
%if %{defined pyproject_wheel}
%pyproject_wheel
%else
%py3_build_wheel
%endif

%install
# install the wheel as normal
%if %{defined pyproject_install}
%pyproject_install
%else
%py3_install_wheel *.whl
%endif
# then relocate all of the entry point scripts
mkdir -p %{buildroot}%{_plugindir}/
mv -v \
  %{buildroot}%{_bindir}/check_* \
  %{buildroot}%{_plugindir}/

# -- changelog

%changelog
* Wed Aug 13 2025 Duncan Macleod <duncan.macleod@ligo.org> - 1.3.1-1
- Update to 1.3.1
- Add minimum version requirement for python3-gwdatafind
- Add missing common requirement for nagios-plugins-igwn-pelican

* Tue Apr 29 2025 Duncan Macleod <duncan.macleod@ligo.org> - 1.3.0-1
- Update to 1.3.0
- Rename source RPM to match upstream source dist
- Update Python macros for EL8+
- Add support for EL9 (without -gds package)
- Add nagios-plugins-igwn-pelicanb package
- Use pyproject macros for build, and hack setup.cfg for older distributions

* Wed Feb 7 2024 Duncan Macleod <duncan.macleod@ligo.org> - 1.2.1-1
- update to 1.2.1

* Wed Feb 7 2024 Duncan Macleod <duncan.macleod@ligo.org> - 1.2.0-1
- update to 1.2.0
- add python3-pip build requirement

* Fri Jan 26 2024 Duncan Macleod <duncan.macleod@ligo.org> - 1.1.0-1
- nagios-plugins-igwn-gds: new subpackage
- nagios-plugins-igwn-kerberos: add ldap3 requirement and bundle check_kerberos* plugins
- nagios-plugins-igwn-scitoken: add dateutil and tz requirements

* Tue Nov 28 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.1-2
- add requirements on 'common' for gwdatafind and xrootd packages

* Tue Sep 26 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.1-1
- update to 1.0.1
- add metapackage requirement on nagios-plugins-igwn-kerberos

* Thu Aug 31 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.0-1
- first packaged release of this project
