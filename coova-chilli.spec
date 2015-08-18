Summary:   Coova-Chilli is a Wireless LAN Access Point Controller
Name:      coova-chilli
Version:   1.3.1.3
Release:   2%{?dist}
URL:       http://coova.github.io/
Source0:   %{name}-%{version}.tar.gz
# These should be periodically refreshed upon rebuild with
# wget -O coova-chilli-uam-index.html http://ap.coova.org/uam/
# wget -O coova-chilli-uam-chilli.js http://ap.coova.org/js/chilli.js
#Source100: coova-chilli-uam-index.html
#Source101: coova-chilli-uam-chilli.js
#Source110: coova-chilli-httpd.conf
Patch100:  startup_script.patch
Patch110:  default_config.patch
Patch120:  up_script.patch
Patch130:  chilliController.patch
License:   GPL
Group:     System Environment/Daemons

%define chilli_uid    208
%define chilli_user   chilli
%define chilli_gid    208
%define chilli_group  chilli
%define chilli_dir    /usr/share/chilli
Requires(pre): /sbin/chkconfig, %{_sbindir}/groupadd, %{_sbindir}/useradd

Requires: httpd haserl

%if %{!?_without_ssl:1}0
BuildRequires: openssl-devel libtool gengetopt
%endif


%description

Coova-Chilli is a fork of the ChilliSpot project - an open source captive
portal or wireless LAN access point controller. It supports web based login
(Universal Access Method, or UAM), standard for public HotSpots, and it
supports Wireless Protected Access (WPA), the standard for secure roamable
networks. Authentication, Authorization and Accounting (AAA) is handled by
your favorite radius server. Read more at http://coova.github.io/.

%prep
%setup
%patch100 -p0
%patch110 -p0
%patch120 -p0
%patch130 -p0

%build
sh bootstrap
%configure \
    --disable-static \
    --enable-shared \
    --enable-largelimits \
    --enable-miniportal \
    --enable-chilliredir \
    --enable-chilliproxy \
    --enable-chilliscript \
    --with-poll \
    --enable-libjson \
    --enable-dhcpopt \
    --enable-gardenext \
    --enable-gardenaccounting \
    --enable-chillixml \
    --enable-proxyvsa \
    --enable-ipwhitelist \
    --enable-uamdomainfile \
    --enable-redirdnsreq \
    --enable-authedallowed \
    --enable-statusfile \
    --enable-multiroute \
    --enable-multilan \
    --enable-location \
%if %{!?_without_ssl:1}0
    --with-openssl \
    --enable-chilliradsec \
%endif

#--with-nfcoova \

