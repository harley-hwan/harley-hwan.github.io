---
title: (Win32) 마우스 클릭 프로그램
description: 마우스 클릭 프로그램 작성 (윈도우 프로그램)
date: 2022-02-10 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, slider, windowprogramming]
---

# [Win32] 

- 최초 작성일: 2022년 2월 10일 (목)

## 

이번 예제를 통해 마우스를 이용해 이벤트가 발생하는 간단한 윈도우 프로그램을 작성한다.

마우스의 왼쪽과 오른쪽 버튼의 클릭을 구분 인식하는 것으로 [Win32 프로젝트]로 만들어진 프로젝트이다.

필자는 Visual Studio 2019 Pro 환경을 사용하였고, 버전이 달라도 크게 상관은 없을 것이다.

<br/>

## 

### 

다음과 같이 프로젝트를 새로 생성해주자. (Windows Desktop Application (Windows 데스크톱 응용 프로그램))

![image](https://user-images.githubusercontent.com/68185569/153343243-ce2ee8a1-e700-4255-b6e6-80a6a9f9cb49.png)

프로젝트명은 'FirstProject'로 하였다.

<br/>

### 

그럼, 이제 코드를 삽입해보자.

FirstProject.cpp 파일에 다음과 같이 코드를 삽입하자.

```c++
// FirstProject.cpp : Defines the entry point for the application.
//
#include <windows.h>

//#include "stdafx.h"
#include <TCHAR.H>

#include "framework.h"
#include "FirstProject.h"

#define MAX_LOADSTRING 100

// Global Variables:
HINSTANCE hInst;                                // current instance
WCHAR szTitle[MAX_LOADSTRING];                  // The title bar text
WCHAR szWindowClass[MAX_LOADSTRING];            // the main window class name

// Forward declarations of functions included in this code module:
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    About(HWND, UINT, WPARAM, LPARAM);

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(lpCmdLine);

    // TODO: Place code here.
    

    // Initialize global strings
    LoadStringW(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
    LoadStringW(hInstance, IDC_FIRSTPROJECT, szWindowClass, MAX_LOADSTRING);
    MyRegisterClass(hInstance);

    // Perform application initialization:
    if (!InitInstance (hInstance, nCmdShow))
    {
        return FALSE;
    }

    HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_FIRSTPROJECT));

    MSG msg;    // 메시지 구조체

    // Main message loop:
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
    return (int) msg.wParam;
}

//
//  FUNCTION: MyRegisterClass()
//
//  PURPOSE: Registers the window class.
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex;

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = WndProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hIcon          = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_FIRSTPROJECT));
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+1);
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_FIRSTPROJECT);
    wcex.lpszClassName  = szWindowClass;
    wcex.hIconSm        = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

    return RegisterClassExW(&wcex);
}

//
//   FUNCTION: InitInstance(HINSTANCE, int)
//
//   PURPOSE: Saves instance handle and creates main window
//
//   COMMENTS:
//
//        In this function, we save the instance handle in a global variable and
//        create and display the main program window.
//
BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   hInst = hInstance; // Store instance handle in our global variable

   // 윈도우 생성 (hWnd == 윈도우 핸들)
   HWND hWnd = CreateWindowW(szWindowClass, szTitle, WS_OVERLAPPEDWINDOW,
      CW_USEDEFAULT, 0, CW_USEDEFAULT, 0, nullptr, nullptr, hInstance, nullptr);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow);
   UpdateWindow(hWnd);

   return TRUE;
}

//
//  FUNCTION: WndProc(HWND, UINT, WPARAM, LPARAM)
//
//  PURPOSE: Processes messages for the main window.
//
//  WM_COMMAND  - process the application menu
//  WM_PAINT    - Paint the main window
//  WM_DESTROY  - post a quit message and return
//
//
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    HDC hdc;
    PAINTSTRUCT ps;
    TCHAR   str1[200] = TEXT("마우스를 클릭하세요");
    TCHAR   str2[200] = TEXT("오른쪽 마우스 / 왼쪽 마우스를 클릭하시면 메시지 상자가 나타납니다.");

    switch (message)
    {
    case WM_COMMAND:
        {
            int wmId = LOWORD(wParam);
            // Parse the menu selections:
            switch (wmId)
            {
            case IDM_ABOUT:
                DialogBox(hInst, MAKEINTRESOURCE(IDD_ABOUTBOX), hWnd, About);
                break;
            case IDM_EXIT:
                DestroyWindow(hWnd);
                break;
            default:
                return DefWindowProc(hWnd, message, wParam, lParam);
            }
        }
        break;

    case WM_CREATE:
        break;

    case WM_LBUTTONDOWN:
        MessageBox(hWnd, TEXT("왼쪽 마우스를 클릭하셨습니다."), TEXT("왼쪽 마우스 클릭!"), MB_OK);
        break;

    case WM_RBUTTONDOWN:
        MessageBox(hWnd, TEXT("오른쪽 마우스를 클릭하셨습니다."), TEXT("오른쪽 마우스 클릭!"), MB_OK);
        break;

    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hWnd, &ps);
            // TODO: Add any drawing code that uses hdc here...
            TextOut(hdc, 100, 100, str1, lstrlen(str1));
            TextOut(hdc, 100, 200, str2, lstrlen(str2));
            EndPaint(hWnd, &ps);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

// Message handler for about box.
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        break;
    }
    return (INT_PTR)FALSE;
}

```
<br/>

### 

#### WM_MOUSE 

|메시지|설명|
|---|---|
|WM_LBUTTONDOWN|마우스의 왼쪽 버튼을 누를 경우|
|WM_LBUTTONUP|마우스의 왼쪽 버튼에서 뗄 경우|
|WM_LBUTTONDBLCLK|마우스의 왼쪽 버튼을 더블클릭할경우|
|WM_RBUTTONDOWN|마우스의 오른쪽 버튼을 누를 경우|
|WM_RBUTTONUP|마우스의 오른쪽 버튼에서 뗄 경우|
|WM_RBUTTONDBLCLK|마우스의 오른쪽 버튼을 더블클릭할 경우|
|WM_MOUSEMOVE|마우스가 움직일 때|
|WM_MOUSEWHEEL|마우스 휠이 움직일 경우|

<br/>

#### GDI Object

|GDI Object|핸들타입|기능|
|---|---|---|
|펜|HPEN|선을 생성|
|브러시|hbrush|면을 생성|
|폰트|HFONT|문자 출력에 사용되는 글꼴|
|비트맵|HBITMAP|비트맵 이미지|
|팔레트|hpalette|팔레트|
|영역|HRGN|영역|

<br/>

#### HBRUSH/HPEN COLOR

|BLACK_BRUSH|검정 브러시|
|GRAY_BRUSH|회색 브러시|
|NULL_BRUSH|투명 브러시|
|WHITE_BRUSH|흰색 브러시|
|DKGRAY_BRUSH|어두운 회색 브러시|
|LTGRAY_BRUSH|밝은 회색 브러시|
|BLACK_PEN|검정 펜|
|WHITE_PEN|흰색 펜|
|NULL_PEN|투명펜|

<br/>

#### WinMain() 

<window.h> 파일에 포함된 함수로서, 윈도우 어플리케이션에서는 WinMain() 함수가 반드시 포함되어야 한다.

<br/>

#### (WINDCLASS)

```c++
typedef struct tagWNDCLASS
{
  UINT      style;        // 윈도우 스타일 정의. 일반적으로 CS_HREDRAW | CS_VREDRAW로 사용
  WNDPROC   lpfnWndProc;  // 윈도우 메시지 처리 함수 지정
  int       cbClsExtra;   // 특수목적의 여분의 사용 공간
  int       cbWndExtra;   // ''
  HINSTANCE hInstnace;    // 윈도우클래스 등록 번호
  HICON     hIcon;        // 마우스 아이콘 지정
  HCURSOR   hCursor;      // 마우스 커서 지정
  HBRUSH    hbrBackgound; // 윈도우 배경 색상
  LPCSTR    lpszMenuName; // 프로그램이 사용할 메뉴 지정
  LPCSTR    lpszClassName // 윈도우 클래스의 이름을 문자열로 정의
}
```
<br/>

#### windows.h

C 언어 또는 C++에서 Window API를 구현하는 데 있어서 기본적인 함수이다.

<br/>

#### WndProc

WndProc 는 Window Procedure로서 메시지가 발생할 때 처리하는 메시지 처리 함수이다. 또한 메시지가 이볅되면 윈도우즈에 메시지가 호출되어 처리된다.

이러한 함수를 응용 프로그램 내에서 CallBack 함수라 한다.

WM_CREATE, WM_LBUTTONDOWN, WM_RBUTTONDOWN, WM_PAINT, WM_DESTROY는 메시지 처리 함수이다.

```c++
LRESULT CALLBACK WndProc(
  _In_  HWND    hwnd,   // 메시지를 받을 윈도우 핸들
  _In_  UINT    uMsg,   // 메시지 종류
  _In_  WPARAM  wParam, // 메시지의 부가 정보
  _In_  LPARAM  lParam  // ''
);
```
<br/>

#### TextOut()

간단한 텍스트를 출력하는 함수이다.

```c++
TextOut(hdc, int n, int y, "문자열", 문자열 길이)
```

- (x, y) 좌표를 시작으로 문자열을 출력

<br/>

#### Text()

문자열 상수만 포함되어야 한다.

<br/>

### 1

![image](https://user-images.githubusercontent.com/68185569/153347483-4ef5fa05-7412-44e6-a6e9-2105541cadb0.png)

![image](https://user-images.githubusercontent.com/68185569/153347507-5284b9ad-ecfb-413c-9fb1-4dfcc4936859.png)
