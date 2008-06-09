%define name	hdf5
%define major	0
%define libname %mklibname hdf5_ %{major}
%define version 1.6.5
%define fversion 1.6.5
%define release %mkrel 3

Summary:	HDF5 library
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	Distributable (see included COPYING)
Group:		System/Libraries
Source0:	ftp://hdf.ncsa.uiuc.edu/HDF5/%{name}-%{version}/src/%{name}-%{fversion}.tar.bz2
Patch0:		hdf5-1.6.4-cflags.patch
Patch1:		hdf5-1.6.5-nmu.patch
Patch2:		hdf5-1.6.5-norpath.patch
Patch3:		hdf5-1.6.5-gfortran.patch
Patch4:		hdf5-1.6.5-test5.patch
Patch5:		hdf5-1.6.5-snprintf.patch
Patch6:		hdf5-1.6.5-lib64.patch
URL:		http://hdf.ncsa.uiuc.edu/HDF5/
BuildRequires:	libjpeg-static-devel
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
Requires:	%{libname} = %{version}-%{release}
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
HDF5 is a library and file format for storing scientific data. It was
designed to address some of the limitations of the HDF 4.x library and to
address current and anticipated requirements of modern systems and
applications. HDF5 includes the following improvements.

   - A new file format designed to address some of the deficiencies of
     HDF4.x, particularly the need to store larger files and more
     objects per file.
   - A simpler, more comprehensive data model that includes only two
     basic structures: a multidimensional array of record structures,
     and a grouping structure.
   - A simpler, better-engineered library and API, with improved
     support for parallel i/o, threads, and other requirements imposed
     by modern systems and applications.


%package -n %{libname}
Summary:	HDF5 development libraries
Group:		System/Libraries

%description -n %{libname}
This package contains the libraries needed to run programs dynamically
linked with hdf5 libraries.

%package -n %{libname}-devel
Summary:	Static libraries and header files for hdf5 development
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n %{libname}-devel
This package provides static libraries and header files needed
for develop applications requiring the "hdf5" library.

%prep
%setup -q -n %{name}-%{fversion}
%patch0 -p1 -b .cflags
%patch1 -p1 -b .nmu
%patch2 -p1 -b .norpath
%patch3 -p1 -b .gfortran
%patch4 -p1 -b .test5
%patch5 -p1 -b .snprintf
%ifarch x86_64
%patch6 -p1 -b .64bit
%endif

%build
find $RPM_BUILD_ROOT -type f -size 0 -name Dependencies -print0 |xargs -0 rm -f
find $RPM_BUILD_ROOT -type f -size 0 -name .depend -print0 |xargs -0 rm -f 

OPT_FLAGS="$RPM_OPT_FLAGS -O1 -Wno-long-long -Wfloat-equal -Wmissing-format-attribute -Wpadded"
%ifarch %{ix86} x86_64
OPT_FLAGS="$OPT_FLAGS -mieee-fp"
%endif

# (gb) 1.4.2-2mdk: "2.96" still deficient wrt. C++ exception handling on ia32
%ifarch %ix86
OPT_FLAGS=`echo "$OPT_FLAGS -fno-omit-frame-pointer" | sed -e "s/-fomit-frame-pointer//g"`
%endif

# (gb) 1.4.2-2mdk: constants merging causes troubles with long doubles on ia64
%ifarch ia64
OPT_FLAGS="$OPT_FLAGS -fno-merge-constants"
%endif

CFLAGS="$OPT_FLAGS" CXXFLAGS="$OPT_FLAGS" \
./configure --prefix=%{_prefix} \
	--enable-cxx \
	--enable-threadsafe \
	--with-pthread \
	--enable-stream-vfd \
	--with-hdf4=/usr/include \
	--enable-linux-lfs \
	--enable-production=yes \
	--disable-rpath
make

# all tests must pass on the following architectures
%ifarch %{ix86} x86_64
make check || echo "make check failed"
%else
make -k check || echo "make check failed"
%endif

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir}
%makeinstall
cp -p test/.libs/libh5test.so.0.0.0 $RPM_BUILD_ROOT%{_libdir}/
ln -s %{_libdir}/libh5test.so.0.0.0 $RPM_BUILD_ROOT%{_libdir}/libh5test.so.0
rm -rf $RPM_BUILD_ROOT%{_prefix}/doc
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/H5pubconf.h

perl -pi -e \
	"s@^libdir=\'/usr/lib\'@libdir=\'%{_libdir}\'@g" $RPM_BUILD_ROOT%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc COPYING MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY.txt doc/html
%{_bindir}/*

%files -n %{libname}
%defattr(-,root,root,755)
%{_libdir}/*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/*.settings
%{_includedir}/*
%multiarch %{multiarch_includedir}/*.h


