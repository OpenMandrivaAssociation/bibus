%define libreofficedir %{_libdir}/libreoffice

Name:		bibus
Version:	1.5.2
Release:	1
Summary:	Bibliographic database manager with OpenOffice.org integration
Source0:	http://freefr.dl.sourceforge.net/sourceforge/bibus-biblio/%{name}_%{version}.orig.tar.gz
Patch0:		bibus-1.4.3.1-fix-desktop-file.patch
Patch1:		bibus-1.5.1-fix_path_search.patch
Patch2:         bibus-1.5.2-mga-ubu-fix_libreoffice.patch
Source11:	%{name}.16.png
Source12:	%{name}.32.png
Source13:	%{name}.48.png
License:	GPLv2+
Group:		Publishing
Url:		http://bibus-biblio.sourceforge.net
BuildRequires:  desktop-file-utils
BuildRequires:  python-devel
BuildRequires:  gettext
BuildRequires:  libreoffice-devel
BuildRequires:  libreoffice-pyuno
Requires:       python >= 2.5
Requires:       wxPython > 2.6
Suggests:       %{_lib}sqlite3_0

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
%patch1 -p1
%patch2 -p1

mv locale/zh_cn locale/zh_CN
mv locale/cn locale/zh_TW

%install
%make -f Setup/Makefile \
    DESTDIR=%{buildroot}%{_prefix} \
    sysconfdir=%{buildroot}%{_sysconfdir} \
    python=%{_bindir}/python \
    oopath=%{libreofficedir}/program \
    ooure=%{libreofficedir}/ure-link/lib \
    oobasis=%{libreofficedir}/program \
    install

# we use our own doc installation macro
rm -rf %{buildroot}%{_docdir}/bibus
# rpm deals with uninstallation
rm -f %{buildroot}%{_datadir}/bibus/Setup/uninstall.sh
# fix symlink pathname
ln -sf %{_datadir}/bibus/bibusStart.py %{buildroot}%{_bindir}/bibus
# dirty hack for wrong pathnames in bibus.cfg
sed -e "s|%{buildroot}/|/|g" %{buildroot}%{_datadir}/bibus/bibus.cfg \
	> %{buildroot}%{_datadir}/bibus/bibuscorr.cfg
install -m644 --backup=off %{buildroot}%{_datadir}/bibus/bibuscorr.cfg \
	%{buildroot}%{_datadir}/bibus/bibus.cfg
rm -f %{buildroot}%{_datadir}/bibus/bibuscorr.cfg
# we use distro's iconsdir
rm -rf %{buildroot}%{_iconsdir}/hicolor

# localization
%find_lang %{name}

# icons
install -m644 %{SOURCE11} -D %{buildroot}%{_miconsdir}/%{name}.png
install -m644 %{SOURCE12} -D %{buildroot}%{_iconsdir}/%{name}.png
install -m644 %{SOURCE13} -D %{buildroot}%{_liconsdir}/%{name}.png

# Menu item, using the provide .desktop file

# Position the bibus.desktop entry
install -m644 --backup=off Setup/bibus.desktop -D %{buildroot}%{_datadir}/applications/bibus.desktop

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="Office" \
  --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

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
Utilities/open_url.py \
Utilities/title_case.py;
do
	chmod 755     %{buildroot}/%{_datadir}/%{name}/$file
done

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
