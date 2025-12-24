---
title: "(WPF) 2. WPF 프로젝트의 구조 및 UI 구성"
description: "Visual Studio 활용 및 XAML 기본 이해"
date: 2023-05-19 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, ui, xaml, visualstudio]
---

# WPF 프로젝트의 구조 및 UI 구성
- 최초 작성일: 2023년 5월 19일 (금)

## 목차
1. [Visual Studio에서 WPF 프로젝트 시작하기](#visual-studio에서-wpf-프로젝트-시작하기)
2. [솔루션 탐색기 구조 이해](#솔루션-탐색기-구조-이해)
3. [XAML과 UI 구성 요소](#xaml과-ui-구성-요소)
4. [버튼 및 이벤트 핸들러 추가](#버튼-및-이벤트-핸들러-추가)
5. [라벨(Label) 추가 및 수정](#라벨-label-추가-및-수정)
6. [앱 실행 원리 이해](#앱-실행-원리-이해)

---

## Visual Studio에서 WPF 프로젝트 시작하기

WPF 애플리케이션을 개발하기 위해서는 먼저 Visual Studio를 실행하고 새로운 WPF 프로젝트를 생성해야 한다.

1. **Visual Studio 실행** 후 `새 프로젝트 만들기`를 클릭한다.
2. `WPF 애플리케이션 (.NET Core)`을 검색한 후 선택한다.
3. 프로젝트 이름을 `FirstProject`로 설정하고 저장 경로를 선택한다.
4. `.NET Core` 또는 최신 `.NET` 버전을 선택한 후 `만들기` 버튼을 클릭한다.
5. `Ctrl + F5`를 눌러 프로젝트를 실행하면 기본적인 WPF 창이 표시된다.

이제 프로젝트 구조를 살펴보고 UI를 구성하는 방법을 알아보자.

---

## 솔루션 탐색기 구조 이해

Visual Studio의 **솔루션 탐색기**에서 기본적인 프로젝트 구조를 확인할 수 있다.

- **FirstProject** (솔루션)
  - **Dependencies**: 프로젝트에서 사용하는 외부 라이브러리 및 패키지를 관리하는 공간이다.
  - **App.xaml 및 App.xaml.cs**: 애플리케이션의 전반적인 설정과 시작 지점을 정의하는 파일이다.
  - **MainWindow.xaml 및 MainWindow.xaml.cs**: 기본 UI 화면을 담당하며 XAML 파일과 코드 비하인드 파일로 구성된다.

이제 XAML을 활용하여 UI를 구성하는 방법을 살펴보자.

---

## XAML과 UI 구성 요소

### XAML 파일 이해

XAML은 WPF에서 UI를 구성하는 XML 기반의 마크업 언어이다. UI 요소를 선언적으로 정의할 수 있으며, `MainWindow.xaml` 파일을 열어보면 기본적인 구조를 확인할 수 있다.

  ```xml
  <Window x:Class="FirstProject.MainWindow"
          xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
          Title="First Project" Height="350" Width="525">
      <Grid>
          <!-- UI 요소가 여기에 추가됨 -->
      </Grid>
  </Window>
  ```

### 도구 상자 활용

Visual Studio의 **도구 상자 (Toolbox)** 에는 WPF에서 사용할 수 있는 다양한 UI 컨트롤이 포함되어 있다.

1. `도구 상자 (Toolbox)`를 열어 `Button` 컨트롤을 드래그하여 `MainWindow.xaml`의 `<Grid>` 내부에 추가한다.
2. 추가된 버튼은 XAML 코드에서 다음과 같이 자동으로 생성된다.

  ```xml
  <Button Content="Button" HorizontalAlignment="Left" Margin="641,49,0,0" VerticalAlignment="Top" Height="51" Width="104" Click="Button_Click"/>
  ```

이제 버튼 클릭 이벤트를 처리하는 방법을 살펴보자.

---

## 버튼 및 이벤트 핸들러 추가

1. `MainWindow.xaml`에서 버튼을 추가한 후 속성 창에서 `Click` 이벤트를 더블 클릭한다.
2. `MainWindow.xaml.cs`에서 자동으로 생성된 이벤트 핸들러에 코드를 추가한다.

  ```csharp
  private void Button_Click(object sender, RoutedEventArgs e)
  {
      MessageBox.Show("버튼이 클릭되었습니다!");
  }
  ```

3. `Ctrl + S`를 눌러 저장한 후, `Ctrl + F5`를 눌러 실행하면 버튼 클릭 시 메시지 박스가 나타나는 것을 확인할 수 있다.

---

## 라벨 (Label) 추가 및 수정

라벨을 추가하고, 코드에서 동적으로 내용을 변경해 보자.

1. `MainWindow.xaml`에서 `<Label>` 태그를 추가한다.

  ```xml
  <Label Name="MyLabel" Content="초기 텍스트" Width="200" Height="30"/>
  ```

2. 버튼 클릭 이벤트에서 라벨의 내용을 변경하도록 수정한다.

  ```csharp
  private void Button_Click(object sender, RoutedEventArgs e)
  {
      MyLabel.Content = "버튼이 눌렸습니다!";
  }
  ```

3. 실행 후 버튼을 클릭하면 라벨의 텍스트가 변경되는지 확인한다.

---

## 앱 실행 원리 이해

WPF 애플리케이션이 실행될 때 **App.xaml** 파일이 초기 설정을 담당한다.

1. `App.xaml` 파일을 열어보면 `StartupUri` 속성이 `MainWindow.xaml`로 지정되어 있다.
2. 이는 애플리케이션이 실행될 때 자동으로 `MainWindow`를 로드하도록 하는 역할을 한다.

  ```xml
  <Application x:Class="FirstProject.App"
               StartupUri="MainWindow.xaml">
  </Application>
  ```

3. `MainWindow.xaml.cs`의 생성자에서 `InitializeComponent();` 메서드를 호출하여 XAML에서 정의된 UI를 초기화한다.

  ```csharp
  public MainWindow()
  {
      InitializeComponent();
  }
  ```

이제 WPF 프로젝트의 기본 구조와 UI 요소를 구성하는 방법을 이해할 수 있다.

