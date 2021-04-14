%define		crates_ver	0.4.4
%define 	module	adblock

Summary:	Brave's adblock library in Python
Name:		python3-%{module}
Version:	0.4.4
Release:	1
License:	MIT or Apache v2.0
Group:		Libraries/Python
Source0:	https://files.pythonhosted.org/packages/source/a/adblock/%{module}-%{version}.tar.gz
# Source0-md5:	6958de33e5034c1241a69c91989f0e86
# ./create-crates.sh
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	932c699a7fa6016098e56026ae389322
URL:		https://github.com/ArniDagur/python-adblock
BuildRequires:	cargo
BuildRequires:	maturin >= 0.10
BuildRequires:	python3-devel >= 1:3.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	rust >= 1.45
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch x32
%define		cargo_outdir	target/x86_64-unknown-linux-gnux32
%else
%define		cargo_outdir	target
%endif

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
CARGO_HOME="$(pwd)/.cargo" \
CARGO_NET_OFFLINE=true \
CARGO_TERM_VERBOSE=true \
%{?__jobs:CARGO_BUILD_JOBS="%{__jobs}"} \
RUSTFLAGS="%{rpmrustflags}" \
/usr/bin/maturin build --release --no-sdist \
%ifarch x32
	--target x86_64-unknown-linux-gnux32
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{py3_sitedir}
cp -p %{cargo_outdir}/release/libadblock.so $RPM_BUILD_ROOT%{py3_sitedir}/%{module}.so

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python3-%{module}
%defattr(644,root,root,755)
%doc CHANGELOG.md README.md
%attr(755,root,root) %{py3_sitedir}/%{module}.so
