%define name resolvconf
%define version 1.41

Summary: Nameserver information handler
Name: %{name}
Version: %{version}
Release: %mkrel 3
Source0: ftp://ftp.debian.org/debian/pool/main/r/resolvconf/%{name}_%{version}.tar.gz
Source1: list-by-metric
Source2: resolvconf.init
# fix path for run-parts
Patch0: resolvconf-1.36-path.patch
# allow /var/run/resolvconf/resolv.conf to be a symlink
Patch1: resolvconf-1.41-symlink.patch
Patch2: resolvconf-1.38-metric.patch
# use same level for eth* ath* wlan* ppp*, to sort them by metric
Patch3: resolvconf-1.38-mdvorder.patch
License: GPL
Group: Networking/Other
Url: http://packages.debian.org/unstable/net/resolvconf
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Conflicts: initscripts < 8.48-3mdv2007.1
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description
Resolvconf is a framework for keeping track of the system's
information about currently available nameservers. It sets itself up
as the intermediary between programs that supply nameserver
information and programs that use nameserver information. Examples of
programs that supply nameserver information are: ifupdown, DHCP
clients, the PPP daemon and local nameservers. Examples of programs
that use this information are: DNS caches, resolver libraries and the
programs that use them.

%prep
%setup -q
%patch0 -p1 -b .path
%patch1 -p1 -b .symlink
%patch2 -p1 -b .metric
%patch3 -p1 -b .mdvorder

%build

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}
cp -a etc/%{name} %{buildroot}%{_sysconfdir}
# remove patch backup files
rm -f %{buildroot}%{_sysconfdir}/%{name}/interface-order.*
rm -f %{buildroot}%{_sysconfdir}/%{name}/update.d/*.*

touch %{buildroot}%{_sysconfdir}/%{name}/resolv.conf.d/tail

install -d %{buildroot}/sbin
install bin/%{name} %{buildroot}/sbin
install -d %{buildroot}/lib/%{name}
install bin/list-records %{buildroot}/lib/%{name}
install -m 755 %{SOURCE1} %{buildroot}/lib/%{name}/list-by-metric
install -d %{buildroot}/var/run/%{name}/interface
ln -s ../../var/run/%{name} %{buildroot}%{_sysconfdir}/%{name}/run
ln -sf ../../../etc/resolv.conf %{buildroot}/var/run/resolvconf/resolv.conf
touch %{buildroot}/var/run/%{name}/enable-updates

install -d %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

install -d %{buildroot}%{_mandir}/man{5,8}
install -m 644 man/interface-order.5 %{buildroot}%{_mandir}/man5
install -m 644 man/resolvconf.8 %{buildroot}%{_mandir}/man8

%triggerpostun -- initscripts < 8.48-3mdv2007.1
cp -a %{_sysconfdir}/resolv.conf %{_sysconfdir}/%{name}/resolv.conf.d/tail

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README COPYING
/sbin/%{name}
/lib/%{name}
%{_initrddir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/run
%config(noreplace) %{_sysconfdir}/%{name}/interface-order
%dir %{_sysconfdir}/%{name}/resolv.conf.d
%config(noreplace) %{_sysconfdir}/%{name}/resolv.conf.d/*
%dir %{_sysconfdir}/%{name}/update.d
%config(noreplace) %{_sysconfdir}/%{name}/update.d/*
%dir %{_sysconfdir}/%{name}/update-libc.d
%{_mandir}/man?/*
%dir /var/run/%{name}
%dir /var/run/%{name}/interface
%config(noreplace) /var/run/%{name}/resolv.conf
%config(missingok,noreplace) /var/run/%{name}/enable-updates


