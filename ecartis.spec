%define		_snap	20020718
%define		_rel	1

Summary:	Ecartis Mailing List Manager
Summary(pl):	Zarz�dca List Dyskusyjnych
Name:		ecartis
Version:	1.0.0
Release:	%{_snap}.%{_rel}
License:	GPL
Vendor:		NodeRunner Software
Group:		Applications/Mail
Source0:	ftp://ftp.ecartis.org/pub/ecartis/snapshots/tar/%{name}-%{version}-snap%{_snap}.tar.gz
Source1:	%{name}.logrotate
#Original taken from: http://www.misiek.eu.org/ipv6/listar-0.129a-ipv6-20000915.patch.gz
Patch0:		%{name}-ipv6.patch
Patch1:		%{name}-conf.patch
URL:		http://www.ecartis.org/
Requires(pre):	%{_sbindir}/useradd
Requires(pre):	%{_sbindir}/groupadd
Requires(post):	/bin/hostname
Requires(postun):	%{_sbindir}/userdel
Requires(postun):	%{_sbindir}/groupdel
Provides:	listar
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	listar

%define		_ecartisdir	/usr/lib/ecartis
%define		_ecartisdata	/var/lib/ecartis

%description
Ecartis is a modular mailing list manager; all its functionality is
encapsulated in individual 'epm' (Ecartis Plugin Module) files. This
allows new commands and functionality to be added on the fly. Ecartis
has several useful features, including the ability to have 'flags' set
on user accounts (similar to L-soft Listserv), and a very secure
remote administration method over e-mail.

Errors to this package should be reported to bugs@ecartis.org or via
the web at http://bugs.ecartis.org/ecartis

NOTE: This package used to be named Listar, but has recently changed
name due to trademark issues.

%description -l pl
Ecartis jest modu�owym narz�dziem do zarz�dzania listami dyskusyjnymi.
Ca�a jego funkcjonalno�� zawiera si� w pojedynczych plikach 'epm'
(Ecartis Plugin Module), dzi�ki czemu mo�na w locie dodawa� nowe
polecenia i funkcjonalno��. Ecartis ma wiele przydatnych funkcji, np. 
mo�liwo�� ustawienia 'flag' na kontach u�ytkownik�w (podobnie jak w 
programie L-soft Listserv), i bardzo bezpieczn� metod� zdalnej administracji 
przy u�yciu poczty elektronicznej.

Informacje o b��dach w pakiecie nale�y wysy�a� na adres bugs@ecartis.org 
lub zg�asza� na stronie http://bugs.ecartis.org/ecartis.

UWAGA: Pakiet nazywa� si� kiedy� Listar, jednak nazwa zosta�a
zmieniona ze wzgl�du na problemy ze znakiem handlowym.

%package cgi
Summary:	Web interface for Ecartis
Summary(pl):	Web interfejs dla Ecartis
Group:		Applications/Mail
Requires:	%{name} = %{version}
Requires:	webserver
Obsoletes:	listar-cgi

%description cgi
ecartis-cgi program, which provides a web-based front-end for your
Ecartis mailing lists.

%description cgi -l pl
Program ecartis-cgi, kt�ry jest interfejsem web do menad�era Ecartis.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__make} -Csrc -fMakefile.dist WFLAGS="%{rpmcflags} -Wall"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{%{name},logrotate.d,cron.daily} \
	$RPM_BUILD_ROOT%{_ecartisdata}/{queue,lists/{test/text,SITEDATA/cookies}} \
	$RPM_BUILD_ROOT%{_ecartisdir}/{modules,scripts,templates} \
	$RPM_BUILD_ROOT{/home/httpd/cgi-bin/,/var/log}

%{__make} -Csrc -fMakefile.dist install

install %{name}	$RPM_BUILD_ROOT%{_ecartisdir}

