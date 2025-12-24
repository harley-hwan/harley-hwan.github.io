---
title: (MFC) 메시지 박스 프로그램 -2
description: MessageBox 프로그램 작성
date: 2022-02-23 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, messagebox]
---

# [MFC] 메시지 박스 프로그램 작성 -2

- 최초 작성일: 2022년 2월 23일 (수)

## 목차



## 목적

2개의 버튼을 생성하고, 생성된 버튼을 클릭하면 새로운 창이 표시된다.

<br/>

## 구현

### 프로젝트 생성

아래와 같이 MFC Application을 생성해준다. 프로젝트명은 MsgBox2로 했다.

![image](https://user-images.githubusercontent.com/68185569/155264036-7d2ed1fb-0d85-4b20-ab48-68f2e9a1028f.png)

<br/>

그리고, Application type (응용 프로그램 종류)는 'Dialog based (대화 상자 기반)'를 선택하고 [Finish] 버튼을 클릭한다.

![image](https://user-images.githubusercontent.com/68185569/155261120-68dfaad7-09d3-41fb-b396-e9569d0b5c86.png)

<br/>

### 다이얼로그 생성 및 설정

그러면 아래와 같은 창이 나오는데, 안 나온다면 [Ctrl]-[Shift]-[R] 혹은 [메뉴]-[보기]-[다른 창]-[리소스 뷰]를 클릭하면 된다.

![image](https://user-images.githubusercontent.com/68185569/155261424-cbb0d2e8-080d-4e1e-ba5e-0e45e5241bca.png)

<br/>

그러면, 가운데 Dialog에 있는 모든 컨트롤들을 삭제해준다. ( [Ctrl + A] + [Delete] )

![image](https://user-images.githubusercontent.com/68185569/155261482-becf4476-1e49-46b6-9ea6-c98f1c5a58c2.png)

<br/>

그런 다음, Toolbox(도구상자)로부터 Edit Control 1개와 Button 3개를 끌어와 생성하고, 아래와 같이 설정한다.

![image](https://user-images.githubusercontent.com/68185569/155264959-0af8555a-c8f7-4e31-9e9a-4a4d2db4c945.png)
![image](https://user-images.githubusercontent.com/68185569/155264949-62dbc6cb-9a03-4449-95ba-f306c1fddc66.png)

<br/>

### 멤버 변수 추가

멤버 함수를 추가하기 위해서 [메뉴]-[프로젝트]-[클래스 마법사] 또는, [Ctrl + Shift + X] 키를 눌러 [클래스 마법사]를 실행시킨다.

그럼, 아래의 창이 뜨는데 거기서 [Member Variables(멤버 변수)] 탭에서 'IDC_EDIT_RESULT'를 클릭한 후 'Add Variable(변수 추가)' 버튼을 클릭한다.

![image](https://user-images.githubusercontent.com/68185569/155265086-372d55f7-da55-44ac-9acd-09033429ff1b.png)

<br/>

Control Variable(제어 변수) 창에서 다음과 같이 설정하고 Finish 버튼을 클릭한다. 그 다음, 멤버 변수 'm_strResult'가 추가된 것을 확인하고 확인 버튼을 누른다.

![image](https://user-images.githubusercontent.com/68185569/155265197-791e9cf8-1ffb-4af8-9dd7-5a8adc3a8c2d.png)

<br/>

또한 [클래스 뷰]-[MsgBox2]-[CMsgBox2Dlg] 에서도 'm_strResult'가 추가된 것 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/155265385-e0291bc1-c743-4303-9db7-f7dc32122411.png)

<br/>

### 멤버 함수 추가

그러면, 클래스 마법사를 키고 IDC_BUTTON_YN [명령], BN_CLICKED [메시지] 를 클릭하고 [처리기 추가] 를 눌러 멤버 함수를 추가한다.

![image](https://user-images.githubusercontent.com/68185569/155266077-0a376910-596a-49c2-9828-df50372d8a40.png)

<br/>

그 다음, 아래와 같이 코드를 삽입해주고, 프로그램을 빌드한 후 실행한다.

```c++
void CMsgBox2Dlg::OnClickedButtonYn()
{
	// TODO: Add your control notification handler code here
	int iResults;
	iResults = AfxMessageBox(_T("YES/NO 버튼을 누르셨습니다."), (MB_YESNO | MB_ICONEXCLAMATION));
	if (iResults == IDYES)
	{
		m_strResult = _T("YES 버튼을 누르셨습니다.");
		UpdateData(FALSE);
	}
	if (iResults == IDNO)
	{
		m_strResult = _T("NO 버튼을 누르셨습니다.");
		UpdateData(FALSE);
	}
}
```

<br/>

### 실행 결과 1

![image](https://user-images.githubusercontent.com/68185569/155265940-ab814dd2-a5b1-407f-8969-3dd4f028d4a0.png)

<br/>

마찬가지로, OK and Cancel 버튼에 멤버 함수를 추가하고, 아래의 코드를 삽입하고 프로그램을 빌드 후 실행한다.

```c++
void CMsgBox2Dlg::OnClickedButtonOc()
{
	// TODO: Add your control notification handler code here
	int iResults;
	iResults = AfxMessageBox(_T("OK/CANCEL 버튼을 누르셨습니다."), (MB_OKCANCEL | MB_ICONEXCLAMATION));
	if (iResults == IDOK)
	{
		m_strResult = _T("OK 버튼을 누르셨습니다.");
		UpdateData(FALSE);
	}
	if (iResults == IDCANCEL)
	{
		m_strResult = _T("CANCEL 버튼을 누르셨습니다.");
		UpdateData(FALSE);
	}
}
```

<br/>

### 실행 결과 2

![image](https://user-images.githubusercontent.com/68185569/155266612-a28548fa-8284-4436-aedc-dc53d6a44a4d.png)

<br/>

## 마무리

마지막으로, Exit 버튼에 대한 멤버 함수 'OnClickedButtonExit()'를 생성하고 아래의 코드를 삽입해주면, Exit 클릭시 프로그램이 종료된다.

```c++
void CMsgBox2Dlg::OnClickedButtonExit()
{
	// TODO: Add your control notification handler code here
	OnOK();
}
```
