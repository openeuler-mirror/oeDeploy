%define _python_bytecompile_errors_terminate_build 0
Name:               oedp
Version:            __VERSION__
Release:            release_number
Summary:            openEuler deploy tool
License:            MulanPSL-2.0
URL:                https://atomgit.com/openeuler/oeDeploy
Source0:            %{name}-%{version}.tar.gz

BuildArch:  noarch

Requires: python3, ansible, tar, rsync
Requires: python3-prettytable, python3-netaddr, python3-packaging

%description
openEuler deploy tool


%prep
%setup -b 0 -n %{name}-%{version}


%build
%define debug_package %{nil}


%install
mkdir -p -m 700 %{buildroot}%{_var}/oedp/details
mkdir -p -m 700 %{buildroot}%{_var}/oedp/log
mkdir -p -m 700 %{buildroot}%{_var}/oedp/plugin
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python
mkdir -p -m 700 %{buildroot}%{_var}/oedp/python/venv
mkdir -p -m 700 %{buildroot}%{_usr}/lib/oedp
mkdir -p -m 700 %{buildroot}%{_usr}/share/applications
mkdir -p -m 700 %{buildroot}%{_sysconfdir}/oedp/config
mkdir -p -m 777 %{buildroot}/opt/oedp/plugins
mkdir -p %{buildroot}%{_bindir}

touch %{buildroot}%{_var}/oedp/log/oedp.log
cp -rdpf %{_builddir}/%{name}-%{version}/src %{buildroot}%{_usr}/lib/oedp
mv %{buildroot}%{_usr}/lib/oedp/src/config/* %{buildroot}%{_sysconfdir}/oedp/config
mkdir -p -m 700 %{buildroot}%{_sysconfdir}/oedp/config/repo/cache
install -c -m 0400 %{_builddir}/%{name}-%{version}/static/* %{buildroot}%{_usr}/share/applications
install -c -m 0500 %{_builddir}/%{name}-%{version}/oedp.py %{buildroot}%{_bindir}/oedp


%post
if [ $1 -ge 1 ]; then
    # 安装或升级时执行
    /usr/bin/oedp repo make-local /opt/oedp/plugins/ || :
fi


%postun
if [ $1 -eq 0 ]; then
    # 卸载时删除可能会残留的目录（保留 /opt/oedp/plugins）
    rm -rf /etc/oedp
    rm -rf /var/oedp
    rm -rf /usr/lib/oedp
fi


%files
%attr(0555,root,root) %dir %{_var}/oedp
%attr(0777,root,root) %dir %{_var}/oedp/details
%attr(0777,root,root) %dir %{_var}/oedp/log
%attr(0777,root,root) %dir %{_var}/oedp/plugin
%attr(0555,root,root) %dir %{_var}/oedp/python
%attr(0555,root,root) %dir %{_var}/oedp/python/venv
%attr(0555,root,root) %dir %{_usr}/lib/oedp
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config/repo
%attr(0777,root,root) %dir %{_sysconfdir}/oedp/config/repo/cache
%attr(0777,root,root) %dir /opt/oedp/plugins

%attr(0666,root,root) %{_var}/oedp/log/oedp.log
%attr(0555,root,root) %{_usr}/lib/oedp/src/*
%attr(0666,root,root) %config(noreplace) %{_sysconfdir}/oedp/config/log.conf
%attr(0666,root,root) %config(noreplace) %{_sysconfdir}/oedp/config/repo/repo.conf
%attr(0644,root,root) %{_usr}/share/applications/*
%attr(0555,root,root) %{_bindir}/oedp


%changelog
* Wed Dev 3 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.6-0
- Local plugin repository enabled by default

* Tue Nov 18 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.5-0
- Use /opt/oedp/plugins directory as the local plugin repository for oeDeploy.
- Add plugin repository creation functionality to the oedp command.

* Wed Sep 17 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.4-0
- Add Python 3.8 compatibility

* Sun Jul 27 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.3-0
- Downlowd details when repo updating.
- The operation log will be recorded in the plugin directory.

* Sat Jul 5 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.2-0
- Add local deployment mode and runtime printing.

* Tue Jun 3 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.1-0
- Add the command 'oedp list' to support querying the plugin list.

* Thu May 15 2025 Yu Diandian <yudiandian@huawei.com> - 1.1.0-3
- Fix known issues with version query

* Sun Apr 27 2025 Ding Jiahui <dingjiahui4@huawei.com> - 1.1.0-2
- Fix some bugs of init module

* Sun Apr 27 2025 Liu Jiangbin <liujiangbin3@h-partners.com> - 1.1.0-1
- Support configurable plugin sources
- Support one-click initialization
- Fix the log permission bug

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