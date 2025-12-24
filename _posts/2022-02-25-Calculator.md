---
title: (MFC) 계산기 프로그램 작성 I
description: Calculator Program 1
date: 2022-02-25 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, calculator]
---

# [MFC] 계산기 프로그램 작성 1

- 최초 작성일: 2022년 2월 25일 (금)

## 목차

[TOC]

## 목적

사칙 연산과 CString 함수의 형 변환을 이용하여 계산기 프로그램을 작성한다.

<br/>

### 프로젝트 생성

- 프로젝트명: 'Calc'
- 응용 프로그램 종류: '대화 상자 기반'

<br/>

### 다이얼로그 설정

![image](https://user-images.githubusercontent.com/68185569/155664654-42f13675-ba60-43c9-85fb-e1b83736c382.png)

![image](https://user-images.githubusercontent.com/68185569/155662132-e66c92ef-b872-40d1-b331-f030b3adf08f.png)



<br/>

### 멤버 변수 설정

아래와 같이, [클래스 뷰]-[Calc]-[CCalcDlg]에서 [추가]-[변수 추가]를 클릭하고 멤버 변수를 추가한다.

![image](https://user-images.githubusercontent.com/68185569/155664966-14d69c18-c8d6-4585-8bcf-6b460bfb7c4c.png)

![image](https://user-images.githubusercontent.com/68185569/155661411-b0448ed6-4362-4ef8-970e-88725296171f.png)

<br/>

그리고 클래스 마법사를 실행시키고, [멤버 변수] 탭에서 아래와 같이 멤버 변수들을 추가한다.

![image](https://user-images.githubusercontent.com/68185569/155665510-b5e2f007-5740-40c7-8cb0-09071c0ea4da.png)

![image](https://user-images.githubusercontent.com/68185569/155665778-d5f6aecb-7570-4e30-8364-d2b8f917500d.png)

<br/>

또한, 클래스 마법사에서 다음과 같이 버튼 클릭시에 대한 멤버 함수를 추가하고, 코드를 작성하자.

![image](https://user-images.githubusercontent.com/68185569/155672210-78256d1b-ae21-42ff-be38-c2364cc41119.png)


### 코드 작성

```c++
void CCalcDlg::OnClickedButtonAdd()
{
	// TODO: Add your control notification handler code here
	m_nOption = 1;
}

void CCalcDlg::OnClickedButtonSub()
{
	// TODO: Add your control notification handler code here
	m_nOption = 2;
}

void CCalcDlg::OnClickedButtonMul()
{
	// TODO: Add your control notification handler code here
	m_nOption = 3;
}

void CCalcDlg::OnClickedButtonDiv()
{
	// TODO: Add your control notification handler code here
	m_nOption = 4;
}

void CCalcDlg::OnClickedButtonEqu()
{
	// TODO: Add your control notification handler code here
	char temp[10];
	double tmpResult;

	UpdateData(TRUE);

	switch (m_nOption)
	{
		case 1:
			tmpResult = atof(m_nNum1) + atof(m_nNum2);	// [프로젝트 속성]-[구성 속성]-[고급]-[문자 집합]-[멀티바이트 문자 집합 사용] 안하면 에러뜸.
			break;
		case 2:
			tmpResult = atof(m_nNum1) - atof(m_nNum2);
			break;
		case 3:
			tmpResult = atof(m_nNum1) * atof(m_nNum2);
			break;
		case 4:
			tmpResult = atof(m_nNum1) / atof(m_nNum2);
			break;
		default:
			tmpResult = 0.00;
			break;
	}

	sprintf_s(temp, "%2.f", tmpResult);
	m_nResult = temp;
	UpdateData(FALSE);
}

void CCalcDlg::OnClickedButtonClear()
{
	// TODO: Add your control notification handler code here
	UpdateData(TRUE);
	m_nNum1 = L"";
	m_nNum2 = _T("");
	m_nResult = _T("");
	UpdateData(FALSE);
}

void CCalcDlg::OnClickedButtonExit()
{
	// TODO: Add your control notification handler code here
	PostQuitMessage(0);
}
```

<br/>

### 결과

![image](https://user-images.githubusercontent.com/68185569/155672509-8ce8846c-ae0f-4521-b013-d7484b451a61.png)

![image](https://user-images.githubusercontent.com/68185569/155672643-a0175b9d-d417-4310-94e0-7377f42b3c9a.png)

![image](https://user-images.githubusercontent.com/68185569/155672597-34f8314c-ad8f-4bd1-a03f-7481b61f39b4.png)

![image](https://user-images.githubusercontent.com/68185569/155672740-f8732fec-68c4-46d1-88bb-3a9bb31ac747.png)






