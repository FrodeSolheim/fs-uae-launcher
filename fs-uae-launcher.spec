%define name fs-uae-launcher
%define version 2.5.29dev
%define unmangled_version 2.5.29dev
%define release 1%{?dist}

Summary: Graphical configuration frontend and launcher for FS-UAE
Name: %{name}
Version: %{version}
Release: %{release}
URL: http://fs-uae.net/
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPL-2.0+
Group: Applications/Emulators
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Frode Solheim <frode@fs-uae.net>
Requires: python3-qt4 fs-uae python3-setuptools
BuildRequires: python3-devel python3-setuptools

%if 0%{?suse_version}
%global __python  /usr/bin/python3
%global __python3  /usr/bin/python3
%else
%if 0%{?mandriva_version}
%else
%global __python %{__python3}
%endif
%endif

%description
FS-UAE Launcher is a graphical configuration program and launcher for FS-UAE.

%prep
%setup -n %{name}-%{unmangled_version}

%build
%{__python} setup.py build
make

%install
make install DESTDIR=%{buildroot} prefix=%{_prefix}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%_bindir/*
%_datadir/%{name}/
%_datadir/doc/%{name}/
%_datadir/applications/*.desktop
%_datadir/icons/*/*/*/*.png
%_datadir/locale/*/*/*.mo

%dir %_datadir/icons/hicolor
%dir %_datadir/icons/hicolor/128x128
%dir %_datadir/icons/hicolor/128x128/apps
%dir %_datadir/icons/hicolor/16x16
%dir %_datadir/icons/hicolor/16x16/apps
%dir %_datadir/icons/hicolor/256x256
%dir %_datadir/icons/hicolor/256x256/apps
%dir %_datadir/icons/hicolor/32x32
%dir %_datadir/icons/hicolor/32x32/apps
%dir %_datadir/icons/hicolor/48x48
%dir %_datadir/icons/hicolor/48x48/apps
%dir %_datadir/icons/hicolor/64x64
%dir %_datadir/icons/hicolor/64x64/apps

%doc

%changelog
