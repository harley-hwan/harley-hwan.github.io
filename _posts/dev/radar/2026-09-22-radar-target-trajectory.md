---
title: "(Radar) 13. 표적 궤적 모의 — 초기값과 기동 지시에서 시각별 참값 궤적을 만들기"
description: "추적 필터를 시험하려면 표적이 실제로 어디에 있었는지 참값이 먼저 있어야 한다 — 표적과 기동을 어떤 값으로 받아 어떤 구조체에 담는지, G 값 하나를 선회 각속도로 바꾸는 식과 그 가정, 기수 방향 속력을 동체·NED·ECEF 로 두 번 돌려 속도 벡터로 만드는 법, 반 스텝 중점법으로 0.1 초씩 전진하는 이유, 수평을 어느 자리에서 잡아야 고도가 지켜지는지, 그리고 60 초 기본 시나리오와 지그재그 응용 시나리오를 C 로 돌려 숫자와 그림으로 확인하기까지."
date: 2026-09-22 10:00:00 +0900
slug: 'radar-target-trajectory'
categories: [Dev, Radar]
series: radar
series_order: 13
tags: [radar, target-simulation, trajectory, constant-turn-rate, midpoint-method, ecef, ned, radar-sensor]
math: true
---

이번 장에서는 표적 궤적 모의를 다루겠다. 표적의 초기 위치·자세·속력과 기동 지시를 넣으면 0.1 초마다 표적이 어디에 있는지 계산해 위도·경도·고도로 내놓는 프로그램이다. 표적을 어떤 값으로 받아 어떤 구조체에 담을지, 기동 지시 한 줄을 각속도로 어떻게 바꿀지, 속력 하나를 ECEF 속도 벡터로 어떻게 만들지, 한 스텝을 어떻게 전진시킬지를 차례로 정리하고, 마지막에 60 초 기본 시나리오와 지그재그 기동을 넣은 응용 시나리오를 C 로 돌려 확인하겠다.

조건은 이렇게 잡았다. 시뮬레이션 시간은 60 초, 갱신 간격은 0.1 초다. 표적은 10 개까지, 표적마다 기동은 30 개까지 둘 수 있어야 하고, 표적의 위치와 속도는 ECEF 좌표계에서 갱신하며 결과는 위경도로 낸다. 플랫폼은 레이다를 실은 우리 쪽이고, 여기서는 정지해 있는 것으로 둔다.

| | 위도 [°] | 경도 [°] | 고도 [m] | 속력 [m/s] | 자세 (roll, yaw, pitch) [°] |
|---|---:|---:|---:|---:|---|
| 플랫폼 | 32.0 | 126.0 | 0 | 0 | (0, 0, 0) |
| 대함 표적 | 32.125 | 126.03 | 0 | 30 | (0, 270, 0) 서쪽 |
| 대공 표적 | 32.12 | 126.0 | 300 | 200 | (0, 180, 0) 남쪽 |

좌표계와 변환식은 [12장](/posts/radar-coordinate-frames/)에 정리해 두었고, 여기서는 그때 쓴 변환 함수를 그대로 가져다 쓴다.

* * *

## 1. 궤적 모의가 하는 일

레이다 처리를 시험하려면 표적이 실제로 어디에 있었는지를 아는 쪽이 있어야 한다. 그 참값을 만드는 블록이 궤적 모의다. 뒤에 오는 측정 모의가 이 참값을 안테나 기준 거리·각도로 바꾸고 잡음을 더하며, 추적 필터는 그 측정값으로 표적 상태를 추정한다. 추적이 맞게 됐는지는 맨 앞 블록이 만든 참값과 비교해서 판정한다.

![레이다 처리 흐름에서 궤적 모의가 놓이는 자리](/assets/img/posts/radar-target-trajectory/fig1-sim-chain.svg){: width="860"}
_그림 1. 궤적 모의는 처리 흐름의 맨 앞에서 참값을 만든다. 잡음은 여기서 넣지 않고 다음 블록이 더한다._

표적 하나는 입력값 일곱 개로 정한다. 위도·경도·고도, 속력, 그리고 roll·pitch·yaw 다. 속도는 크기만 받고 방향은 자세각이 정한다. yaw 가 180° 면 기수가 남쪽이라 속력 200 m/s 하나로 남쪽 200 m/s 속도가 된다. 계산할 때는 이 일곱 값을 ECEF 위치 세 성분, ECEF 속도 세 성분, 자세각 셋, 모두 아홉 개의 상태값으로 바꿔 둔다.

위치를 ECEF 에서 갱신하는 데는 이유가 있다. 위경도는 각도라서 속도에 시간을 곱해 더할 수 없다. 국지 수평 좌표계 NED 는 원점이 자리마다 달라서 표적 둘을 한 좌표로 둘 수 없다. ECEF 는 지구에 고정된 직교 좌표라 위치에 속도 × 시간을 그대로 더할 수 있고, 표적이 몇 개든 같은 좌표에 놓인다. 결과를 위경도로 내는 것은 사람이 읽고 뒤쪽 블록이 쓰는 형식이기 때문이다.

* * *

## 2. 표적과 기동을 담는 구조체

기동 한 건은 네 값으로 적는다. 어느 축으로 도는가, 얼마나 세게 도는가, 언제부터 언제까지인가다. 세기는 G 값의 크기로, 도는 방향은 부호로 받는다.

```c
// 기동 회전축. 기동 입력의 축 번호를 그대로 쓴다.
typedef enum
{
	TGT_TURN_NONE	= 0,
	TGT_TURN_ROLL	= 1,
	TGT_TURN_YAW	= 2,
	TGT_TURN_PITCH	= 3
} EN_TurnType;

// 기동 1건. gravityValue 부호가 회전 방향. + 는 우측 뱅크 / 우선회 / 기수 상승.
typedef struct
{
	EN_TurnType				enTurnType;						// 회전축 (0 없음, 1 Roll, 2 Yaw, 3 Pitch)
	FLOAT64					gravityValue;					// [G] 세기, 부호가 회전 방향
	FLOAT64					startTime;						// [s] 시작 시각
	FLOAT64					endTime;						// [s] 종료 시각
} ST_TargetManeuver;

// 표적 초기 설정. 속도는 기수 방향 크기 V_heading 만 입력.
typedef struct
{
	STRUCT_Coord_Lla		st_InitLla;						// 초기 위도, 경도 [rad], 고도 [m]
	STRUCT_Coord_Attitude	st_InitAtt;						// 초기 Roll, Pitch, Yaw [rad]
	FLOAT64					headingSpeed;					// 속력 V_heading [m/s]
	INT32					nManeuverNum;					// 기동 수 (0 ~ TGT_MAX_MANEUVER_NUM)
	ST_TargetManeuver		st_Maneuver[TGT_MAX_MANEUVER_NUM];	// 기동 목록
} ST_TargetInit;
```

표적 10 개와 기동 30 개라는 상한은 고정 배열로 두고, 화면에서 추가 단추를 누를 때 개수를 막는다. 각도는 구조체 안에서 전부 라디안이고 도 단위는 화면에서 읽고 쓸 때만 바꾼다.

