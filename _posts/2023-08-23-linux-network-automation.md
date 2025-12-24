---
title: "리눅스 네트워크 자동화: 이더넷 디바이스 설정 스크립트"
description: "임베디드 시스템을 위한 네트워크 자동 구성 가이드"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, embedded, networking, bash, ethernet, automation, system-config]
---

# : 
- 최초 작성일: 2023년 8월 23일(수)

<br/>

## 

### 

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

### XML IP 

```bash
IP1=`cat /system_config.xml|grep -i "NET_CONFIG"|gawk -F"<" '{print $2}'|gawk -F">" '{print $2}'`
ETH_IP="192.168.1."$IP1
```
<br/>

## 

### 1. 

```bash
function ETH_INIT()
{
  sudo echo " "  >> /etc/network/interfaces
  sudo echo -n "allow-hotplug " >> /etc/network/interfaces
  sudo echo $ETH_NAME >> /etc/network/interfaces
  sudo echo -n "auto " >> /etc/network/interfaces
  sudo echo $ETH_NAME >> /etc/network/interfaces
  sudo echo "iface" $ETH_NAME "inet static" >> /etc/network/interfaces
  sudo echo "address $ETH_IP" >> /etc/network/interfaces
  sudo echo "netmask 255.255.255.0" >> /etc/network/interfaces
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
  sudo echo "source-directory /etc/network/interfaces.d" >> /etc/network/interfaces
  sudo echo "auto lo" >> /etc/network/interfaces
  sudo echo "iface lo inet loopback" >> /etc/network/interfaces
  sudo echo "allow-hotplug eth0" >> /etc/network/interfaces
  sudo echo "auto eth0" >> /etc/network/interfaces
  sudo echo "    iface eth0 inet static" >> /etc/network/interfaces
  sudo echo "    address 192.168.1.1" >> /etc/network/interfaces
  sudo echo "    netmask 255.255.255.0" >> /etc/network/interfaces
}
```

<br/>

## 

### 1. 

```bash
# 
ETH_NAME=`ifconfig | grep -i "eth" | gawk -F" " '{print$1}'`
echo "ETH_NAME: $ETH_NAME"

# IP 
ETH_ADR=`ifconfig $ETH_NAME|grep "inet "|gawk '{print $2}'`
echo "ETH ADR: $ETH_ADR"

# interfaces 
GET_NAME=`cat /etc/network/interfaces|grep $ETH_NAME|grep "inet static"|gawk -F" " '{print $2}'`
echo "GET_NAME: $GET_NAME"

# IP 
GET_ADR=`cat /etc/network/interfaces|grep "192.168.1"|gawk -F" " '{print $2}'`
echo "GET_ADR: $GET_ADR"
```

<br/>

## 

### 1. 

```bash
# 
ETH_STATUS=`ip link show|grep "eth"|gawk -F" " '{print $9}'`
echo "ETH_STATUS: $ETH_STATUS"

# 
if [ "$ETH_STATUS" != "UP" ]; then
    sudo ip link set $ETH_NAME up
    sleep 1
    ETH_STATUS=`ip link show|grep "eth"|gawk -F" " '{print $9}'`
    echo "ETH activation status: $ETH_STATUS"
fi
```

### 2. 

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

## 

### 1. 

```bash
function log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    logger -t network-config "$1"
}

function handle_error() {
    log_message "Error: $1"
    exit 1
}

# 
if [ ! -f "/etc/network/interfaces" ]; then
    handle_error "Network interfaces file not found"
fi
```

### 2. 

```bash
function backup_interfaces() {
    local backup_file="/etc/network/interfaces.backup.$(date '+%Y%m%d%H%M%S')"
    cp /etc/network/interfaces $backup_file
    log_message "Network configuration backed up to $backup_file"
}

# 
backup_interfaces
```

<br/>

## 
이 스크립트는 임베디드 리눅스 시스템에서 이더넷 인터페이스를 자동으로 감지하고 설정하는 강력한 도구다. 주요 기능은 다음과 같다:

1. 이더넷 인터페이스 자동 감지
2. 네트워크 설정 파일 자동 구성
3. IP 주소 자동 할당 및 변경
4. 오류 처리 및 로깅
5. 설정 백업 및 복구

이러한 자동화 스크립트는 임베디드 시스템의 초기 설정과 유지보수를 단순화하고, 설정 오류를 최소화하는데 도움을 준다.
