#!/usr/bin/env bash

exit_script() {
    trap - SIGINT SIGTERM
    kill -- -$$
    rm /flow-capture.pid.555
}

trap exit_script SIGINT SIGTERM

flow-capture -p /flow-capture.pid -w /var/log/flow -n 720 0/0.0.0.0/555
export PID=`cat /flow-capture.pid.555`

while true; do
    ps -p ${PID} | grep 'flow-capture' > /dev/null
    if [[ $? != 0 ]]; then
        echo 'flow-capture down'
        exit 1
    fi

    flow-cat /var/log/flow/ | \
    flow-export -f3 -mUNIX_SECS,EXADDR,SRCADDR,DSTADDR,SRCPORT,DSTPORT,PROT \
    -u "root:$MYSQL_ROOT_PASSWORD:db:3306:$MYSQL_DATABASE:panel_flow"

    rm -r /var/log/flow/*

    sleep 180
done