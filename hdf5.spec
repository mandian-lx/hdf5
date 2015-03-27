%define _disable_ld_no_undefined 0

%define major	8
%define libname %mklibname hdf5_ %{major}
%define libname_hl %mklibname hdf5_hl %{major}
%define devname %mklibname %{name} -d

Summary:	HDF5 library


Name:		hdf5
Version:	1.8.14
Release:	1
License:	Distributable (see included COPYING)
Group:		System/Libraries
Url:		http://www.hdfgroup.org/HDF5/
Source0:	ftp://ftp.hdfgroup.org:21/HDF5/current/src/%{name}-%{version}.tar.bz2
Patch0:		%{name}-1.8.8-fix-str-fmt.patch
Patch8:		%{name}-1.8.1-lib64.patch

BuildRequires:	gcc-gfortran
BuildRequires:	jpeg-devel
BuildRequires:	krb5-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)

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

%description -n %{libname}
This package contains the libraries needed to run programs dynamically
linked with hdf5 libraries.

%package -n %{libname_hl}
Summary:	HDF5 high level libraries


Group:		System/Libraries

%description -n %{libname_hl}
This package contains the high level libraries needed to run programs
dynamically linked with hdf5 libraries.

%package -n %{devname}
Summary:	Devel libraries and header files for hdf5 development


Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Requires:	%{libname_hl} = %{version}
Obsoletes:	%{_lib}hdf5-static-devel < 1.8.9-3

%description -n %{devname}
This package provides devel libraries and header files needed
for develop applications requiring the "hdf5" library.

%prep
%setup -q
#%patch0 -p1
%ifarch x86_64
%patch8 -p0
%endif
find -name '*.[ch]' -o -name '*.f90' -exec chmod -x {} +

%build
find %{buildroot} -type f -size 0 -name Dependencies -print0 |xargs -0 rm -f
find %{buildroot} -type f -size 0 -name .depend -print0 |xargs -0 rm -f

OPT_FLAGS="%{optflags} -O1 -Wno-long-long -Wfloat-equal -Wmissing-format-attribute -Wpadded"
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

%ifarch x86_64
OPT_FLAGS="$OPT_FLAGS -fPIC"
%endif

%configure \
	--disable-static \
	--disable-dependency-tracking \
	--enable-cxx \
	--enable-fortran \
	--with-pthread \
	--enable-linux-lfs \
%ifarch x86_64
	--with-pic \
%endif
	--enable-production=yes

%make

#%check
# all tests must pass on the following architectures
#%ifarch %{ix86} x86_64
#%make check || echo "make check failed"
#%else
#%make -k check || echo "make check failed"
#%endif

%install
mkdir -p %{buildroot}%{_libdir}
%makeinstall_std

%multiarch_includes %{buildroot}/%{_includedir}/H5pubconf.h

%files
%doc COPYING MANIFEST README.txt release_docs/RELEASE.txt
%{_bindir}/*

%files -n %{libname}
%{_libdir}/libhdf5.so.%{major}*
%{_libdir}/libhdf5_cpp.so.%{major}*
%{_libdir}/libhdf5_fortran.so.%{major}*

%files -n %{libname_hl}
%{_libdir}/libhdf5_hl.so.%{major}*
%{_libdir}/libhdf5_hl_cpp.so.%{major}*
%{_libdir}/libhdf5hl_fortran.so.%{major}*

%files -n %{devname}
%{_libdir}/*.so
%{_libdir}/*.settings
%{_includedir}/*.h
%{_includedir}/*.mod
%{_datadir}/hdf5_examples/
%{multiarch_includedir}/H5pubconf.h
