# Disable binary stripping and debug subpackage
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%global selinux_variants mls strict targeted

Name:		bitcoin
Version:	0.12.1
Release:	1%{?dist}
Summary:	Peer-to-peer digital currency

Group:		Applications/System
License:	MIT
URL:		http://bitcoin.org/
# Deterministic source output of gitian, some files are copied into this RPM
Source0:	https://bitcoin.org/bin/bitcoin-core-%{version}/bitcoin-%{version}.tar.gz
Source1:    bitcoind.tmpfiles
Source2:	bitcoin.sysconfig
Source3:	bitcoin.service
Source4:	bitcoin.init
Source5:	bitcoin.te
Source6:	bitcoin.fc
Source7:	bitcoin.if
Source8:	README.server.fedora
Source9:	README.utils.fedora
Source10:	README.gui.fedora
# Deterministic binary outputs of gitian that are repackaged by this RPM
Source11:	https://bitcoin.org/bin/bitcoin-core-%{version}/%{name}-%{version}-linux32.tar.gz
Source12:       https://bitcoin.org/bin/bitcoin-core-%{version}/%{name}-%{version}-linux64.tar.gz
# We do not build the source so we instead install this pre-configured copy into the -devel package
Source13:       libbitcoinconsensus.pc
# XXX: seems to be broken in F23?
#NoSource:	11, 12

# desktop-file-validate
BuildRequires:  desktop-file-utils

%package libs
Summary:	Peer-to-peer digital currency


%package devel
Summary:	Peer-to-peer digital currency
Requires:	bitcoin-libs%{?_isa} = %{version}-%{release}


%package utils
Summary:	Peer-to-peer digital currency
Obsoletes:	bitcoin-cli <= 0.9.3


%package server
Summary:	Peer-to-peer digital currency
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
BuildRequires:	systemd
Requires(pre):	shadow-utils
Requires(post):	/usr/sbin/semodule, /sbin/restorecon, /sbin/fixfiles
Requires(postun):	/usr/sbin/semodule, /sbin/restorecon, /sbin/fixfiles
# SELinux disabled for now because gitian can't build it???
#Requires:	selinux-policy
#Requires:	policycoreutils-python
Requires:   openssl-libs
Requires:	bitcoin-utils%{_isa} = %{version}


%description
Bitcoin is an experimental new digital currency that enables instant
payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer
technology to operate with no central authority: managing transactions
and issuing money are carried out collectively by the network.

Bitcoin is also the name of the open source software which enables the
use of this currency.

This package provides Bitcoin-QT, a user-friendly wallet manager for
personal use.


%description libs
Bitcoin is an experimental new digital currency that enables instant
payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer
technology to operate with no central authority: managing transactions
and issuing money are carried out collectively by the network.

This package provides libbitcoinconsensus, which is used by third party
applications to verify scripts (and other functionality in future).


%description devel
Bitcoin is an experimental new digital currency that enables instant
payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer
technology to operate with no central authority: managing transactions
and issuing money are carried out collectively by the network.

This package provides the libraries and header files necessary to
compile programs which use libbitcoinconsensus.


%description utils 
Bitcoin is an experimental new digital currency that enables instant
payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer
technology to operate with no central authority: managing transactions
and issuing money are carried out collectively by the network.

This package provides bitcoin-cli, a utility to communicate with and
control a Bitcoin server via its RPC protocol, and bitcoin-tx, a utility
to create custom Bitcoin transactions.


%description server
Bitcoin is an experimental new digital currency that enables instant
payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer
technology to operate with no central authority: managing transactions
and issuing money are carried out collectively by the network.

This package provides bitcoind, a peer-to-peer node and wallet server.


%prep
# Unpack source tarball
# We do not build it, but we do copy things from it into the output RPMS
%setup -q -n %{name}-%{version}
# Unpack gitian linux32 tarball into linux32/
# Unpack gitian linux64 tarball into linux64/
for bits in 32 64; do
  mkdir gitian${bits}
  cd gitian${bits}
  tar xfv %{SOURCE11}
  cd -
done

# Install README files
cp -p %{SOURCE8} %{SOURCE9} %{SOURCE10} .

