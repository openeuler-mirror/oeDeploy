#!/bin/bash

DIR=$(cd `dirname $0/`;pwd)

get_source() {
  source "$DIR/source.cfg"

  KSL_version=${KSL_version:-"2.5.0"}
  HMPP_version=${HMPP_version:-"2.5.0"}
  Hyperscan_branch=${Hyperscan_branch:-"v5.4.2.aarch64"}
  KAE_tag=${KAE_tag:-"kae2"}

  KSL_url=${KSL_url:-"https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boostkit-ksl-${KSL_version}-1.aarch64.rpm"}
  HMPP_url=${HMPP_url:-"https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boostkit-hmpp-${HMPP_version}-1.aarch64.rpm"}
  ragel_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/ragel-6.10.tar.gz"
  boost_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boost_1_87_0.tar.gz"
  pcre_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/pcre-8.43.tar.gz"

  Hyperscan_git="https://gitee.com/kunpengcompute/hyperscan.git"
  KAE_git="https://gitee.com/kunpengcompute/KAE.git"
}

download() {
  download_dir=$DIR/download
  mkdir $download_dir
  pushd $download_dir

  wget --no-check-certificate $KSL_url
  wget --no-check-certificate $HMPP_url
  wget --no-check-certificate $ragel_url
  wget --no-check-certificate $boost_url
  wget --no-check-certificate $pcre_url

  popd
}

pushd $DIR

get_source()
download()

popd
