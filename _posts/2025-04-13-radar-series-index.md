---
title: "(Radar) 레이다 신호처리 목차"
description: "단위·파장·데시벨 같은 기초부터 IQ 신호, CW와 FMCW의 갈림길, CW 수신 체인 구현, 그리고 펄스 레이다까지 이어지는 레이다 신호처리 시리즈 목차"
date: 2025-04-13 10:00:00 +0900
slug: 'radar-series-index'
categories: [Dev, Radar]
series: radar
series_order: -1
series_hub: true
pin: true
tags: [radar, radar-sensor, iq-signal, cw-radar, fmcw, pulse-radar, doppler, signal-processing]
toc: false
---

레이다 신호처리를 실제로 만지면서 필요했던 것들을 순서대로 정리한 시리즈다. 데이터시트를 읽는 데 필요한 기초에서 시작해, 센서가 뱉는 IQ 신호가 무엇인지, 그 IQ를 접느냐 접지 않느냐가 CW와 FMCW를 어떻게 가르는지, CW 수신 체인을 코드로 어떻게 세우는지, 그리고 감시·추적 레이다의 표준인 펄스 파형은 무엇이 다른지까지 이어진다.

2~4장은 아직 비어 있다. 탐지거리에 영향을 미치는 요소, 용어, 개발 관련 정책 용어 순으로 채울 자리다.

0. [(Radar) 0. 레이다 개발 전에 알아야 할 기초](/posts/radar-fundamentals/) — 단위, 파장과 주파수, 주파수 밴드, 데시벨, 듀티 사이클, 도플러
1. [(Radar) 1. 레이다의 특성](/posts/radar-characteristics/) — 재는 것 넷, 세 개의 '최대', 밴드별 성격, 레이다 방정식과 SNR, 계통도와 전시
2. (Radar) 2. 레이다 탐지거리에 영향을 미치는 요소 — 작성 예정
3. (Radar) 3. 레이다 용어 — 작성 예정
4. (Radar) 4. 개발 관련 정책 용어 — 작성 예정
5. [(Radar) 5. 레이다 센서의 IQ 신호 이해하기](/posts/radar-IQ-signal/) — 위상에 숨은 정보, 직교 복조, 왜 채널이 두 개여야 하는가
6. [(Radar) 6. CW 레이다와 FMCW 레이다 — 같은 IQ, 접느냐 접지 않느냐](/posts/cw-vs-fmcw-radar/) — 접기의 대가 $N$, 레인지 상관, 24 GHz 도플러의 실제 숫자
7. [(Radar) 7. CW 수신 체인 구현 — IQ 신호에서 속도와 각도 구하기](/posts/cw-receive-chain-cpp/) — DC 제거, I/Q 보정, 창, FFT, 피크 보간, 채널 위상차
8. [(Radar) 8. PW 레이다 — 펄스로 거리를 재는 법](/posts/pw-radar/) — 두 개의 벽, 거리 모호성, 펄스 압축, PRF 체제, MTI와 blind speed, 데이터 큐브
9. [(Radar) 9. 표적 추적 — 검출 목록을 트랙으로 잇기](/posts/radar-tracking/) — 찌그러진 오차 타원, 칼만과 α-β, 게이팅과 연관, IMM, 트랙 관리, NIS 검정
10. [(Radar) 10. 위상배열 레이다 — 관성 없는 빔이 바꾸는 것](/posts/phased-array-radar/) — 배열 인자와 조향, 격자엽, 스캔 손실, 빔 스퀸트, AESA와 디지털 배열, 자원 관리

5~7장은 24 GHz 근거리 CW 를 기준으로 쓰고, 8~10장은 X 밴드 감시 레이다로 기준을 옮긴다. 파형이 바뀌면 숫자 감각이 통째로 달라지기 때문이다. 8장까지가 전파를 검출 목록으로 바꾸는 과정이고, 9장이 그 목록을 트랙으로 바꾸는 과정이라면, 10장은 그 트랙이 다시 다음 빔을 어디로 보낼지 정하는 과정이다. 고리가 10장에서 닫힌다.

### 함께 보면 좋은 글

- [(C++) 3채널 레이다 센서로 물체 운동의 스핀축 계산하기](/posts/cpp-3-channel-radar-sensor-spin-axis-calculation/) — 7장 각도 계산의 응용. RX를 'ㄴ' 자로 놓고 상하·좌우 위상차에서 스핀축을 구한다
- [레이다 센서 신호 처리 및 검증 툴 (MFC)](/posts/RadarSensorProj/) — 원시 IQ 데이터를 눈으로 확인하는 시각화 툴

### 이 시리즈가 다루지 않는 것

범위를 미리 적어 둔다.

- **안테나 소자 설계.** 10장은 배열 수준까지다. 개별 방사 소자의 형상과 정합, 소자 간 상호 결합(mutual coupling)은 범위 밖이다.
- **RF 프런트엔드 회로.** 믹서와 LO는 블록으로만 다루고 LNA 설계, 정합, 기판 손실, 송신관은 범위 밖이다.
- **다중 센서 융합.** 9장은 레이다 한 대까지다. 센서 정합(registration)과 순서가 뒤바뀐 측정은 이름만 짚고 넘어간다.
