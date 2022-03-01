%define		crates_ver	0.5.2
%define 	module	adblock

Summary:	Brave's adblock library in Python
Name:		python3-%{module}
Version:	0.5.2
Release:	1
License:	MIT or Apache v2.0
Group:		Libraries/Python
Source0:	https://files.pythonhosted.org/packages/source/a/adblock/%{module}-%{version}.tar.gz
# Source0-md5:	bc38178bd980bbb0472bead80f835367
# ./create-crates.sh
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	bc781735a3f336a7e403fe8dc3ef3749
URL:		https://github.com/ArniDagur/python-adblock
BuildRequires:	cargo
BuildRequires:	maturin >= 0.10
BuildRequires:	python3-devel >= 1:3.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.012
BuildRequires:	rust >= 1.45
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Python wrapper for Brave's adblocking library, which is written in
Rust.

%prep
%setup -q -n %{module}-%{version} -a1

%{__mv} %{module}-%{crates_ver}/* .
sed -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export CARGO_NET_OFFLINE=true
export CARGO_TERM_VERBOSE=true
%{?__jobs:export CARGO_BUILD_JOBS="%{__jobs}"}
export RUSTFLAGS="%{rpmrustflags}"
%ifarch %{ix86}
export RUSTFLAGS="$RUSTFLAGS -C opt-level=1"
%endif
/usr/bin/maturin build --release --no-sdist \
	--target %{rust_target}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{py3_sitedir}
cp -p %{cargo_objdir}/libadblock.so $RPM_BUILD_ROOT%{py3_sitedir}/%{module}.so

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python3-%{module}
%defattr(644,root,root,755)
%doc CHANGELOG.md README.md
%attr(755,root,root) %{py3_sitedir}/%{module}.so
