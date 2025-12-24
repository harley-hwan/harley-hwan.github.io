---
title: (Win32) 그림 그리기 프로그램
description: 그림 그리기 프로그램 작성 (윈도우 프로그램)
date: 2022-02-10 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, win32, windowprogramming]
---

# [Win32] 그림 그리기 프로그램

- 최초 작성일: 2022년 2월 10일 (목)

## 목적

이번 예제를 통해 자유롭게 움직여서 그림 그리는 프로젝트를 완성한다.

생성되는 윈도우 프로그램은 MousePos 변수를 이용한다. 

MousePos 변수는 마우스 위치 좌표 값을 실시간으로 검출되고 마우스 위치값을 지속적으로 update할 수 있다.

<br/>

## 실습

### 프로젝트 생성

다음과 같이 프로젝트를 새로 생성해주자. (Windows Desktop Application (Windows 데스크톱 응용 프로그램))

![image](https://user-images.githubusercontent.com/68185569/153343243-ce2ee8a1-e700-4255-b6e6-80a6a9f9cb49.png)

프로젝트명은 'SecondProject'로 하였다.

<br/>

### 코드 작성

그럼, 이제 코드를 삽입해보자.

SecondProject.cpp 파일에 다음과 같이 코드를 삽입하자.

```c++
// SecondProject.cpp : Defines the entry point for the application.

#include "framework.h"
#include "SecondProject.h"

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
    LoadStringW(hInstance, IDC_SECONDPROJECT, szWindowClass, MAX_LOADSTRING);
    MyRegisterClass(hInstance);

    // Perform application initialization:
    if (!InitInstance (hInstance, nCmdShow))
    {
        return FALSE;
    }

    HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_SECONDPROJECT));

    MSG msg;

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

//  FUNCTION: MyRegisterClass()
//
//  PURPOSE: Registers the window class.
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex;

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;      // 클래스 스타일
    wcex.lpfnWndProc    = WndProc;                      // 윈도우 프로시저
    wcex.cbClsExtra     = 0;                            // 윈도우 클래스 데이터 영역
    wcex.cbWndExtra     = 0;                            // 윈도우의 데이터 영역
    wcex.hInstance      = hInstance;                    // 인스턴스 핸들
    wcex.hIcon          = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_SECONDPROJECT));  // 아이콘 핸들
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);                           // 커서 핸들
    wcex.hbrBackground  = (HBRUSH)GetStockObject(LTGRAY_BRUSH);                     // 배경 브러시 핸들 (밝은 회색배경)
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_SECONDPROJECT);                      // 메뉴 이름
    wcex.lpszClassName  = szWindowClass;                                            // 윈도우 클래스 이름
    wcex.hIconSm        = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

    /*if (!RegisterClass(&wcex))
        return 1;*/

    return RegisterClassExW(&wcex);     // 윈도우클래스 register
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

    static POINT MousePos;     // 마우스 x,y 좌표를 저장할 변수

    static BOOL bDrawing = FALSE;

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

    case WM_LBUTTONDOWN:
        MousePos.x = LOWORD(lParam);
        MousePos.y = HIWORD(lParam);
        bDrawing = TRUE;
        SetCapture(hWnd);
        break;

    case WM_MOUSEMOVE:
        if (bDrawing == TRUE) {
            hdc = GetDC(hWnd);
            MoveToEx(hdc, MousePos.x, MousePos.y, NULL);
            MousePos.x = LOWORD(lParam);
            MousePos.y = HIWORD(lParam);
            LineTo(hdc, MousePos.x, MousePos.y);
            ReleaseDC(hWnd, hdc);
        }
        break;

    case WM_LBUTTONUP:
        bDrawing = FALSE;
        ReleaseCapture();
        break;

    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            hdc = BeginPaint(hWnd, &ps);
            // TODO: Add any drawing code that uses hdc here...
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

### 실행 결과

<iframe id="video" width="750" height="500" src="/assets/video/2022-02-10-MouseDraw.mp4" frameborder="0"> </iframe>
