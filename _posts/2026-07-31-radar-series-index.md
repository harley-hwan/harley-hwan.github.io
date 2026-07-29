---
title: "(Radar) 레이다 신호처리 목차"
description: "24 GHz CW 레이다를 기준으로 단위·파장·데시벨 같은 기초부터 IQ 신호, CW와 FMCW의 갈림길, 그리고 수신 체인 구현까지 이어지는 시리즈 목차"
date: 2026-07-31 10:00:00 +0900
slug: 'radar-series-index'
categories: [Dev, Radar]
series: radar
series_order: -1
series_hub: true
pin: true
tags: [radar, radar-sensor, iq-signal, cw-radar, fmcw, doppler, signal-processing]
toc: false
---

24 GHz CW 레이다를 실제로 만지면서 필요했던 것들을 순서대로 정리한 시리즈다. 데이터시트를 읽는 데 필요한 기초에서 시작해, 센서가 뱉는 IQ 신호가 무엇인지, 그 IQ를 접느냐 접지 않느냐가 CW와 FMCW를 어떻게 가르는지, 마지막으로 CW 수신 체인을 코드로 어떻게 세우는지까지 이어진다.

0. [(Radar) 0. 레이다 개발 전에 알아야 할 기초](/posts/radar-fundamentals/) — 단위, 파장과 주파수, 주파수 밴드, 데시벨, 듀티 사이클, 도플러
1. [(Radar) 1. 레이다 센서의 IQ 신호 이해하기](/posts/radar-IQ-signal/) — 위상에 숨은 정보, 직교 복조, 왜 채널이 두 개여야 하는가
2. [(Radar) 2. CW 레이다와 FMCW 레이다 — 같은 IQ, 접느냐 접지 않느냐](/posts/cw-vs-fmcw-radar/) — 접기의 대가 $N$, 레인지 상관, 24 GHz 도플러의 실제 숫자
3. [(Radar) 3. CW 수신 체인 구현 — IQ 신호에서 속도와 각도 구하기](/posts/cw-receive-chain-cpp/) — DC 제거, I/Q 보정, 창, FFT, 피크 보간, 채널 위상차

### 함께 보면 좋은 글

- [(C++) 3채널 레이다 센서로 물체 운동의 스핀축 계산하기](/posts/cpp-3-channel-radar-sensor-spin-axis-calculation/) — 3편 8절 각도 계산의 응용. RX를 'ㄴ' 자로 놓고 상하·좌우 위상차에서 스핀축을 구한다
- [레이다 센서 신호 처리 및 검증 툴 (MFC)](/posts/RadarSensorProj/) — 원시 IQ 데이터를 눈으로 확인하는 시각화 툴

### 이 시리즈가 다루지 않는 것

범위를 미리 적어 둔다. 없어서 헤매는 것보다는 없다고 알고 넘어가는 편이 낫다.

- **펄스 레이다의 처리 체인.** 0편 8절에서 듀티 사이클로, 2편 7절에서 선택지로 언급하지만 펄스 압축과 거리 게이트는 다루지 않는다.
- **안테나 설계와 빔포밍.** 소자 간격 $\lambda/2$와 빔폭 $\approx \lambda/D$까지만 쓰고, 배열 합성과 MIMO 가상 배열은 결론에서 이름만 나온다.
- **RF 프런트엔드 회로.** 믹서와 LO는 블록으로만 다루고 LNA 설계, 정합, 기판 손실은 범위 밖이다.
- **표적 추적.** 3편은 프레임 하나까지다. 프레임을 시간축으로 잇는 문제는 다음 글에서 다룰 예정이다.