make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT%{_prefix}/include/*
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
#cp -f chilli $RPM_BUILD_ROOT%{_sysconfdir}/init.d/chilli

# Place a default config file to be edited by the admin
cp -p $RPM_BUILD_ROOT%{_sysconfdir}/chilli/defaults $RPM_BUILD_ROOT%{_sysconfdir}/chilli/config
# throw away the initial comments telling to copy the defaults to config
perl -ni -e '1 .. /^\s*$/ and /^#/ or print' $RPM_BUILD_ROOT%{_sysconfdir}/chilli/config

mkdir -p $RPM_BUILD_ROOT/var/www/html/chilli
mv $RPM_BUILD_ROOT%{_sysconfdir}/chilli/www $RPM_BUILD_ROOT/var/www/html/chilli
ln -s /var/www/html/chilli/www $RPM_BUILD_ROOT%{_sysconfdir}/chilli/www

# uam/ and hotspotlogin.cgi seem not needed any more.
# mkdir -p $RPM_BUILD_ROOT%{_datadir}/chilli/uam
# cp %{SOURCE100} $RPM_BUILD_ROOT%{_datadir}/chilli/uam/index.html
# cp %{SOURCE101} $RPM_BUILD_ROOT%{_datadir}/chilli/uam/chilli.js
# perl -pi -e 's-ap.coova.org/js/chilli.js-10.1.0.1/uam/chilli.js-g' $RPM_BUILD_ROOT%{_datadir}/chilli/uam/index.html
# mkdir -p $RPM_BUILD_ROOT%{_datadir}/chilli/images
# cp $RPM_BUILD_ROOT%{_datadir}/chilli/coova.jpg $RPM_BUILD_ROOT%{_datadir}/chilli/images/
#
# mkdir -p $RPM_BUILD_ROOT%{_datadir}/chilli/cgi-bin
# cp doc/hotspotlogin.cgi $RPM_BUILD_ROOT%{_datadir}/chilli/cgi-bin/

#mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
#cp %{SOURCE110} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/chilli.conf

%check
rm -f $RPM_BUILD_ROOT%{_libdir}/python/*.pyc
rm -f $RPM_BUILD_ROOT%{_libdir}/python/*.pyo

%clean
rm -rf $RPM_BUILD_ROOT
make clean

%pre
%{_sbindir}/groupadd -g %{chilli_gid} -r %{chilli_group} 2>/dev/null
%{_sbindir}/useradd -d %{chilli_dir} -s /sbin/nologin -g %{chilli_group} -M -r -u %{chilli_uid} %{chilli_user} 2>/dev/null || :

%post
/sbin/chkconfig --add chilli
#/sbin/service httpd condrestart 2>&1 >/dev/null
/sbin/service chilli condrestart 2>&1 >/dev/null

%preun
if [ $1 = 0 ]; then
        /sbin/service chilli stop > /dev/null 2>&1
        /sbin/chkconfig --del chilli
fi

%files
%defattr(-,root,root)
%{_sbindir}/*
%{_libdir}/*.so*
%{_libdir}/python/CoovaChilliLib.py*
%{_sysconfdir}/init.d/chilli
#%{_sysconfdir}/httpd/conf.d/chilli.conf
%doc AUTHORS COPYING ChangeLog INSTALL README doc/dictionary.coovachilli doc/hotspotlogin.cgi
%config %{_sysconfdir}/chilli.conf
%config %{_sysconfdir}/chilli/gui-config-default.ini
%config %{_sysconfdir}/chilli/defaults
%config %{_sysconfdir}/chilli/config
%dir %{_sysconfdir}/chilli
%dir /var/www/html/chilli/www
%attr(755,root,root)/var/www/html/chilli/www/config.sh
%attr(4750,root,root)%{_sbindir}/chilli_script
%{_sysconfdir}/chilli/www
/var/www/html/chilli/www/*
%{_sysconfdir}/chilli/wwwsh
%{_sysconfdir}/chilli/functions
%{_sysconfdir}/chilli/*.sh
%{_sysconfdir}/chilli/wpad.dat
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*

%changelog
* Fri Jun 26 2015 Giovanni Bezicheri <giovanni.bezicheri@nethesis.it>
* Fix json encoding for radius reply.

* Tue May 13 2015 Giovanni Bezicheri <giovanni.bezicheri@nethesis.it>
* Add support for json uri.

* Fri Nov 14 2014 Giovanni Bezicheri <giovanni.bezicheri@nethesis.it>
- Add HS_LANIF_KEEPADDR option in chilli sysconfig.

* Thu Jul 10 2014 Giovanni Bezicheri <giovanni.bezicheri@nethesis.it>
- 1.3.1 release for NethServer. See ChangeLog.

* Sat Jan 2 2010 <david@coova.com>
- 1.2.0 release
* Thu Sep 30 2007 <david@coova.com>
- 1.0.8 release
* Thu Aug 20 2007 <david@coova.com>
- 1.0-coova.7 release
* Thu Jun 7 2007 <david@coova.com>
- 1.0-coova.6 release
* Wed May 16 2007  <david@coova.com>
- 1.0-coova.5 release
* Wed Feb 07 2007  <david@coova.com>
- 1.0-coova.4 release
* Wed Nov 15 2006  <david@coova.com>
- 1.0-coova.3 release
* Thu Mar 25 2004  <support@chillispot.org>
- Initial release.
