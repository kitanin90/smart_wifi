#!/usr/bin/env bash

exit_script() {
    trap - SIGINT SIGTERM
    kill -- -$$
    rm /flow-capture.pid.555
}

trap exit_script SIGINT SIGTERM

flow-capture -p /flow-capture.pid -w /var/log/flow -n 1440 0/172.20.0.1/555
export PID=`cat /flow-capture.pid.555`

while true; do
    ps -p ${PID} | grep 'flow-capture' > /dev/null
    if [[ $? != 0 ]]; then
        echo 'flow-capture down'
        exit 1
    fi

    flow-cat /var/log/flow/ | \
    flow-export -f3 -mUNIX_SECS,UNIX_NSECS,SYSUPTIME,EXADDR,DFLOWS,DPKTS,DOCTETS,FIRST,LAST,ENGINE_TYPE,ENGINE_ID,SRCADDR,DSTADDR,NEXTHOP,INPUT,OUTPUT,SRCPORT,DSTPORT,PROT,TOS,TCP_FLAGS,SRC_MASK,DST_MASK \
    -u "root:$MYSQL_ROOT_PASSWORD:db:3306:$MYSQL_DATABASE:panel_flow"

    sleep 30
done