install modules/*.lpm		$RPM_BUILD_ROOT%{_ecartisdir}/modules
install scripts/*		$RPM_BUILD_ROOT%{_ecartisdir}/scripts
install ecartis.cfg.dist	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/ecartis.cfg
install ecartis.hlp		$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/ecartis.hlp
install ecartis.aliases.dist	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/ecartis.aliases
install banned			$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/banned
install spam-regexp.sample	$RPM_BUILD_ROOT%{_ecartisdir}/spam-regexp.sample
install templates/*.lsc		$RPM_BUILD_ROOT%{_ecartisdir}/templates
install -D lists/test/text/*	$RPM_BUILD_ROOT%{_ecartisdata}/lists/test/text

install %{SOURCE1}		$RPM_BUILD_ROOT/etc/logrotate.d/%{name}

# Links for configuration:
ln -sf %{_sysconfdir}/%{name}/%{name}.cfg	$RPM_BUILD_ROOT%{_ecartisdir}/%{name}.cfg
ln -sf %{_sysconfdir}/%{name}/%{name}.aliases	$RPM_BUILD_ROOT%{_ecartisdir}/%{name}.aliases
ln -sf %{_sysconfdir}/%{name}/banned		$RPM_BUILD_ROOT%{_ecartisdir}/banned
ln -sf %{_sysconfdir}/%{name}/%{name}.hlp	$RPM_BUILD_ROOT%{_ecartisdir}/%{name}.hlp
touch	$RPM_BUILD_ROOT%{_var}/log/%{name}.log
touch	$RPM_BUILD_ROOT%{_ecartisdata}/lists/SITEDATA/cookies

cat << EOF > $RPM_BUILD_ROOT/home/httpd/cgi-bin/ecartisgate.cgi
#!/bin/sh
%{_ecartisdir}/%{name} -lsg2
EOF

cat << EOF > $RPM_BUILD_ROOT/etc/cron.daily/%{name}
%{_ecartisdir}/%{name} -procbounce
%{_ecartisdir}/%{name} -procdigest
EOF

# For compatibility with Listar:
ln -sf %{_ecartisdir}/%{name} $RPM_BUILD_ROOT%{_ecartisdir}/listar
ln -sf /home/httpd/cgi-bin/ecartisgate.cgi $RPM_BUILD_ROOT/home/httpd/cgi-bin/listargate.cgi

%pre
if [ -n "`getgid %{name}`" ]; then
	if [ "`getgid %{name}`" != "64" ]; then
		echo "Error: group %{name} doesn't have gid=64. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	echo "Adding group %{name} GID=64"
	/usr/sbin/groupadd -f -g 64 -r %{name}
fi

if [ -n "`id -u %{name} 2>/dev/null`" ]; then
	if [ "`id -u %{name}`" != "64" ]; then
		echo "Error: user %{name} doesn't have uid=64. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	echo "Adding user %{name} UID=64"
	/usr/sbin/useradd -u 64 -r -d %{_ecartisdir}  -s /bin/false -c "Ecartis User" -g %{name} %{name} 1>&2
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel	%{name}
	/usr/sbin/groupdel	%{name}
fi

%post
# alias:
umask 022
if [ -f /etc/mail/aliases ]; then
	if [ -e /etc/smrsh ]; then
		if ! grep -q "^%{name}:" /etc/mail/aliases; then
			echo "%{name}:  \"|/etc/smrsh/ecartis\"" >> /etc/mail/aliases
			newaliases || :
		fi
	else
		if ! grep -q "^%{name}:" /etc/mail/aliases; then
			echo "%{name}:  \"|%{_ecartisdir}/%{name}\"" >> /etc/mail/aliases
			newaliases || :
		fi
	fi
fi

# mailname:
if [ ! -f /etc/mail/mailname -a -d /etc/mail -a -x /bin/hostname ]; then
	hostname -f > /etc/mail/mailname
fi

# Detect SMRSH
if [ -e /etc/smrsh -a ! -e /etc/smrsh/ecartis ]; then
    echo "#!/bin/sh" > /etc/smrsh/ecartis
    echo "%{_ecartisdir}/ecartis \$@" >> /etc/smrsh/ecartis
    chmod ug+rx /etc/smrsh/ecartis

    echo "Your installation has been detected to have SMRSH, the SendMail"
    echo "Restricted SHell, installed.  If this is your first install, you"
    echo "will want to: "
    echo ""
    echo "1) add 'listserver-bin-dir = /etc/smrsh' to ecartis.cfg"
    echo "2) change the address for Ecartis in the aliases file to be"
    echo "   /etc/smrsh/ecartis instead of /home/ecartis/ecartis"
    chmod a+x /etc/smrsh/ecartis
fi

# Force the %{_ecartisdir} directory permissions to something sane
chmod 711 %{_ecartisdir}

# Run upgrade
echo "Run upgrade now... "
%{_ecartisdir}/%{name} -upgrade
exit 0

%triggerpostun -- listar
echo "Upgrading from listar..."
if [ -e /etc/smrsh ]; then
	ln -sf /etc/smrsh/ecartis /etc/smrsh/listar
fi
echo "Copying lists from listar directories"
cp -R /var/lib/listar/lists %{_ecartisdata}
chown -R ecartis.ecartis %{_ecartisdata}
if [ -e /etc/smrsh ]; then
	echo "Making link /etc/smrsh/listar to /etc/smrsh/ecartis:"
	ln -sf ecartis /etc/smrsh/listar
fi

%clean
rm -Rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ECARTIS.TODO NOTE README* src/{CHANGELOG,CREDITS}

%attr(750,root,root) /etc/cron.daily/%{name}
%attr(640,root,root) %config %verify(not size mtime md5) /etc/logrotate.d/%{name}
%attr(775,ecartis,ecartis) %dir %{_sysconfdir}/%{name}
%attr(644,root,ecartis) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/*
%attr(640,root,ecartis) %config(noreplace) %verify(not size mtime md5) %{_ecartisdir}/%{name}.aliases
%attr(640,root,ecartis) %config(noreplace) %verify(not size mtime md5) %{_ecartisdir}/%{name}.hlp
%attr(640,root,ecartis) %config(noreplace) %verify(not size mtime md5) %{_ecartisdir}/%{name}.cfg
%attr(640,root,ecartis) %config(noreplace) %verify(not size mtime md5) %{_ecartisdir}/banned
%attr(640,ecartis,ecartis) %ghost /var/log/%{name}.log
%attr(711,ecartis,ecartis) %dir %{_ecartisdir}
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/templates
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/modules
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/scripts
%attr(751,ecartis,ecartis) %dir %{_ecartisdata}/lists
%attr(750,ecartis,ecartis) %dir %{_ecartisdata}/queue
%attr(640,root,ecartis) %{_ecartisdir}/spam-regexp.sample
%attr(750,ecartis,ecartis) %{_ecartisdir}/modules/*
%attr(750,ecartis,ecartis) %{_ecartisdir}/scripts/*
%attr(4755,ecartis,ecartis) %{_ecartisdir}/ecartis

%files cgi
%defattr(644,root,root,755)
%doc src/modules/lsg2/*.txt
%attr(755,root,   root) /home/httpd/cgi-bin/*.cgi
%attr(770,root,ecartis) %dir %{_ecartisdata}/lists/SITEDATA
%attr(660,root,ecartis) %{_ecartisdata}/lists/SITEDATA/cookies
%{_ecartisdir}/templates/*.lsc