설정과 결과는 구조체를 따로 둔다. 설정 `ST_SimConfig` 는 시뮬레이션 시간과 간격, 플랫폼 하나, 표적 열 개를 담아 처음에 한 번 읽는다. 결과 `ST_SimSample` 은 한 시각의 플랫폼과 표적 상태를 담고 스텝마다 새로 나온다. 플랫폼도 표적과 같은 상태 구조체 `ST_TargetState` 를 쓴다. 기동이 없을 뿐 움직이는 방식이 같기 때문이다.

```c
// 플랫폼 또는 표적 하나의 한 시각 상태. 위치, 속도는 ECEF 이고 LLA 는 출력용.
typedef struct
{
	FLOAT64					simTime;						// 시각 [s]
	STRUCT_Coord_Rect		st_PosEcef;						// ECEF 위치 [m]
	STRUCT_Coord_Rect		st_VelEcef;						// ECEF 속도 [m/s]
	STRUCT_Coord_Lla		st_Lla;							// 위도, 경도 [rad], 고도 [m]
	STRUCT_Coord_Attitude	st_Att;							// Roll, Pitch, Yaw [rad]
} ST_TargetState;

// 한 시각의 결과. 플랫폼, 표적 상태.
typedef struct
{
	FLOAT64					simTime;						// 시각 [s] = nStepIndex * stepTime
	INT32					nStepIndex;						// 스텝 번호 (0 ~ nStepNum)
	INT32					nTargetNum;						// 표적 수
	ST_TargetState			st_Platform;					// 플랫폼 상태
	ST_TargetState			st_Target[TGT_MAX_TARGET_NUM];	// 표적 상태 (nTargetNum 개)
} ST_SimSample;

// 시뮬레이션 진행 상태. 복사해 둔 설정 포함.
typedef struct
{
	INT32					nStepNum;						// 스텝 수 (결과는 nStepNum + 1 개)
	ST_SimSample			st_Sample;						// 가장 최근 결과
	ST_SimConfig			st_Config;
} ST_SimState;
```

![설정과 결과 구조체의 관계](/assets/img/posts/radar-target-trajectory/fig2-structs.svg){: width="860"}
_그림 2. 설정은 처음 한 번만 읽고, 스텝마다 바뀌는 것은 결과뿐이다. 화면 쪽은 함수 둘과 구조체 둘만 본다._

계산을 맡는 함수는 둘이고, 둘 다 진행 상태 `ST_SimState` 하나를 받는다. `f_Tgt_InitSim` 을 한 번 부르면 설정을 그 안에 복사하고 스텝 수를 정한 뒤 0 초 결과를 만든다. `f_Tgt_StepSim` 을 부를 때마다 그 안의 결과 `st_Sample` 이 0.1 초 뒤 상태로 바뀐다. 600 번 부르면 60 초가 되고, 0 초를 포함해 결과는 601 개다. 화면 쪽은 설정을 채워 넘기고 스텝마다 `st_Sample` 을 꺼내 읽기만 하면 된다. 헤더에는 그림을 그릴 때 ECEF, NED, 위경도를 서로 바꾸는 함수 셋도 있지만 궤적 계산에는 관여하지 않는다.

기동 구간은 시작 시각을 포함하고 종료 시각은 포함하지 않는 반열린 구간으로 둔다. 한 기동의 종료 시각에 다음 기동이 바로 시작할 수 있게 하려는 것이다. 구간이 겹치면 목록 앞쪽 기동이 우선하고, 어느 구간에도 들지 않는 시각에는 각속도가 0 이라 직진한다.

* * *

## 3. G 값 하나를 각속도로

기동 지시에서 받는 값은 G 하나인데 계산에 필요한 것은 1 초에 몇 도 도는가, 곧 각속도다. 속력 $V$ 로 원을 그리며 돌 때 중심 쪽으로 필요한 가속도를 구심가속도(centripetal acceleration)라 하고, 크기는 $V\omega$ 다. 이 가속도를 중력가속도 $g$ 의 $n$ 배로 두면 각속도와 선회 반경이 바로 나온다.

$$
\omega = \frac{n\,g}{V}, \qquad R = \frac{V}{\omega} = \frac{V^2}{n\,g}
$$

속력이 분모에 있어서 같은 G 라도 빠른 표적일수록 천천히 돌고 반경은 속력의 제곱으로 벌어진다.

| G 값 | 30 m/s 의 각속도 [°/s] | 30 m/s 의 반경 [m] | 200 m/s 의 각속도 [°/s] | 200 m/s 의 반경 [m] |
|---:|---:|---:|---:|---:|
| 1 | 18.7 | 92 | 2.8 | 4 079 |
| 2 | 37.5 | 46 | 5.6 | 2 039 |
| 4 | 74.9 | 23 | 11.2 | 1 020 |
| 8 | 149.8 | 11 | 22.5 | 510 |

![같은 G 값에서 속력에 따라 달라지는 선회](/assets/img/posts/radar-target-trajectory/fig3-turn-rate.svg){: width="860"}
_그림 3. 왼쪽은 느린 표적이 1 G, 빠른 표적이 8 G 로 도는 원을 같은 축척으로 그린 것이다. 8 배 센 기동인데도 빠른 쪽의 원이 훨씬 크다. 오른쪽은 90° 를 도는 데 걸리는 시간이다._

기동 표의 한 줄로 쓰면 이렇다. 대공 표적이 12 초부터 20 초까지 우측으로 4 G 면 `{ TGT_TURN_YAW, 4.0, 12.0, 20.0 }` 이고, 각속도는 $4 \times 9.80665 / 200 = 0.196$ rad/s, 초당 11.2° 라 8 초 동안 89.9° 를 돌아 거의 직각으로 꺾인다. 반경은 1 020 m 다.

이 글에 실은 코드는 저장소 코드에서 비교 실험용 인자(플랫폼 기준 계산, 비중점법)와 계산 로그 기록 인자를 뺀 것이다. 흐름은 같다. 아래의 `ST_AttRate` 는 Roll·Pitch·Yaw 가 1 초에 바뀌는 양 [rad/s] 셋을 담는 구조체다. 코드는 지금 시각에 걸린 기동을 찾아 이 식 한 줄로 각속도를 만들고, 기동 축 한 칸에만 넣는다.

