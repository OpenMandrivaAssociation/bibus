%define name	bibus
%define version	1.5.1
%define	release	%mkrel 1

# Detect the correct path for openoffice
# Starting with the 2010.0 edition, there is no more an openoffice64 specific package

%if %{mdkversion} < 201000
    %ifarch %ix86	 
    %define ooname openoffice.org
    %define oorelease %(rpm -q --queryformat %{VERSION} openoffice.org)
    %define ooext %{_libdir}/ooo-%{oorelease}
    %endif
    %ifarch x86_64
    %define ooname openoffice.org64
    %define oorelease %(rpm -q --queryformat %{VERSION} openoffice.org64)
    %define ooext %{_libdir}/ooo-%{oorelease}_64
    %endif
%else
    %define ooname openoffice.org
    %define oorelease %(rpm -q --queryformat %{VERSION} openoffice.org)
    %define ooext %{_libdir}/ooo-%{oorelease}
%endif

Summary:	Bibliographic database manager with OpenOffice.org integration
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	http://freefr.dl.sourceforge.net/sourceforge/bibus-biblio/%{name}-%{version}.tar.gz
Patch0:		bibus-1.4.3.1-fix-desktop-file.patch
Source11:	%{name}.16.png
Source12:	%{name}.32.png
Source13:	%{name}.48.png
License:	GPLv2+
Group:		Publishing
Url:		http://bibus-biblio.sourceforge.net
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	desktop-file-utils
BuildRequires:	python >= 2.5
BuildRequires:	%ooname >= 3
Requires:	python >= 2.5
Requires:	%ooname >= 3
Requires:	%ooname-pyuno
#Requires:	python-sqlite2
Requires:	wxPythonGTK

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

mv locale/zh_cn locale/zh_CN
mv locale/cn locale/zh_TW

%install
rm -rf $RPM_BUILD_ROOT

%if %{mdkversion} < 200710
# Before 2007.1 there was no x86_64 OpenOffice.org build
%make -f Setup/Makefile \
	DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
	sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	python=%{_bindir}/python \
	oopath=%{_libdir}/ooo-2.1/%{progdir} \
	install
%elsif %{mdkversion} < 200900
      %make -f Setup/Makefile \
      DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
      sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
      python=%{_bindir}/python \
      oopath=%{ooext}/program \
      install
%else %if %{mdkversion} >= 200900
	%make -f Setup/Makefile \
		DESTDIR=$RPM_BUILD_ROOT%{_prefix} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		python=%{_bindir}/python \
		oopath=%{ooext}/program \
		ooure=%{ooext}/basis-link/ure-link/lib \
		oobasis=%{ooext}/basis-link/program \
		install
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
  --add-category="Office" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*

# Adjust some permissions
for file in bibus.py bibusStart.py CleanDB.py CodecChoice.py \
Data/parsePubMedJ.py display_panel.py \
FirstStart/FirstTimeWizard_DB.py \
FirstStart/Wizard_SQLite.py \
FirstStart/Wizard_MySQL.py \
FirstStart/MySQL_Setup.py \
Pref_Connection.py Pref_DB.py Pref_Display.py \
Pref_Duplicates_Base.py Pref_Journals.py Pref_Search.py \
RefDisplayDates.py \
moveFile.py \
lyx_remote.py \
BIBbase.py \
Pref_PubMed.py \
RefEditor_Files.py \
LyX/test/test_constants.py \
LyX/test/test_bindings.py \
LyX/test/test_lyxserver_no_running_lyx.py \
LyX/test/test_lfuns.py \
LyX/test/test_lyxclient.py \
LyX/test/test_lyxserver.py \
LyX/test/test_lyxclient_no_running_lyx.py \
LyX/test/test_lyx_remote.py \
LyX/examples/lyx-remote \
LyX/examples/lyx-Mx \
LyX/examples/lyx-bindings \
LyX/examples/lyx-with-client \
LyX/examples/lyx-python \
Utilities/open_url.py \
Utilities/title_case.py;
do
	chmod 755     $RPM_BUILD_ROOT/%{_datadir}/%{name}/$file
done

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
%attr(644,root,root) %{_miconsdir}/%{name}.png
%attr(644,root,root) %{_iconsdir}/%{name}.png
%attr(644,root,root) %{_liconsdir}/%{name}.png
%{_mandir}/man1/%{name}.1*
%config(noreplace) %{_sysconfdir}/bibus.config
%{_bindir}/bibus
%{_datadir}/%{name}
%{_datadir}/applications/bibus.desktop
