%define _disable_ld_no_undefined 0

%define name	hdf5
%define major	7
%define major_hl	7
%define libname %mklibname hdf5_ %{major}
%define libname_hl %mklibname hdf5_hl %{major_hl}
%define develname %mklibname %{name} -d
%define develnamest %mklibname %{name} -d -s
%define version 1.8.9
%define release %mkrel 1

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
Summary:	Devel libraries and header files for hdf5 development
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Requires:	%{libname_hl} = %{version}
Obsoletes:	%{mklibname -d hdf 5 0} < %{version}

%description -n %{develname}
This package provides devel libraries and header files needed
for develop applications requiring the "hdf5" library.









%package -n %{develnamest}
Summary:	Static libraries and header files for hdf5 development
Group:		Development/C
Provides:	%{name}-devel-static = %{version}-%{release}
Requires:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Requires:	%{libname_hl} = %{version}
Obsoletes:	%{mklibname -d hdf 5 0} < %{version}

%description -n %{develnamest}
This package provides static libraries and header files needed
for develop applications requiring the "hdf5" library.




%prep
%setup -qn %{name}-%{version}
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

#%check
# all tests must pass on the following architectures
#%ifarch %{ix86} x86_64
#%make check || echo "make check failed"
#%else
#%make -k check || echo "make check failed"
#%endif

%install
rm -rf %{buildroot}
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
%{_libdir}/libhdf5_hl.so.%{major_hl}*
%{_libdir}/libhdf5_hl_cpp.so.%{major_hl}*
%{_libdir}/libhdf5hl_fortran.so.%{major_hl}*

%files -n %{develnamest}
%{_libdir}/*.*a

%files -n %{develname}
%{_libdir}/*.so
%{_libdir}/*.settings
%{_includedir}/*.h
%{_includedir}/*.mod
%{_datadir}/hdf5_examples/
%multiarch %{multiarch_includedir}/H5pubconf.h


%changelog
* Thu May 31 2012 Alexander Khrukin <akhrukin@mandriva.org> 1.8.9-1mdv2012.0
+ Revision: 801590
- version update 1.8.9

* Wed Apr 04 2012 Paulo Andrade <pcpa@mandriva.com.br> 1.8.8-2
+ Revision: 789246
- Rebuild for .la files removal.

* Thu Dec 01 2011 Andrey Bondrov <abondrov@mandriva.org> 1.8.8-1
+ Revision: 737050
- New version 1.8.8, new library major 7

* Thu Nov 17 2011 Paulo Andrade <pcpa@mandriva.com.br> 1.8.5-3
+ Revision: 731478
- Do not provide hdf5 in libraries otherwise buildrequires hdf5 fails.

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 1.8.5-2
+ Revision: 661671
- multiarch fixes

* Fri Aug 13 2010 Emmanuel Andry <eandry@mandriva.org> 1.8.5-1mdv2011.0
+ Revision: 569401
- drop p

* Mon Apr 26 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1.8.4-4mdv2010.1
+ Revision: 539387
- add virtual provides needef for hdf-java

* Mon Apr 26 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1.8.4-3mdv2010.1
+ Revision: 539340
- update to patch1 postrelease
- disable all strange gcc flags
- spec file clean

* Sun Jan 17 2010 Emmanuel Andry <eandry@mandriva.org> 1.8.4-2mdv2010.1
+ Revision: 492750
- fix linking with p0
- drop p7 fixed upstream
- enable c++ and fortran support
- drop obsolete configure arguments
- use pic for x86_64
- update files list
- remove threadsafe, not compatible with c++

* Thu Jan 07 2010 Emmanuel Andry <eandry@mandriva.org> 1.8.4-1mdv2010.1
+ Revision: 487354
- New version 1.8.4
- fix SOURCE and URL
- drop p1 (merged upstream)
- rediff p2 and p9

* Sat Jul 25 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.8.3-1mdv2010.0
+ Revision: 399850
- new version

* Thu Apr 09 2009 Funda Wang <fwang@mandriva.org> 1.8.1-3mdv2009.1
+ Revision: 365348
- fix str fmt

* Sun Sep 28 2008 Funda Wang <fwang@mandriva.org> 1.8.1-3mdv2009.0
+ Revision: 288987
- conflicts with old lib

* Sun Sep 28 2008 Funda Wang <fwang@mandriva.org> 1.8.1-2mdv2009.0
+ Revision: 288976
- obsoletes old devel package

* Tue Aug 19 2008 Emmanuel Andry <eandry@mandriva.org> 1.8.1-1mdv2009.0
+ Revision: 274052
- fix typos
- fix file list
- enable parallel build
- define _disable_ld_no_undefined
- enable threadsafe, cxx breaks build
- update file list
- disable P4, use multiarch macro
- use P8 and P6 from opensuse
- add package for high level libraries
- update major
- fix summary
- add fedora patches
- disable threadsafe, incompatible with cxx
- use configure macro
- New version
- drop patches 1,2,3,4 and 5
- use configure2_5x
- Apply devel policy
- protect major

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 1.6.5-3mdv2008.1
+ Revision: 126630
- kill re-definition of %%buildroot on Pixel's request