# Prep SELinux policy
mkdir SELinux
cp -p %{SOURCE5} %{SOURCE6} %{SOURCE7} SELinux


%build
# Build SELinux policy (disabled for now because gitian can't build it???)
#pushd SELinux
#for selinuxvariant in %{selinux_variants}
#do
#  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
#  mv bitcoin.pp bitcoin.pp.${selinuxvariant}
#  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
#done
#popd


%install
rm -rf %{buildroot}
mkdir %{buildroot}

# Install executables
mkdir -p -m 755 %{buildroot}%{_bindir}
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/bin/bitcoind    %{buildroot}%{_bindir}/bitcoind
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/bin/bitcoin-cli %{buildroot}%{_bindir}/bitcoin-cli
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/bin/bitcoin-tx  %{buildroot}%{_bindir}/bitcoin-tx
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/bin/bitcoin-qt  %{buildroot}%{_bindir}/bitcoin-qt

# Install -libs
mkdir -p -m 755 %{buildroot}%{_libdir}
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/lib/libbitcoinconsensus.so.0.0.0 %{buildroot}%{_libdir}/libbitcoinconsensus.so.0.0.0
ln -sf libbitcoinconsensus.so.0.0.0 %{buildroot}%{_libdir}/libbitcoinconsensus.so.0 
ln -sf libbitcoinconsensus.so.0.0.0 %{buildroot}%{_libdir}/libbitcoinconsensus.so

# Install -devel
mkdir -p -m 755 %{buildroot}%{_includedir}
install -m755 -p gitian%{__isa_bits}/%{name}-%{version}/include/bitcoinconsensus.h %{buildroot}%{_includedir}/bitcoinconsensus.h
mkdir -p -m 755 %{buildroot}%{_libdir}/pkgconfig
install -m755 -p %{SOURCE13}                                                       %{buildroot}%{_libdir}/pkgconfig/libbitcoinconsensus.pc

# Install example config file
# missing from gitian source tarball
#cp contrib/debian/examples/bitcoin.conf bitcoin.conf.example

# Install ancillary files
mkdir -p -m 755 %{buildroot}%{_datadir}/pixmaps
# gitian source tarball lacks xpm's, but that seems OK as most packages install only the png's
#install -D -m644 -p share/pixmaps/bitcoin*.{png,xpm,ico} %{buildroot}%{_datadir}/pixmaps/
#install -D -m644 -p contrib/debian/bitcoin-qt.desktop %{buildroot}%{_datadir}/applications/bitcoin-qt.desktop
#desktop-file-validate %{buildroot}%{_datadir}/applications/bitcoin-qt.desktop
#install -D -m644 -p contrib/debian/bitcoin-qt.protocol %{buildroot}%{_datadir}/kde4/services/bitcoin-qt.protocol
install -D -m644 -p %{SOURCE1} %{buildroot}%{_tmpfilesdir}/bitcoin.conf
install -D -m600 -p %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/bitcoin
install -D -m644 -p %{SOURCE3} %{buildroot}%{_unitdir}/bitcoin.service
install -d -m750 -p %{buildroot}%{_localstatedir}/lib/bitcoin
install -d -m750 -p %{buildroot}%{_sysconfdir}/bitcoin
#install -D -m644 -p contrib/debian/manpages/bitcoind.1 %{buildroot}%{_mandir}/man1/bitcoind.1
#install -D -m644 -p contrib/debian/manpages/bitcoin-qt.1 %{buildroot}%{_mandir}/man1/bitcoin-qt.1
#install -D -m644 -p contrib/debian/manpages/bitcoin.conf.5 %{buildroot}%{_mandir}/man5/bitcoin.conf.5
#gzip %{buildroot}%{_mandir}/man1/bitcoind.1
#gzip %{buildroot}%{_mandir}/man1/bitcoin-qt.1
#gzip %{buildroot}%{_mandir}/man5/bitcoin.conf.5

# Install SELinux policy (selinux disabled for now because gitian can't built it???)
#for selinuxvariant in %{selinux_variants}
#do
#	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
#	install -p -m 644 SELinux/bitcoin.pp.${selinuxvariant} \
#		%{buildroot}%{_datadir}/selinux/${selinuxvariant}/bitcoin.pp
#done


