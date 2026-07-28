---
title: "리눅스 네트워크 자동화: 이더넷 디바이스 설정 스크립트"
description: "임베디드 시스템을 위한 네트워크 자동 구성 가이드"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, embedded, networking, bash, ethernet, automation, system-config]
---
<br/>

## 스크립트 개요

임베디드 리눅스 장비를 여러 대 세팅하다 보면 장비마다 이더넷 설정을 잡아주는 일이 반복된다. 매번 콘솔에 들어가 /etc/network/interfaces를 손으로 고치는 대신, 이더넷 인터페이스를 감지해 설정 파일과 실제 IP를 비교하고 필요한 경우에만 다시 설정하는 스크립트를 만들었다. 장비별 IP의 마지막 자리는 시스템 설정 XML에서 읽어온다.

### 기본 설정 및 변수

```bash
#!/bin/bash

ETH_IP="192.168.1.100"
ENX_STATUS=0

if [ -z $1 ]; then
 IP=100
else
 IP=$1
fi
```

### XML 파싱 및 IP 설정

```bash
IP1=`cat /system_config.xml|grep -i "NET_CONFIG"|gawk -F"<" '{print $2}'|gawk -F">" '{print $2}'`
ETH_IP="192.168.1."$IP1
```
<br/>

## 구현 세부사항

### 1. 네트워크 설정 초기화 함수

```bash
function ETH_INIT()
{
  echo " " | sudo tee -a /etc/network/interfaces > /dev/null
  echo "allow-hotplug $ETH_NAME" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "auto $ETH_NAME" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "iface $ETH_NAME inet static" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "address $ETH_IP" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "netmask 255.255.255.0" | sudo tee -a /etc/network/interfaces > /dev/null
  sudo ifconfig $ETH_NAME $ETH_IP netmask 255.255.255.0
}

function ETH_CHANGE_IP()
{
  sudo sed -i "s/192.168.1.100/192.168.1.$IP/g" /etc/network/interfaces
  sudo ifconfig $ETH_NAME $ETH_IP netmask 255.255.255.0
}

function INTERFACES_INIT()
{
  sudo rm -rf /etc/network/interfaces
  sleep 1
  echo "source-directory /etc/network/interfaces.d" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "auto lo" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "iface lo inet loopback" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "allow-hotplug eth0" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "auto eth0" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "    iface eth0 inet static" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "    address 192.168.1.1" | sudo tee -a /etc/network/interfaces > /dev/null
  echo "    netmask 255.255.255.0" | sudo tee -a /etc/network/interfaces > /dev/null
}
```

파일에 쓸 때 `sudo echo ... >> 파일` 형태를 쓰면 리다이렉션이 sudo 권한 밖의 현재 쉘에서 일어나기 때문에, 비root 사용자로 실행하면 권한 오류가 난다. 그래서 `sudo tee -a`로 append한다.

<br/>

## 주요 함수 분석

### 1. 이더넷 인터페이스 검출

```bash
# 이더넷 디바이스 이름 검출
ETH_NAME=`ifconfig | grep -i "eth" | gawk -F" " '{print$1}'`
echo "ETH_NAME: $ETH_NAME"

# 현재 IP 주소 확인
ETH_ADR=`ifconfig $ETH_NAME|grep "inet "|gawk '{print $2}'`
echo "ETH ADR: $ETH_ADR"

# interfaces 파일에서 설정 확인
GET_NAME=`cat /etc/network/interfaces|grep $ETH_NAME|grep "inet static"|gawk -F" " '{print $2}'`
echo "GET_NAME: $GET_NAME"

# 설정된 IP 주소 확인
GET_ADR=`cat /etc/network/interfaces|grep "192.168.1"|gawk -F" " '{print $2}'`
echo "GET_ADR: $GET_ADR"
```

<br/>

## 실행 흐름과 동작 원리

### 1. 인터페이스 상태 확인 및 활성화

```bash
# 이더넷 상태 확인
ETH_STATUS=`ip link show|grep "eth"|gawk -F" " '{print $9}'`
echo "ETH_STATUS: $ETH_STATUS"

# 필요시 인터페이스 활성화
if [ "$ETH_STATUS" != "UP" ]; then
    sudo ip link set $ETH_NAME up
    sleep 1
    ETH_STATUS=`ip link show|grep "eth"|gawk -F" " '{print $9}'`
    echo "ETH activation status: $ETH_STATUS"
fi
```

### 2. 네트워크 설정 검증 및 적용

```bash
if [ -z $ETH_NAME ]; then
    echo "Error: No ethernet interface detected"
    exit 1
else
    echo "Configuring ethernet interface..."
    if [ -z $GET_NAME ]; then
        echo "Initializing network configuration..."
        ETH_INIT
        exit 0
    else
        echo "Checking IP configuration..."
        if [ "$ETH_ADR" == "$ETH_IP" ]; then
            echo "IP configuration is correct"
        else
            echo "Updating network configuration..."
            INTERFACES_INIT
            ETH_INIT
            exit 0
        fi
    fi
fi
```

<br/>

## 확장 예시

오류 처리나 설정 백업이 필요하면 다음처럼 덧붙일 수 있다. 아래 내용은 위 스크립트에는 포함되어 있지 않다.

### 1. 오류 처리 및 로깅

```bash
function log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    logger -t network-config "$1"
}

function handle_error() {
    log_message "Error: $1"
    exit 1
}

# 사용 예시
if [ ! -f "/etc/network/interfaces" ]; then
    handle_error "Network interfaces file not found"
fi
```

### 2. 네트워크 설정 백업

```bash
function backup_interfaces() {
    local backup_file="/etc/network/interfaces.backup.$(date '+%Y%m%d%H%M%S')"
    cp /etc/network/interfaces $backup_file
    log_message "Network configuration backed up to $backup_file"
}

# 설정 변경 전 백업 실행
backup_interfaces
```

<br/>

## 결론
이더넷 인터페이스 감지부터 설정 파일 구성, IP 할당까지 스크립트 하나로 처리하게 되면서 장비를 세팅할 때 네트워크 설정에 손댈 일이 거의 없어졌다.
