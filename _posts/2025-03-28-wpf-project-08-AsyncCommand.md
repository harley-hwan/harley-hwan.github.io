---
title: "(WPF) 8. AsyncRelayCommand로 비동기 작업 처리하기"
description: "Async/await를 활용해 UI를 멈추지 않고 작업 실행하기"
date: 2025-03-28 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, async, await, asyncRelayCommand, mvvm, command]
---

# AsyncRelayCommand로 비동기 작업 처리하기

- 최초 작성일: 2025년 3월 28일 (일)

## 비동기 작업이 필요한 이유

WPF 애플리케이션에서 버튼 클릭으로 시간이 오래 걸리는 작업을 수행하면 UI가 멈추는 현상을 겪게 된다. 예를 들어, 버튼 클릭 시 5초 정도 걸리는 파일 처리나 웹 요청을 UI 스레드에서 바로 실행하면 그 5초 동안 윈도우가 **“응답 없음”** 상태로 얼어붙게 된다. 이는 WPF의 **UI 스레드**가 긴 작업을 처리하느라 화면 그리기나 사용자 입력 처리와 같은 다른 일을 못 하기 때문에 발생한다.

이 문제를 해결하려면 작업을 **비동기(async)**로 처리하여 UI 스레드를 블로킹하지 않아야 한다. 즉, 오래 걸리는 작업은 별도 작업으로 실행하고, 완료되면 결과를 받아 UI를 업데이트하는 방식이다. MVVM 패턴에서는 보통 `ICommand` 구현체인 **커맨드(Command)**를 통해 버튼 클릭 같은 이벤트를 처리한다. 그런데 흔히 사용하는 RelayCommand(동기 커맨드)로 긴 작업을 실행하면 결국 UI 프리즈 문제가 생긴다. 이를 우회하기 위해 **AsyncRelayCommand**와 같은 비동기 커맨드를 사용하여 오래 걸리는 작업을 처리할 수 있다.

---

## NuGet 패키지 설치 방법

AsyncRelayCommand는 .NET Community Toolkit의 MVVM 패키지에 포함되어 있다. 이 기능을 프로젝트에서 사용하려면 NuGet을 통해 해당 라이브러리를 추가해야 한다:

1. Visual Studio에서 **NuGet 패키지 관리자**를 연다 (프로젝트를 마우스 오른쪽 클릭하여 **NuGet 패키지 관리** 메뉴 선택).
2. **CommunityToolkit.Mvvm** 패키지를 검색한다.
3. 검색 결과에서 **CommunityToolkit.Mvvm**를 선택하고 최신 버전을 설치한다.
4. 패키지 설치 후 코드 파일 상단에 `using CommunityToolkit.Mvvm.Input;` 지시어를 추가하면 AsyncRelayCommand 클래스를 사용할 수 있다.

> **Note:** CommunityToolkit.Mvvm 패키지는 과거 **Microsoft.Toolkit.Mvvm**으로 불리던 라이브러리의 최신 버전이다.  

---

## ViewModel 코드 작성

