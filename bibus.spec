%define name	bibus
%define version	1.4.3.1
%define bibusrel	2
#define release		%mkrel %{bibusrel}.1
%define	 release		%mkrel 1

Summary: 	Bibliographic database manager with OpenOffice.org integration
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
Source0: 	%{name}-%{version}.tar.bz2
Patch0:		bibus-1.4.3.1-fix-desktop-file.patch.bz2
Source11:	%{name}.16.png
Source12:	%{name}.32.png
Source13:	%{name}.48.png
License: 	GPLv2
Group: 		Publishing
Url: 		http://bibus-biblio.sourceforge.net
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:  desktop-file-utils
BuildRequires:	python
Requires: 	python
%ifarch i586
Requires: 	openoffice.org >= 2
Requires:	openoffice.org-pyuno
%endif
%ifarch x86_64
Requires:	openoffice.org64 >= 2
Requires:	openoffice.org64-pyuno
%endif
Requires: 	python-sqlite2
Requires: 	wxPythonGTK

%description
Bibus is a bibliographic and reference management software. Besides besides
searching, editing and sorting bibliographic records, it features:
- Online PubMed and eTBLAST queries
- Direct reference insertion in OpenOffice.org
- File exchange capabilities with other reference managers
- Hierarchical organization of the references with user-defined keys
- Multi-user design
- Live queries (i.e. upgraded when database is modified).

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1

rm -rf Docs/html/en/eTBlast\ Interface\ to\ Bibus_files/CVS

if [ -d ./CVS ]; then
   find . -type d -perm 0700 -exec chmod 755 {} \;
   find . -type f -perm 0555 -exec chmod 755 {} \;
   find . -type f -perm 0444 -exec chmod 644 {} \;
fi

for i in `find . -type d -name CVS`  `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

find Docs/ -type f -exec chmod 0644 {} \;
mv locale/zh_cn locale/zh_CN
mv locale/cn locale/zh

%install
rm -rf $RPM_BUILD_ROOT

%if %{mdkversion} == 200710
    %define oorelease 2.1
    %define progdir "program"
%endif
%if %{mdkversion} == 200800
    %define oorelease 2.2
    %define progdir "program"
%endif
%if %{mdkversion} == 200810
    %define oorelease 2.4
    %define progdir "program"
%endif
%if %{mdkversion} == 200900
    %define oorelease 3.0
    %define progdir "basis%{oorelease}/program"
%endif
%if %{mdkversion} == 200910
    %define oorelease 3.0
    %define progdir "basis%{oorelease}/program"
%endif

%if %{mdkversion} < 200710
# Before 2007.1 there was no x86_64 OpenOffice.org build
%make -f Setup/Makefile \
	DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
	sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	python=%{_bindir}/python \
	oopath=%{_libdir}/ooo-2.1/%{progdir} \
	install
%else
	%ifarch x86_64
	%make -f Setup/Makefile \
		DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		python=%{_bindir}/python \
		oopath=%{_libdir}/ooo-%{oorelease}_64/%{progdir} \
		install
	%endif

	%ifarch i586
	%make -f Setup/Makefile \
		DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		python=%{_bindir}/python \
		oopath=%{_libdir}/ooo-%{oorelease}/%{progdir} \
		install
	%endif
%endif

# we use our own doc installation macro
rm -rf $RPM_BUILD_ROOT%{_docdir}/bibus
# rpm deals with uninstallation
rm -f $RPM_BUILD_ROOT%{_datadir}/bibus/Setup/uninstall.sh
# fix symlink pathname
ln -sf %{_datadir}/bibus/bibusStart.py $RPM_BUILD_ROOT%{_bindir}/bibus
# dirty hack for wrong pathnames in bibus.cfg
sed -e "s|$RPM_BUILD_ROOT/|/|g" $RPM_BUILD_ROOT%{_datadir}/bibus/bibus.cfg \
	> $RPM_BUILD_ROOT%{_datadir}/bibus/bibuscorr.cfg
install -m644 --backup=off $RPM_BUILD_ROOT%{_datadir}/bibus/bibuscorr.cfg \
	$RPM_BUILD_ROOT%{_datadir}/bibus/bibus.cfg
rm -f $RPM_BUILD_ROOT%{_datadir}/bibus/bibuscorr.cfg
# we use distro's iconsdir
rm -rf $RPM_BUILD_ROOT%{_iconsdir}/hicolor

# Create bibus.sh for launching bibus
cat > $RPM_BUILD_ROOT%{_bindir}/bibus.sh << EObibus
#!/bin/sh
export LD_LIBRARY_PATH=%{_libdir}/ooo-%{oorelease}/%{progdir}
export PYTHONPATH=%{_libdir}/ooo-%{oorelease}/%{progdir}
%{_bindir}/python %{_datadir}/bibus/bibus.py
EObibus
chmod 755 $RPM_BUILD_ROOT%{_bindir}/bibus.sh

# localization
%find_lang %{name}

# icons
install -m644 %{SOURCE11} -D $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png
install -m644 %{SOURCE12} -D $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
install -m644 %{SOURCE13} -D $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png

# Menu item, using the provide .desktop file

# Position the bibus.desktop entry
install -m644 --backup=off Setup/bibus.desktop -D $RPM_BUILD_ROOT%{_datadir}/applications/bibus.desktop

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="X-MandrivaLinux-Office-Publishing;Office" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*

# Adjust some permissions
chmod 755     $RPM_BUILD_ROOT/%{_datadir}/%{name}/*.py
chmod 755     $RPM_BUILD_ROOT/%{_datadir}/%{name}/FirstStart/*.py

%clean
rm -rf $RPM_BUILD_ROOT

%if %mdkversion < 200900
%post
%{update_menus}
%endif

%if %mdkversion < 200900
%postun
%{clean_menus}
%endif

%files -f %{name}.lang
%defattr(-,root,root,0755)
%doc Docs/html/ScreenShots Docs/html/en Docs/{CHANGELOG,copying,*.txt}
%attr(644,root,root)    %{_miconsdir}/%{name}.png
%attr(644,root,root)    %{_iconsdir}/%{name}.png
%attr(644,root,root)    %{_liconsdir}/%{name}.png
%{_mandir}/man1/%{name}.1*
%config(noreplace) %{_sysconfdir}/bibus.config
%{_bindir}/bibus
%{_bindir}/bibus.sh
%{_datadir}/%{name}
%{_datadir}/applications/bibus.desktop
