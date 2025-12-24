---
title: Ethernet Configuration Check via Script
description: "ifconfig, grep, gawk, sudo, bash, shell, script"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, ifconfig, grep, gawk, sudo, bash, shell, script]
---

# Ethernet Configuration Check via Script

- 최초 작성일: 2023년 8월 23일(수)

## 목차



<br/>

## 코드

```bash
#!/bin/bash
# kjh [2023.08.23]
# check eth

ETH_IP="192.168.8.3"
ETH_NAME=`ifconfig | grep -i "enx" | gawk -F" " '{print$1}'`
ETH_adr=`ifconfig $ETH_NAME|grep "inet addr:"|gawk -F":" '{print $2}'|gawk -F" " '{print $1}'`
echo $ETH_adr
echo $ETH_IP

if [ -z $ETH_NAME ]; then
 echo "is not eth name"
else
 if [ -z $ETH_adr ]; then
  echo "is not eth adr"
 else
  if [ $ETH_adr == $ETH_IP ]; then
        echo "ip is same"
  else
        ETH_Remake=1
        sudo /home/pi/test/detect_eth.sh
        sleep 1
        sudo service network-manager restart
        #sleep 1
        #sudo hostapd -B /home/pi/hostapd.conf
        echo "ip is not same, run detect_eth.sh"
  fi
 fi
fi
```

<br/>

## 설명

### **1. `ifconfig` 명령어**
- `ifconfig`: 네트워크 인터페이스의 구성을 표시하거나 수정하는 프로그램. 이 스크립트에서는 인터페이스의 이름과 IP 주소를 가져오기 위해 사용되었다.

### **2. `grep` 명령어**
- `grep`: 주어진 패턴과 일치하는 줄을 검색. 이 스크립트에서는 "enx"라는 패턴으로 네트워크 인터페이스 이름을 찾기 위해 사용되었다.

### **3. `gawk` 명령어**
- `gawk`: GNU awk의 줄임말로, 텍스트 처리 및 데이터 추출을 위한 프로그래밍 언어. 여기서는 특정 패턴에 일치하는 필드를 추출하기 위해 사용되었다.

### **4. 변수 설명**
- `ETH_IP`: 스크립트에서 확인하려는 IP 주소로, "192.168.8.3"로 설정.
- `ETH_NAME`: 현재 시스템의 네트워크 인터페이스 이름을 저장.
- `ETH_adr`: 해당 네트워크 인터페이스에 할당된 IP 주소를 저장.

### **5. 조건문 설명**
- 첫 번째 조건문은 `ETH_NAME` 변수의 값을 확인하여 네트워크 인터페이스 이름이 존재하는지 확인.
- 두 번째 조건문은 `ETH_adr` 변수의 값을 확인하여 인터페이스에 IP 주소가 할당되었는지 확인.
- 마지막 조건문은 `ETH_adr`의 IP 주소와 `ETH_IP`의 IP 주소가 일치하는지 확인. 일치하지 않을 경우, `detect_eth.sh` 스크립트를 실행하고 네트워크 매니저 서비스를 재시작.

---

스크립트의 주 목적은 주어진 IP 주소와 현재 네트워크 인터페이스의 IP 주소를 확인하고, 불일치할 경우 네트워크 설정을 재구성하는 것이다.