```c
// simTime 에 걸린 기동의 각속도 반환. 기동 없으면 0.
static ST_AttRate f_Tgt_GetAttRate(const ST_TargetInit *st_Target, FLOAT64 simTime)
{
	ST_AttRate				st_AttRate = { 0.0, 0.0, 0.0 };
	const ST_TargetManeuver	*st_ActiveManeuver = NULL;
	const ST_TargetManeuver	*st_Maneuver;
	FLOAT64					omega;
	INT32					nManeuver;

	for (nManeuver = 0; nManeuver < st_Target->nManeuverNum; nManeuver++)
	{
		st_Maneuver = &st_Target->st_Maneuver[nManeuver];

		if ((st_ActiveManeuver == NULL) && (st_Maneuver->startTime <= simTime) && (simTime < st_Maneuver->endTime))
		{
			st_ActiveManeuver = st_Maneuver;
		}
	}

	if (st_ActiveManeuver != NULL)
	{
		// 각속도 omega = n * g / V.
		omega = (st_ActiveManeuver->gravityValue * G_FORCE) / st_Target->headingSpeed;

		switch (st_ActiveManeuver->enTurnType)
		{
		case TGT_TURN_ROLL:		st_AttRate.Roll = omega;	break;
		case TGT_TURN_YAW:		st_AttRate.Yaw = omega;		break;
		case TGT_TURN_PITCH:	st_AttRate.Pitch = omega;	break;
		case TGT_TURN_NONE:
		default:											break;
		}
	}

	return st_AttRate;
}
```

> 이 식은 G 값을 구심가속도의 크기로 읽은 것이다. 항공기 문헌의 하중배수(load factor) $n$ 으로 읽으면 양력의 수평 성분만 선회에 쓰여 $\omega = g\sqrt{n^2 - 1}/V$ 가 되고, 1 G 는 수평 비행이라 돌지 않는다. 기동 입력의 Gravity Value 는 회전의 세기로 쓰기로 했으므로 앞의 식을 썼다. 어느 해석인지는 입력을 만드는 쪽과 맞춰 두어야 한다.
{: .prompt-warning }

회전축에 따라 궤적에 미치는 영향이 다르다. yaw 기동은 수평면에서 방향을 바꾸는 선회다. pitch 기동은 기수를 들고 내려 상승과 하강을 만든다. 200 m/s 로 날다가 pitch 가 10° 가 되면 수직 성분이 $200 \sin 10° = 34.7$ m/s 가 된다. roll 기동은 자세값만 바꾸고 궤적은 바꾸지 않는다. 속도가 동체 x 축을 따라 있어서 그 축 둘레로 돌리는 roll 로는 속도 방향이 변하지 않기 때문이다. 실제 항공기는 기체를 기울여 선회하지만 이 모의에서는 선회를 yaw 로 바로 지시한다.

이 모의가 전제하는 운동 모델을 적어 둔다. 속도가 늘 동체 x 축을 따르고 바람·받음각·옆미끄럼이 없으므로 yaw 는 기수 방향이자 진행 방향이고, pitch 는 기수 각도이자 비행경로각(flight-path angle)이다. 실제 항공기는 바람 때문에 기수 방향과 진행 방향이 다르고 받음각 때문에 pitch 와 비행경로각이 다르지만, 궤적 참값에 필요한 것은 진행 방향과 비행경로각이므로 입력을 그 뜻으로 읽으면 된다. 각속도는 roll·pitch·yaw 값에 바로 더하는 오일러각 변화율이지 동체축 각속도가 아니다. 속력은 상수라 상승·하강에 따른 속력 교환이 없다. 10° 로 오르며 200 m/s 를 유지하려면 실제로는 $g \sin 10° = 1.70$ m/s² 의 감속을 추력으로 메워야 하는데 모의는 그 부분을 생략한다. pitch 기동에는 수평으로 되돌리는 동작이 없어서 1 G 를 10 초 걸면 pitch 가 28.1° 가 되고 상승률이 94 m/s 에 이르며, 32.0 초면 90° 에 닿아 오일러각의 특이점에 든다. 상승했다가 수평으로 돌아오려면 부호가 반대인 pitch 기동을 하나 더 넣어야 한다. 기동 한 건은 축 하나만 돌리고 구간이 겹치면 앞 기동만 적용되므로 상승 선회처럼 두 축이 함께 도는 기동은 표현하지 못한다. 걸린 기동의 각속도를 모두 더하도록 바꾸면 된다. 기동 시작과 끝에서 각속도가 0 에서 $\omega$ 로 한 번에 바뀌는 것도 모델의 선택이고, 추적 필터에게는 가장 급한 경우라 시험용으로 알맞다.

입력 검사는 코어가 하지 않으므로 화면 쪽에서 막아야 한다. 각속도 식의 분모가 속력이라 속력 0 인 표적에 기동이 걸리면 각속도가 무한대가 되고 자세와 위치가 모두 NaN 이 되는데, 오류 없이 조용히 진행된다. 기동이 있는 표적은 속력이 0 보다 커야 하고, 시작은 종료보다 앞서야 하며, 종료는 시뮬레이션 시간 안에 있어야 한다. yaw 는 되감지 않고 계속 더해 가므로 남쪽을 보던 표적이 좌로 90° 를 네 번 돌면 −180° 로 찍힌다. 삼각함수에는 영향이 없지만 결과 표와 CSV 에 그대로 나가므로 출력할 때 0 ~ 360° 로 되감아 두는 편이 읽기 좋다.

* * *

## 4. 속력 하나를 속도 벡터로

입력은 기수 방향 속력 하나인데 위치에 더하려면 ECEF 의 x·y·z 세 성분이 있어야 한다. 그래서 회전을 두 번 한다. 동체 좌표계에서 $(V, 0, 0)$ 인 속도를 자세각으로 돌리면 북·동·아래 성분이 되고, 그것을 표적이 있는 자리의 위도·경도로 한 번 더 돌리면 ECEF 속도가 된다.

$$
\mathbf{v}_{ned} = C_{ned \leftarrow body}(\phi, \theta, \psi)\begin{bmatrix} V \\ 0 \\ 0 \end{bmatrix}, \qquad
\mathbf{v}_{ecef} = C_{ecef \leftarrow ned}(\varphi, \lambda)\,\mathbf{v}_{ned}
$$

![속력 하나를 두 번 돌려 ECEF 속도 벡터로 만드는 과정](/assets/img/posts/radar-target-trajectory/fig4-velocity-chain.svg){: width="860"}
_그림 4. 첫 회전은 자세각이, 둘째 회전은 표적 자리의 위도·경도가 정한다. 속도는 방향만 있어서 회전만 하고 원점은 옮기지 않는다._

대공 표적으로 따라가면 이렇다. yaw 180° 로 200 m/s 면 NED 속도는 북쪽 성분이 $-200$ 이라 $(-200, 0, 0)$ m/s 다. 위도 32.12°, 경도 126.0° 로 돌리면 ECEF 속도는 $(-62.5, 86.0, -169.4)$ m/s 이고 크기는 그대로 200 m/s 다. 대함 표적은 yaw 270° 로 30 m/s 라 NED 로 $(0, -30, 0)$, ECEF 로 $(24.3, 17.6, 0.0)$ m/s 다.

