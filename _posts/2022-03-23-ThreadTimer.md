---
title: (MFC) Timer with thread
description: 쓰레드를 활용한 타이머 구현
date: 2022-03-23 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, thread, timer]
---

# Timer with Thread (MFC)

- 최초 작성일: 2022년 3월 23일(수)

## 목차

[TOC]

## 목적

- 간단한 예제를 통해 쓰레드를 활용한 타이머를 구현해보자.

<br/>

## 구현

아래와 같이 간단한 다이얼로그를 만들어주자. 현재 시간이 출력되는 Static Text를 하나 생성해주고, 쓰레드의 Start와 Stop을 위한 버튼을 2개 만들어준다.

![image](https://user-images.githubusercontent.com/68185569/159655688-8825f994-835b-404a-8a50-ec5c9ebf7346.png)

<br/>

그런 다음, 쓰레드를 위한 TimeThread와 Button을 위한 함수를 선언해주자. 

우선, ThreadEXDlg.h 헤더 파일에서 다음와 같이 코드를 삽입해주자.

```C++
// CThreadEXDlg dialog
class CThreadEXDlg : public CDialogEx
{
// Construction
public:
	CThreadEXDlg(CWnd* pParent = nullptr);	// standard constructor
	CWinThread* p1;
	CString m_staticDisp;
	afx_msg void OnBnClickedButton1();	// Start Button
	afx_msg void OnBnClickedButton2();	// Stop Button
	static UINT TimeThread(LPVOID _mothod); // Thread

// Dialog Data
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_THREADEX_DIALOG };
#endif
```

<br/>

그러면 다음으로 해당 함수를 구현해줘야 한다.

아래의 코드와 같이 ThreadEXDlg.cpp 파일에서 추가해준다.

이때 OnBnClickedButton1 의 함수는 리소스 뷰의 다이얼로그에서 해당 버튼을 더블 클릭하면 자동 생성되는데, 안 된다면 임의로 삽입해주자.

```c++
// Start Button을 눌렀을 때
void CThreadEXDlg::OnBnClickedButton1()
{
	// TODO: Add your control notification handler code here
	p1 = AfxBeginThread(TimeThread, this);

	if (p1 == NULL) {
		AfxMessageBox(L"Error!");
	}
}
// Stop Button을 눌렀을 때
void CThreadEXDlg::OnBnClickedButton2()
{
	// TODO: Add your control notification handler code here
	// thread 중지
	if (NULL != p1) {
		::SuspendThread(p1->m_hThread);
	}
}
```

<br/>

그러면 마지막으로, TimeThread 함수를 구현해주자.

우선 ctime.h 헤더파일을 include 해주고, CTIme을 통해 현재 시간을 가져온 후 년/월/일/시/분/초를 출력한다.

이때 Sleep(1000)을 주면 ms(밀리세컨드) 단위이기 때문에 1000이면 1초이다. 1초마다 값이 갱신된다.

아래의 코드를 삽입하고 실행해보자.

```c++
UINT CThreadEXDlg::TimeThread(LPVOID _mothod)
{
	CThreadEXDlg* fir = (CThreadEXDlg*)_mothod;
	while (1) {
		CTime cTime = CTime::GetCurrentTime();
		fir->m_staticDisp.Format(_T("%d년 %d월 %d일\n%d시 %d분 %d초"),
			cTime.GetYear(), cTime.GetMonth(), cTime.GetDay(),
			cTime.GetHour(), cTime.GetMinute(), cTime.GetSecond());
		fir->SetDlgItemText(IDC_STATIC_DIS, fir->m_staticDisp);
		Sleep(1000);
	}
	return 0;
}
```

### Result1

<iframe id="video" width="750" height="500" src="/assets/video/ThreadTimer1.mp4" frameborder="0"> </iframe>

<br/>

그러면 이번에는, 다른 방법으로 구현해보자.

<br/>

## 구현2

```c++
UINT CThreadEXDlg::TimeThread(LPVOID _mothod)
{
	CThreadEXDlg* fir = (CThreadEXDlg*)_mothod;
	
	clock_t sclock, nclock;
	time_t seconds;
	struct tm now;
	int tail = 0;

	sclock = clock();
	time(&seconds);
	localtime_s(&now, &seconds);
	print_time(&now, tail);

	while (1) {
		if (_kbhit())	// 키보드 입력을 확인함. 키가 눌러지면 1 반환.
		{
			break;
		}
		nclock = clock();

		if (nclock - sclock >= (CLOCKS_PER_SEC / 1000))
		{
			tail++;
			if (tail == 1000)//1초가 지나면
			{
				tail = 0;
				sclock = clock();
				time(&seconds);
				localtime_s(&now, &seconds);
			}
			print_time(&now, tail);
		}
	}
	return 0;
}

void print_time(struct tm* now, int tail)
{
	COORD CursorPostion = { 0,1 };
	SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), CursorPostion);

	printf("%2d시 %2d분 %2d초 %2d\n", now->tm_hour, now->tm_min, now->tm_sec, tail);
}
```

<br/>

### Result2

<iframe id="video" width="750" height="500" src="/assets/video/ThreadTimer2.mp4" frameborder="0"> </iframe>

<br/>

## 구현3

아래의 코드 커서 위치를 지정하는 부분을 지워보자.

```c++
void print_time(struct tm* now, int tail)
{
	//COORD CursorPostion = { 0,1 };
	//SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), CursorPostion);

	printf("%2d시 %2d분 %2d초 %2d\n", now->tm_hour, now->tm_min, now->tm_sec, tail);
}
```

<br/>

### Result3

<iframe id="video" width="750" height="500" src="/assets/video/ThreadTimer3.mp4" frameborder="0"> </iframe>
