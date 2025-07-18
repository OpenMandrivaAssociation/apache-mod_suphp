#Module-Specific definitions
%define mod_name mod_suphp
%define mod_conf A36_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	0.7.1
Release:	9
Group:		System/Servers
License:	GPL
URL:		https://www.suphp.org/
Source0: 	http://www.suphp.org/download/suphp-%{version}.tar.gz
Source1:	%{mod_conf}
Source2:	suphp.conf
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	automake
Requires:	php-cgi
Requires:	php-fcgi
Epoch:		1

%description
suPHP is a tool for executing PHP scripts with the permissions of their owners.
It consists of an Apache module (mod_suphp) and a setuid root binary (suphp)
that is called by the Apache module to change the uid of the process executing
the PHP interpreter.

This package provides support for php as of:

 o mod_suphp.so uses the %{_bindir}/php-cgi binary
 o mod_suphp_fcgi.so uses the %{_bindir}/php-fcgi binary

%prep

%setup -q -n suphp-%{version}

cp %{SOURCE1} %{mod_conf}
cp %{SOURCE2} suphp.conf

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
rm -f configure
libtoolize --copy --force
aclocal
automake --add-missing --copy
autoconf

COMMON_CONFIGURE="--enable-checkpath \
    --enable-checkuid \
    --enable-checkgid \
    --with-apxs=%{_bindir}/apxs \
    --with-apr=%{_bindir}/apr-1-config \
    --with-setid-mode=owner \
    --with-min-uid=500 \
    --with-min-gid=500 \
    --with-apache-user=apache"


%configure2_5x --localstatedir=/var/lib \
    $COMMON_CONFIGURE \
    --with-php=%{_bindir}/php-cgi \
    --with-logfile=/var/log/httpd/suphp_log

pushd src/apache2
    %{_bindir}/apxs \
    -I. \
    -DHAVE_CONFIG_H \
    -DSUPHP_PATH_TO_SUPHP=\\\"%{_sbindir}/suphp\\\" \
    -c mod_suphp.c
popd
cp src/apache2/.libs/mod_suphp.so .

%make -C src suphp
cp src/suphp suphp
make clean

%configure2_5x --localstatedir=/var/lib \
    $COMMON_CONFIGURE \
    --with-php=%{_bindir}/php-fcgi \
    --with-logfile=/var/log/httpd/suphp_fcgi_log

cp src/apache2/mod_suphp.c src/apache2/mod_suphp_fcgi.c
perl -pi -e "s|suphp|suphp_fcgi|g" src/apache2/mod_suphp_fcgi.c
perl -pi -e "s|suPHP|suPHP_fcgi|g" src/apache2/mod_suphp_fcgi.c

pushd src/apache2
    %{_bindir}/apxs \
    -I. \
    -DHAVE_CONFIG_H \
    -DSUPHP_PATH_TO_SUPHP=\\\"%{_sbindir}/suphp_fcgi\\\" \
    -c mod_suphp_fcgi.c
popd
cp src/apache2/.libs/mod_suphp_fcgi.so .

%make -C src suphp
cp src/suphp suphp_fcgi
make clean

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 mod_suphp.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 mod_suphp_fcgi.so %{buildroot}%{_libdir}/apache-extramodules/

install -m0755 suphp %{buildroot}%{_sbindir}/suphp
install -m0755 suphp_fcgi %{buildroot}%{_sbindir}/suphp_fcgi

install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}
install -m0644 suphp.conf %{buildroot}%{_sysconfdir}/suphp.conf

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/apache-%{mod_name} << EOF
/var/log/httpd/suphp_log /var/log/httpd/suphp_fcgi_log {
    size=2000M
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
    prerotate
	%{_initrddir}/httpd closelogs > /dev/null 2>&1
    endscript
    postrotate
	%{_initrddir}/httpd closelogs > /dev/null 2>&1
    endscript
}
EOF

cat > REAME.MDK << EOF
A P A C H E - M O D _ S U P H P
-------------------------------

This package provides ways to run php scripts under the uid and gid of the
user owning the vhost using the CGI mode oh php.

The documentation states it is possible to use suphp with the mod_php DSO
installed, but this is not recommended and beyond the scope of this simple
documentation.

You have three suphp DSO's to choose from, but you have to manually 
enable the ones you want to use in the %{_sysconfdir}/httpd/conf.d/%{mod_conf1}
file.

 o mod_suphp.so uses the %{_bindir}/php-cgi binary
 o mod_suphp_fcgi.so uses the %{_bindir}/php-fcgi binary

Additionally you also have to install the nessesary php bits like so:

urpmi php-cgi

Or:

urpmi php-fcgi

Good luck!

Regards // Oden Eriksson
EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog README REAME.MDK doc
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/suphp.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/apache-%{mod_name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(4755,root,root) %{_sbindir}/suphp
%attr(4755,root,root) %{_sbindir}/suphp_fcgi
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_suphp.so
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_suphp_fcgi.so


%changelog
* Sun Jun 10 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1:0.7.1-8
+ Revision: 804360
- Rebuild for apache 2.4.x

* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-7
+ Revision: 772770
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-6
+ Revision: 678424
- mass rebuild

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-5mdv2011.0
+ Revision: 627736
- don't force the usage of automake1.7

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-4mdv2011.0
+ Revision: 588070
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-3mdv2010.1
+ Revision: 516186
- rebuilt for apache-2.2.15

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-2mdv2010.0
+ Revision: 406658
- rebuild

* Sun Jun 21 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-1mdv2010.0
+ Revision: 387749
- 0.7.1
- nuke redundant patches

* Tue Jan 06 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.3-4mdv2009.1
+ Revision: 326263
- rebuild

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.3-3mdv2009.0
+ Revision: 235108
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.3-2mdv2009.0
+ Revision: 215647
- fix rebuild
- hard code %%{_localstatedir}/lib to ease backports

* Mon Mar 31 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.3-1mdv2009.0
+ Revision: 191190
- 0.6.3 (Major security fixes)
- rediffed P0,P1

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.2-3mdv2008.1
+ Revision: 181923
- rebuild

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 1:0.6.2-2mdv2008.1
+ Revision: 170752
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sun Oct 14 2007 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.2-1mdv2008.1
+ Revision: 98200
- 0.6.2

* Wed Oct 03 2007 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-6mdv2008.0
+ Revision: 94907
- remove the php4 hacks

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-5mdv2008.0
+ Revision: 82682
- rebuild


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 0.6.1-4mdv2007.1
+ Revision: 140760
- rebuild

* Thu Nov 09 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-3mdv2007.1
+ Revision: 79521
- Import apache-mod_suphp

* Sun Jul 16 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-3mdk
- add changes and patches from the package by Andreas Thienemann
- split the different modules for each php version into its own sub
  packages

* Sun Apr 16 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-2mdk
- fix build against apache-2.2.0 (P0)

* Thu Dec 01 2005 Oden Eriksson <oeriksson@mandriva.com> 1:0.6.1-1mdk
- 0.6.1 (Major bugfixes)

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 1:0.5.2-1mdk
- fix versioning

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_0.5.2-2mdk
- fix deps

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_0.5.2-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Mon Apr 04 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_0.5.2-1mdk
- initial package

