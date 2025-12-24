---
title: (MFC) Text Control의 값을 버튼 클릭하여 클립보드에 복사하기
description: "c++, mfc, clipboard, copy, copytoclipboard, OpenClipboard(), EmptyClipboard(), wcstombs_s()"
date: 2023-03-10 10:00:00 +0900
categories: [Dev, MFC]
tags: [c, c++, mfc, clipboard, copy, copytoclipboard, OpenClipboard(), EmptyClipboard(), wcstombs_s()]
---

# Text Control 
- 최초 작성일: 2023년 3월 10일 (금)

## 

MFC 기반의 윈도우 응용 프로그램에서, 버튼을 클릭하면 시리얼 번호를 클립보드에 복사하는 기능을 구현하는 함수들이다.
 
- SetClipboardText 함수는 CStringW 타입의 strText 변수에 저장된 문자열을 클립보드에 복사한다.
- 먼저 OpenClipboard 함수를 호출하여 클립보드를 열고 EmptyClipboard 함수를 호출하여 클립보드에 있는 이전 내용을 모두 삭제한다.
- 그 다음, strText 변수에 저장된 문자열의 크기를 구한다.
- CString 클래스의 GetLength 함수를 사용하여 문자열의 길이를 구하고, 그 길이에 널 문자(\0) 하나를 더한 값을 sizeof(char)로 곱하여 문자열의 크기를 구한다. 이 값은 바이트 단위로 계산된다.
- 그리고 GlobalAlloc 함수를 호출하여 클립보드에 저장할 글로벌 메모리를 할당한다.
- GMEM_DDESHARE 플래그를 사용하여 공유 메모리를 할당한다.
- 할당된 메모리를 GlobalLock 함수를 호출하여 잠금 상태로 만든 다음, wcstombs_s 함수를 사용하여 CStringW 타입의 문자열을 char 타입의 문자열로 변환하여 복사한다.
- 마지막으로, SetClipboardData 함수를 호출하여 클립보드에 복사된 데이터를 저장한다. CF_TEXT는 char 타입의 텍스트 데이터를 나타내는 클립보드 포맷이다.
- CloseClipboard 함수를 호출하여 클립보드를 닫는다.
- OnBnClickedButtonCopySerial 함수는 버튼을 클릭하면 호출되며, m_stSerialNumber 컨트롤에서 시리얼 번호를 가져온다.
- GetWindowTextA 함수를 사용하여 CStringA 타입으로 변환한 후, CStringW 타입으로 변환하여 SetClipboardText 함수를 호출한다.
 
 <br/>

![image](https://user-images.githubusercontent.com/68185569/224242519-9299558f-474c-4c80-b408-17d8f649dba6.png)

<br/>

### 

```c++
void SetClipboardText(CStringW strText)
{
	if (OpenClipboard())
	{
		EmptyClipboard();

		// Get the size of the text in bytes.
		int nSize = (strText.GetLength() + 1) * sizeof(char);

		// Allocate global memory for the text.
		HGLOBAL hClipboardData = GlobalAlloc(GMEM_DDESHARE, nSize);
		if (hClipboardData != NULL)
		{
			// Lock the memory and copy the text to the clipboard.
			LPSTR pchData = (LPSTR)GlobalLock(hClipboardData);
			if (pchData != NULL)
			{
				wcstombs_s(NULL, pchData, nSize, strText, _TRUNCATE);
				GlobalUnlock(hClipboardData);
				SetClipboardData(CF_TEXT, hClipboardData);
			}
		}

		CloseClipboard();
	}
}

void OnBnClickedButtonCopySerial()
{
	CStringA strText;
	m_stSerialNumber.GetWindowTextA(strText);
	CStringW strTextW(strText);
	SetClipboardText(strTextW);
}

```
