%define name	bibus
%define version 1.4
%define bibusrel 0rc2
%define release %mkrel %{bibusrel}.2

Summary: 	Bibliographic database manager with OpenOffice.org integration
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
Source0: 	%{name}-%{version}.%{bibusrel}.tar.bz2
#Patch0:		bibus-1.2.0-makefile.patch
Patch1:		bibus-1.2.0-fix-desktop-file.patch
Source11:	%{name}.16.png
Source12:	%{name}.32.png
Source13:	%{name}.48.png
License: 	GPL
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
%setup -q -n %{name}-%{version}.%{bibusrel}
#%patch0 -p1
%patch1 -p1
find Docs/ -type f -exec chmod 0644 {} \;
#mv locale/zh_cn locale_CN
for file in Docs/html/en/bibMSW_files/filelist.xml \
'Docs/html/en/eTBlast Interface to Bibus.htm' \
'Docs/html/en/eTBlast Interface to Bibus_files/filelist.xml' \
Docs/html/en/bibMSW.htm;
do
	tr -d '\r' < "$file" > tmp
	mv tmp "$file"
done

%install
rm -rf $RPM_BUILD_ROOT

%if %{mdkversion} == 200710
    %define oorelease 2.1
%endif
%if %{mdkversion} == 200800
    %define oorelease 2.2
%endif
%if %{mdkversion} == 200810
    %define oorelease 2.4
%endif

%if %{mdkversion} < 200710
# Before 2007.1 there was no x86_64 OpenOffice.org build
%make -f Setup/Makefile \
	DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
	sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	python=%{_bindir}/python \
	oopath=%{_libdir}/ooo-2.1/program \
	install
%else
	%ifarch x86_64
	%make -f Setup/Makefile \
		DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		python=%{_bindir}/python \
		oopath=%{_libdir}/ooo-%{oorelease}_64/program \
		install
	%endif

	%ifarch i586
	%make -f Setup/Makefile \
		DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		python=%{_bindir}/python \
		oopath=%{_libdir}/ooo-%{oorelease}/program \
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
export LD_LIBRARY_PATH=%{_libdir}/ooo-%{oorelease}/program
export PYTHONPATH=%{_libdir}/ooo-%{oorelease}/program
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

# fix pathnames in bibus.desktop
install -m644 --backup=off Setup/bibus.desktop -D $RPM_BUILD_ROOT%{_datadir}/applications/bibus.desktop
echo 'Exec=%{_bindir}/bibus' >> $RPM_BUILD_ROOT%{_datadir}/applications/bibus.desktop
echo 'Icon=%{_iconsdir}/%{name}.png' >> $RPM_BUILD_ROOT%{_datadir}/applications/bibus.desktop

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="X-MandrivaLinux-Office-Publishing;Office" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*

# Old menu style

### We don't need this entry since the application provides its own .desktop file
### # XDG menu 
### mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
### cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
### [Desktop Entry]
### Name=Bibus
### Comment="Bibliographic database manager with OpenOffice.org integration"
### Exec=%{name}.sh
### Icon=%{name}
### Terminal=false
### Type=Application
### Categories=X-MandrivaLinux-Office-Publishing;Office;
### StartupNotify=true
### EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{update_menus}

%postun
%{clean_menus}

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
%attr(755,root,root)	%{_datadir}/%{name}/Pref_Duplicates_Base.py
%attr(755,root,root)	%{_datadir}/%{name}/display_panel.py
%attr(755,root,root)	%{_datadir}/%{name}/bibus.py
%attr(755,root,root)    %{_datadir}/%{name}/Pref_Display.py 
%attr(755,root,root)    %{_datadir}/%{name}/Pref_Search.py 
%attr(755,root,root)    %{_datadir}/%{name}/FirstStart/MySQL_Setup.py 
%attr(755,root,root)    %{_datadir}/%{name}/FirstStart/FirstTimeWizard_WP.py 
%attr(755,root,root)    %{_datadir}/%{name}/FirstStart/Wizard_SQLite.py 
%attr(755,root,root)    %{_datadir}/%{name}/FirstStart/Wizard_MySQL.py 
%attr(755,root,root)    %{_datadir}/%{name}/FirstStart/FirstTimeWizard_DB.py 
%attr(755,root,root)    %{_datadir}/%{name}/CodecChoice.py 
%attr(755,root,root)	%{_datadir}/%{name}/Pref_Connection.py
%attr(755,root,root)	%{_datadir}/%{name}/Pref_DB.py


