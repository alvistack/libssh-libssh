# Copyright 2024 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

Name: libssh
Epoch: 100
Version: 0.10.5
Release: 1%{?dist}
Summary: A library implementing the SSH protocol
License: LGPL-2.1-or-later
URL: https://git.libssh.org/projects/libssh.git
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: gnupg2
BuildRequires: krb5-devel
BuildRequires: libcmocka-devel
BuildRequires: openssl-devel
BuildRequires: pkgconfig
BuildRequires: xz
BuildRequires: zlib-devel
Requires: libssh-config = %{epoch}:%{version}-%{release}
Provides: libssh_threads.so.4()(64bit)

%description
The ssh library was designed to be used by programmers needing a working SSH
implementation by the mean of a library. The complete control of the client is
made by the programmer. With libssh, you can remotely execute programs, transfer
files, use a secure and transparent tunnel for your remote programs. With its
Secure FTP implementation, you can play with remote files easily, without
third-party programs others than libcrypto (from openssl).

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%cmake \
    -DCLIENT_TESTING="OFF" \
    -DSERVER_TESTING="OFF" \
    -DSLOW_TEST_SYSTEM="OFF" \
    -DUNIT_TESTING="OFF" \
    -DWITH_EXAMPLES="OFF"
%cmake_build

%check

%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
%package -n libssh4
Summary: SSH library
Group: System/Libraries
Requires: libssh-config >= %{epoch}:%{version}-%{release}

%description -n libssh4
An SSH implementation in the form of a library. With libssh, you can remotely
execute programs, transfer files, use a secure and transparent tunnel for your
remote programs. It supports SFTP as well.

This package provides libssh from https://www.libssh.org that should not be
confused with libssh2 available from https://www.libssh2.org (libssh2 package)

%package config
Summary: SSH library configuration files
Group: Productivity/Networking/SSH

%description config
Configuration files for the SSH library.

%package devel
Summary: SSH library development headers
Group: Development/Libraries/C and C++
Requires: cmake
Requires: libssh4 = %{epoch}:%{version}-%{release}

%description devel
Development headers for the SSH library.

%install
%cmake_install
install -d -m755 %{buildroot}%{_sysconfdir}/libssh

%post -n libssh4 -p /sbin/ldconfig
%postun -n libssh4 -p /sbin/ldconfig

%files -n libssh4
%doc AUTHORS README CHANGELOG
%{_libdir}/libssh.so.*

%files config
%dir %{_sysconfdir}/libssh

%files devel
%dir %{_libdir}/cmake/libssh
%{_includedir}/libssh
%{_libdir}/cmake/libssh
%{_libdir}/libssh.so
%{_libdir}/pkgconfig/libssh.pc
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package devel
Summary: Development files for libssh
Requires: libssh = %{epoch}:%{version}-%{release}

%description devel
The libssh-devel package contains libraries and header files for developing
applications that use libssh.

%package config
Summary: Configuration files for libssh
BuildArch: noarch
Obsoletes: libssh < %{epoch}:%{version}-%{release}

%description config
The libssh-config package provides the default configuration files for libssh.

%install
%cmake_install
install -d -m755 %{buildroot}%{_sysconfdir}/libssh

#
# Workaround for the removal of libssh_threads.so
#
# This will allow libraries which link against libssh_threads.so or packages
# requiring it to continue working.
#
pushd %{buildroot}%{_libdir}
for i in libssh.so*;
do
    _target="${i}"
    _link_name="${i%libssh*}libssh_threads${i##*libssh}"
    if [ -L "${i}" ]; then
        _target="$(readlink ${i})"
    fi
    ln -s "${_target}" "${_link_name}"
done;
popd

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%{_libdir}/libssh.so.4*
%{_libdir}/libssh_threads.so.4*

%files devel
%dir  %{_libdir}/cmake/
%{_includedir}/libssh/
%{_libdir}/cmake/libssh/
%{_libdir}/libssh.so
%{_libdir}/libssh_threads.so
%{_libdir}/pkgconfig/libssh.pc

%files config
%attr(0755,root,root) %dir %{_sysconfdir}/libssh
%endif

%changelog