NuGet 패키지 설치를 마쳤다면, 이제 ViewModel에서 AsyncRelayCommand를 활용해 보자. AsyncRelayCommand는 `ICommand`를 구현한 클래스이며, `Task`를 반환하는 비동기 메서드를 받아 UI 스레드를 블로킹하지 않고 실행해 준다. 아래는 긴 작업을 비동기로 처리하는 ViewModel 코드 예시이다:

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public class MyViewModel : ObservableObject
{
    // 1. 비동기 커맨드 프로퍼티 선언
    public IAsyncRelayCommand LoadDataCommand { get; }

    // 2. 예시로 UI에 표시할 결과 문자열 프로퍼티
    private string _resultText;
    public string ResultText
    {
        get => _resultText;
        set => SetProperty(ref _resultText, value);
    }

    public MyViewModel()
    {
        // 3. AsyncRelayCommand 초기화: 실행할 비동기 메서드 지정
        LoadDataCommand = new AsyncRelayCommand(LoadDataAsync);
    }

    // 4. 오래 걸리는 작업을 비동기로 처리하는 메서드
    private async Task LoadDataAsync()
    {
        // (예시) 3초 동안 대기했다가 결과 설정
        await Task.Delay(3000);
        // 5. 작업 완료 후 결과 프로퍼티 갱신 (UI에 반영)
        ResultText = "데이터 로드 완료";
    }
}
```

1. **비동기 명령 프로퍼티 선언:** `LoadDataCommand`라는 커맨드 프로퍼티를 정의한다. 타입은 `IAsyncRelayCommand` 인터페이스로 선언하였는데, 이는 AsyncRelayCommand의 인터페이스 타입이다. (`AsyncRelayCommand` 타입으로 직접 써도 무방하다.) 이 커맨드는 나중에 XAML에서 바인딩하여 사용할 것이다.  
2. **결과 저장 프로퍼티:** `ResultText`라는 문자열 프로퍼티를 추가했다. 백그라운드 작업의 결과를 저장해 UI에 표시하는 용도이다. `ObservableObject`를 상속받았기 때문에 `SetProperty` 메서드를 통해 값이 변경되면 `PropertyChanged` 이벤트가 자동으로 발생하여 바인딩된 UI가 업데이트된다. (MyViewModel이 `ObservableObject`를 상속함으로써 **INotifyPropertyChanged** 구현을 이미 갖추고 있다.)  
3. **커맨드 초기화:** 생성자에서 `LoadDataCommand`를 초기화한다. `AsyncRelayCommand` 생성자에 실행할 비동기 메서드(`LoadDataAsync`)를 전달한다. 이렇게 설정하면 버튼 클릭 시 `LoadDataAsync` 메서드가 호출된다.  
4. **비동기 작업 메서드:** `LoadDataAsync` 메서드는 실제 오래 걸리는 작업을 수행한다. 반환 타입을 `Task`로 하고 `async` 키워드를 붙여 비동기 메서드로 정의한다.  
5. **`await`를 통한 UI 비동기 처리:** `await Task.Delay(3000)`는 3초 동안 비동기적으로 대기하는 예제이다. 이 줄을 실행하면 3초 동안 **UI 스레드를 블로킹하지 않고** 기다린다. 즉, 3초 대기 동안에도 UI는 반응성을 유지한다. 3초 후 대기가 끝나면 다음 줄로 진행한다. 아래줄에서 `ResultText = "데이터 로드 완료";`로 결과를 설정하면, 앞서 정의한 `ResultText` 프로퍼티의 set 접근자에서 `PropertyChanged`가 발생하여 UI의 바인딩된 텍스트가 갱신된다.

정리하면, 위 ViewModel에서는 **AsyncRelayCommand**를 사용하여 `LoadDataAsync` 작업을 비동기로 실행하고, 완료 시 결과를 `ResultText`에 저장한다. 이때 `await` 덕분에 작업 대기 중에도 UI가 멈추지 않으며, `ResultText` 변경은 UI에 자동 반영된다.

---

## XAML 코드 예시

이제 View(XAML)에서 해당 커맨드를 어떻게 사용하는지 알아보자. View의 `DataContext`를 우리의 ViewModel로 설정한 후, 버튼과 텍스트블록에 바인딩을 걸어준다. 아래 XAML은 간단한 예제이다 (DataContext 설정은 예시로 포함):

```xml
<!-- Window의 DataContext에 ViewModel 인스턴스를 할당했다고 가정 -->
<Window x:Class="MyApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:local="clr-namespace:MyApp"
        Title="Async Command Example" Height="150" Width="300">
    <Window.DataContext>
        <local:MyViewModel/>
    </Window.DataContext>

    <StackPanel Margin="20">
        <!-- 1. 버튼의 Command 속성을 ViewModel의 AsyncRelayCommand에 바인딩 -->
        <Button Content="데이터 불러오기" Command="{Binding LoadDataCommand}" Margin="0 0 0 10"/>
        <!-- 2. TextBlock의 Text 속성을 ViewModel의 ResultText 프로퍼티에 바인딩 -->
        <TextBlock Text="{Binding ResultText}" FontWeight="Bold" />
    </StackPanel>
</Window>
```

- **1:** `<Button>`의 `Command` 속성을 ViewModel의 `LoadDataCommand`에 바인딩했다. 이렇게 하면 버튼을 클릭할 때 해당 커mand(`LoadDataCommand`)가 실행된다. 즉, 앞서 정의한 `LoadDataAsync` 메서드가 호출된다.  
- **2:** `<TextBlock>`은 `Text="{Binding ResultText}"`로 바인딩되어 있다. ViewModel에서 `ResultText` 값이 변경되면 TextBlock에 자동으로 반영되어 결과가 표시된다. 예제에서는 작업 완료 후 `"데이터 로드 완료"` 문자열이 나타나게 된다.

이처럼 XAML에서 **AsyncRelayCommand**도 일반 `ICommand`와 동일한 방법으로 바인딩하여 사용할 수 있다. 추가로, AsyncRelayCommand는 실행 상태를 나타내는 `IsRunning` 프로퍼티를 제공한다. **`IsRunning`**은 커맨드가 실행중일 때 `true`가 되므로, 이를 이용해 UI 피드백을 줄 수 있다. 예를 들어 `ProgressBar`의 표시 여부를 `IsRunning`에 바인딩하거나, 커맨드 실행 중 버튼을 비활성화(disable)하여 중복 클릭을 막는 등의 처리가 가능하다.

---

## 잘못된 예 vs 좋은 예

비동기 처리를 잘못 구현하면 여전히 UI가 멈추거나 예기치 않은 문제가 생길 수 있다. 특히 `async/await`를 제대로 쓰지 않고 **Task를 동기 대기**하면 의미가 없어진다. 아래 코드 비교를 통해 올바른 사용 방법을 확인해 보자.

**잘못된 예:** 일반 RelayCommand 안에서 `Task.Wait()`(동기 대기)로 비동기 작업을 처리하는 경우이다. UI 스레드를 그대로 잠겨 버리므로 피해야 한다.

```csharp
// 잘못된 방식: 동기식 커맨드에서 비동기 작업을 강제로 대기
public RelayCommand LoadDataCommand { get; }

