#Module-Specific definitions
%define mod_name1 mod_suphp
%define mod_name2 mod_suphp4
%define mod_conf1 A36_%{mod_name1}.conf
%define mod_conf2 A36_%{mod_name2}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_suphp is a DSO module for the apache web server
Name:		apache-%{mod_name1}
Version:	0.6.1
Release:	%mkrel 5
Group:		System/Servers
License:	GPL
URL:		http://www.suphp.org/
Source0: 	http://www.suphp.org/download/suphp-%{version}.tar.bz2
Source1:	%{mod_conf1}.bz2
Source2:	%{mod_conf2}.bz2
Source3:	suphp5.conf.bz2
Source4:	suphp4.conf.bz2
Patch0:		mod_suphp-0.6.1-userdir.patch
Patch1:		mod_suphp-0.6.1-AddHandler.patch
Patch2:		mod_suphp-0.6.1-apr.patch
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	automake1.7
Requires:	php-cgi
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
suPHP is a tool for executing PHP5 scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp) and a
setuid root binary (suphp) that is called by the Apache module to
change the uid of the process executing the PHP5 interpreter. 

This package provides support for php5 as of:

 o mod_suphp5.so uses the %{_bindir}/php-cgi binary
 o mod_suphp5_fcgi.so uses the %{_bindir}/php-fcgi binary

%package -n	apache-%{mod_name2}
Summary:	Mod_suphp is a DSO module for the apache web server
Group:		System/Servers
Requires:	php4-cgi
Epoch:		1

%description -n	apache-%{mod_name2}
suPHP is a tool for executing PHP4 scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp4) and a
setuid root binary (suphp4) that is called by the Apache module to
change the uid of the process executing the PHP4 interpreter. 

This package provides support for php4 as of:

 o mod_suphp4.so uses the %{_bindir}/php4-cgi binary

%prep

%setup -q -n suphp-%{version}
%patch0 -p 1 -b .userdir
%patch1 -p 1 -b .AddHandler
%patch2 -p 0 -b .apr

bzcat %{SOURCE1} > %{mod_conf1}
bzcat %{SOURCE2} > %{mod_conf2}
bzcat %{SOURCE3} > suphp5.conf
bzcat %{SOURCE4} > suphp4.conf

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
rm -f configure
libtoolize --copy --force
aclocal-1.7
automake-1.7 --add-missing --copy
autoconf

COMMON_CONFIGURE="--enable-checkpath \
    --enable-checkuid \
    --enable-checkgid \
    --with-apxs=%{_sbindir}/apxs \
    --with-setid-mode=owner \
    --with-min-uid=500 \
    --with-min-gid=500 \
    --with-apache-user=apache"

%configure2_5x \
    $COMMON_CONFIGURE \
    --with-php=%{_bindir}/php4-cgi \
    --with-logfile=/var/log/httpd/suphp4_log

cp src/apache2/mod_suphp.c src/apache2/mod_suphp4.c
perl -pi -e "s|suphp|suphp4|g" src/apache2/mod_suphp4.c 
perl -pi -e "s|suPHP|suPHP4|g" src/apache2/mod_suphp4.c 

pushd src/apache2
    %{_sbindir}/apxs \
    -I. \
    -DHAVE_CONFIG_H \
    -DSUPHP_PATH_TO_SUPHP=\\\"%{_sbindir}/suphp4\\\" \
    -c mod_suphp4.c
popd
cp src/apache2/.libs/mod_suphp4.so .

perl -pi -e "s|suphp\.conf|suphp4\.conf|g" src/Makefile
%make -C src suphp
cp src/suphp suphp4
make clean

%configure2_5x \
    $COMMON_CONFIGURE \
    --with-php=%{_bindir}/php-cgi \
    --with-logfile=/var/log/httpd/suphp5_log

cp src/apache2/mod_suphp.c src/apache2/mod_suphp5.c
perl -pi -e "s|suphp|suphp5|g" src/apache2/mod_suphp5.c 
perl -pi -e "s|suPHP|suPHP5|g" src/apache2/mod_suphp5.c 

