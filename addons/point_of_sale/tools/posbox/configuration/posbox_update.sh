#!/usr/bin/env bash

sudo service led-status stop

cd /home/pi/orj
localbranch=$(git symbolic-ref -q --short HEAD)
localremote=$(git config branch.$localbranch.remote)

if [[ "$(git remote get-url "$localremote")" != *orj/orj* ]]; then
    git remote set-url "${localremote}" "https://github.com/orj/orj.git"
fi

echo "addons/point_of_sale/tools/posbox/overwrite_after_init/home/pi/orj" >> .git/info/sparse-checkout

git fetch "${localremote}" "${localbranch}" --depth=1
git reset "${localremote}"/"${localbranch}" --hard

sudo git clean -dfx
if [ -d /home/pi/orj/addons/point_of_sale/tools/posbox/overwrite_after_init ]; then
    cp -a /home/pi/orj/addons/point_of_sale/tools/posbox/overwrite_after_init/home/pi/orj/* /home/pi/orj/
    rm -r /home/pi/orj/addons/point_of_sale/tools/posbox/overwrite_after_init
fi

# TODO: Remove this code when v16 is deprecated
orj_conf="addons/point_of_sale/tools/posbox/configuration/orj.conf"
if ! grep -q "server_wide_modules" $orj_conf; then
    echo "server_wide_modules=hw_drivers,hw_escpos,hw_posbox_homepage,point_of_sale,web" >> $orj_conf
fi

sudo service led-status start
