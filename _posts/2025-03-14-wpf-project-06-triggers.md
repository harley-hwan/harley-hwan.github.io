---
title: "(WPF) 6. WPF에서 트리거와 데이터 트리거 활용하기"
description: "트리거를 활용한 스타일 및 데이터 연동 방법"
date: 2025-03-14 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, triggers, data-triggers, ui, xaml]
---

# 트리거와 데이터 트리거 활용하기

- 최초 작성일: 2025년 3월 14일 (금)

## 목차

1. [트리거(Trigger) 개요](#트리거trigger-개요)
2. [트리거를 활용한 스타일 변경](#트리거를-활용한-스타일-변경)
3. [데이터 트리거(DataTrigger)를 통한 컨트롤 상태 변경](#데이터-트리거datatrigger를-통한-컨트롤-상태-변경)
4. [INotifyPropertyChanged와 데이터 트리거 활용](#inotifypropertychanged와-데이터-트리거-활용)

---

## 트리거(Trigger) 개요

WPF에서 **트리거(Trigger)**는 특정 이벤트나 속성 값의 변화가 발생했을 때, 미리 정의된 스타일을 자동으로 적용하여 UI를 동적으로 변경할 수 있는 기능이다. 대표적인 사용 예는 버튼 클릭, 마우스 오버, 컨트롤 활성화 여부 등에 따라 컨트롤의 스타일을 변경하는 경우가 있다.

---

## 트리거를 활용한 스타일 변경

아래의 예제는 버튼 위에 마우스를 올리거나 클릭했을 때 글자 색상을 변경하는 방법을 보여준다.

```xml
<Style x:Key="ButtonTriggerStyle" TargetType="Button">
    <Style.Triggers>
        <Trigger Property="IsMouseCaptureWithin" Value="True">
            <Setter Property="Foreground" Value="Blue"/>
        </Trigger>
        <Trigger Property="IsMouseOver" Value="True">
            <Setter Property="Foreground" Value="Green"/>
        </Trigger>
    </Style.Triggers>
</Style>

<Button Content="트리거 테스트" Style="{StaticResource ButtonTriggerStyle}" />
```

- 버튼 클릭 시 글자색이 파란색으로 변경된다.
- 마우스가 올라가면 글자색이 초록색으로 변경된다.

---

## 데이터 트리거(DataTrigger)를 통한 컨트롤 상태 변경

**데이터 트리거(DataTrigger)**는 특정 데이터의 상태나 다른 컨트롤의 속성 값이 변경될 때 이를 감지하여 UI의 스타일 또는 상태를 변경한다. 예를 들어, 체크박스를 선택하면 버튼의 글자 색상과 활성 상태를 변경하는 방법을 아래에서 확인할 수 있다.

```xml
<CheckBox x:Name="CheckBox1" Content="버튼 비활성화"/>

<Button Content="테스트 버튼">
    <Button.Style>
        <Style TargetType="Button">
            <Style.Triggers>
                <DataTrigger Binding="{Binding ElementName=CheckBox1, Path=IsChecked}" Value="True">
                    <Setter Property="Foreground" Value="Red"/>
                    <Setter Property="IsEnabled" Value="False"/>
                </DataTrigger>
            </Style.Triggers>
        </Style>
    </Button.Style>
</Button>
```

위의 예제를 실행하면 체크박스를 선택할 경우 버튼의 글자가 빨간색으로 변경되고 버튼이 비활성화된다.

---

## INotifyPropertyChanged와 데이터 트리거 활용

데이터 트리거는 MVVM 패턴에서 ViewModel의 속성 값 변경에 따라 View를 동적으로 변경하는 데 사용된다. **INotifyPropertyChanged** 인터페이스를 통해 데이터의 변화를 View에 즉시 반영할 수 있다.

### ViewModel 클래스 생성 과정

MVVM 패턴을 명확히 활용하기 위해 ViewModel 클래스는 일반적으로 프로젝트 내의 `ViewModels`라는 별도의 폴더에 생성한다. 다음과 같은 순서를 따른다.

1. 솔루션 탐색기에서 프로젝트를 마우스 오른쪽 버튼으로 클릭하고, **새 폴더**를 선택한 후 폴더명을 `ViewModels`로 설정한다.
2. `ViewModels` 폴더를 마우스 오른쪽 버튼으로 클릭하고, **추가 → 클래스**를 선택한다.
3. 클래스 이름을 `MainViewModel`로 입력하고 추가 버튼을 클릭한다.

### MainViewModel 클래스 작성 예제

```csharp
using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace WpfAppProject.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        private int progressValue;

        public int ProgressValue
        {
            get => progressValue;
            set
            {
                if (progressValue != value)
                {
                    progressValue = value;
                    NotifyPropertyChanged();
                }
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        private void NotifyPropertyChanged([CallerMemberName] string propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
```

### View와 ViewModel 연결

아래는 MainWindow 코드에서 ViewModel과 View를 연결하는 방법이다.

```csharp
public MainWindow()
{
    InitializeComponent();
    var mainViewModel = new MainViewModel { ProgressValue = 30 };
    DataContext = mainViewModel;
}

private void btnTest1_Click(object sender, RoutedEventArgs e)
{
    ((MainViewModel)DataContext).ProgressValue = 100;
}
```

### 데이터 트리거를 이용한 상태 변경

아래 예제는 프로그레스 바의 값이 100일 때 자동으로 프로그레스 바를 숨기도록 하는 데이터 트리거 설정 방법이다.

```xml
<ProgressBar x:Name="progressBar1" Minimum="0" Maximum="100" Value="{Binding ProgressValue}" Height="20">
    <ProgressBar.Style>
        <Style TargetType="ProgressBar">
            <Style.Triggers>
                <DataTrigger Binding="{Binding Value, ElementName=progressBar1}" Value="100">
                    <Setter Property="Visibility" Value="Collapsed"/>
                </DataTrigger>
            </Style.Triggers>
        </Style>
    </ProgressBar.Style>
</ProgressBar>
```

이 설정을 통해 프로그레스 바가 작업 완료(100%) 시 자동으로 숨겨진다.

