---
title: (MFC) 계산기 프로그램 작성 II
description: Calculator Program 2
date: 2022-02-25 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, calculator]
---

# [MFC] 계산기 프로그램 작성 2

- 최초 작성일: 2022년 2월 25일 (금)

## 목차

[TOC]

## 목적

사칙 연산과 CString 함수의 형 변환을 이용하여 계산기 프로그램을 작성한다.

<br/>

### 프로젝트 생성

- 프로젝트명: 'CalcEx'
- 응용 프로그램 종류: '대화 상자 기반'

<br/>

### 다이얼로그 설정

![image](https://user-images.githubusercontent.com/68185569/155677896-a3412f66-ce1b-45ac-b5c5-f173cafba63c.png)
![image](https://user-images.githubusercontent.com/68185569/155679067-238b10c9-9ba5-4772-97df-07fce87f3b7b.png)

<br/>

### 멤버 변수 및 함수 추가

![image](https://user-images.githubusercontent.com/68185569/155679387-335f29f0-5c84-4c2d-8308-f2720771d2d1.png)

![image](https://user-images.githubusercontent.com/68185569/155679358-74ad9f56-9d0d-42b3-9f93-b9473ee979c5.png)

<br/>

### 코드 작성

```c++
void CCalcExDlg::OnClickedButtonInput()
{
	// TODO: Add your control notification handler code here
	char tmp_avg[10];
	char tmp_sum[10];
	char tmp_grade;
	double tmpAvg;
	double tmpSum;
	
	UpdateData(TRUE);

	tmpSum = atof(m_nKOR) + atof(m_nENG) + atof(m_nMATH);
	tmpAvg = tmpSum / 3;
	
	if (tmpAvg >= 90)		tmp_grade = 'A';
	else if (tmpAvg >= 80)	tmp_grade = 'B';
	else if (tmpAvg >= 70)	tmp_grade = 'C';
	else if (tmpAvg >= 60)	tmp_grade = 'D';
	else					tmp_grade = 'F';
	
	sprintf_s(tmp_sum, "%2.f", tmpSum);
	sprintf_s(tmp_avg, "%2.f", tmpAvg);
	
	m_nSUM = tmp_sum;
	m_nAVG = tmp_avg;
	m_nGRADE = tmp_grade;
	UpdateData(FALSE);
}
```



<br/>

### 결과

![image](https://user-images.githubusercontent.com/68185569/155679462-6e2ec402-e827-4d54-85c8-c4da55cbb2b2.png)





