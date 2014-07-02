Summary:	Nameserver information handler
Name:		resolvconf
Version:	1.74
Release:	7
License:	GPLv2+
Group:		Networking/Other
Url:		http://packages.debian.org/unstable/net/resolvconf
Source0:	ftp://ftp.debian.org/debian/pool/main/r/resolvconf/%{name}_%{version}.tar.gz
Source1:	list-by-metric
Source2:	resolvconf.service
Source3:	%{name}-tmpfiles.conf

# allow /run/resolvconf/resolv.conf to be a symlink
Patch1:		resolvconf-1.68-symlink.patch
Patch2:		resolvconf-1.68-metric.patch
# use same level for eth* ath* wlan* ppp*, to sort them by metric
Patch3:		resolvconf-1.72-remove-interface-order.patch
BuildArch:	noarch
Requires(post):	systemd

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
%apply_patches

%build
# fix path for run-parts
for i in ./bin/resolvconf ./etc/resolvconf/update.d/libc; do
sed -i -e 's#PATH=.*#PATH=/sbin:/bin:/usr/bin#' $i;
done

%install
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
ln -s /run/%{name} %{buildroot}%{_sysconfdir}/%{name}/run

install -d %{buildroot}%{_unitdir}
install -m 755 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service

# install tmpfiles
install -D -p -m0644 %{SOURCE3} %{buildroot}%{_prefix}/lib/tmpfiles.d/%{name}.conf

install -d %{buildroot}%{_mandir}/man{5,8}
install -m 644 man/interface-order.5 %{buildroot}%{_mandir}/man5
install -m 644 man/resolvconf.8 %{buildroot}%{_mandir}/man8

%triggerpostun -- resolvconf == 1.69-1
# tranform resolv.conf from a symlink back to a file
    if [ -L /etc/resolv.conf ] && [ "$(readlink /etc/resolv.conf)" = "/run/resolvconf/resolv.conf" ]; then
    rm -f /etc/resolv.conf
    mv /run/resolvconf/resolv.conf /etc/resolv.conf
fi

%files
%doc README
/sbin/%{name}
/lib/%{name}
%{_prefix}/lib/tmpfiles.d/*.conf
%{_unitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/run
%config(noreplace) %{_sysconfdir}/%{name}/interface-order
%dir %{_sysconfdir}/%{name}/resolv.conf.d
%config(noreplace) %{_sysconfdir}/%{name}/resolv.conf.d/*
%dir %{_sysconfdir}/%{name}/update.d
%{_sysconfdir}/%{name}/update.d/*
#dir %{_sysconfdir}/%{name}/update-libc.d
%{_mandir}/man?/*