```c
// 동체 속도 (V, 0, 0) -> NED -> ECEF 속도.
static STRUCT_Coord_Rect f_Tgt_GetVelEcef(const STRUCT_Coord_Attitude *st_Att, const STRUCT_Coord_Lla *st_Lla, FLOAT64 headingSpeed)
{
	STRUCT_Coord_Rect	st_VelNed;
	STRUCT_Coord_Rect	st_VelEcef;

	// 동체 -> NED. 인자 순서 Roll, Yaw, Pitch.
	st_VelNed = f_Trans_Body_To_Ned(headingSpeed, 0.0, 0.0, st_Att->Roll, st_Att->Yaw, st_Att->Pitch);

	// NED -> ECEF. 기준점 0 으로 회전만 적용. 북 · 동 · 아래는 표적 자리 기준.
	st_VelEcef = f_Trans_Ned_To_Ecef(st_VelNed.x, st_VelNed.y, st_VelNed.z, 0.0, 0.0, 0.0, st_Lla->Lat, st_Lla->Lon);

	return st_VelEcef;
}
```

두 회전은 기존 좌표변환 함수를 그대로 부른 것이고 새로 쓴 부분은 둘을 이어 붙인 것뿐이다. 위치를 옮기는 함수에 기준점 자리를 0 으로 주면 더하는 것이 없어 회전만 남는다.

> 변환 함수는 인자 순서가 이름과 다르게 생각될 수 있어 적어 둔다. `f_Trans_Body_To_Ned` 는 자세각을 Roll, Yaw, Pitch 순서로 받아 Yaw 가 가운데이고, `f_Trans_Lla_To_Ecef` 는 경도를 첫째 인자로 받는다. 각도는 전부 라디안이다.
{: .prompt-tip }

* * *

## 5. 한 스텝 전진

표적을 0.1 초 앞으로 보내는 한 스텝은 다섯 단계다. 지금 시각에 걸린 기동을 찾아 각속도를 구하고, 각속도만큼 자세를 돌리고, 그 자세로 속력을 ECEF 속도 벡터로 바꾸고, 속도에 간격을 곱해 위치를 옮기고, 옮긴 위치를 위경도로 바꿔 결과에 담는다.

![한 스텝의 다섯 단계](/assets/img/posts/radar-target-trajectory/fig5-step-flow.svg){: width="860"}
_그림 5. 속도 변환과 위치 이동은 반 스텝 앞 지점에서 한 번 더 한다. 표적끼리는 서로 영향이 없어 표적 수만큼 같은 일을 반복한다._

### 어느 지점의 속도로 옮기는가

위치를 옮길 때 어느 지점의 속도를 쓰느냐에 따라 결과가 달라진다. 가장 간단한 방법은 스텝 시작 시각의 속도로 한 스텝을 가는 것이고 이것을 오일러법(Euler method)이라 한다. 이 모의에서는 자세를 각속도 × 간격으로 정확히 돌리므로 방향 자체는 틀리지 않는다. 틀리는 것은 방향을 반 스텝 늦게 쓴다는 점이다. 스텝 시작 방향으로 한 스텝을 가는 것은 속도를 시각에 대해 적분할 때 구간 왼쪽 끝의 값으로 넓이를 구하는 것이라, 참 위치와의 차이는 다음과 같다.

$$
\Delta\mathbf{p}_k \approx \tfrac{1}{2}\,V\,\Delta t\,(\hat{\mathbf{u}}_0 - \hat{\mathbf{u}}_k)
$$

$\hat{\mathbf{u}}$ 는 진행 방향의 단위 벡터다. 이 차이는 스텝 수가 아니라 출발 이후 방향이 얼마나 바뀌었는가에만 달려 있다. 선회 궤적은 바깥으로 벌어지는 것이 아니라 같은 반지름의 원이 출발 방향으로 반 스텝만큼 옮겨진 것이다. 200 m/s 로 0.1 초면 반 스텝은 10 m 이고, 90° 를 돌면 차이는 $10\sqrt 2 = 14.1$ m, 180° 면 20 m, 한 바퀴를 다 돌면 다시 0 에 가까워진다.

그래서 반 스텝을 먼저 가 보고, 그 지점의 자세와 위치로 속도를 다시 구해, 그 속도로 시작 위치에서 한 스텝을 옮긴다. 구간 가운데의 값으로 넓이를 구하는 중점법(midpoint method)이다. 남는 오차는 간격의 제곱에 비례하고 선회 하나에서 $\Delta t^2 V\omega/12$ 를 넘지 않는다. 8 G 로 200 m/s 를 도는 경우 6.5 cm 다.

$$
\begin{aligned}
\Theta_{mid} &= \Theta_k + \tfrac{1}{2}\,\omega\,\Delta t, & \Theta_{k+1} &= \Theta_k + \omega\,\Delta t \\
\mathbf{p}_{mid} &= \mathbf{p}_k + \tfrac{1}{2}\,\mathbf{v}(\Theta_k, \mathbf{p}_k)\,\Delta t \\
\mathbf{v}_{mid} &= \mathbf{v}(\Theta_{mid}, \mathbf{p}_{mid}), & \mathbf{p}_{k+1} &= \mathbf{p}_k + \mathbf{v}_{mid}\,\Delta t
\end{aligned}
$$

$\Theta$ 는 자세각 셋, $\omega$ 는 기동 각속도, $\mathbf{v}(\Theta, \mathbf{p})$ 는 4절의 두 회전으로 만든 ECEF 속도다. 반 스텝 지점의 위치가 필요한 것은 그 자리의 위도·경도로 두 번째 회전을 하기 때문이다.

![출발 속도로 가는 것과 중간 지점 속도로 가는 것의 차이](/assets/img/posts/radar-target-trajectory/fig6-midpoint.svg){: width="860"}
_그림 6. 왼쪽은 출발 속도로만 간 자리가 궤적에서 벗어난 것이다. 방향을 반 스텝 늦게 쓰는 만큼 참 궤적을 출발 방향으로 밀어 놓은 꼴이 된다. 오른쪽은 반 스텝 지점의 속도로 출발 자리에서 한 스텝을 가서 궤적 위에 머문다._

둥근 지구 위를 직진할 때의 고도 상승은 성질이 다르다. 그때는 방향이 위치에서 나오므로 한 스텝의 현이 떠오르는 $(V\Delta t)^2/2R$ 가 스텝마다 실제로 쌓인다. 두 방법의 차이가 실제로 얼마인지는 9절에서 숫자로 잰다.

### 코드

