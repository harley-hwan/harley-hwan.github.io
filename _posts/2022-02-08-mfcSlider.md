---
title: (MFC) 색상 슬라이드 프로그램 작성
description: 슬라이더(Slider Control)의 이용
date: 2022-02-08 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, slider, rgb, windowprogramming]
---

# [MFC] 색상 슬라이드 프로그램 작성

- 최초 작성일: 2022년 2월 8일 (화)


## 목차



## 실습

### 프로젝트 생성

다이얼로그 기반으로 mfc App 프로젝트를 새로 생성한다.

프로젝트명은 RGBSlide 라고 했다.

<br/>

### 다이얼로그 편집/디자인

우선, 다이얼로그를 편집하자. 아래와 같이 Resource View에서 해당 다이얼로그를 더블클릭하고, 다이얼로그에 있는 컨트롤들을 모두 삭제한다. (Ctrl + A) + Delete 하면 된다.

![image](https://user-images.githubusercontent.com/68185569/153106813-89d8ff42-1f4d-460f-89c2-7675a7e1695f.png)

<br/>

그러면, Toolbox를 통해 컨트롤과 속성을 아래와 같이 설정한다.

![image](https://user-images.githubusercontent.com/68185569/152954786-dfd9ea8c-d6d4-4b26-b854-31f2c76e6137.png)
![image](https://user-images.githubusercontent.com/68185569/153106446-2434722e-c9b4-4fa5-ad25-1cc40e5635a1.png)

<br/>

### 변수 추가

위의 단계를 마쳤으면, 이제 멤버 변수들을 추가해보자.

우선, 'Slide Control'에 멤버 변수를 추가한다.

[메뉴]-[프로젝트]-[클래스 마법사] 를 클릭하거나 [Ctrl + Shift + X] 키를 눌러 [클래스 마법사]를 실행한다.

그러면, 아래 이미지처럼 창이 뜨는데, Class Name을 고르고 [멤버 변수] 탭에서 'IDC_SLIDER_R'을 클릭한 후 'Add Variable (변수 추가)' 버튼을 눌러 다음과 같이 설정한다.

![image](https://user-images.githubusercontent.com/68185569/153107609-8ca1f3e4-34bc-4086-93e0-004364f003a8.png)

![image](https://user-images.githubusercontent.com/68185569/153106710-7ac6fdc1-0eee-4d60-8d20-cf22ba5b4e12.png)

<br/>

마찬가지로, 'IDC_SLIDER_G'와 'IDC_SLIDER_B' 도 똑같이 설정한다.

<br/>

다음으로, [멤버 변수] 탭에서 'IDC_EDIT_R'을 클릭하고 'Add Variable (변수 추가)' 버튼을 눌러 다음과 같이 설정하고, 'IDC_EDIT_G', 'IDC_EDIT_B'도 똑같이 설정한다. 

![image](https://user-images.githubusercontent.com/68185569/153107847-9beecc9a-ceaa-406c-acf3-c53c5e83eeb2.png)

<br/>

설정을 마치면 아래와 같이 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/153107445-3d3cc9ab-54fe-4724-8f8d-0366b922141f.png)

<br/>

그러면, [Class View]-[RGBSlide]-[CRGBSlideDlg] 에 'SLIDER Control' 변수 3개와 'EDIT Control' 변수 3개가 생성된 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/153108693-a3ae6bc4-cd2b-4ad1-b0f1-37e19ff73707.png)

<br/>

마지막으로, [Class View]-[CRGBSlideDlg]에서 마우스 오른쪽 버튼을 누르고 [Add]-[Add Variable]를 클릭하여 다음과 같이 변수를 하나 추가해준다.

![image](https://user-images.githubusercontent.com/68185569/153109231-5fe5a9cd-5976-43b2-aa27-cd420f94103a.png)

<br/>

### 코드 작성

 OnInitDialog() 함수에서 RGB 값을 각각 초기화한다.
 
 [Class View]-[RGBSlide]-[CRGBSlideDlg]-[OnInitdialog()]를 더블클릭해서 추가하면 된다.
 
![image](https://user-images.githubusercontent.com/68185569/153109498-9d9f5d6d-69b0-4b64-b7de-21a5a4993b82.png)

<br/>

다음으로, OnPaint() 함수에 다음과 같이 코드를 삽입해준다.

```c++
void CRGBSlideDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
		
		// 추가할 코드
		CRect rect;
		CClientDC rgbdc(GetDlgItem(IDC_STATIC_RGB));
		CStatic* pSRGB = (CStatic*)GetDlgItem(IDC_STATIC_RGB);
		pSRGB->GetClientRect(rect);
		rgbdc.FillSolidRect(rect, m_cRGB);
		pSRGB->ValidateRect(rect);
	}
}
```

<br/>

그럼 이제, 슬라이더에서 마우스가 움직일 때 그 값을 알아내기 위해 'WM_HSCROLL' 메시지를 이용해 OnHScroll(~) 함수를 추가하자.

클래스 마법사를 키고, 클래스 이름에서 'CRGBSlideDlg'를 선택하고 [Message] 탭에서 'WM_HSCROLL' 메시지를 더블클릭하고 확인 버튼을 누르면, OnHScroll 함수가 자동으로 생성된다.

그럼, 아래와 같이 코드를 작성하자.

```c++
void CRGBSlideDlg::OnHScroll(UINT nSBCode, UINT nPos, CScrollBar* pScrollBar)
{
	// TODO: Add your message handler code here and/or call default

	CRect rect;
	GetDlgItem(IDC_STATIC_RGB)->GetWindowRect(&rect);
	ScreenToClient(&rect);
	int nR = m_sldR.GetPos();
	int nG = m_sldG.GetPos();
	int nB = m_sldB.GetPos();

	if ((pScrollBar == (CScrollBar*)&m_sldR) || 
		(pScrollBar == (CScrollBar*)&m_sldG) || 
		(pScrollBar == (CScrollBar*)&m_sldB))
	{
		// 슬라이더 위치를 검사
		int nPosR = m_sldR.GetPos();
		int nPosG = m_sldG.GetPos();
		int nPosB = m_sldB.GetPos();

		m_nR = nPosR;
		m_nG = nPosG;
		m_nB = nPosB;

		m_cRGB = RGB(m_nR, m_nG, m_nB);
		UpdateData(FALSE);
		InvalidateRect(&rect);
	}
	else
	{
		CDialogEx::OnHScroll(nSBCode, nPos, pScrollBar);
	}
}
```

<br/>

그럼, 진짜 마지막으로 'Clear' 버튼과 '나가기' 버튼의 기능을 추가해주자.

똑같이, 클래스 마법사를 열어 다음과 같이 멤버 함수를 추가해주자. 'Clear'와 'Exit' 둘다 해준다.

![image](https://user-images.githubusercontent.com/68185569/153110474-6b2cd0fd-e323-4389-91c2-d83da44f4082.png)

![image](https://user-images.githubusercontent.com/68185569/153110602-74c3156b-cfe0-49ff-8371-6f652778ca69.png)

<br/>

그렇게 함수가 추가되면, 코드를 다음과 같이 삽입해준다.

![image](https://user-images.githubusercontent.com/68185569/153111285-53ea5748-3a02-487a-a006-0ac3dff3a230.png)

<br/>

근데, OnOK() 함수는 그냥 되는데, Clear() 함수는 에러가 뜨는 걸 볼 수 있다. 이유는, OnOk() 함수는 내장함수이기 때문에 따로 정의해주지 않아도 그대로 사용할 수 있지만, Clear() 함수는 따로 정의해주어야 한다.

그러므로, [Class View]-[RGBSlide]-[CRGBSlideDlg]에서 마우스 오른쪽 버튼을 누른 후, [추가]-[함수 추가]를 클릭하여, 다음과 같이 Clear 함수를 생성하고, 아래와 같이 정의해주자. 

초기화 상태로 되돌리는 것이 목적이기 때문에, 모든 값들을 0으로 초기화해주면 된다.

![image](https://user-images.githubusercontent.com/68185569/153111263-c405b5b4-9983-4f8b-840d-4c796d6cc977.png)

```c++
void CRGBSlideDlg::Clear()
{
	// TODO: Add your implementation code here.
	UpdateData(TRUE);

	CRect rect;
	GetDlgItem(IDC_STATIC_RGB)->GetWindowRect(&rect);
	ScreenToClient(&rect);
	InvalidateRect(&rect);

	m_cRGB = RGB(0, 0, 0);

	m_nR = 0;
	m_nG = 0;
	m_nB = 0;

	m_cRGB = RGB(0, 0, 0);
	UpdateData(FALSE);
}
```

<br/>

### 실행 결과 1

<iframe id="video" width="750" height="500" src="/assets/video/2022-02-08-mfcSlider.mp4" frameborder="0"> </iframe>

