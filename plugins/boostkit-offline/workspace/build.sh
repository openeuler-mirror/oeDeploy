#!/bin/bash

DIR=$(cd `dirname $0/`;pwd)

get_source() {
  source "$DIR/source.cfg"

  KSL_version=${KSL_version:-"2.5.0"}
  Hyperscan_branch=${Hyperscan_branch:-"v5.4.2.aarch64"}
  KAE_branch=${$KAE_branch:-"kae2"}
  Libgcrypt_version=${Libgcrypt_version:-"1.51"}

  KSL_url=${KSL_url:-"https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boostkit-ksl-${KSL_version}-1.aarch64.rpm"}
  ragel_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/ragel-6.10.tar.gz"
  boost_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boost_1_87_0.tar.gz"
  pcre_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/pcre-8.43.tar.gz"
  Libgcrypt_url="https://www.gnupg.org/ftp/gcrypt/libgpg-error/libgpg-error-${Libgcrypt_version}.tar.gz"

  Hyperscan_git=${Hyperscan_git:-"https://gitee.com/kunpengcompute/hyperscan.git"}
  KAE_git=${KAE_git:-"https://gitee.com/kunpengcompute/KAE.git"}
}

download() {
  download_dir=$DIR/download
  mkdir $download_dir
  pushd $download_dir

  wget --no-check-certificate $KSL_url
  wget --no-check-certificate $ragel_url
  wget --no-check-certificate $boost_url
  wget --no-check-certificate $pcre_url
  wget --no-check-certificate $Libgcrypt_url

  git clone $Hyperscan_git -b khsel
  cp hyperscan/khsel.patch ./
  git checkout $Hyperscan_branch

  git clone $KAE_git -b $KAE_branch --depth=1

  popd
}

build_dir() {
  download_dir=$DIR/download
  target_dir=$DIR/roles/AccLib/prepare/files/BoostKit-AccLib

  Hyperscan_dir=$target_dir/Hyperscan
  mkdir -p $Hyperscan_dir
  cp -af $download_dir/boost_*.tar.gz $Hyperscan_dir
  cp -af $download_dir/pcre-*.tar.gz $Hyperscan_dir
  cp -af $download_dir/ragel-*.tar.gz $Hyperscan_dir
  cp -arf $download_dir/hyperscan $Hyperscan_dir

  KAE_dir=$target_dir/KAE
  mkdir -p $KAE_dir
  cp -arf $download_dir/KAE $KAE_dir

  KSL_dir=$target_dir/KSL
  mkdir -p $KSL_dir/rpm
  cp -af $download_dir/boostkit-ksl-*.rpm $KSL_dir/rpm

  resources_dir=$target_dir/resources
  mkdir -p $resources_dir/libgcrypt
  cp -af $download_dir/libgpg-error-*.tar.gz $resources_dir/libgcrypt

  patch_dir=$target_dir/patch
  mkdir -p $patch_dir
  cp -af $download_dir/*.patch $patch_dir
}

pushd $DIR

get_source
download
build_dir

popd