```c
// 중점법으로 한 스텝 전진. 반 스텝 뒤(중간 지점) 속도로 이동.
static VOID f_Tgt_Propagate(ST_TargetState *st_State, const ST_AttRate *st_AttRate, FLOAT64 headingSpeed, FLOAT64 stepTime, FLOAT64 nextTime)
{
	ST_TargetState			st_NextState;
	STRUCT_Coord_Attitude	st_AttMid;
	STRUCT_Coord_Lla		st_LlaMid;
	STRUCT_Coord_Rect		st_PosMid;
	STRUCT_Coord_Rect		st_VelStart;
	STRUCT_Coord_Rect		st_VelMid;
	FLOAT64					halfStep;

	// 반 스텝 뒤 자세, 스텝 끝 자세.
	halfStep = 0.5 * stepTime;

	st_AttMid.Roll	= st_State->st_Att.Roll + (st_AttRate->Roll * halfStep);
	st_AttMid.Pitch	= st_State->st_Att.Pitch + (st_AttRate->Pitch * halfStep);
	st_AttMid.Yaw	= st_State->st_Att.Yaw + (st_AttRate->Yaw * halfStep);

	st_NextState.st_Att.Roll	= st_State->st_Att.Roll + (st_AttRate->Roll * stepTime);
	st_NextState.st_Att.Pitch	= st_State->st_Att.Pitch + (st_AttRate->Pitch * stepTime);
	st_NextState.st_Att.Yaw		= st_State->st_Att.Yaw + (st_AttRate->Yaw * stepTime);

	// 반 스텝 뒤 위치. 스텝 시작 속도 사용.
	st_VelStart = f_Tgt_GetVelEcef(&st_State->st_Att, &st_State->st_Lla, headingSpeed);

	st_PosMid.x = st_State->st_PosEcef.x + (st_VelStart.x * halfStep);
	st_PosMid.y = st_State->st_PosEcef.y + (st_VelStart.y * halfStep);
	st_PosMid.z = st_State->st_PosEcef.z + (st_VelStart.z * halfStep);

	// 반 스텝 뒤 위경도, 자세로 중간 지점 속도 계산.
	st_LlaMid = f_Trans_Ecef_To_Lla(st_PosMid.x, st_PosMid.y, st_PosMid.z);
	st_VelMid = f_Tgt_GetVelEcef(&st_AttMid, &st_LlaMid, headingSpeed);

	// 중간 지점 속도로 한 스텝 이동.
	st_NextState.st_PosEcef.x = st_State->st_PosEcef.x + (st_VelMid.x * stepTime);
	st_NextState.st_PosEcef.y = st_State->st_PosEcef.y + (st_VelMid.y * stepTime);
	st_NextState.st_PosEcef.z = st_State->st_PosEcef.z + (st_VelMid.z * stepTime);

	// 새 위치의 LLA, 속도 계산 후 한꺼번에 덮어씀.
	st_NextState.st_Lla		= f_Trans_Ecef_To_Lla(st_NextState.st_PosEcef.x, st_NextState.st_PosEcef.y, st_NextState.st_PosEcef.z);
	st_NextState.st_VelEcef	= f_Tgt_GetVelEcef(&st_NextState.st_Att, &st_NextState.st_Lla, headingSpeed);
	st_NextState.simTime	= nextTime;

	*st_State = st_NextState;
}
```

반 스텝 뒤 자세와 위치는 이번 스텝의 방향을 정하는 데만 쓰고 버린다. 다음 스텝으로 넘어가는 것은 스텝 끝 자세와 그 자세로 다시 구한 속도다. 8 G 로 초당 22.5° 를 도는 중이면 반 스텝 뒤 자세는 1.12° 더 돌아 있고, 200 m/s 면 반 스텝 뒤 위치는 10 m 앞이다. 계산을 마칠 때까지 지금 상태는 건드리지 않고 `st_NextState` 를 다 채운 뒤 한 번에 덮어쓴다. 중간에 바꾸면 뒤 계산이 바뀐 값을 읽기 때문이다.

한 스텝을 진행하는 함수는 플랫폼과 표적을 차례로 옮긴다. 플랫폼은 기동이 없어 각속도 0 을 넘기고, 표적은 지금 시각에 걸린 기동의 각속도를 넘긴다.

```c
// 플랫폼, 전 표적 한 스텝 진행.
VOID f_Tgt_StepSim(ST_SimState *st_Sim)
{
	const ST_SimConfig		*st_Config = &st_Sim->st_Config;
	const ST_AttRate		st_NoManeuverRate = { 0.0, 0.0, 0.0 };
	ST_SimSample			*st_Sample = &st_Sim->st_Sample;
	ST_AttRate				st_ManeuverRate;
	FLOAT64					curTime;
	FLOAT64					nextTime;
	INT32					nTarget;

	// 시각 = 스텝 번호 * stepTime.
	curTime		= (FLOAT64)st_Sample->nStepIndex * st_Config->stepTime;
	nextTime	= (FLOAT64)(st_Sample->nStepIndex + 1) * st_Config->stepTime;

	// 플랫폼: 기동 없음, 각속도 0.
	f_Tgt_Propagate(&st_Sample->st_Platform, &st_NoManeuverRate, st_Config->st_Platform.headingSpeed, st_Config->stepTime, nextTime);

	// 표적: 현재 시각의 기동 각속도로 전진.
	for (nTarget = 0; nTarget < st_Config->nTargetNum; nTarget++)
	{
		st_ManeuverRate = f_Tgt_GetAttRate(&st_Config->st_Target[nTarget], curTime);
		f_Tgt_Propagate(&st_Sample->st_Target[nTarget], &st_ManeuverRate, st_Config->st_Target[nTarget].headingSpeed, st_Config->stepTime, nextTime);
	}

	st_Sample->nStepIndex	= st_Sample->nStepIndex + 1;
	st_Sample->simTime		= nextTime;
}
```

시각은 지난 시각에 0.1 을 더해 가지 않고 스텝 번호에 간격을 곱해 만든다. 0.1 을 600 번 더하면 반올림 오차가 쌓이지만 곱하면 그렇지 않다. 스텝 수도 시뮬레이션 시간을 간격으로 나눈 값에 0.5 를 더해 잘라 반올림한다. 103.6 초를 0.1 초로 나누면 1035.999… 로 조금 모자라게 나와서 그냥 자르면 한 스텝이 빠지기 때문이다.

기동 구간 판정도 시각으로 한다. 스텝 번호 × 0.1 과 화면에서 읽은 십진수는 같은 값을 뜻해도 마지막 비트가 다를 수 있다. 0.1 초 간격에서는 스텝 번호 × 0.1 이 십진수보다 작아지는 경우가 1 200 스텝 안에 하나도 없고 커지는 경우만 432 번 있어서, 시작은 제때 걸리고 종료는 제때 빠진다. 간격이 달라지면 반대로 틀어질 수 있으므로 시각이 아니라 스텝 번호로 비교하는 쪽이 안전하다. 시작·종료 시각을 스텝 수를 셀 때와 같은 반올림으로 번호로 바꿔 두고 정수로 비교하면 된다.

```c
nStart		= (INT32)((st_Maneuver->startTime / stepTime) + 0.5);
nEnd		= (INT32)((st_Maneuver->endTime / stepTime) + 0.5);
isActive	= (nStart <= nStepIndex) && (nStepIndex < nEnd);
```

구간은 어차피 스텝 격자에 맞춰지므로 2.75 초에 시작해 6.75 초에 끝나는 기동은 2.8 초부터 6.8 초까지 걸린다.

계산 로그는 화면 쪽이 값을 다시 계산해 적는 것이 아니다. 설정 구조체에 함수 포인터 하나와 사용자 포인터 하나를 두고, 코어가 스텝마다 출발 속도의 북·동·아래 성분과 ECEF 성분, 반 스텝 뒤 자세와 위치, 중간 지점 속도, 스텝 끝 상태를 구조체 하나에 담아 그 함수로 넘긴다. 포인터가 NULL 이면 기록을 건너뛰어 계산에는 비용도 영향도 없다. 로그에 찍히는 값이 계산에 쓴 바로 그 값이라 로그와 코드가 어긋날 일이 없고, 궤적이 이상할 때 어느 단계에서 틀어졌는지를 스텝 단위로 좁힐 수 있다. 수치 계산을 맡는 코어에는 이런 기록 훅을 처음부터 두는 편이 낫다.

