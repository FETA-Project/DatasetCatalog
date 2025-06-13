%define version %(grep -E '^VERSION =' app.py | cut -d'"' -f2)

Name: katoda
Summary: Dataset Catalog.
Version: %{version}
Release: 1%{?dist}
URL: http://www.liberouter.org/
Source: https://github.com/FETA-Project/DatasetCatalog/%{name}-%{version}.tar.gz
Group: Liberouter
License: BSD
Vendor: CESNET, z.s.p.o.
Packager: David Benes <benesdavid@cesnet.cz>
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}
BuildRequires: python3.11
Requires: python3.11, git
Autoreq: no
Provides: katoda

%description
This package contains the katoda dataset catalog.

%prep
%setup

%build

%install
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/katoda
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/katoda
mkdir -p $RPM_BUILD_ROOT/%{_prefix}/lib/systemd/system
mkdir -p $RPM_BUILD_ROOT/opt/katoda/venv

cp -r *.py $RPM_BUILD_ROOT/opt/katoda/
cp analysis_example.toml $RPM_BUILD_ROOT/opt/katoda/
cp -r static/ $RPM_BUILD_ROOT/opt/katoda/
chmod +x $RPM_BUILD_ROOT/opt/katoda/app.py
cp requirements.txt $RPM_BUILD_ROOT/%{_datadir}/katoda/requirements.txt
cp config.env.example $RPM_BUILD_ROOT/%{_sysconfdir}/katoda/config.env.example
cp katoda.service $RPM_BUILD_ROOT/%{_prefix}/lib/systemd/system

%post
systemctl daemon-reload

%postun
rm -rf /opt/katoda/venv

%posttrans
/usr/bin/python3.11 -m venv /opt/katoda/venv
source /opt/katoda/venv/bin/activate; pip install -r %{_datadir}/katoda/requirements.txt
echo "Config file can be found at: " %{_sysconfdir}/katoda

%files
%{_prefix}/lib/systemd/system/katoda.service
%dir /opt/katoda
/opt/katoda/*.py
/opt/katoda/analysis_example.toml
/opt/katoda/static
%{_datadir}/katoda
%{_sysconfdir}/katoda/config.env.example %config(noreplace)
