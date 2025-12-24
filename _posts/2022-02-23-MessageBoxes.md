---
title: (MFC) 메시지 박스 프로그램 -3
description: MessageBox 프로그램 작성
date: 2022-02-23 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, messagebox]
---

# [MFC] -3

- 최초 작성일: 2022년 2월 23일 (수)

## 

#### 1. 'MessageBoxes' .

#### 2. .

<br/>

#### 1. .

![image](https://user-images.githubusercontent.com/68185569/155272724-abc66b05-6e8c-44cd-94ef-62e2f49ba437.png)

<br/>

#### 2. [MFC?] .

![image](https://user-images.githubusercontent.com/68185569/155272851-b91abe20-ee72-4173-9e62-916b79177279.png)

<br/>

#### 3. 6 .

![image](https://user-images.githubusercontent.com/68185569/155276901-186988ec-3e4a-4c54-ac99-9c9b18494657.png)

<br/>

## 

### 

아래와 같이 MFC Application을 생성해준다. 프로젝트명은 MessageBoxes로 했다.

![image](https://user-images.githubusercontent.com/68185569/155267462-ed1b5472-223a-46c9-b7c9-858acd19ece2.png)

<br/>

그리고, Application type (응용 프로그램 종류)는 'Dialog based (대화 상자 기반)'를 선택하고 [Finish] 버튼을 클릭한다.

![image](https://user-images.githubusercontent.com/68185569/155261120-68dfaad7-09d3-41fb-b396-e9569d0b5c86.png)

<br/>

### 

그러면 아래와 같은 창이 나오는데, 안 나온다면 [Ctrl]-[Shift]-[R] 혹은 [메뉴]-[보기]-[다른 창]-[리소스 뷰]를 클릭하면 된다.

![image](https://user-images.githubusercontent.com/68185569/155261424-cbb0d2e8-080d-4e1e-ba5e-0e45e5241bca.png)

<br/>

그러면, 가운데 Dialog에 있는 모든 컨트롤들을 삭제해준다. ( [Ctrl + A] + [Delete] )

![image](https://user-images.githubusercontent.com/68185569/155261482-becf4476-1e49-46b6-9ea6-c98f1c5a58c2.png)

<br/>

컨트롤과 속성값은 아래와 같이 설정한다.

![image](https://user-images.githubusercontent.com/68185569/155273406-5d6b8852-22d4-4089-8c0a-e14b190de1ed.png)
![image](https://user-images.githubusercontent.com/68185569/155273293-6288723c-e9d6-4099-97f6-bc33a6855843.png)

<br/>

### 

버튼을 누를 때마다 Edit Control에 출력하기 위해 멤버 변수를 추가해주어야 한다.

멤버 함수를 추가하기 위해서 [메뉴]-[프로젝트]-[클래스 마법사] 또는, [Ctrl + Shift + X] 키를 눌러 [클래스 마법사]를 실행시킨다.

그럼, 아래의 창이 뜨는데 거기서 [Member Variables(멤버 변수)] 탭에서 'IDC_EDIT_RESULT'를 클릭한 후 'Add Variable(변수 추가)' 버튼을 클릭한다.

Control Variable(제어 변수) 창에서 다음과 같이 설정하고 Finish 버튼을 클릭한다. 그 다음, 멤버 변수 'm_strResult'가 추가된 것을 확인하고 확인 버튼을 누른다.

![image](https://user-images.githubusercontent.com/68185569/155273504-6f43a9fe-beeb-45d7-910e-95843411b14f.png)

![image](https://user-images.githubusercontent.com/68185569/155273640-4c4e2dc0-f911-4984-a2c1-054b73579cf0.png)

<br/>

또한 [클래스 뷰]-[MessageBoxes]-[CMessageBoxesDlg] 에서도 'm_strResult'가 추가된 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/155273798-4604626d-ad87-4a10-a720-9adaa9cc9871.png)

<br/>

### 

이제, 버튼을 눌렀을 때 함수를 실행하기 위해 멤버 함수를 추가해주어야 한다.

클래스 마법사를 키고 IDC_BUTTON_YN [명령], BN_CLICKED [메시지] 를 클릭하고 [처리기 추가] 를 눌러 멤버 함수들을 아래와 같이 추가한다.

![image](https://user-images.githubusercontent.com/68185569/155274017-c647dfc7-a3cf-488b-b8f8-cf0fa9de24fb.png)

<br/>

그 다음, 아래와 같이 코드를 삽입해주고, 프로그램을 빌드한 후 실행한다.

```c++
void CMessageBoxesDlg::OnClickedButtonYnc()
{
	// TODO: Add your control notification handler code here
	int iResults;
	m_strResult = _T("YES/NO/CANCEL 버튼을 눌렀습니다.");
	UpdateData(FALSE);
	iResults = AfxMessageBox(_T("YES/NO/CANCEL 버튼을 눌렀습니다."), (MB_YESNOCANCEL | MB_ICONINFORMATION));

	if (iResults == IDYES)
	{
		m_strResult = _T("OK 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDNO)
	{
		m_strResult = _T("NO 버튼을 눌렀습니다1");
		UpdateData(FALSE);
	}
	if (iResults == IDCANCEL)
	{
		m_strResult = _T("CANCEL 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
}

void CMessageBoxesDlg::OnClickedButtonYn()
{
	// TODO: Add your control notification handler code here
	int iResults;
	m_strResult = _T("YES/NO 버튼을 눌렀습니다.");
	UpdateData(FALSE);
	iResults = AfxMessageBox(_T("YES/NO 버튼을 눌렀습니다."), (MB_YESNO | MB_ICONWARNING));

	if (iResults == IDYES)
	{
		m_strResult = _T("YES 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDNO)
	{
		m_strResult = _T("NO 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
}

void CMessageBoxesDlg::OnClickedButtonRc()
{
	// TODO: Add your control notification handler code here
	int iResults;
	m_strResult = _T("RETRY/CANCEL 버튼을 눌렀습니다.");
	UpdateData(FALSE);
	iResults = AfxMessageBox(_T("RETRY/CANCEL 버튼을 눌렀습니다."), (MB_RETRYCANCEL | MB_ICONQUESTION));

	if (iResults == IDRETRY)
	{
		m_strResult = _T("RETRY 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDCANCEL)
	{
		m_strResult = _T("CANCEL 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
}

void CMessageBoxesDlg::OnClickedButtonOk()
{
	// TODO: Add your control notification handler code here
	int iResults{};
	m_strResult = _T("OK 버튼을 눌렀습니다!");
	UpdateData(FALSE);

	AfxMessageBox(_T("OK 버튼을 눌렀습니다."), MB_ICONERROR);
}

void CMessageBoxesDlg::OnClickedButtonOc()
{
	// TODO: Add your control notification handler code here
	int iResults;
	m_strResult = _T("OK/CANCEL 버튼을 눌렀습니다.");
	UpdateData(FALSE);
	iResults = AfxMessageBox(_T("OK/CANCEL 버튼을 눌렀습니다."), (MB_OKCANCEL | MB_ICONSTOP));

	if (iResults == IDOK)
	{
		m_strResult = _T("OK 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDCANCEL)
	{
		m_strResult = _T("CANCEL 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
}

void CMessageBoxesDlg::OnClickedButtonMfc()
{
	// TODO: Add your control notification handler code here
	m_strResult = _T("MFC 버튼을 눌렀습니다!");
	UpdateData(FALSE);

	MessageBox(_T("Microsoft Foundation Class 입니다."));
}

void CMessageBoxesDlg::OnClickedButtonExit()
{
	// TODO: Add your control notification handler code here
	OnOK();
}

void CMessageBoxesDlg::OnClickedButtonAri()
{
	// TODO: Add your control notification handler code here
	int iResults;
	m_strResult = _T("ABORT/RETRY/IGNORE 버튼을 눌렀습니다!");
	UpdateData(FALSE);
	iResults = AfxMessageBox(_T("ABORT/RETRY/IGNORE 버튼을 눌렀습니다."), (MB_ABORTRETRYIGNORE | MB_ICONINFORMATION));
	
	if (iResults == IDABORT)
	{
		m_strResult = _T("ABORT 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDRETRY)
	{
		m_strResult = _T("RETRY 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
	if (iResults == IDIGNORE)
	{
		m_strResult = _T("IGNORE 버튼을 눌렀습니다!");
		UpdateData(FALSE);
	}
}
```

<br/>

### 

![image](https://user-images.githubusercontent.com/68185569/155276020-059d377d-b542-43ce-bd31-bc5a52916fbf.png)

![image](https://user-images.githubusercontent.com/68185569/155275844-678f27e9-d55f-4d51-a8a1-8a32a7080cd1.png)
![image](https://user-images.githubusercontent.com/68185569/155275883-91434d15-7501-4e5d-84ee-ce67e67dbfec.png)
![image](https://user-images.githubusercontent.com/68185569/155275906-4dd54fb9-ad64-4fc9-8676-3a8b9bb5e077.png)
![image](https://user-images.githubusercontent.com/68185569/155275922-4c4c528d-3ae1-41fe-ad57-55d55ea979ec.png)
![image](https://user-images.githubusercontent.com/68185569/155275940-d9e7ac88-d890-4914-8c00-1313a5f0de06.png)
![image](https://user-images.githubusercontent.com/68185569/155275959-a24ee3f0-9f4d-4293-83b1-524366423cf9.png)
