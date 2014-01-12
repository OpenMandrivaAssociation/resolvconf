Summary:	Nameserver information handler
Name:		resolvconf
Version:	1.72
Release:	4
Source0:	ftp://ftp.debian.org/debian/pool/main/r/resolvconf/%{name}_%{version}.tar.gz
Source1:	list-by-metric
Source2:	resolvconf.init
Source3:	%{name}-tmpfiles.conf

# allow /run/resolvconf/resolv.conf to be a symlink
Patch1:		resolvconf-1.68-symlink.patch
Patch2:		resolvconf-1.68-metric.patch
# use same level for eth* ath* wlan* ppp*, to sort them by metric
Patch3:		resolvconf-1.72-remove-interface-order.patch
License:	GPLv2+
Group:		Networking/Other
Url:		http://packages.debian.org/unstable/net/resolvconf
BuildArch:	noarch
Conflicts:	initscripts < 8.48-3mdv2007.1
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
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
%patch1 -p1 -b .symlink
%patch2 -p1 -b .metric
%patch3 -p1 -b .mdvorder

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

install -d %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

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


%post
systemd-tmpfiles --create %{name}.conf
%_post_service %{name}

%preun
%_preun_service %{name}

%files
%doc README COPYING
/sbin/%{name}
/lib/%{name}
%{_prefix}/lib/tmpfiles.d/*.conf
%{_initrddir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/run
%config(noreplace) %{_sysconfdir}/%{name}/interface-order
%dir %{_sysconfdir}/%{name}/resolv.conf.d
%config(noreplace) %{_sysconfdir}/%{name}/resolv.conf.d/*
%dir %{_sysconfdir}/%{name}/update.d
%{_sysconfdir}/%{name}/update.d/*
#dir %{_sysconfdir}/%{name}/update-libc.d
%{_mandir}/man?/*

%changelog
* Mon Feb 20 2012 abf
- The release updated by ABF

* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 1.46-2mdv2011.0
+ Revision: 669419
- mass rebuild

* Sun Aug 15 2010 Emmanuel Andry <eandry@mandriva.org> 1.46-1mdv2011.0
+ Revision: 570147
- New version 1.46
- fix license

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.45-3mdv2010.1
+ Revision: 523919
- rebuilt for 2010.1

* Wed Sep 23 2009 Eugeni Dodonov <eugeni@mandriva.com> 1.45-2mdv2010.0
+ Revision: 447844
- Update resolvconf init script priority when upgrading (#43654).

* Wed Aug 19 2009 Frederik Himpe <fhimpe@mandriva.org> 1.45-1mdv2010.0
+ Revision: 418252
- Update to new version 1.45
- Rediff mdvorder patch

* Tue Aug 18 2009 Colin Guthrie <cguthrie@mandriva.org> 1.41-5mdv2010.0
+ Revision: 417828
- Fix some errors relating to restarting nscd

* Mon Aug 10 2009 Eugeni Dodonov <eugeni@mandriva.com> 1.41-4mdv2010.0
+ Revision: 414305
- Add standard chkconfig header to init script to prevent possible loops in prcsys.
  Use absolute path for resolv.conf (#49146).

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 1.41-3mdv2009.1
+ Revision: 351568
- rebuild

* Tue Aug 19 2008 Olivier Blin <oblin@mandriva.com> 1.41-2mdv2009.0
+ Revision: 273656
- require rpm-helper for post/preun (#40193)

* Tue Aug 05 2008 Olivier Blin <oblin@mandriva.com> 1.41-1mdv2009.0
+ Revision: 263872
- force creation of /var/run/resolvconf/resolv.conf at init since rc.sysinit removes it now
- rediff symlink patch
- 1.41

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 1.38-5mdv2009.0
+ Revision: 225318
- rebuild

* Fri Mar 14 2008 Olivier Blin <oblin@mandriva.com> 1.38-4mdv2008.1
+ Revision: 187994
- use same level for eth* ath* wlan* ppp*, to sort them by metric
- update metric patch to sort by metric each interface-order line individually
- update list-by-metric to sort arguments only if specified

* Fri Mar 14 2008 Olivier Blin <oblin@mandriva.com> 1.38-3mdv2008.1
+ Revision: 187814
- update list-by-metric to better handle routes with null metric or with link scope (#33256)
- restore BuildRoot

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuild

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - new version

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Jul 06 2007 Olivier Blin <oblin@mandriva.com> 1.37-8mdv2008.0
+ Revision: 49156
- start in runlevel 2 as well (thanks to Goetz Waschk)

* Fri May 04 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.37-7mdv2008.0
+ Revision: 22504
- oops, /var/run/resolvconf/interface got excluded, include it!

* Fri May 04 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.37-6mdv2008.0
+ Revision: 22184
- fix file inclusion

* Mon Apr 23 2007 Olivier Blin <oblin@mandriva.com> 1.37-5mdv2008.0
+ Revision: 17509
- use subsys lock files not to be restarted when changing runlevels (thanks to fcrozat for the report)


* Mon Mar 19 2007 Olivier Blin <oblin@mandriva.com> 1.37-4mdv2007.1
+ Revision: 146573
- migrate resolv.conf to /etc/resolvconf/resolv.conf.d/tail on upgrades (#27947)
- package /etc/resolvconf/resolv.conf.d/tail
- mark config files as noreplace

* Wed Jan 03 2007 Olivier Blin <oblin@mandriva.com> 1.37-3mdv2007.1
+ Revision: 103610
- do not package russian man pages, they are not in sync
- update interface-order.5 and resolvconf.8 man page about metric usage
- update resolvconf.8 man page for Mandriva and merge REPORT_ABSENT_SYMLINK fix in patch
- keep patch backup files in build tree, remove them in buildroot only
- do not package patch backup files (#27913)

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - add doc files

* Tue Jan 02 2007 Olivier Blin <oblin@mandriva.com> 1.37-1mdv2007.1
+ Revision: 103267
- 1.37
- add initscript (partly based on Debian's initscript)

* Thu Dec 21 2006 Olivier Blin <oblin@mandriva.com> 1.36-1mdv2007.1
+ Revision: 100884
- sort interface records by the related interface metric
- make /var/run/resolvconf/resolv.conf a symlink to /etc/resolv.conf
- more path fixes
- make the package noarch
- enable resolvconf updates by default (by touching /var/run/%%{name}/enable-updates)
- fix path for run-parts
- initial resolvconf package
- Create resolvconf