public MyViewModel()
{
    LoadDataCommand = new RelayCommand(() =>
    {
        // 비동기 작업을 동기적으로 기다림 -> UI 스레드 블로킹 발생
        LoadDataAsync().Wait();
    });
}
```

위 코드처럼 `LoadDataAsync().Wait();`를 호출하면 작업이 완료될 때까지 UI 스레드가 기다리게 된다. 이 동안 앱의 화면 갱신과 입력 처리가 중단되어 사용자 입장에서는 프로그램이 먹통이 된 것처럼 보인다. `Task.Wait()`나 `Task.Result`를 UI 쓰레드에서 호출하는 것은 **Deadlock**(교착 상태)을 일으킬 위험도 있으므로 지양해야 한다.

**올바른 예:** AsyncRelayCommand를 사용하여 **await**으로 비동기 작업을 처리하는 경우이다. AsyncRelayCommand 자체가 `ICommand`를 구현하므로 별도의 RelayCommand 래핑 없이 바로 사용하면 된다.

```csharp
// 올바른 방식: AsyncRelayCommand로 비동기 작업 수행
public IAsyncRelayCommand LoadDataCommand { get; }

public MyViewModel()
{
    // 비동기 메서드를 커맨드에 직접 전달 (내부적으로 await 처리, UI 블로킹 없음)
    LoadDataCommand = new AsyncRelayCommand(LoadDataAsync);
}
```

이 방식에서는 별도로 `Wait()`를 호출하지 않는다. `LoadDataAsync` 메서드의 내부에서 `await`를 사용하고 있으므로 버튼 클릭 시 UI 스레드를 막지 않고 작업이 시작된다. AsyncRelayCommand는 작업 완료 후 UI 스레드로 결과를 마샬링(marshalling)해주므로, `ResultText` 업데이트처럼 UI 바인딩 갱신도 안전하게 처리된다. 결과적으로 **UI는 멈추지 않고**, 작업 완료 시점에만 UI가 업데이트된다.

---

## 실행 결과 설명

이제 완성된 예제를 실행해 보면 어떻게 동작하는지 확인할 수 있다. 애플리케이션을 시작하고 **“데이터 불러오기”** 버튼을 클릭하면, `LoadDataCommand`가 실행되어 `LoadDataAsync` 메서드가 호출된다. 이 메서드는 3초 동안 비동기 대기를 하고 나서 `ResultText`를 `"데이터 로드 완료"`로 설정한다. 중요한 점은 이 3초 동안 **애플리케이션 UI가 계속 반응한다**는 것이다. 작업이 진행되는 동안에도 윈도우를 드래그하거나 다른 입력을 시도할 수 있으며, 앱이 “먹통”이 되지 않는다. 만약 별도로 로딩 중임을 표시하는 UI 요소(예: ProgressBar)를 `IsRunning`에 바인딩했다면, 버튼을 누른 순간부터 완료 시까지 그 표시가 나타났다가 완료 후 사라질 것이다. 

3초가 지나면 TextBlock에 결과 문자열이 표시되어 사용자는 작업 완료를 확인할 수 있다. 전체 흐름 동안 UI 스레드는 블로킹되지 않았고, 긴 작업도 백그라운드에서 원활히 처리되었다. 이처럼 **AsyncRelayCommand**를 사용하면 WPF MVVM에서 시간 소요가 큰 작업도 사용자 경험을 해치지 않으면서 수행할 수 있다. 이제 필요에 따라 이 패턴을 응용하여 파일 다운로드, 데이터베이스 쿼리 등 다양한 작업을 UI 프리즈 없이 구현할 수 있을 것이다.
