#!/bin/bash

get_source() {
  source "$DIR/source.cfg"

  KSL_version=${KSL_version:-"2.5.0"}
  Hyperscan_branch=${Hyperscan_branch:-"v5.4.2.aarch64"}
  KAE_branch=${KAE_branch:-"kae2"}

  KSL_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boostkit-ksl-${KSL_version}-1.aarch64.rpm"
  ragel_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/ragel-6.10.tar.gz"
  boost_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/boost_1_87_0.tar.gz"
  pcre_url="https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/pcre-8.43.tar.gz"
  libgpg_url="https://www.gnupg.org/ftp/gcrypt/libgpg-error/libgpg-error-1.51.tar.gz"

  Hyperscan_git=${Hyperscan_git:-"https://gitee.com/kunpengcompute/hyperscan.git"}
  KAE_git=${KAE_git:-"https://gitee.com/kunpengcompute/KAE.git"}
}

download() {
  download_dir=$DIR/build/AccLib/download
  mkdir $download_dir
  pushd $download_dir

  wget -N --no-check-certificate $KSL_url
  wget -N --no-check-certificate $ragel_url
  wget -N --no-check-certificate $boost_url
  wget -N --no-check-certificate $pcre_url
  wget -N --no-check-certificate $libgpg_url

  git clone $Hyperscan_git -b khsel
  cp hyperscan/khsel.patch ./
  pushd hyperscan
  git checkout $Hyperscan_branch
  popd

  git clone $KAE_git -b $KAE_branch --depth=1

  pip download "argparse>=1.4.0"

  popd
}

build_dir() {
  download_dir=$DIR/build/AccLib/download
  target_dir=$DIR/roles/AccLib/prepare/files/BoostKit-AccLib
  wheel_dir=$DIR/roles/AccLib/prepare/files/BoostKit-AccLib-wheels

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

  mkdir -p $wheel_dir
  cp -af $download/*.whl $wheel_dir
}

edit_xml() {
  xml_file=$DIR/roles/AccLib/prepare/files/BoostKit-AccLib/scripts/version.xml

  sed -i "s|<ragel>.*</ragel>|<ragel>${ragel_url}</ragel>|g" $xml_file
  sed -i "s|<boost>.*</boost>|<boost>${boost_url}</boost>|g" $xml_file
  sed -i "s|<pcre>.*</pcre>|<pcre>${pcre_url}</pcre>|g" $xml_file
  sed -i "s|<hyperscan_code>.*</hyperscan_code>|<hyperscan_code>${Hyperscan_git}</hyperscan_code>|g" $xml_file
  sed -i "s|<kae_code>.*</kae_code>|<kae_code>${KAE_git}</kae_code>|g" $xml_file
  sed -i "s|<libgpg>.*</libgpg>|<libgpg>${libgpg_url}</libgpg>|g" $xml_file
}


build_tar() {
  pushd $DIR/roles/AccLib/prepare/files
  tar -zcvf BoostKit-AccLib.tar.gz BoostKit-AccLib/
  popd
}

pushd $DIR

get_source
download
build_dir
edit_xml
build_tar

popd
