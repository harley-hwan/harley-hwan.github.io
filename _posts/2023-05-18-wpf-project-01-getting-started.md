---
title: "(WPF) 1. WPF 프로젝트 시작하기 (프로젝트 생성, MVVM)"
description: "Data Control with C#"
date: 2023-05-18 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, mvvm, data-binding]
---

# WPF 프로젝트 시작하기 (프로젝트 생성, MVVM)
- 최초 작성일: 2023년 5월 18일 (목)

## WPF 프로젝트 생성

### 프로젝트 생성 및 선택

Visual Studio 2019 Professional 또는 최신 버전에서 WPF 애플리케이션 프로젝트를 생성하는 방법을 설명한다. 아래 이미지와 함께 단계별로 따라가면 쉽게 설정할 수 있다.

1. **Visual Studio 실행** 후 `새 프로젝트 만들기` 선택
2. **WPF 애플리케이션**을 검색하여 선택 (헷갈리지 않도록 주의)
   - `WPF 애플리케이션 (.NET Core)`: 다양한 운영체제에서 실행 가능하며, 최신 기술을 지원
   - `WPF 애플리케이션 (.NET Framework)`: Windows 전용이지만 기존 시스템과의 호환성이 뛰어남
3. **프로젝트 이름 및 저장 경로 설정**
4. `.NET Core` 또는 최신 `.NET` 버전 선택 후 `만들기`

> **추천:** 최신 프로젝트에서는 `.NET Core` 또는 `.NET 5/6/7`을 선택하는 것이 바람직하다. `.NET Framework`는 Windows 환경에서만 실행되며, 최신 기능이 제한될 수 있다.

![WPF 프로젝트 생성](https://github.com/harley-hwan/harley-hwan.github.io/assets/68185569/f2657c02-6a39-4ee6-ba5a-932ee220e533)

![프로젝트 설정 화면](https://github.com/harley-hwan/harley-hwan.github.io/assets/68185569/c50103a7-dfb7-4d33-aa16-06a7a406aa4a)

---

## MVVM 패턴의 이해

### MVVM이란?
MVVM (Model-View-ViewModel)은 WPF 및 다른 UI 프레임워크에서 널리 사용되는 아키텍처 패턴으로, UI와 비즈니스 로직을 분리하여 모듈화 및 유지보수를 용이하게 한다.

### MVVM의 구성 요소
1. **Model (모델)**
   - 애플리케이션의 데이터와 비즈니스 로직을 포함한다.
   - 예: 데이터베이스에서 가져온 사용자 정보, 파일 데이터 등

2. **View (뷰)**
   - 사용자 인터페이스(UI)를 나타낸다.
   - XAML 파일로 작성되며, 데이터 바인딩을 통해 뷰모델과 연결된다.

3. **ViewModel (뷰모델)**
   - View와 Model 사이에서 중개자 역할을 한다.
   - `INotifyPropertyChanged`를 구현하여 데이터 변경 시 UI가 자동으로 업데이트되도록 한다.

> **MVVM의 장점:** UI와 로직을 분리하여 코드의 재사용성을 높이고, 유지보수를 쉽게 한다.

---

## WPF에서 MVVM 적용하기

### MVVM을 적용한 WPF 프로젝트 기본 구성

1. **모델 (Model) 생성**
   - 애플리케이션에서 사용할 데이터를 정의하는 클래스를 만든다.
   - 예: `User.cs`를 생성하여 사용자 정보를 저장하는 클래스 작성

2. **뷰모델 (ViewModel) 생성**
   - `INotifyPropertyChanged` 인터페이스를 구현하여 UI 업데이트를 자동화한다.
   - 예: `MainViewModel.cs`를 만들어 UI와 연결되는 데이터를 처리

3. **뷰 (View) 구성**
   - XAML을 활용하여 UI 디자인을 구성한다.
   - 데이터 바인딩을 사용하여 ViewModel의 데이터를 뷰에 표시한다.

4. **데이터 바인딩 설정**
   - `{Binding}` 구문을 활용하여 ViewModel의 속성을 UI에 연결

5. **명령 패턴 사용 (Command Binding)**
   - 버튼 클릭 등의 이벤트를 `ICommand` 인터페이스를 활용해 처리한다.

6. **뷰와 뷰모델 연결 (DataContext 설정)**
   - `MainWindow.xaml.cs`에서 `DataContext`를 `MainViewModel`로 설정하여 데이터 바인딩을 활성화한다.

---

## 프로젝트 구조 및 예제

### 프로젝트 폴더 구조

WPF 프로젝트에서 MVVM 패턴을 적용할 때 일반적인 폴더 구조는 다음과 같다:

```
WPFProject/
├── Model/
│   ├── User.cs
├── View/
│   ├── MainWindow.xaml
├── ViewModel/
│   ├── MainViewModel.cs
├── App.xaml
├── MainWindow.xaml.cs
```

### 예제 코드

#### 1. 모델 (User.cs)
```csharp
public class User
{
    public string Name { get; set; }
    public int Age { get; set; }
}
```

#### 2. 뷰모델 (MainViewModel.cs)
```csharp
using System.ComponentModel;

public class MainViewModel : INotifyPropertyChanged
{
    private string _userName;
    public string UserName
    {
        get { return _userName; }
        set { _userName = value; OnPropertyChanged("UserName"); }
    }

    public event PropertyChangedEventHandler PropertyChanged;
    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

#### 3. 뷰 (MainWindow.xaml)
```xml
<Window x:Class="WPFProject.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MVVM Example" Height="200" Width="300">
    <Grid>
        <TextBox Text="{Binding UserName, UpdateSourceTrigger=PropertyChanged}" Width="200" Height="30" Margin="10"/>
    </Grid>
</Window>
```

#### 4. 데이터 컨텍스트 설정 (MainWindow.xaml.cs)
```csharp
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        this.DataContext = new MainViewModel();
    }
}
```

---

## 마무리

최신 WPF 프로젝트에서는 `.NET Core` 또는 `.NET 5/6/7`을 사용하는 것이 권장된다. MVVM 패턴을 적용하여 프로젝트를 시작하면 유지보수성과 확장성을 극대화할 수 있다.