%clean
rm -rf %{buildroot}


%pre server
getent group bitcoin >/dev/null || groupadd -r bitcoin
getent passwd bitcoin >/dev/null ||
	useradd -r -g bitcoin -d /var/lib/bitcoin -s /sbin/nologin \
	-c "Bitcoin wallet server" bitcoin
exit 0


%post server
%systemd_post bitcoin.service
# disabled for now until gitian can build selinux policies
exit 0

for selinuxvariant in %{selinux_variants}
do
	/usr/sbin/semodule -s ${selinuxvariant} -i \
		%{_datadir}/selinux/${selinuxvariant}/bitcoin.pp \
		&> /dev/null || :
done
# FIXME This is less than ideal, but until dwalsh gives me a better way...
/usr/sbin/semanage port -a -t bitcoin_port_t -p tcp 8332
/usr/sbin/semanage port -a -t bitcoin_port_t -p tcp 8333
/usr/sbin/semanage port -a -t bitcoin_port_t -p tcp 18332
/usr/sbin/semanage port -a -t bitcoin_port_t -p tcp 18333
/sbin/fixfiles -R bitcoin-server restore &> /dev/null || :
/sbin/restorecon -R %{_localstatedir}/lib/bitcoin || :


%posttrans server
/usr/bin/systemd-tmpfiles --create


%preun server
%systemd_preun bitcoin.service


%postun server
%systemd_postun bitcoin.service
if [ $1 -eq 0 ] ; then
	# FIXME This is less than ideal, but until dwalsh gives me a better way...
	/usr/sbin/semanage port -d -p tcp 8332
	/usr/sbin/semanage port -d -p tcp 8333
	/usr/sbin/semanage port -d -p tcp 18332
	/usr/sbin/semanage port -d -p tcp 18333
	for selinuxvariant in %{selinux_variants}
	do
		/usr/sbin/semodule -s ${selinuxvariant} -r bitcoin \
		&> /dev/null || :
	done
	/sbin/fixfiles -R bitcoin-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/bitcoin ] && \
		/sbin/restorecon -R %{_localstatedir}/lib/bitcoin \
		&> /dev/null || :
fi


%files
%defattr(-,root,root,-)
%license COPYING
#%doc README.md README.gui.fedora doc/assets-attribution.md doc/multiwallet-qt.md doc/release-notes.md doc/tor.md bitcoin.conf.example
%{_bindir}/bitcoin-qt
#%{_datadir}/applications/bitcoin-qt.desktop
#%{_datadir}/kde4/services/bitcoin-qt.protocol
#%{_datadir}/pixmaps/*
#%{_mandir}/man1/bitcoin-qt.1.gz


%files libs
%defattr(-,root,root,-)
%license COPYING
#%doc README.md
%{_libdir}/libbitcoinconsensus.so*


%files devel
%defattr(-,root,root,-)
%license COPYING
#%doc README.md
%{_includedir}/bitcoinconsensus.h
%{_libdir}/pkgconfig/libbitcoinconsensus.pc


%files utils
%defattr(-,root,root,-)
%license COPYING
#%doc README.md README.utils.fedora bitcoin.conf.example
%{_bindir}/bitcoin-cli
%{_bindir}/bitcoin-tx


%files server
%defattr(-,root,root,-)
%license COPYING
#%doc README.md README.server.fedora doc/dnsseed-policy.md doc/release-notes.md doc/tor.md bitcoin.conf.example
%dir %attr(750,bitcoin,bitcoin) %{_localstatedir}/lib/bitcoin
%dir %attr(750,bitcoin,bitcoin) %{_sysconfdir}/bitcoin
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/sysconfig/bitcoin
#%doc SELinux/*
%{_bindir}/bitcoind
%{_unitdir}/bitcoin.service
%{_tmpfilesdir}/bitcoin.conf
#%{_mandir}/man1/bitcoind.1.gz
#%{_mandir}/man5/bitcoin.conf.5.gz

#%{_datadir}/selinux/*/bitcoin.pp


%changelog
* Thu May 05 2016 Warren Togami <wtogami@gmail.com> 0.12.1-1
- adapted from Michael Hampton's bitcoin-0.12.1 for gitian deterministic rpm

