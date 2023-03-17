#!/bin/sh
YESTERDAY=`/bin/date -d "-$1 days" "+%Y%m%d"`
MON=`/bin/date -d "-$1 days" "+%Y%m"`

CONDITION=$YESTERDAY"*.*.*.*"

#LINE_LIST="ABH125c_1 ABH250c_1 ABH125c_2 ABH250c_2"

## 신규 확장 라인 400/800 2개 추가 (라인명 확인 필요)
LINE_LIST="ABH125c_1 ABH250c_1 ABH125c_2 ABH250c_2 ABS400c"

DIR_LIST="NG NG_OK NG_XML XML"


for line in $LINE_LIST
do
  for dir in $DIR_LIST
  do
    echo "*******DATA : " $dir/$MON " *******"
    azcopy \
       --source /data/mccb/$line/$dir/$MON \
       --destination https://cj01vision001.blob.core.windows.net/mccb/$line/$dir/$MON \
       --dest-key T7Q7tncoj0Er29cvCK6DsU9w0gnM0tvfYoWOc1Btacx+TySBxPdx+h+n3YUghgpRpZUcSfkHiGgLX98wGDXnmA== \
       --include $CONDITION \
       --recursive \
       --quiet
  done
done