* * *

## 6. 수평은 어느 자리에서 잡는가

4절의 두 번째 회전에는 위도·경도가 들어간다. 어느 자리의 값을 넣느냐가 궤적의 모양을 바꾼다.

수평은 그 자리에서 아래, 곧 지구 중심 쪽에 수직인 방향이다. 지구가 둥글어서 자리마다 아래가 다르고 수평도 다르다. 대공 표적은 플랫폼에서 13.3 km 떨어져 있고, 두 자리의 수평 사이 각은 거리를 지구 반지름으로 나눈 0.12° 다.

![표적 자리의 수평과 플랫폼 자리의 수평](/assets/img/posts/radar-target-trajectory/fig7-horizontal-ref.svg){: width="860"}
_그림 7. 왼쪽은 스텝마다 표적 자리의 수평을 다시 잡아 둥근 땅을 따라가는 경우, 오른쪽은 플랫폼 자리의 수평을 그대로 써서 직선으로 나는 경우다. 곡률은 크게 과장했다._

이 모의는 매 스텝 표적이 있는 자리의 위경도로 속도를 돌린다. 그러면 속도가 늘 그 자리의 수평을 향해서 표적이 둥근 땅을 따라 돌며 고도 300 m 를 지킨다. 실제 비행기도 고도계와 자세계로 자기 자리의 수평을 잡고 난다.

플랫폼의 위경도로 돌리면 다르다. 표적의 속도가 플랫폼 자리의 수평과 나란한 직선을 따르는데, 그 직선은 표적 자리에서 보면 기수를 0.12° 숙인 방향이다. 플랫폼에 다가갈수록 땅과의 간격이 줄어 60 초 뒤 대공 표적의 고도는 300 m 에서 286.2 m 가 되고, 바다 위를 가는 대함 표적은 $-0.54$ m 로 바다 밑으로 들어간다. 기하로 보면 표적은 처음부터 플랫폼의 접평면 위 $300 - d^2/2R = 286.1$ m 높이에 있고, 직선으로 날면 그 높이를 유지한 채 땅이 올라오는 것이다.

표적의 궤적은 표적의 입력값만으로 정해져야 한다. 플랫폼을 어디에 두든 같은 입력이면 같은 궤적이 나와야 하고, 플랫폼을 옮기면 거리·방위·고각만 바뀌어야 한다. 플랫폼 기준으로 계산하면 플랫폼이 앞에 있을 때와 뒤에 있을 때 같은 표적의 고도가 반대로 움직여서 이 조건이 깨진다. 플랫폼을 반대로 표적 뒤에 두어 보면 그렇다. 대공 표적 출발점에서 북쪽으로 같은 13.3 km 떨어진 위도 32.24° 에 플랫폼을 놓고 플랫폼 기준으로 계산하면, 표적이 플랫폼에서 멀어지는 동안 접평면 아래로 땅이 내려가서 60 초 뒤 고도가 336.5 m 로 올라간다. 접평면 기하로도 $300 + (d_1^2 - d_0^2)/2R$ 에 $d_0 = 13.3$ km, $d_1 = 25.3$ km 를 넣으면 336.4 m 다. 같은 입력인데 플랫폼 자리에 따라 고도가 14 m 내려가기도 하고 36 m 올라가기도 한다. 표적 자리의 수평으로 계산하면 플랫폼을 어디로 옮기든 60 초 뒤 고도는 300.000 m 그대로다. 코드에서 두 방식의 차이는 `f_Trans_Ned_To_Ecef` 에 넣는 위도·경도다. 플랫폼 기준에서는 기준점에 플랫폼의 ECEF 위치와 위경도를 넣고 더해진 위치를 다시 빼므로 회전만 남고, 회전에 쓰는 위도·경도만 플랫폼 것이 된다. 화면에서 플랫폼 기준 비교를 켜면 두 결과를 나란히 볼 수 있게 두었고, 그 차이도 9절에 그림으로 두었다.

* * *

## 7. 기본 시나리오 결과

기본 시나리오의 값을 그대로 넣고 60 초를 0.1 초 간격으로 돌렸다. 스텝은 600 번, 0 초를 포함한 결과는 601 개다. 10 초마다 끊어 적으면 아래와 같다.

| 시각 [s] | 대함 위도 [°] | 대함 경도 [°] | 대함 고도 [m] | 대공 위도 [°] | 대공 경도 [°] | 대공 고도 [m] |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 32.125000 | 126.030000 | 0.0000 | 32.120000 | 126.000000 | 300.0000 |
| 10 | 32.125000 | 126.026821 | 0.0000 | 32.101965 | 126.000000 | 300.0000 |
| 20 | 32.125000 | 126.023642 | 0.0000 | 32.083929 | 126.000000 | 300.0000 |
| 30 | 32.125000 | 126.020463 | 0.0000 | 32.065894 | 126.000000 | 300.0000 |
| 40 | 32.125000 | 126.017283 | 0.0000 | 32.047859 | 126.000000 | 300.0000 |
| 50 | 32.125000 | 126.014104 | 0.0000 | 32.029823 | 126.000000 | 300.0000 |
| 60 | 32.125000 | 126.010925 | 0.0000 | 32.011788 | 126.000000 | 300.0000 |

![기본 시나리오 60 초 결과](/assets/img/posts/radar-target-trajectory/fig8-basic-result.svg){: width="860"}
_그림 8. 왼쪽은 플랫폼을 원점으로 위에서 내려다본 궤적이고 점은 10 초 간격이다. 오른쪽처럼 두 표적의 고도는 60 초 동안 처음 값 그대로다._

대공 표적은 남쪽으로 12 000.00 m, 대함 표적은 서쪽으로 1 800.00 m 를 직진했다. 각각 속력에 60 초를 곱한 거리다. 대함 표적의 위도와 대공 표적의 경도는 소수 여섯 자리까지 변하지 않았고, 두 표적의 고도는 첫 스텝에서 $3 \times 10^{-5}$ m 올라간 뒤 60 초까지 그 값에 머물고, 속력은 처음 값 그대로다. 이 $3 \times 10^{-5}$ m 는 궤적이 떠오른 것이 아니라 ECEF 위치를 위경도로 되돌릴 때 생기는 변환 잔차다. 변환 함수는 반복 횟수를 다섯 번으로 고정해 두어 그 자리에서 이만큼이 남고, 0 초 위치를 ECEF 로 바꿨다가 전진 없이 바로 되돌려도 같은 $3.08 \times 10^{-5}$ m 가 나온다. 한 스텝에 3 m 가는 대함 표적과 20 m 가는 대공 표적에 같은 값이 남는 것도 적분과 관계없다는 뜻이다. 수렴할 때까지 반복하는 변환([12장](/posts/radar-coordinate-frames/) 1.6절)으로 다시 재면 60 초 동안의 고도 변화는 두 표적 모두 $1 \times 10^{-8}$ m 를 넘지 않는다. 플랫폼 기준으로 보면 대공 표적은 북쪽 13 307 m 에서 출발해 1 307 m 까지 다가왔다.

