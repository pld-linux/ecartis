%define		_snap	20030303
%define		_rel	2

Summary:	Ecartis mailing list manager
Summary(pl):	Zarz±dca list dyskusyjnych Ecartis
Name:		ecartis
Version:	1.0.0
Release:	%{_snap}.%{_rel}
License:	GPL v2
Vendor:		NodeRunner Software
Group:		Applications/Mail
Source0:	ftp://ftp.ecartis.org/pub/ecartis/snapshots/tar/%{name}-%{version}-snap%{_snap}.tar.gz
Source1:	%{name}.logrotate
#Original taken from: http://www.misiek.eu.org/ipv6/listar-0.129a-ipv6-20000915.patch.gz
Patch0:		%{name}-ipv6.patch
Patch1:		%{name}-conf.patch
Patch2:		%{name}-paths.patch
# Does not work :-/ Connection refused..
URL:		http://www.ecartis.org/
Requires(pre):	user-ecartis
Requires(post):	/bin/hostname
Requires(post):	fileutils
Requires(post):	grep
Provides:	listar
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	listar

%define		_ecartisdir	/usr/lib/ecartis
%define		_ecartisdata	/var/lib/ecartis
%define		_cgidir		/home/services/httpd/cgi-bin/

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
Ecartis jest modu³owym narzêdziem do zarz±dzania listami dyskusyjnymi.
Ca³a jego funkcjonalno¶æ zawiera siê w pojedynczych plikach 'epm'
(Ecartis Plugin Module), dziêki czemu mo¿na w locie dodawaæ nowe
polecenia i funkcjonalno¶æ. Ecartis ma wiele przydatnych funkcji, np. 
mo¿liwo¶æ ustawienia 'flag' na kontach u¿ytkowników (podobnie jak w 
programie L-soft Listserv), i bardzo bezpieczn± metodê zdalnej administracji 
przy u¿yciu poczty elektronicznej.

Informacje o b³êdach w pakiecie nale¿y wysy³aæ na adres bugs@ecartis.org 
lub zg³aszaæ na stronie http://bugs.ecartis.org/ecartis.

UWAGA: Pakiet nazywa³ siê kiedy¶ Listar, jednak nazwa zosta³a
zmieniona ze wzglêdu na problemy ze znakiem handlowym.

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
Program ecartis-cgi, który jest interfejsem WWW do programu
zarz±dzaj±cego Ecartis.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__make} -Csrc -fMakefile.dist WFLAGS="%{rpmcflags} -Wall"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{%{name},logrotate.d,cron.daily} \
	$RPM_BUILD_ROOT%{_ecartisdata}/{queue,lists/{test/text,SITEDATA/cookies}} \
	$RPM_BUILD_ROOT%{_ecartisdir}/{modules,scripts,templates} \
	$RPM_BUILD_ROOT{%{_cgidir},/var/log}

%{__make} -Csrc -fMakefile.dist install

install %{name}	$RPM_BUILD_ROOT%{_ecartisdir}

install modules/*.lpm		$RPM_BUILD_ROOT%{_ecartisdir}/modules
install scripts/*		$RPM_BUILD_ROOT%{_ecartisdir}/scripts
install ecartis.cfg.dist	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/ecartis.cfg
install ecartis.aliases.dist	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/ecartis.aliases
install banned			$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/banned
install spam-regexp.sample	$RPM_BUILD_ROOT%{_ecartisdir}/spam-regexp.sample
install templates/*.lsc		$RPM_BUILD_ROOT%{_ecartisdir}/templates
install ecartis.hlp		$RPM_BUILD_ROOT%{_ecartisdata}/ecartis.hlp
install -D lists/test/text/*	$RPM_BUILD_ROOT%{_ecartisdata}/lists/test/text

install %{SOURCE1}		$RPM_BUILD_ROOT/etc/logrotate.d/%{name}

touch	$RPM_BUILD_ROOT%{_var}/log/%{name}.log
touch	$RPM_BUILD_ROOT%{_ecartisdata}/lists/SITEDATA/cookies

cat << EOF > $RPM_BUILD_ROOT%{_cgidir}/ecartisgate.cgi
#!/bin/sh
%{_ecartisdir}/%{name} -lsg2
EOF

cat << EOF > $RPM_BUILD_ROOT/etc/cron.daily/%{name}
%{_ecartisdir}/%{name} -procbounce
%{_ecartisdir}/%{name} -procdigest
EOF

# For compatibility with Listar:
ln -sf %{_ecartisdir}/%{name} $RPM_BUILD_ROOT%{_ecartisdir}/listar
ln -sf %{_cgidir}/ecartisgate.cgi $RPM_BUILD_ROOT%{_cgidir}/listargate.cgi

%clean
rm -rf $RPM_BUILD_ROOT

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
echo "Running \"%{_ecartisdir}/%{name} -upgrade\" now... "
%{_ecartisdir}/%{name} -upgrade
echo "done."
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

%files
%defattr(644,root,root,755)
%doc ECARTIS.TODO NOTE README* src/{CHANGELOG,CREDITS}

%attr(750,root,root) /etc/cron.daily/%{name}
%attr(640,root,root) %config %verify(not size mtime md5) /etc/logrotate.d/%{name}
%attr(775,ecartis,ecartis) %dir %{_sysconfdir}/%{name}
%attr(644,root   ,ecartis) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/*
%attr(640,ecartis,ecartis) %ghost /var/log/%{name}.log
%attr(711,ecartis,ecartis) %dir %{_ecartisdir}
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/templates
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/modules
%attr(750,ecartis,ecartis) %dir %{_ecartisdir}/scripts
%attr(751,ecartis,ecartis) %dir %{_ecartisdata}/lists
%attr(750,ecartis,ecartis) %dir %{_ecartisdata}/queue
%attr(750,ecartis,ecartis) %{_ecartisdata}/*.hlp
%attr(640,root   ,ecartis) %{_ecartisdir}/spam-regexp.sample
%attr(750,ecartis,ecartis) %{_ecartisdir}/modules/*
%attr(750,ecartis,ecartis) %{_ecartisdir}/scripts/*
%attr(4755,ecartis,ecartis) %{_ecartisdir}/ecartis

%files cgi
%defattr(644,root,root,755)
%doc src/modules/lsg2/*.txt
%attr(755,root,   root) %{_cgidir}/*.cgi
%attr(770,root,ecartis) %dir %{_ecartisdata}/lists/SITEDATA
%attr(660,root,ecartis) %{_ecartisdata}/lists/SITEDATA/cookies
%{_ecartisdir}/templates/*.lsc
