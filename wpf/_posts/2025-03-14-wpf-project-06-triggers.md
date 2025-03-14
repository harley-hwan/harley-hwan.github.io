---
layout: post
title: "(WPF) 6. WPF에서 트리거와 데이터 트리거 활용하기"
subtitle: "트리거를 활용한 스타일 및 데이터 연동 방법"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [c#, wpf, triggers, data-triggers, ui, xaml]
comments: true
filename: "2025-03-14-wpf-project-06-triggers.md"
---

# (WPF) 6. 트리거와 데이터 트리거 활용하기

- 최초 작성일: 2025년 3월 14일 (금)

## 목차

1. [트리거(Trigger) 개요](#트리거trigger-개요)
2. [트리거를 활용한 스타일 변경](#트리거를-활용한-스타일-변경)
3. [데이터 트리거(DataTrigger)를 통한 컨트롤 상태 변경](#데이터-트리거datatrigger를-통한-컨트롤-상태-변경)
4. [INotifyPropertyChanged와 데이터 트리거 활용](#inotifypropertychanged와-데이터-트리거-활용)

---

## 트리거(Trigger) 개요

WPF의 트리거는 특정 이벤트나 속성의 변화가 발생했을 때 컨트롤의 스타일을 변경하는 기능이다. 대표적으로 마우스 클릭이나 호버 등의 이벤트에서 유용하게 사용할 수 있다.

---

## 트리거를 활용한 스타일 변경

다음은 버튼 위에 마우스를 올리거나 클릭했을 때 글자 색상을 변경하는 예제이다.

```xml
<Style.Triggers>
    <Trigger Property="IsMouseCapture" Value="True">
        <Setter Property="Control.Foreground" Value="Blue"/>
    </Trigger>
    <Trigger Property="IsMouseOver" Value="True">
        <Setter Property="Control.Foreground" Value="Blue"/>
    </Trigger>
</Style.Triggers>
```

위 코드를 적용하면 버튼을 클릭하거나 마우스를 올릴 때 글자 색상이 변경된다.

---

## 데이터 트리거(DataTrigger)를 통한 컨트롤 상태 변경

데이터 트리거를 사용하면 특정 컨트롤의 속성 변화에 따라 다른 컨트롤의 스타일을 변경할 수 있다. 예를 들어 체크박스를 선택하면 버튼의 글자색이 변경되고, 버튼의 활성 상태를 변경하는 예제이다.

```xml
<DataTrigger Binding="{Binding ElementName=CheckBox1, Path=IsChecked}" Value="True">
    <Setter Property="Control.Foreground" Value="Red"/>
    <Setter Property="Control.IsEnabled" Value="False"/>
</DataTrigger>
```

이렇게 설정하면 체크박스 선택 시 버튼이 빨간색으로 변경되고 사용이 금지된다.

---

## INotifyPropertyChanged와 데이터 트리거 활용

데이터 트리거는 MVVM 패턴에서 ViewModel의 속성 값 변경에 따라 View를 동적으로 변경하는 데 유용하게 사용된다. 예시로 프로그레스 바를 업데이트하는 예제를 살펴본다.

### ViewModel 생성 예제

```csharp
public class MainViewModel : INotifyPropertyChanged
{
    private int progressValue;
    public event PropertyChangedEventHandler PropertyChanged;

    public int ProgressValue
    {
        get { return progressValue; }
        set
        {
            progressValue = value;
            NotifyPropertyChanged(nameof(ProgressValue));
        }
    }

    protected void NotifyPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

### ProgressBar 바인딩 예제

```xml
<ProgressBar x:Name="progressBar1" Minimum="0" Maximum="100"
             Value="{Binding ProgressValue}" />
```

### 데이터 트리거 설정 예제

```xml
<Style.Triggers>
    <DataTrigger Binding="{Binding ElementName=progressBar1, Path=Value}" Value="100">
        <Setter Property="Control.Visibility" Value="Hidden"/>
    </DataTrigger>
</Style.Triggers>
```

위 예제를 적용하면 프로그레스 바의 값이 100이 될 때 프로그레스 바가 사라지도록 설정할 수 있다.

---

이 글에서는 WPF의 트리거와 데이터 트리거를 활용하여 동적이고 유연한 UI를 구현하는 방법을 설명했다.