프로그램은 계산을 맡는 C DLL 과 화면을 맡는 MFC 다이얼로그로 나눠 두었다. 화면 쪽은 입력 표의 글자를 보관하고 프리셋을 불러와 설정 구조체를 채우는 부분, 설정 하나로 DLL 을 전 구간 돌려 결과를 모으는 부분, 궤적·고도·속력을 그리는 부분, 표 편집, 계산 로그 콘솔로 나뉘고, DLL 내부는 보지 않고 헤더의 구조체와 함수로만 주고받는다. 화면에서는 플랫폼과 표적의 초기값 일곱 칸과 기동 표를 바로 고칠 수 있고, 칸을 하나 고치면 같은 설정을 기본, 비중점법, 플랫폼 기준으로 세 번 돌려 두므로 결과 표의 비교 열과 그림의 점선은 다시 계산하지 않고 바로 켜고 끈다. 프리셋은 기본 시나리오, 8절의 응용 시나리오, 그리고 지그재그를 60 초에 맞추기 전의 원본 크기 세 가지다. 표는 CSV 로 저장할 수 있고, 계산 로그를 켜면 콘솔 창에 입력값을 라디안과 ECEF 로 바꾼 0 초 상태가 먼저 찍히고, 첫 스텝과 걸린 기동이 바뀌는 스텝은 각속도·반 스텝 자세·반 스텝 위치·중간 지점 속도·새 위치 순서로 중간값이 모두 찍히며, 나머지 스텝은 1 초마다 한 줄로 요약된다. 위 표의 값은 그 DLL 을 돌려 얻은 것이고, 화면은 8절 끝에 두었다.

* * *

## 8. 응용 시나리오

기본 시나리오는 두 표적 모두 직진이라 기동 계산을 확인할 수 없다. 그래서 지그재그 기동 열 개를 넣은 시나리오를 하나 더 두었다. 60 초 안에 돌려면 G 값을 어떻게 잡아야 하는지가 먼저다. 각도 $\theta$ 를 도는 데 걸리는 시간은 $T = \theta/\omega$ 다.

| G 값 | 30 m/s 가 45° | 30 m/s 가 90° | 200 m/s 가 90° | 200 m/s 가 150° |
|---:|---:|---:|---:|---:|
| 1 | 2.4 s | 4.8 s | 32.0 s | 53.4 s |
| 2 | 1.2 s | 2.4 s | 16.0 s | 26.7 s |
| 4 | 0.6 s | 1.2 s | 8.0 s | 13.3 s |
| 8 | 0.3 s | 0.6 s | 4.0 s | 6.7 s |

느린 대함 표적은 1 G 로 45° 씩 네 번, 한 번에 2.4 초씩 돌게 했다. 대공 표적은 90° 다섯 번과 150° 한 번을 60 초 안에 돌아야 하는데 4 G 로도 모두 53 초가 걸려 직진할 틈이 거의 없다. 그래서 8 G 로 정해 90° 는 4.0 초, 150° 는 6.7 초에 돌고 나머지 33 초를 직진한다. G 의 부호가 방향이고 음수가 좌선회다.

대함 표적의 1 G 는 60 초 안에 네 번 꺾기 위해 고른 값이지 배가 낼 수 있는 기동이 아니다. 30 m/s 에서 1 G 는 초당 18.7°, 반경 92 m 인데, 같은 속력에서 초당 1° 로 돌면 0.053 G 에 반경 1.7 km, 초당 3° 라도 0.16 G 에 반경 573 m 다. 응용 시나리오는 적분기와 기동 처리를 확인하는 자리라 센 값을 썼고, 추적 필터를 평가할 때는 표적 종류가 실제로 내는 가속도 범위로 시나리오를 따로 둬야 한다. 기동 세기는 필터가 허용하는 가속도 잡음의 크기와 바로 맞물리기 때문이다.

| 표적 | 축 | G | 시작 [s] | 종료 [s] | 회전 |
|---|---|---:|---:|---:|---|
| 대함 | yaw | −1 | 8.0 | 10.4 | 좌 45°, 서 → 남서 |
| 대함 | yaw | +1 | 15.8 | 18.2 | 우 45°, 남서 → 서 |
| 대함 | yaw | +1 | 41.9 | 44.3 | 우 45°, 서 → 북서 |
| 대함 | yaw | −1 | 49.7 | 52.1 | 좌 45°, 북서 → 서 |
| 대공 | yaw | −8 | 2.7 | 6.7 | 좌 90°, 남 → 동 |
| 대공 | yaw | +8 | 13.2 | 17.2 | 우 90°, 동 → 남 |
| 대공 | yaw | +8 | 18.5 | 22.5 | 우 90°, 남 → 서 |
| 대공 | yaw | −8 | 36.1 | 40.1 | 좌 90°, 서 → 남 |
| 대공 | yaw | −8 | 41.4 | 45.4 | 좌 90°, 남 → 동 |
| 대공 | yaw | +8 | 53.3 | 60.0 | 우 150°, 동 → 남서 |

![응용 시나리오의 궤적과 기동 시각](/assets/img/posts/radar-target-trajectory/fig9-zigzag-result.svg){: width="860"}
_그림 9. 굵게 그린 구간이 선회 중이고 나머지는 직진이다. 아래 띠의 막대 하나가 위 궤적에서 꺾인 곳 하나다._

기동 구간에서만 방향이 바뀌고 나머지 구간은 직진한다. 대함 표적은 서쪽으로 가다가 8 초부터 남서쪽으로 틀어 원래 위도에서 남쪽으로 168.6 m 비켜 갔다가, 41.9 초부터 북서쪽으로 돌아 52.1 초에 위도 32.125000° 로 정확히 돌아온다. 한 번의 선회에서 도는 각은 $18.73°/\mathrm{s} \times 2.4\ \mathrm{s} = 44.95°$ 라 45° 에서 0.05° 모자라지만 좌우 두 번씩 대칭이라 서로 지워진다. 대공 표적은 남쪽으로 출발해 동·남·서·남·동 순서로 89.90° 씩 돌고, 마지막 53.3 초부터 150.58° 를 돌아 yaw 240.68° 인 남서향으로 끝난다. 60 초 뒤 위치는 위도 32.078757°, 경도 126.009723°, 고도 300.000 m 다.

지그재그를 60 초에 맞춰 줄이기 전의 원래 크기 시나리오도 세 번째 프리셋으로 두었다. 대공 표적은 4 G 로 돌아 선회 반경이 1 020 m 로 8 G 의 두 배이고, 90° 를 8.0 초에 89.90° 로, 마지막 150° 는 134 스텝 13.4 초에 150.58° 로 돈다. 대공 표적이 23 200 m 를 나는 116.0 초에 시뮬레이션이 끝나고, 대함 표적은 같은 시각에 끝나도록 직진 세 구간을 28.4 초, 852 m 씩 같게 맞췄다. 시간을 뺀 나머지 조건은 기본 시나리오와 같다.

