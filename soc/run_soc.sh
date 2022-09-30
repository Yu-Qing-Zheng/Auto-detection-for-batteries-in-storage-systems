#!/bin/bash
while :
do
    date
    plcs=`cat plcs.txt`
    for i in $plcs
    do
        nohup /usr/local/python3/bin/python3 main_entry.py $i >> logs/plc_$i.log 2>&1 & 
        # nohup /usr/local/python3/bin/python3 main_entry.py $i >> /dev/null 2>&1 &
    done
    sleep 60
done
