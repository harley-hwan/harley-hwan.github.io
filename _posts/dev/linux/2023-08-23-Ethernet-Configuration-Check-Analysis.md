---
title: Ethernet Configuration Check via Script
description: "ifconfig와 grep, gawk로 이더넷 인터페이스의 IP를 확인하고 목표 IP와 다르면 재설정 스크립트를 실행하는 bash 스크립트를 분석한다."
date: 2023-08-23 10:00:00 +0900
slug: 'Ethernet-Configuration-Check-Analysis'
categories: [Dev, Linux]
tags: [linux, ifconfig, grep, gawk, sudo, bash, shell, script]
---
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

`ifconfig`는 네트워크 인터페이스의 구성을 표시하거나 수정하는 명령어다. 이 스크립트에서는 `ifconfig` 출력에서 `grep`으로 "enx" 패턴이 들어간 줄을 걸러 USB 이더넷 인터페이스 이름을 찾고, `gawk`로 구분자를 기준 삼아 필요한 필드만 잘라낸다. 이렇게 찾은 인터페이스 이름이 `ETH_NAME`에, 해당 인터페이스에 할당된 IP 주소가 `ETH_adr`에 들어가고, `ETH_IP`는 확인하려는 목표 IP 주소인 "192.168.8.3"이다.

조건문은 순서대로 인터페이스 이름이 존재하는지, 인터페이스에 IP 주소가 할당되어 있는지, 그리고 그 IP가 `ETH_IP`와 일치하는지 확인한다. 일치하지 않으면 `detect_eth.sh` 스크립트를 실행하고 네트워크 매니저 서비스를 재시작한다.

---

스크립트의 주 목적은 주어진 IP 주소와 현재 네트워크 인터페이스의 IP 주소를 확인하고, 불일치할 경우 네트워크 설정을 재구성하는 것이다.
