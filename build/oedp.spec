%define _python_bytecompile_errors_terminate_build 0
Name:               oedp
Version:            1.0.0
Release:            release_number
Summary:            openEuler deploy tool
License:            NA
Source0:            %{name}-%{version}.tar.gz

Requires: python3, ansible

%description
openEuler deploy tool


%prep
%setup -b 0 -n %{name}-%{version}


%build
%define debug_package %{nil}


%install
mkdir -p -m 700 %{buildroot}%{_var}/oedp/log
mkdir -p -m 700 %{buildroot}%{_var}/oedp/plugin
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python/third_libs
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python/venv
mkdir -p -m 700 %{buildroot}%{_usr}/lib/oedp
mkdir -p -m 700 %{buildroot}%{_usr}/share/applications
mkdir -p -m 700 %{buildroot}%{_sysconfdir}/oedp/config
mkdir -p %{buildroot}%{_bindir}

cp -rdpf %{_builddir}/%{name}-%{version}/src %{buildroot}%{_usr}/lib/oedp
mv %{buildroot}%{_usr}/lib/oedp/src/config/log.conf %{buildroot}%{_sysconfdir}/oedp/config
install -c -m 0400 %{_builddir}/%{name}-%{version}/static/* %{buildroot}%{_usr}/share/applications
install -c -m 0500 %{_builddir}/%{name}-%{version}/oedp.py %{buildroot}%{_bindir}/oedp
install -c -m 0400 %{_builddir}/%{name}-%{version}/python_third_libs/* %{buildroot}%{_var}/oedp/python/third_libs


%post
set -e

# 创建 Python 虚拟环境
pushd %{_var}/oedp/python/venv
python3 -m venv oedp
source oedp/bin/activate
for python_third_lib in $(ls %{_var}/oedp/python/third_libs); do
    pip install %{_var}/oedp/python/third_libs/${python_third_lib}
done

# 创建软连接
python_version_info=$(python3 --version)
major_minor_version=$(echo ${python_version_info} | awk '{split($2, v, "."); print "python" v[1] "." v[2]}')
site_packages_dir=%{_var}/oedp/python/venv/oedp/lib/${major_minor_version}/site-packages
ln -s %{_usr}/lib/oedp/src %{_var}/oedp/python/venv/oedp/lib/${major_minor_version}/site-packages/src
popd


%postun
set -e

# 删除可能会残留的目录
rm -rf /var/oedp
rm -rf /usr/lib/oedp


%files
%attr(0500,root,root) %dir %{_var}/oedp
%attr(0700,root,root) %dir %{_var}/oedp/log
%attr(0500,root,root) %dir %{_var}/oedp/plugin
%attr(0500,root,root) %dir %{_var}/oedp/python
%attr(0500,root,root) %dir %{_var}/oedp/python/third_libs
%attr(0500,root,root) %dir %{_var}/oedp/python/venv
%attr(0500,root,root) %dir %{_usr}/lib/oedp
%attr(0700,root,root) %dir %{_sysconfdir}/oedp/config

%attr(0600,root,root) %ghost %{_var}/oedp/log/oedp.log
%attr(0400,root,root) %{_var}/oedp/python/third_libs/*
%attr(0500,root,root) %{_usr}/lib/oedp/src/*
%attr(0600,root,root) %config %{_sysconfdir}/oedp/config/log.conf
%attr(0755,root,root) %{_usr}/share/applications/*
%attr(0500,root,root) %{_bindir}/oedp