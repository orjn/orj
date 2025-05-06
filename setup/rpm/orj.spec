%global name orj
%global release 1
%global unmangled_version %{version}
%global __requires_exclude ^.*orj/addons/mail/static/scripts/orj-mailgate.py$

Summary: Orj Server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: LGPL-3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Orj S.A. <info@orj.net>
Requires: sassc
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
Url: https://www.orj.net

%description
Orj is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%generate_buildrequires
%pyproject_buildrequires

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%post
#!/bin/sh

set -e

ORJ_CONFIGURATION_DIR=/etc/orj
ORJ_CONFIGURATION_FILE=$ORJ_CONFIGURATION_DIR/orj.conf
ORJ_DATA_DIR=/var/lib/orj
ORJ_GROUP="orj"
ORJ_LOG_DIR=/var/log/orj
ORJ_LOG_FILE=$ORJ_LOG_DIR/orj-server.log
ORJ_USER="orj"

if ! getent passwd | grep -q "^orj:"; then
    groupadd $ORJ_GROUP
    adduser --system --no-create-home $ORJ_USER -g $ORJ_GROUP
fi
# Register "$ORJ_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $ORJ_USER" 2> /dev/null || true
# Configuration file
mkdir -p $ORJ_CONFIGURATION_DIR
# can't copy debian config-file as addons_path is not the same
if [ ! -f $ORJ_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $ORJ_USER
db_password = False
addons_path = %{python3_sitelib}/orj/addons
default_productivity_apps = True
" > $ORJ_CONFIGURATION_FILE
    chown $ORJ_USER:$ORJ_GROUP $ORJ_CONFIGURATION_FILE
    chmod 0640 $ORJ_CONFIGURATION_FILE
fi
# Log
mkdir -p $ORJ_LOG_DIR
chown $ORJ_USER:$ORJ_GROUP $ORJ_LOG_DIR
chmod 0750 $ORJ_LOG_DIR
# Data dir
mkdir -p $ORJ_DATA_DIR
chown $ORJ_USER:$ORJ_GROUP $ORJ_DATA_DIR

INIT_FILE=/lib/systemd/system/orj.service
touch $INIT_FILE
chmod 0700 $INIT_FILE
cat << EOF > $INIT_FILE
[Unit]
Description=Orj Open Source ERP and CRM
After=network.target

[Service]
Type=simple
User=orj
Group=orj
ExecStart=/usr/bin/orj --config $ORJ_CONFIGURATION_FILE --logfile $ORJ_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF


%files
%{_bindir}/orj
%{python3_sitelib}/%{name}-*.egg-info
%{python3_sitelib}/%{name}
