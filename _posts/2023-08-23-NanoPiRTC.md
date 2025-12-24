---
title: NanoPi의 RTC 설정 스크립트
description: "linux, bash, shell, script, date, hwclock"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, bash, shell, script, date, hwclock]
---

# NanoPi의 RTC 설정 스크립트

- 최초 작성일: 2023년 8월 23일(수)

## 전체 개요

이 스크립트는 사용자로부터 연, 월, 일, 시, 분, 초를 입력 받아 NanoPi의 시스템 시간을 설정하고, 해당 시간을 하드웨어 클록(RTC)에 동기화하는 역할을 한다.

<br/>

## 코드

```bash
#!/bin/bash

# kjh [2023.08.23]
# NanoPi set RTC

#echo "$0 start"

year=$1
mon=$2
day=$3
hour=$4
min=$5
sec=$6

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ] || [ -z $6 ]
then
    echo "para error !!! year mon day hour min(*hour 24 format) "
    exit 0
fi

date -s "$1-$2-$3 $4:$5:$6"

sleep 1
hwclock --localtime --systohc

#check
YEAR=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $1}'`
MON=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $2}'`
DAY=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $3}'`
HOUR=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $4}'`
MIN=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $5}'`

if [ "$2" == "$MON" ]; then
 echo "MON same"
else
 echo "MON not same"
 date -s "$1-$2-$3 $4:$5:$6"
 sleep 1
 hwclock --localtime --systohc
fi
if [ "$3" == "$DAY" ]; then
 echo "DAY same"
else
 echo "DAY not same"
 date -s "$1-$2-$3 $4:$5:$6"
 sleep 1
 hwclock --localtime --systohc
fi
if [ "$4" == "$HOUR" ]; then
 echo "HOUR same"
else
 echo "HOUR not same"
 date -s "$1-$2-$3 $4:$5:$6"
 sleep 1
 hwclock --localtime --systohc
fi

#echo "$0 end"

```

<br/>

## 설명

- 연, 월, 일, 시, 분, 초 인자를 받는다.

```bash
year=$1
mon=$2
day=$3
hour=$4
min=$5
sec=$6
```

- 실행 시, 모든 인자가 정확히 입력되었는지 확인하며, 만약 그렇지 않다면 에러 메시지를 출력하고 스크립트를 종료한다.

```bash
if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ] || [ -z $6 ]
then
    echo "para error !!! year mon day hour min(*hour 24 format) "
    exit 0
fi
```

- `date` 명령어를 이용해 시스템 시간을 사용자가 입력한 값으로 설정한다.

```bash
date -s "$1-$2-$3 $4:$5:$6"
```

- 이후 `hwclock` 명령어를 사용해 시스템 시간을 하드웨어 클록에 동기화한다.

```bash
hwclock --localtime --systohc
```

- `date` 명령어와 `gawk`를 결합하여 현재 시스템의 연, 월, 일, 시, 분 값을 추출한다.

```bash
YEAR=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $1}'`
MON=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $2}'`
DAY=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $3}'`
HOUR=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $4}'`
MIN=`sudo date +"%Y %m %d %H %M" | gawk -F" " '{print $5}'`
```

- 마지막 부분에서는 사용자의 입력값과 현재 시스템의 시간을 비교하며, 일치하지 않는 경우 시간을 다시 설정하고 RTC를 동기화한다.

이 스크립트는 특히 시간 설정이 중요한 임베디드 환경에서 유용하게 사용된다.
