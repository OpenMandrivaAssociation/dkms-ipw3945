%define module_name ipw3945
%define module_path %{_usrsrc}/%{module_name}-%{version}-%{release}

Summary:	Intel(R) PRO/Wireless 3945ABG Network Connection driver
Name:		dkms-%{module_name}
Version:	1.2.2
Release:	%mkrel 6
License:	GPL
Group:		System/Kernel and hardware
URL:		http://ipw3945.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/ipw3945/%{module_name}-%{version}.tar.bz2
Source1:	kernel-2.6.24-MAC_BUF_ARG.patch
Source2:	kernel-2.6.24-SET_MODULE_OWNER.patch
Requires(pre):	dkms
Requires(post):	dkms
Suggests:	ipw3945d
Suggests:	ipw3945-ucode
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
This package contains the Intel(R) PRO/Wireless 3945ABG Network Connection
driver for Linux which supports the following network adapters:
- Intel(R) PRO/Wireless 3945ABG Network Connection Adapter
- Intel(R) PRO/Wireless 3945BG Network Connection Adapter

%prep
%setup -q -n %{module_name}-%{version}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{module_path}
mkdir -p %{buildroot}/%{module_path}/snapshot
mkdir -p %{buildroot}/%{module_path}/patches
cp -a Makefile ipw3945.h ipw3945.c ipw3945_daemon.h %{buildroot}/%{module_path}
cp -a snapshot/{check_ieee80211_compat,find_ieee80211} %{buildroot}/%{module_path}/snapshot
cp -a %SOURCE1 %SOURCE2 %{buildroot}/%{module_path}/patches/
cat > %{buildroot}/%{module_path}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{module_name}"
DEST_MODULE_LOCATION[0]="/kernel/3rdparty/%{module_name}"
BUILT_MODULE_NAME[0]="%{module_name}"
MAKE[0]="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; \
	make KSRC=\${kernel_source_dir} IEEE80211_INC=\${kernel_source_dir}/include \
	CONFIG_IPW3945_MONITOR=y IEEE80211_IGNORE_DUPLICATE=y"
CLEAN="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; \
	make KSRC=\${kernel_source_dir} clean"
REMAKE_INITRD="no"
AUTOINSTALL="yes"
PATCH[0]=%(basename %SOURCE1)
PATCH[1]=%(basename %SOURCE2)
PATCH_MATCH[0]="2\.6\.2[456]"
PATCH_MATCH[1]="2\.6\.2[456]"
EOF

# allow monitor mode
perl -pi -e 's/ //' \ %{buildroot}/%{module_path}/Makefile

%clean
rm -rf %{buildroot}

%post
dkms add     -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build   -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade
# rmmod any old driver if present and not in use
rmmod %{module_name} > /dev/null 2>&1 || true

%preun
dkms remove  -m %{module_name} -v %{version}-%{release} --all --rpm_safe_upgrade

%files
%defattr(-,root,root)
%doc LICENSE* README.ipw3945 INSTALL ISSUES CHANGES load unload dvals FILES
%{module_path}


