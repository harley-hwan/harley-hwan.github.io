---
title: (MFC) 마우스 좌표값 구하기 프로그램
description: 마우스 좌표값 구하기 프로그램 작성 (윈도우 프로그램)
date: 2022-02-10 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, win32, windowprogramming]
---

# [MFC] 마우스 좌표값 구하기 프로그램

- 최초 작성일: 2022년 2월 10일 (목)

## 목차



## 목적

이번 예제에서는 빈 프로젝트를 이용하는 것이 아닌, MFC를 이용하여 마우스 좌표값을 보여주는 프로그램을 작성한다.

마우스 좌표값은 마우스가 움질일 때마다, 윈도우에 좌표값을 보여준다.

프로그램은 MFC 클래스 마법사 (Class Wizard)를 사용하여 멤버함수를 생성하고, 생성된 함수는 마우스 위치 좌표값을 계속 Update한다.

<br/>

## 실습

### 프로젝트 생성

다음과 같이 프로젝트를 새로 생성해주자. (MFC app)

![image](https://user-images.githubusercontent.com/68185569/153352859-cf3894e7-b5aa-4645-a52e-8b97fa20a43f.png)

![image](https://user-images.githubusercontent.com/68185569/153352957-b9f2525a-797c-447c-a755-9c724b53de96.png)

프로젝트명은 'MouseMFC'로 하였다.

<br/>

### 코드 작성

[View]-[Solution Explorer] 를 눌러 솔루션 탐색기를 띄우고, 거기서 [MouseMFC]-[Header Files]-[MouseMFCView.h] 파일을 더블클릭한다.

그러면, 해당 헤더 파일의 코드를 확인할 수 있는데, 다음과 같이 코드(변수)를 추가한다.

![image](https://user-images.githubusercontent.com/68185569/153353557-91bf57ae-f11c-434a-9ac0-625b078a01a2.png)

<br/>

위의 변수 코드를 추가했으면, 클래스 뷰에서 [MouseMFC]-[CMouseMFCView] 를 보면 OnDraw(CDC * pDC) 함수를 볼 수 있다.

![image](https://user-images.githubusercontent.com/68185569/153354358-a37c5829-2cb4-4a94-be61-9384dc137e9d.png)

<br/>

그걸 더블클릭하면 코드로 이동할 수 있는데, 다음과 같이 코드를 삽입해준다.

```c++
void CMouseMFCView::OnDraw(CDC* /*pDC*/)
{
	CMouseMFCDoc* pDoc = GetDocument();
	ASSERT_VALID(pDoc);
	if (!pDoc)
		return;

	// TODO: add draw code for native data here
	CClientDC dc(this);
	CString strPoint;
	strPoint.Format(_T("마우스 좌표 (%4d, %4d)"), m_Pos.x, m_Pos.y);
	dc.TextOutW(0, 0, strPoint);
}
```

<br/>

위의 코드 작성을 모두 완료했다면, 이번에는 마우스 이동 함수인 'WM_MOUSEMOVE'를 클래스 마법사에서 추가해야 한다.

[Menu]-[Project]-[Class Wizard] 를 누르거나 [Ctrl + Shift + X] 를 눌러 클래스 클래스 마법사를 실행하자.

그러면, 아래의 창을 볼 수 있는데, 'CMouseMFCView' 클래스를 선택하고, [Message] 탭에서  'WM_MOUSEMOVE' 메시지를 더블클릭하자.

그러면, 우측에 'OnMouseMove' 함수가 추가되는 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/153355054-96a95fc0-36e3-4af6-81aa-02b247e49fdb.png)

<br/>

그리고, 함수에 다음의 코드를 추가해주자.

```c++
// CMouseMFCView message handlers

void CMouseMFCView::OnMouseMove(UINT nFlags, CPoint point)
{
	// TODO: Add your message handler code here and/or call default
	m_Pos = point;
	Invalidate();

	CView::OnMouseMove(nFlags, point);
}
```

<br/>

### 실행 결과

<iframe id="video" width="750" height="500" src="/assets/video/2022-02-10-MouseMove.mp4" frameborder="0"> </iframe>