pushd src/apache2
    %{_sbindir}/apxs \
    -I. \
    -DHAVE_CONFIG_H \
    -DSUPHP_PATH_TO_SUPHP=\\\"%{_sbindir}/suphp5\\\" \
    -c mod_suphp5.c
popd
cp src/apache2/.libs/mod_suphp5.so .

perl -pi -e "s|suphp\.conf|suphp5\.conf|g" src/Makefile
%make -C src suphp
cp src/suphp suphp5
make clean

%configure2_5x \
    $COMMON_CONFIGURE \
    --with-php=%{_bindir}/php-fcgi \
    --with-logfile=/var/log/httpd/suphp5_fcgi_log

cp src/apache2/mod_suphp.c src/apache2/mod_suphp5_fcgi.c
perl -pi -e "s|suphp|suphp5_fcgi|g" src/apache2/mod_suphp5_fcgi.c
perl -pi -e "s|suPHP|suPHP5_fcgi|g" src/apache2/mod_suphp5_fcgi.c

pushd src/apache2
    %{_sbindir}/apxs \
    -I. \
    -DHAVE_CONFIG_H \
    -DSUPHP_PATH_TO_SUPHP=\\\"%{_sbindir}/suphp5_fcgi\\\" \
    -c mod_suphp5_fcgi.c
popd
cp src/apache2/.libs/mod_suphp5_fcgi.so .

%make -C src suphp
cp src/suphp suphp5_fcgi
make clean

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 mod_suphp4.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 mod_suphp5.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 mod_suphp5_fcgi.so %{buildroot}%{_libdir}/apache-extramodules/

install -m0755 suphp4 %{buildroot}%{_sbindir}/suphp4
install -m0755 suphp5 %{buildroot}%{_sbindir}/suphp5
install -m0755 suphp5_fcgi %{buildroot}%{_sbindir}/suphp5_fcgi

install -m0644 %{mod_conf1} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf1}
install -m0644 %{mod_conf2} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf2}
install -m0644 suphp5.conf %{buildroot}%{_sysconfdir}/suphp5.conf
install -m0644 suphp4.conf %{buildroot}%{_sysconfdir}/suphp4.conf

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/apache-%{mod_name1} << EOF
/var/log/httpd/suphp5_log /var/log/httpd/suphp5_fcgi_log {
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

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/apache-%{mod_name2} << EOF
/var/log/httpd/suphp4_log {
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

This package provides ways to run php4 and php5 scripts under 
the uid and gid of the user owning the vhost using the CGI mode
oh php.

The documentation states it is possible to use suphp with the
mod_php DSO installed, but this is not recommended and beyond
the scope of this simple documentation.

You have three suphp DSO's to choose from, but you have to manually 
enable the ones you want to use in the %{_sysconfdir}/httpd/conf.d/%{mod_conf1}
file.

 o mod_suphp4.so uses the %{_bindir}/php4-cgi binary
 o mod_suphp5.so uses the %{_bindir}/php-cgi binary
 o mod_suphp5_fcgi.so uses the %{_bindir}/php-fcgi binary

In theory it should be possible to enable all three of them, but
it is not recommended.

Additionally you also have to install the nessesary php bits like so:

urpmi php-cgi

Or:

urpmi php-fcgi

Good luck!

Regards // Oden Eriksson
EOF

%post -n apache-%{mod_name1}
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun -n apache-%{mod_name1}
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%post -n apache-%{mod_name2}
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun -n apache-%{mod_name2}
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -n apache-%{mod_name1}
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog README REAME.MDK doc
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/suphp5.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/apache-%{mod_name1}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf1}
%attr(4755,root,root) %{_sbindir}/suphp5
%attr(4755,root,root) %{_sbindir}/suphp5_fcgi
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_suphp5.so
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_suphp5_fcgi.so

%files -n apache-%{mod_name2}
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog README REAME.MDK doc
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/suphp4.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/apache-%{mod_name2}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf2}
%attr(4755,root,root) %{_sbindir}/suphp4
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_suphp4.so


