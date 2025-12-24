---
title: STM32F Digital Board Firmware Download
description: Bash Script for STM32F Firmware Update
date: 2023-09-01 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, STM32F, firmware, download, bash]
---

# STM32F Digital Board Firmware Download via Bash


- 최초 작성일: 2023년 9월 1일(금)

## 목차



<br/>

## 코드

```bash
#!/bin/bash

# digital board(stm32f) firmware download 

FILE=$1
COUNT1=0
UNTIL=10

# STEP1 : FW File check(???())
if [ -f "$FILE" ]; then
 echo "FW File Check[ok]"
 sudo /home/pi/test/test_fwdown $FILE
 sleep 3
 echo 1 > /home/pi/test/fw_finish.log
 sudo rm -rf /home/pi/test/fw_down.log
else
 echo "file not exist!!! or file name is wrong" 
 exit 0
fi

# STEP2 : Wait 5 second until detect STM DUT  
while [ $COUNT1 -ne $UNTIL ]
 do
  USBis=`lsusb | grep -i "STM" | gawk -F" " '{printf $8}'`
  if [ "$USBis" == "STM" ]; then
   VEN=`lsusb | grep -i "STM" | gawk -F" " '{printf $6}' | gawk -F":" '{print $1}'`
   PRO=`lsusb | grep -i "STM" | gawk -F" " '{printf $6}' | gawk -F":" '{print $2}'`
   if [ "$VEN" == "0483" ] && [ "$PRO" == "df11" ]; then
    COUNT1=10
    echo "found STM DFU $FILE"
    sudo dfu-util -a 0 -D $FILE | tee /home/pi/test/fw_down.log
        sleep 7
    # check finished 
    sudo /home/pi/test/check_fw_finish.sh
    echo "DB Reset!!!" 
    #sudo /home/pi/test/test_dbrst
    sudo /home/pi/test/db_hwrst
    sudo /home/pi/test/usb_reset.sh
    exit 0
   fi
  else
   COUNT1=$(($COUNT1+1))
   echo "[FW_DOWN]Check STM DUT[$COUNT1]"
  fi
 sleep 0.5
 done

 echo "STM is Not founded [$VEN $PRO]" 
exit 0
```

<br/>

## 설명

이 Bash 스크립트는 STM32F 디지털 보드의 펌웨어를 다운로드하기 위한 프로세스를 제공한다.

#### **1. 주석 및 초기화**

```bash
#!/bin/bash

# digital board(stm32f) firmware download 

FILE=$1
COUNT1=0
UNTIL=10
```

- 스크립트는 Bash 셸에서 실행됨.
- `FILE` 변수에 첫 번째 인자 (스크립트를 실행할 때 전달되는 파일 이름)를 할당함.
- `COUNT1`은 초기값 0을 갖는 카운터 변수.
- `UNTIL` 변수는 값 10을 갖고, 어떤 조건이 충족될 때까지 대기할 최대 시간을 설정하는데 사용됨.

#### **2. 펌웨어 파일 확인 및 다운로드**

```bash
# STEP1 : FW File check(???())
if [ -f "$FILE" ]; then
 ...
else
 ...
fi
```

- STEP1은 펌웨어 파일을 확인하는 단계
- `if [ -f "$FILE" ]`를 통해 `$FILE`이 실제로 존재하는 파일인지 확인.
- 파일이 존재한다면, 이 파일은 STM32F 펌웨어 파일로 간주되며, 펌웨어 다운로드 작업 수행.
- 만약 파일이 존재하지 않으면, 오류 메시지가 출력되며 스크립트 종료.

#### **3. STM DUT 확인**

```bash
# STEP2 : Wait 5 second until detect STM DUT  
while [ $COUNT1 -ne $UNTIL ]
 ...
 done
```

- STEP2는 STM DUT (Device Under Test)를 감지할 때까지 최대 5초 동안 대기하는 단계.
- `lsusb` 명령은 시스템에 연결된 USB 장치 나열.
- 해당 장치 목록 중 "STM"이 포함된 장치를 찾아낸다.
- 찾아낸 장치의 Vendor ID (`VEN`)와 Product ID (`PRO`)를 추출한다.
- 만약 Vendor ID가 "0483"이고 Product ID가 "df11"인 경우, STM DUT가 감지된 것으로 판단하며, 펌웨어 다운로드 작업이 수행된다.

#### **4. 펌웨어 다운로드**

```bash
sudo dfu-util -a 0 -D $FILE | tee /home/pi/test/fw_down.log
```

- `dfu-util`은 USB DFU (Device Firmware Upgrade) 프로토콜을 사용하여 펌웨어를 다운로드하는 도구이다.
- 다운로드한 내용은 `/home/pi/test/fw_down.log` 파일에 로깅된다.

#### **5. 펌웨어 다운로드 완료 확인 및 장치 재설정**

```bash
sudo /home/pi/test/check_fw_finish.sh
echo "DB Reset!!!" 
sudo /home/pi/test/db_hwrst
sudo /home/pi/test/usb_reset.sh
```

- 다운로드 완료를 확인하기 위해 `check_fw_finish.sh` 스크립트 실행.
- 펌웨어 다운로드 후 장치를 재설정하기 위해 `db_hwrst`와 `usb_reset.sh` 스크립트를 차례대로 실행.

<br/>

요약하면, 이 스크립트는 STM32F 디지털 보드에 펌웨어를 다운로드하는 과정을 담고 있다.

파일 존재 여부를 확인한 후, STM DUT를 감지하고, 해당 장치에 펌웨어를 다운로드한 다음 장치를 재설정하는 작업을 수행한다.

