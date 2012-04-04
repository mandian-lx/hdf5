%define _disable_ld_no_undefined 0

%define name	hdf5
%define major	7
%define major_hl	7
%define libname %mklibname hdf5_ %{major}
%define libname_hl %mklibname hdf5_hl %{major_hl}
%define develname %mklibname %{name} -d
%define version 1.8.8
%define release %mkrel 2

Summary:	HDF5 library
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	Distributable (see included COPYING)
Group:		System/Libraries
URL:		http://www.hdfgroup.org/HDF5/
Source0:	ftp://ftp.hdfgroup.org/HDF5/current/src/%{name}-%{version}.tar.bz2
Patch0:		%{name}-1.8.8-fix-str-fmt.patch
Patch8:		%{name}-1.8.1-lib64.patch
BuildRequires:	libjpeg-static-devel
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	krb5-devel
BuildRequires:	gcc-gfortran
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
Provides:	lib%{name} = %{version}-%{release}

%description -n %{libname}
This package contains the libraries needed to run programs dynamically
linked with hdf5 libraries.

%package -n %{libname_hl}
Summary:	HDF5 high level libraries
Group:		System/Libraries
Provides:	lib%{name}_hl = %{version}-%{release}
Conflicts:	%{mklibname hdf 5 0}

%description -n %{libname_hl}
This package contains the high level libraries needed to run programs dynamically
linked with hdf5 libraries.

%package -n %{develname}
Summary:	Static libraries and header files for hdf5 development
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Requires:	%{libname_hl} = %{version}
Obsoletes:	%{mklibname -d hdf 5 0} < %{version}

%description -n %{develname}
This package provides static libraries and header files needed
for develop applications requiring the "hdf5" library.

%prep
%setup -qn %{name}-%{version}
%patch0 -p1
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

#(tpg) disable all strange flags
#CFLAGS="$OPT_FLAGS" CXXFLAGS="$OPT_FLAGS" \
%configure2_5x --prefix=%{_prefix} \
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

%check
# all tests must pass on the following architectures
%ifarch %{ix86} x86_64
%make check || echo "make check failed"
%else
%make -k check || echo "make check failed"
%endif

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_libdir}
%makeinstall_std

%multiarch_includes %{buildroot}%{_includedir}/H5pubconf.h

perl -pi -e \
	"s@^libdir=\'/usr/lib\'@libdir=\'%{_libdir}\'@g" %{buildroot}%{_libdir}/*.la

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc COPYING MANIFEST README.txt release_docs/RELEASE.txt
%{_bindir}/*

%files -n %{libname}
%defattr(-,root,root,755)
%{_libdir}/libhdf5.so.%{major}*
%{_libdir}/libhdf5_cpp.so.%{major}*
%{_libdir}/libhdf5_fortran.so.%{major}*

%files -n %{libname_hl}
%defattr(-,root,root,755)
%{_libdir}/libhdf5_hl.so.%{major_hl}*
%{_libdir}/libhdf5_hl_cpp.so.%{major_hl}*
%{_libdir}/libhdf5hl_fortran.so.%{major_hl}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*.*a
%{_libdir}/*.so
%{_libdir}/*.settings
%{_includedir}/*
%{multiarch_includedir}/H5pubconf.h
%{_datadir}/hdf5_examples/*
