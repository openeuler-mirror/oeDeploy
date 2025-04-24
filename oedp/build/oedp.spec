%define _python_bytecompile_errors_terminate_build 0
Name:               oedp
Version:            1.0.2
Release:            release_number
Summary:            openEuler deploy tool
License:            MulanPSL-2.0
Source0:            %{name}-%{version}.tar.gz

BuildArch:  noarch

Requires: python3, ansible, python3-prettytable, tar

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

touch %{buildroot}%{_var}/oedp/log/oedp.log
cp -rdpf %{_builddir}/%{name}-%{version}/src %{buildroot}%{_usr}/lib/oedp
mv %{buildroot}%{_usr}/lib/oedp/src/config/* %{buildroot}%{_sysconfdir}/oedp/config
mkdir -p -m 700 %{buildroot}%{_sysconfdir}/oedp/config/repo/cache
install -c -m 0400 %{_builddir}/%{name}-%{version}/static/* %{buildroot}%{_usr}/share/applications
install -c -m 0500 %{_builddir}/%{name}-%{version}/oedp.py %{buildroot}%{_bindir}/oedp


%postun
if [ $1 -eq 0 ]; then
    # 卸载时删除可能会残留的目录
    rm -rf /etc/oedp
    rm -rf /var/oedp
    rm -rf /usr/lib/oedp
fi


%files
%attr(0555,root,root) %dir %{_var}/oedp
%attr(0777,root,root) %dir %{_var}/oedp/log
%attr(0777,root,root) %dir %{_var}/oedp/plugin
%attr(0555,root,root) %dir %{_var}/oedp/python
%attr(0555,root,root) %dir %{_var}/oedp/python/venv
%attr(0555,root,root) %dir %{_usr}/lib/oedp
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config/repo
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config/repo/cache

%attr(0666,root,root) %{_var}/oedp/log/oedp.log
%attr(0555,root,root) %{_usr}/lib/oedp/src/*
%attr(0666,root,root) %config(noreplace) %{_sysconfdir}/oedp/config/log.conf
%attr(0666,root,root) %config(noreplace) %{_sysconfdir}/oedp/config/repo/repo.conf
%attr(0644,root,root) %{_usr}/share/applications/*
%attr(0555,root,root) %{_bindir}/oedp


%changelog
* Mon Mar 31 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.2-1
- Fix the issue where non-root users cannot execute

* Thu Mar 20 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.1-2
- Fix known issues

* Wed Mar 12 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.1-1
- Updated icon click effects on DevStation.
- Added upgrade support for the oedp package.
- Fixed exceptions caused by missing 'tasks' field.
- Fixed other known issues.

* Mon Mar 3 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.0-2
- fix the issue of abnormal termination during the script execution phase after installation

* Sat Feb 22 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.0.0-1
- init package