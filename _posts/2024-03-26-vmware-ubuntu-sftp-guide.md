---
title: "가상머신과 SFTP: VMware Ubuntu 환경에서의 네트워크 설정 가이드"
description: "ens33 네트워크 인터페이스를 통한 SFTP 연결 최적화"
date: 2024-03-26 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, ubuntu, vmware, networking, sftp, filezilla, ens33]
---

# SFTP: VMware Ubuntu 
- 최초 작성일: 2024년 3월 26일 (화)

<br/>

## 

### 
리눅스 시스템에서 네트워크 인터페이스는 다음과 같은 구조로 구성된다:

```plaintext
네트워크 스택 구조
├── 물리적 계층
│   ├── 실제 네트워크 카드
│   └── 가상 네트워크 어댑터
├── 데이터 링크 계층
│   ├── 인터페이스 명명 규칙
│   └── MAC 주소 관리
└── 네트워크 계층
    ├── IP 주소 할당
    └── 라우팅 테이블
```

<br/>

## ens33 

### 1. 
'ens33'의 각 부분이 나타내는 의미:
- 'en': Ethernet 네트워크
- 's': PCI 핫플러그 슬롯 번호
- '33': 특정 포트/슬롯 식별자

### 2. 
1. **네트워크 추상화**
   - 물리적/가상 네트워크 하드웨어 추상화
   - 드라이버와 운영체제 간 인터페이스 제공

2. **통신 제어**
   - 패킷 송수신 관리
   - 네트워크 버퍼링 처리
   - QoS(Quality of Service) 제어

<br/>

## 

### 1. 

```bash
# 
ip addr show ens33

# 
ethtool ens33
```

### 2. 

```bash
# 
sudo ip link set ens33 up

# DHCP IP 
sudo dhclient ens33

# IP ()
sudo ip addr add 192.168.1.100/24 dev ens33
```

### 3. 

```bash
# 
ping -c 4 8.8.8.8

# 
ip route show
```

<br/>

## SFTP 

### 1. SSH 

```bash
# SSH 
sudo apt install openssh-server

# 
sudo systemctl status ssh

# 
sudo ufw allow ssh
```

### 2. FileZilla 
1. **기본 연결 정보**
   - 프로토콜: SFTP
   - 포트: 22
   - 로그온 방식: 일반/키 파일

2. **고급 설정**
   
   ```plaintext
   최적화 설정
   ├── 전송 버퍼 크기: 4MB
   ├── 동시 연결 수: 2
   └── 전송 타입: Binary
   ```

<br/>

## 

### 1. 

```bash
# 
sudo ip link set ens33 down
sudo ip link set ens33 up

# DNS 
cat /etc/resolv.conf

# 
sudo journalctl -u networking.service
```

### 2. 
1. **MTU 최적화**

   ```bash
   # MTU 값 확인
   ip link show ens33

   # MTU 설정
   sudo ip link set ens33 mtu 9000
   ```

2. **TCP 튜닝**
   
   ```bash
   # TCP 윈도우 크기 조정
   sudo sysctl -w net.ipv4.tcp_wmem="4096 87380 16777216"
   sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
   ```

<br/>

## 

### 1. SSH 

```bash
# SSH 
sudo nano /etc/ssh/sshd_config

# 
PermitRootLogin no
PasswordAuthentication yes
MaxAuthTries 3
```

### 2. 

```bash
# UFW 
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH 
sudo ufw allow 22/tcp

# 
sudo ufw enable
```

<br/>

## 
VMware Ubuntu 환경에서 ens33 네트워크 인터페이스를 통한 SFTP 연결은 적절한 설정과 최적화를 통해 안정적이고 보안성 높은 파일 전송 환경을 구축할 수 있다. 네트워크 인터페이스의 특성을 이해하고 적절한 설정을 적용하는 것이 중요하며, 보안 측면도 함께 고려해야 한다.

