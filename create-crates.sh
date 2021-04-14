#!/bin/sh

force_cargo_package=adblock

for cmd in bsdtar rpm-specdump cargo perl; do
  if ! command -v $cmd > /dev/null 2> /dev/null; then
    not_installed="$not_installed$cmd "
  fi
done

if [ -n "$not_installed" ]; then
  echo "ERROR: required commands not found: $not_installed" >&2
  exit 1
fi

pkg_dir=$(readlink -f $(dirname "$0"))
pkg_name=$(basename "$pkg_dir")

if [ ! -f "$pkg_dir/$pkg_name.spec" ]; then
  echo "ERROR: unable to determine package name" >&2
  exit 1
fi

spec_dump=$(rpm-specdump "$pkg_dir/$pkg_name.spec")
pkg_version=$(echo "$spec_dump" | grep PACKAGE_VERSION | cut -f3 -d' ')
pkg_src=$(basename $(echo "$spec_dump" | grep SOURCEURL0 | cut -f3- -d' '))
crates_file="$pkg_name-crates-$pkg_version.tar.xz"
cargo_package=${force_cargo_package:-$pkg_name}

if [ -e "$pkg_dir/$crates_file" ]; then
  echo "ERROR: crates file $crates_file already exists" >&2
  exit 1
fi

if [ ! -f "$pkg_dir/$pkg_src" ]; then
  echo "ERROR: source file $pkg_src not found" >&2
  exit 1
fi

tmpdir=$(mktemp -d)

rm_tmpdir() {
  if [ -n "$tmpdir" -a -d "$tmpdir" ]; then
    rm -rf "$tmpdir"
  fi
}

trap rm_tmpdir EXIT INT HUP

cd "$tmpdir"
bsdtar xf "$pkg_dir/$pkg_src"
src_dir=$(ls)
if [ $(echo "$src_dir" | wc -l) -ne 1 ]; then
  echo "ERROR: unexpected source structure:\n$src_dir" >&2
  exit 1
fi

cd "$src_dir"
cargo vendor
if [ $? -ne 0 ]; then
  echo "ERROR: cargo vendor failed" >&2
  exit 1
fi

# replace cargo package version with @@VERSION@@
perl -pi -e 'BEGIN { undef $/;} s/(\[\[package\]\]\nname\s*=\s*"'"$cargo_package"'"\nversion\s*=\s*")[^"]+/$1\@\@VERSION\@\@/m' Cargo.lock

cd ..
tar cJf "$pkg_dir/$crates_file" "$src_dir"/{Cargo.lock,vendor}

# vim: expandtab shiftwidth=2 tabstop=2
