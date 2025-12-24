---
title: (MFC) Multi-Thread
description: MFC 멀티스레드
date: 2022-04-08 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, multi-thread, thread]
---

# Multi Thread (멀티 스레드)

- 최초 작성일: 2022년 4월 8일(금)

## 목적

- 개념 설명과 예제를 통해 멀티스레드를 이해하자.

<br/>

## 설명

- 멀티태스킹: 운영체제가 여러 개의 응용 프로그램(프로세스)을 동시에 실행한다.
- 멀티스레딩: 응용 프로그램(프로세스)이 여러 개의 스레드를 동시에 실행한다.

<br/>

여기서 프로세스, 스레드 개념이 나오는데

간단하게 설명하면, 프로세스는 응용 프로그램의 실행을 의미하고, 스레드는 응용 프로그램 내에서 실행되는 작업을 의미한다.

<br/>

윈도우 운영체제의 프로세스는 할당된 메모리 영역에 각종 자원을 담고 있는 컨테이너로 정적인 개념이며,

스레드는 CPU 시간을 할당받아 실행되는 동적인 개념이다.

스레드는 프로세스의 가상 주소 공간에 존재하는 실행 흐름으로, 운영체제는 CPU 시간을 각 스레드에 나누어 할당함으로써

여러 개의 스레드가 동시에 실행되는 효과를 만들어 낸다.

<br/>

### MFC 스레드

윈도우 운영체제는 한 종류의 스레드를 제공하지만, MFC가 제공하는 스레드는 특성에 따라 두 종류로 나뉜다.

- 작업자 스레드: 메시지 루프가 없다.
- 사용자 인터페이스 스레드: 메시지 루프가 있다.

작업자 스레드 (Worker Thread)는 메시지 루프가 없어 화면에 보이지 않는 백그라운드 작업을 수행할 때 적합하다.

반면, 사용자 인터페이스 스레드 (User Interface Thread)는 메시지 루프가 있어 윈도우 생성 및 출력, 사용자 입력을 받는 등의 작업을 처리할 때 적합하다.

<br/>

## 구현

### 작업자 스레드1

아래와 같이 새 프로젝트를 생성한다.

- 프로젝트명: WorkerThread1
- 애플리케이션 종류: '단일 문서'
- 프로젝트 스타일: 'MFC standard'
- 고급 기능: 'ActiveX 컨트롤' 옵션 해제

<br/>

그리고, CWorkerThread11View 클래스에 WM_LBUTTONDOWN 메시지 핸들러를 추가하고 다음 코드를 작성한다.

![image](https://user-images.githubusercontent.com/68185569/162364644-d3cabce2-0f2a-4520-ad0a-6f1a3566bb79.png)

<br/>

```c++
void CWorkerThread1View::OnLButtonDown(UINT nFlags, CPoint point)
{
	// TODO: Add your message handler code here and/or call default
	int val = 600;

	// 스레드를 사용하지 않은 경우
	CalcIt((LPVOID)val);

	//CView::OnLButtonDown(nFlags, point);
}
```

<br/>

그 다음, OnLButtonDown() 함수 위쪽에 CalcIt() 함수를 추가해주자.

이때, CalcIt() 함수는 뷰 클래스 멤버 함수가 아니라 전역 함수인 것을 주의하자.

```c++
UINT CalcIt(LPVOID arg)
{
	// LPVOID를 int형으로 타입 캐스팅한다.
	int val = (int)arg;

	// 1부터 val까지 1씩 증가하면서 더한다.
	int result = 0;
	for (int i = 1; i < val; i++) {
		result += i;
		Sleep(10);	// 테스트를 위해 계산 속도를 늦춘다.
	}

	// 계산 결과를 표시한다.
	CString str;
	str.Format(_T("계산 결과 = %d"), result);
	AfxMessageBox(str);

	return 0;
}
```

<br/>

지금까지 작성한 것의 실행 결과는 다음과 같다.

해당 메시지 박스가 나오기 전까지 윈도우를 움직이거나 메뉴를 선택하는 등의 다른 작업을 전혀 할 수 없다는 점을 확인해야한다.

![image](https://user-images.githubusercontent.com/68185569/162366057-69e61278-410c-4e7b-b0fd-13847592a280.png)

<br/>

<br/>

그럼, 이번엔 스레드를 사용하여 OnLButtonDown() 함수를 다음과 같이 수정하자.

```c++
void CWorkerThread1View::OnLButtonDown(UINT nFlags, CPoint point)
{
	// TODO: Add your message handler code here and/or call default
	int val = 600;

	// 스레드를 사용하지 않은 경우
	//CalcIt((LPVOID)val);

	// 스레드를 사용한 경우
	AfxBeginThread(CalcIt, (LPVOID)val);
	//CView::OnLButtonDown(nFlags, point);
}
```

<br/>

스레드를 사용하면, 이전 단계와는 다르게 클릭을 하고 연산을 하고 있을 때에도 다른 작업을 할 수 있는 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/162367562-9bbaff01-48ba-456d-a8e6-eaf7a0ed1000.png)
