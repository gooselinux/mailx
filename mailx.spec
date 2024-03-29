%define use_nss 1
%define mailrc %{_sysconfdir}/mail.rc

Summary: Enhanced implementation of the mailx command
Name: mailx
Version: 12.4
Release: 6%{?dist}
Group: Applications/Internet
# mailx-12.4/nsserr.c, mailx-12.4/nss.c  have MPLv1.1 license
# other files are BSD
License: BSD with advertising and MPLv1.1
URL: http://heirloom.sourceforge.net/mailx.html
Source0: http://downloads.sourceforge.net/heirloom/mailx-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0: nail-11.25-config.patch
Patch1: mailx-12.3-pager.patch

%if %{use_nss}
BuildRequires: nss-devel, pkgconfig, krb5-devel
%else
BuildRequires: openssl-devel
%endif

Obsoletes: nail < %{version}
Provides: nail = %{version}


%description
Mailx is an enhanced mail command, which provides the functionality
of the POSIX mailx command, as well as SysV mail and Berkeley Mail
(from which it is derived).

Additionally to the POSIX features, mailx can work with Maildir/ e-mail
storage format (as well as mailboxes), supports IMAP, POP3 and SMTP
procotols (including over SSL) to operate with remote hosts, handles mime
types and different charsets. There are a lot of other useful features,
see mailx(1).

And as its ancient analogues, mailx can be used as a mail script language,
both for sending and receiving mail.

Besides the "mailx" command, this package provides "mail" and "Mail"
(which should be compatible with its predecessors from the mailx-8.x source),
as well as "nail" (the initial name of this project).


%prep
%setup -q
%patch0 -p1
%patch1 -p1

sed -i 's,/etc/nail.rc,%{mailrc},g' mailx.1 mailx.1.html


%build

%if %{use_nss}
INCLUDES="$INCLUDES `pkg-config --cflags-only-I nss`"
export INCLUDES
%endif

echo PREFIX=%{_prefix} \
     BINDIR=/bin \
     MANDIR=%{_mandir} \
     SYSCONFDIR=%{_sysconfdir} \
     MAILRC=%{mailrc} \
     MAILSPOOL=%{_localstatedir}/mail \
     SENDMAIL=%{_sbindir}/sendmail \
     UCBINSTALL=install \
> makeflags

#  %{?_smp_mflags} cannot be used here
make `cat makeflags` \
     CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" \
     IPv6=-DHAVE_IPv6_FUNCS


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT STRIP=: `cat makeflags` install

ln -s mailx $RPM_BUILD_ROOT/bin/mail

install -d $RPM_BUILD_ROOT%{_bindir}
pref=`echo %{_bindir} | sed 's,/[^/]*,../,g'`

pushd $RPM_BUILD_ROOT%{_bindir}
ln -s ${pref}bin/mailx Mail
ln -s ${pref}bin/mailx nail
popd

pushd $RPM_BUILD_ROOT%{_mandir}/man1
ln -s mailx.1 mail.1
ln -s mailx.1 Mail.1
ln -s mailx.1 nail.1
popd


%clean
rm -rf $RPM_BUILD_ROOT


%triggerpostun -- mailx < 12
[ -f %{mailrc}.rpmnew ] && {
    # old config was changed. Merge both together.
    ( echo '# The settings above was inherited from the old mailx-8.x config'
      echo
      cat %{mailrc}.rpmnew
    ) >>%{mailrc}
} || :


%triggerpostun -- nail <= 12.3

[ -f %{_sysconfdir}/nail.rc.rpmsave ] && {
    # old config was changed...
    save=%{mailrc}.rpmnew
    [ -f $save ] && save=%{mailrc}.rpmsave

    mv -f %{mailrc} $save
    mv -f %{_sysconfdir}/nail.rc.rpmsave %{mailrc}
} || :


%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS README
%config(noreplace) %{mailrc}
/bin/*
%{_bindir}/*
%{_mandir}/*/*


%changelog
* Tue Feb 16 2010 Ivana Hutarova Varekova <varekova@redhat.com> - 12.4-6
- Related: #543948
  minor spec file changes

* Mon Dec 21 2009 Ivana Hutarova Varekova <varekova@redhat.com> - 12.4-5
- Related: #548468
  fix source tag

* Fri Dec 18 2009 Ivana Hutarova Varekova <varekova@redhat.com> - 12.4-4
- Resolves: #548468
  fix license tag

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 12.4-3.1
- Rebuilt for RHEL 6

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Aug 11 2008 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.4-1
- update to 12.4

* Tue Jul 29 2008 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.3-1
- Place mailx to /bin/mailx, to avoid extra symlink in redhat-lsb package
- /bin/mailx is now a base binary, another symlinked to it.

* Thu Jun 26 2008 Dmitry Butskoy <Dmitry@Butskoy.name>
- add missed BR for krb5-devel
- activate IPv6 support
- change config to /etc/mail.rc for compatibility
- add triggerpostun scriptlets against previous mailx and nail
  to check and merge (when possible) their user config changes
- use proper config filename in manuals
- use "less" instead of non-provided "pg" for nobsdcompat mode

* Wed Jun 18 2008 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.3-0
- Change the name from "nail" to upstream's "mailx".
  Merge with the ordinary "mailx" cvs tree for Fedora 10.
  Now this stuff supersedes the old ancient mailx-8.x in Fedora.
- Build with nss instead of openssl, for "Security Consolidation" process.

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 12.3-4
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 12.3-3
 - Rebuild for deps

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 12.3-2
- Rebuild for selinux ppc32 issue.

* Fri Aug 17 2007 Dmitry Butskoy <Dmitry@Butskoy.name>
- Change License tag to "BSD with advertising"

* Tue Jul 24 2007 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.3-1
- update to 12.3

* Fri Jan 12 2007 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.2-1
- update to 12.2
- spec file cleanups

* Fri Jun 16 2006 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.1-1
- update to 12.1

* Wed Mar 22 2006 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.0-2
- complete "mailx to nail" changes in the manual and config files
- drop _smp_mflags: it caused make to work incorrectly.

* Tue Mar 21 2006 Dmitry Butskoy <Dmitry@Butskoy.name> - 12.0-1
- upgrade to 12.0
- change new upstream name "mailx" to the old name "nail" to avoid
  conflicts with the Core mailx package.
- drop Source1, use package's html file instead.

* Mon Oct 17 2005 Dmitry Butskoy <Dmitry@Butskoy.name> - 11.25-4
- don't strip binaries on makeinstall (#170972)

* Mon Oct  3 2005 Dmitry Butskoy <Dmitry@Butskoy.name>
- clear buildroot before install (Michael Schwendt)

* Mon Sep 26 2005 Dmitry Butskoy <Dmitry@Butskoy.name> - 11.25-3
- more spec file cleanups
- accepted for Fedora Extra
  (review by Aurelien Bompard <gauret@free.fr>)

* Mon Aug 22 2005 Dmitry Butskoy <Dmitry@Butskoy.name> - 11.25-2
- spec file cleanups (#166343)

* Fri Aug 19 2005 Dmitry Butskoy <Dmitry@Butskoy.name> - 11.25-1
- initial release
- add "set bsdcompat" to nail.rc as default
- copy nail web page to doc

