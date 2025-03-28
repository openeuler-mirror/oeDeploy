%define _python_bytecompile_errors_terminate_build 0
Name:               oedp
Version:            1.0.1
Release:            release_number
Summary:            openEuler deploy tool
License:            MulanPSL-2.0
Source0:            %{name}-%{version}.tar.gz

BuildArch:  noarch

Requires: python3, ansible, python3-prettytable

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
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python/venv
mkdir -p -m 700 %{buildroot}%{_usr}/lib/oedp
mkdir -p -m 700 %{buildroot}%{_usr}/share/applications
mkdir -p -m 700 %{buildroot}%{_sysconfdir}/oedp/config
mkdir -p %{buildroot}%{_bindir}

cp -rdpf %{_builddir}/%{name}-%{version}/src %{buildroot}%{_usr}/lib/oedp
mv %{buildroot}%{_usr}/lib/oedp/src/config/log.conf %{buildroot}%{_sysconfdir}/oedp/config
install -c -m 0400 %{_builddir}/%{name}-%{version}/static/* %{buildroot}%{_usr}/share/applications
install -c -m 0500 %{_builddir}/%{name}-%{version}/oedp.py %{buildroot}%{_bindir}/oedp


%postun
if [ $1 -eq 0 ]; then
    # 卸载时删除可能会残留的目录
    rm -rf /var/oedp
    rm -rf /usr/lib/oedp
fi


%files
%attr(0500,root,root) %dir %{_var}/oedp
%attr(0700,root,root) %dir %{_var}/oedp/log
%attr(0500,root,root) %dir %{_var}/oedp/plugin
%attr(0500,root,root) %dir %{_var}/oedp/python
%attr(0500,root,root) %dir %{_var}/oedp/python/venv
%attr(0500,root,root) %dir %{_usr}/lib/oedp
%attr(0700,root,root) %dir %{_sysconfdir}/oedp/config

%attr(0600,root,root) %ghost %{_var}/oedp/log/oedp.log
%attr(0500,root,root) %{_usr}/lib/oedp/src/*
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/oedp/config/log.conf
%attr(0755,root,root) %{_usr}/share/applications/*
%attr(0500,root,root) %{_bindir}/oedp


%changelog
* Wed Mar 12 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.1-1
- Updated icon click effects on DevStation.
- Added upgrade support for the oedp package.
- Fixed exceptions caused by missing 'tasks' field.
- Fixed other known issues.

* Mon Mar 3 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.0-2
- fix the issue of abnormal termination during the script execution phase after installation

* Sat Feb 22 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.0-1
- init package