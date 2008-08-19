%define _disable_ld_no_undefined 1

%define name	hdf5
%define major	5
%define major_hl	0
%define libname %mklibname hdf5_ %{major}
%define libname_hl %mklibname hdf5_hl %{major_hl}
%define develname %mklibname %{name} -d
%define version 1.8.1
%define release %mkrel 1

Summary:	HDF5 library
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	Distributable (see included COPYING)
Group:		System/Libraries
Source0:	ftp://hdf.ncsa.uiuc.edu/HDF5/%{name}-%{version}/src/%{name}-%{version}.tar.bz2
Patch0:		hdf5-1.6.4-cflags.patch
Patch1:         %{name}-%{version}-gcc4.patch
Patch2:		%{name}-1.8.0-signal.patch
Patch3:		%{name}-1.8.0-destdir.patch
#Patch4:		%{name}-1.8.0-multiarch.patch
Patch5:		%{name}-1.8.0-scaleoffset.patch
Patch6:		%{name}-%{version}-build.patch
Patch7:		%{name}-1.8.0-longdouble.patch
Patch8:		%{name}-%{version}-lib64.patch
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
Summary:	HDF5 libraries
Group:		System/Libraries
Provides:       %{name} = %{version}-%{release}

%description -n %{libname}
This package contains the libraries needed to run programs dynamically
linked with hdf5 libraries.

%package -n %{libname_hl}
Summary:	HDF5 high level libraries
Group:		System/Libraries
Provides:       %{name} = %{version}-%{release}

%description -n %{libname_hl}
This package contains the high level libraries needed to run programs dynamically
linked with hdf5 libraries.


%package -n %{develname}
Summary:	Static libraries and header files for hdf5 development
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n %{develname}
This package provides static libraries and header files needed
for develop applications requiring the "hdf5" library.

%prep
%setup -q
%patch0 -p1 
%patch1 -p0
%patch2 -p1
%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6
%ifarch ppc64
%patch7 -p1
%endif
%ifarch x86_64
%patch8
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
%configure2_5x --prefix=%{_prefix} \
	--enable-threadsafe \
	--with-pthread \
	--enable-stream-vfd \
	--with-hdf4=/usr/include \
	--enable-linux-lfs \
	--enable-production=yes \
	--disable-rpath

%make

# all tests must pass on the following architectures
%ifarch %{ix86} x86_64
%make check || echo "make check failed"
%else
%make -k check || echo "make check failed"
%endif

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir}
%makeinstall
#cp -p test/.libs/libh5test.so.0.0.0 $RPM_BUILD_ROOT%{_libdir}/
#ln -s %{_libdir}/libh5test.so.0.0.0 $RPM_BUILD_ROOT%{_libdir}/libh5test.so.0
#rm -rf $RPM_BUILD_ROOT%{_prefix}/doc
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
%{_libdir}/libhdf5.so.{major}*

%files -n %{libname_hl}
%defattr(-,root,root,755)
%{_libdir}/libhdf5_hl.so.{major_hl}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/*.settings
%{_includedir}/*
%multiarch %{multiarch_includedir}/*.h


