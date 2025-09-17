# Copyright © 2012–2021 Frode Solheim <frode@solheim.dev>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

%define fsbuild_version 3.2.22

%define name fs-uae-launcher
%define version %{fsbuild_version}
%define unmangled_version %{fsbuild_version}
%define release 1%{?dist}

Summary: Graphical configuration frontend and launcher for FS-UAE
Name: %{name}
Version: %{version}
Release: %{release}
URL: http://fs-uae.net/
Source0: %{name}_%{unmangled_version}.orig.tar.xz
License: GPL-2.0+
Group: Applications/Emulators
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Frode Solheim <frode@solheim.dev>
Requires: fs-uae
Requires: python3-qt5
Requires: python3-lhafile
Requires: python3-requests
Requires: python3-setuptools
BuildRequires: python3-devel
BuildRequires: python3-setuptools

%if 0%{?suse_version}
%global __python  /usr/bin/python3
%global __python3  /usr/bin/python3
%else
%global __python %{__python3}
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
rm -Rf %{buildroot}%{_prefix}/share/fs-uae-launcher/OpenGL

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
%dir %_datadir/icons/hicolor/22x22
%dir %_datadir/icons/hicolor/22x22/apps
%dir %_datadir/icons/hicolor/24x24
%dir %_datadir/icons/hicolor/24x24/apps
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