| 표적 | 축 | G | 시작 [s] | 종료 [s] |
|---|---|---:|---:|---:|
| 대함 | yaw | −1 | 28.4 | 30.8 |
| 대함 | yaw | +1 | 41.4 | 43.8 |
| 대함 | yaw | +1 | 72.2 | 74.6 |
| 대함 | yaw | −1 | 85.2 | 87.6 |
| 대공 | yaw | −4 | 6.0 | 14.0 |
| 대공 | yaw | +4 | 24.1 | 32.1 |
| 대공 | yaw | +4 | 35.2 | 43.2 |
| 대공 | yaw | −4 | 67.5 | 75.5 |
| 대공 | yaw | −4 | 78.5 | 86.5 |
| 대공 | yaw | +4 | 102.6 | 116.0 |

![궤적 모의 프로그램의 운용 화면](/assets/img/posts/radar-target-trajectory/fig10-ui-zigzag.png){: width="860"}
_그림 10. 응용 시나리오를 불러와 대공 표적을 고른 화면이다. 왼쪽 아래 기동 표의 여섯 줄이 위 표의 대공 표적 여섯 줄이고, 오른쪽 궤적 그림의 축은 위도·경도다. 아래 결과 표 옆의 두 체크 상자가 비중점법 비교와 플랫폼 기준 비교이고, 고도가 첫 스텝부터 300.0000308 m 로 적히는 것이 7절에서 말한 변환 잔차다._

* * *

## 9. 두 가지 비교

5절과 6절에서 말로 설명한 두 가지 차이를 같은 코드에 설정값만 바꿔 넣어 재어 보았다.

![중점법을 뺐을 때와 플랫폼 자리의 수평을 썼을 때의 차이](/assets/img/posts/radar-target-trajectory/fig11-compare.svg){: width="860"}
_그림 11. 왼쪽은 응용 시나리오에서 출발 속도로만 간 궤적이 중점법 궤적과 벌어진 거리다. 오른쪽은 기본 시나리오 대공 표적의 고도를 두 수평 기준으로 비교한 것이다._

출발 속도로만 가면 기본 시나리오의 대공 표적이 직진만 해도 60 초 뒤 고도가 300.019 m 로 1.9 cm 올라간다. 한 스텝에 가는 20 m 의 현이 둥근 땅에서 $20^2 / 2R = 3.1 \times 10^{-5}$ m 떠오르고, 그것이 600 번 쌓인 값이다. 중점법에서는 이 표류가 사라진다. 출력 고도에 남는 $3 \times 10^{-5}$ m 는 7절에서 본 변환 잔차라서, 수렴한 변환으로 재면 기본 시나리오에서 $1 \times 10^{-8}$ m, 응용 시나리오의 대공 표적도 $1.6 \times 10^{-6}$ m 다. 적분 방법의 차이를 잴 때는 변환 잔차보다 작은 양이 가려지지 않도록 수렴한 변환으로 고도를 재야 한다. 응용 시나리오에서는 차이가 훨씬 크다. 8 G 로 90° 를 도는 동안 출발 속도로 간 궤적은 참 궤적을 출발 방향으로 10 m 옮긴 원을 그려서, 첫 선회가 끝난 뒤 두 궤적은 $10\sqrt 2 = 14.1$ m 어긋난 채 나란히 직진한다. 차이는 5절의 식대로 출발 이후 방향이 얼마나 바뀌었는가에만 달려 있다. 처음 방향이 남쪽이므로 동쪽이나 서쪽을 향하는 동안은 14.1 m 이고 다시 남쪽을 향하면 0 에 가깝다. 17.2 초에 0.28 m, 40.1 초에 0.39 m 다. 끝 방향 240.68° 에서는 $10 \times 2\sin 30.34° = 10.1$ m 가 되어야 하는데 실제로는 9.7 m 이고, 그 0.4 m 는 앞선 선회들이 남긴 2 차 잔차다. 1 G 로 45° 씩 도는 대함 표적은 $1.5 \times 2\sin 22.5° = 1.15$ m 다.

플랫폼 자리의 수평으로 날린 대공 표적은 고도가 60 초 동안 300 m 에서 286.2 m 로 내려간다. 6절에서 기하로 구한 286.1 m 는 플랫폼 접평면 위의 높이다. 60 초 뒤에도 표적은 플랫폼에서 1 307 m 떨어져 있어 그 자리의 곡률 $1307^2/2R = 0.13$ m 가 더해진 286.2 m 가 되고, 모의값과 맞다. 표적 자리의 수평을 쓴 기본 계산은 300.000 m 를 유지한다.

* * *

## 10. 정리

표적 하나는 위치·고도·속력·자세 일곱 값과 기동 목록으로 정하고, 계산은 ECEF 위치·속도와 자세각 아홉 상태값으로 한다. 기동 한 건은 회전축·G 값·시작·종료 네 값이고, G 값은 $\omega = n g / V$ 로 각속도가 된다. 같은 G 라도 빠른 표적은 천천히 돌고 반경은 속력의 제곱으로 커진다. roll 기동은 이 모의에서 궤적을 바꾸지 않는다.

속력 하나는 자세각과 위도·경도로 두 번 돌려 ECEF 속도 벡터가 된다. 두 번째 회전에는 표적 자신이 있는 자리의 위경도를 넣어야 둥근 땅을 따라 고도가 지켜진다. 한 스텝은 반 스텝 지점의 속도로 옮기는 중점법으로 전진하고, 선회 중에는 이 차이가 10 m 를 넘는다.

기본 시나리오에서 대공 표적은 60 초에 남쪽 12 km, 대함 표적은 서쪽 1.8 km 를 직진했고 고도와 속력은 처음 값 그대로였다. 응용 시나리오의 지그재그는 기동 구간에서만 꺾이고 대함 표적은 비켜 갔던 위도로 정확히 돌아왔다. 이 궤적이 다음 블록의 입력이 된다.

* * *

## 참고 자료

- W. H. Press, S. A. Teukolsky, W. T. Vetterling, B. P. Flannery, *Numerical Recipes*, Cambridge University Press — 오일러법과 중점법(2차 룽게–쿠타)의 식, 한 스텝 오차의 차수 차이
- J. D. Anderson, *Introduction to Flight*, McGraw-Hill — 선회 비행에서 하중배수와 선회 반경·선회율의 관계, 1 G 가 수평 비행이라는 해석 (3절 주석)
- S. Blackman, R. Popoli, *Design and Analysis of Modern Tracking Systems*, Artech House — 일정 선회율 표적 운동 모델, 참값 궤적을 만들어 추적 필터를 평가하는 시뮬레이션의 구성
- P. D. Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, Artech House — ECEF 좌표계에서 위치와 속도를 적분하는 운동학, 국지 수평면이 위치에 따라 달라지는 관계
