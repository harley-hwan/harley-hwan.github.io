---
layout: post
title: "WPF에서 AsyncRelayCommand로 장시간 작업 처리하기"
subtitle: "Async/await를 활용해 UI를 멈추지 않고 작업 실행하기"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [WPF, MVVM, async, AsyncRelayCommand, C#]
comments: true
filename: "2025-03-28-wpf-project-08-AsyncCommand.md"
---

WPF 애플리케이션에서 오래 걸리는 작업을 실행할 때, UI가 멈추지 않도록 비동기 처리가 필요하다. 이번 장에서는 `AsyncRelayCommand`를 사용하여 이러한 장시간 작업을 MVVM 패턴으로 구현하고, `async/await`를 통해 **응답성 있는 UI**를 유지하는 방법을 알아본다.

## 목차
- [비동기 작업이 필요한 이유](#비동기-작업이-필요한-이유)
- [AsyncRelayCommand 설치 방법](#asyncrelaycommand-설치-방법)
- [코드 설명](#코드-설명)
- [실행 결과 확인](#실행-결과-확인)
- [결론](#결론)

## 비동기 작업이 필요한 이유
일반적인 `RelayCommand`를 통해 무거운 작업을 동기적으로 수행하면 UI 스레드가 그 작업이 끝날 때까지 막혀 있게 된다. 예를 들어 버튼 클릭 이벤트에서 복잡한 계산이나 대용량 파일 I/O를 바로 처리하면 프로그램의 창을 움직이거나 다른 입력을 할 수 없게 되고, 심하면 Windows에서 해당 창에 “응답 없음” 표시가 뜨게 된다. **UI 스레드가 작업에 붙잡혀 있는 동안에는 다른 UI 이벤트를 처리하지 못하기 때문**이다 ([Await, and UI, and deadlocks! Oh my! - .NET Blog](https://devblogs.microsoft.com/pfxteam/await-and-ui-and-deadlocks-oh-my/#:~:text=for%20developers%20to%20write%20the,also%20really%20useful%20for%20responsiveness)). 결과적으로 사용자는 프로그램이 멈춘 것처럼 느끼게 되며, 매우 불편한 경험을 하게 된다.

 ([image]()) 동기식 명령 실행 중 UI가 멈춘 모습 (창 제목에 '응답 없음' 표시). 이처럼 시간이 오래 걸리는 작업을 UI 스레드에서 처리하면 화면 갱신도 이루어지지 않고, 사용자는 진행 상황을 알 수 없게 된다. 응용 프로그램이 몇 초 이상 응답하지 않으면 **치명적인 사용자 경험 저하**로 이어진다. 따라서 긴 작업은 UI 스레드를 블로킹하지 않도록 별도의 스레드에서 수행해야 한다.

이를 구현하기 위해 과거에는 `BackgroundWorker`나 스레드 생성, `Dispatcher.Invoke` 등을 사용했으나, **C#의 `async/await` 패턴**을 사용하면 훨씬 간결하게 구현할 수 있다 ([Using Async, Await, and Task to keep the WinForms UI responsive](https://grantwinney.com/using-async-await-and-task-to-keep-the-winforms-ui-more-responsive/#:~:text=Update%3A%20Sep%209%2C%202024)). `async/await`을 쓰면 **현재 스레드를 블로킹하지 않고** 작업을 비동기로 처리할 수 있어 UI 프리즈(freeze)를 쉽게 방지할 수 있다 ([Using Async, Await, and Task to keep the WinForms UI responsive](https://grantwinney.com/using-async-await-and-task-to-keep-the-winforms-ui-more-responsive/#:~:text=Update%3A%20Sep%209%2C%202024)). MVVM 패턴에서는 명령(Command)을 비동기로 실행하기 위해 `AsyncRelayCommand`를 활용할 수 있는데, 이것은 `RelayCommand`를 확장하여 `Task` 반환형 메서드를 사용할 수 있게 해준다 ([AsyncRelayCommand - Community Toolkits for .NET | Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/asyncrelaycommand#:~:text=The%20AsyncRelayCommand%20%20and%20,with%20support%20for%20asynchronous%20operations)).

## AsyncRelayCommand 설치 방법
`AsyncRelayCommand`는 **CommunityToolkit.Mvvm** (구 Microsoft.Toolkit.Mvvm) 라이브러리에서 제공되는 MVVM 도구 중 하나이다. 이 패키지를 NuGet에서 설치하면 `RelayCommand`와 함께 `AsyncRelayCommand` 클래스를 사용할 수 있다. `AsyncRelayCommand`는 내부적으로 `ICommand`를 구현하며, 비동기 작업을 처리할 수 있도록 설계되어 있다 ([AsyncRelayCommand - Community Toolkits for .NET | Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/asyncrelaycommand#:~:text=The%20AsyncRelayCommand%20%20and%20,with%20support%20for%20asynchronous%20operations)). 설치 후 뷰모델 코드에서 `using CommunityToolkit.Mvvm.Input;` 네임스페이스를 추가하면 `AsyncRelayCommand`를 바로 사용할 수 있다.

> **Note:** .NET Community Toolkit의 MVVM 패키지는 .NET 5 이상에서 동작하며, WPF와 WinUI 등 다양한 UI 프레임워크에서 사용 가능하다. 이 패키지에는 `AsyncRelayCommand<T>`(제네릭 버전), `IAsyncRelayCommand` 인터페이스, 명령의 실행 상태를 나타내는 `IsRunning` 프로퍼티 등도 제공된다 ([AsyncRelayCommand - Community Toolkits for .NET | Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/asyncrelaycommand#:~:text=,elements%20such%20as%20loading%20indicators)). 본문에서는 기본적인 사용 방법에 초점을 맞춘다.

## 코드 설명
이제 `AsyncRelayCommand`를 사용하여 **장시간 작업을 수행하면서도 UI가 멈추지 않게 만드는 코드**를 구현해보자. 예제로, 5초 정도 걸리는 가상의 무거운 작업을 실행하면서 진행률을 화면에 표시하는 시나리오를 구성한다. 먼저 MainViewModel에 비동기 명령과 진행률 속성을 정의한다:

```csharp
// MainViewModel.cs (INotifyPropertyChanged 구현 가정)
public class MainViewModel : INotifyPropertyChanged
{
    public ICommand StartTaskCommand { get; set; }

    private int progressValue;
    public int ProgressValue
    {
        get => progressValue;
        set 
        { 
            progressValue = value;
            OnPropertyChanged();   // INotifyPropertyChanged 구현 메서드
        }
    }

    public MainViewModel()
    {
        // AsyncRelayCommand로 비동기 작업 실행 커맨드 설정
        StartTaskCommand = new AsyncRelayCommand(LongTaskAsync);
    }

    // 오래 걸리는 작업을 비동기적으로 처리
    public async Task LongTaskAsync()
    {
        // 진행률 초기화
        ProgressValue = 0;
        // 무거운 작업을 별도 스레드에서 실행
        Task<int> task = Task.Run(() =>
        {
            int result = 0;
            for (int i = 1; i <= 10; i++)
            {
                // 작업 진행 (0.5초 지연)
                Thread.Sleep(500);
                // 진행률 10%씩 증가
                ProgressValue += 10;
                result = i;
            }
            return result;
        });
        // 비동기로 대기: UI 스레드를 블로킹하지 않음
        int finalResult = await task;
        // 작업 완료 후 결과 표시 (UI 스레드)
        MessageBox.Show($"작업 완료! 최종 결과: {finalResult}");
    }

    // ... (OnPropertyChanged 구현 등 생략)
}
```

위 코드에서는 **무거운 작업을 `Task.Run`으로 래핑**하고 `await` 키워드로 그 작업이 완료될 때까지 비동기적으로 기다린다. `Task.Run` 내부의 람다식에서는 `Thread.Sleep`으로 시간이 걸리는 작업을 흉내내고, 반복문을 돌면서 `ProgressValue`를 갱신하고 있다. 중요한 부분은 `await task;` 부분으로, 여기서 UI 스레드는 이 줄에서 작업 완료를 기다리면서도 **블로킹되지 않고 다른 작업을 처리할 수 있게 된다** ([Await, and UI, and deadlocks! Oh my! - .NET Blog](https://devblogs.microsoft.com/pfxteam/await-and-ui-and-deadlocks-oh-my/#:~:text=for%20developers%20to%20write%20the,also%20really%20useful%20for%20responsiveness)). 즉, `LongTaskAsync` 메서드는 처음 호출될 때 `Task.Run(...)`까지 실행하고 나서 바로 **제어를 호출한 쪽(UI 스레드)에 반환**하며, 백그라운드 스레드의 작업이 끝나면 나중에 다시 이어 실행된다. 그 사이에 UI 스레드는 자유롭게 사용자 입력 처리나 화면 갱신을 계속할 수 있어 응답성이 유지된다.

만약 `await`를 쓰지 않고 잘못된 방법으로 `Task.Wait()`를 사용했다면 어떻게 될까? 예를 들어 아래와 같이 코드를 작성하면 문제가 된다:

```csharp
// 잘못된 예: Task.Wait()로 동기 대기 (UI 스레드 블로킹)
StartTaskCommand = new RelayCommand(() =>
{
    Task task = Task.Run(() => LongOperation()); // 백그라운드 작업 시작
    task.Wait();  // 작업이 끝날 때까지 현재 스레드 대기 (UI 멈춤)
});
```

위 코드는 백그라운드 스레드에서 `LongOperation`을 시작한 뒤 **`Wait()`로 UI 스레드를 정지시켜 결과를 기다리기 때문에**, 결국 UI가 멈추는 것은 마찬가지다. 실제로 `task.Wait()`가 호출되면 그 순간 UI 스레드는 작업 완료까지 блок 상태가 되어 버린다 ([c# - Why is Task.Wait() causing application to freeze - Stack Overflow](https://stackoverflow.com/questions/45640363/why-is-task-wait-causing-application-to-freeze#:~:text=You%20have%20a%20deadlock,is%20the%20main%20UI%20thread)). `await`는 이와 달리 **UI 스레드를 차단하지 않고** 비동기 대기를 함으로써 작업이 끝난 뒤 이어서 실행을 계속하게 해준다 ([c# - Why is Task.Wait() causing application to freeze - Stack Overflow](https://stackoverflow.com/questions/45640363/why-is-task-wait-causing-application-to-freeze#:~:text=match%20at%20L258%20on%20the,thread%20not%20being%20available%20indefinitely)). 따라서 WPF 애플리케이션에서는 **절대로 UI 스레드에서 `.Wait()`나 `.Result`로 Task 결과를 동기적으로 기다리지 않도록 해야 한다**.

다음으로, XAML에서 이 뷰모델의 커맨드와 속성을 바인딩하여 UI와 연결한다. MainWindow.xaml에 `DataContext`를 MainViewModel로 설정하고, 버튼과 ProgressBar를 배치하는 예시는 다음과 같다:

```xml
<!-- MainWindow.xaml -->
<Window x:Class="AsyncDemo.MainWindow"
        ... xmlns:local="clr-namespace:AsyncDemo" >
    <Window.DataContext>
        <local:MainViewModel/>
    </Window.DataContext>
    <StackPanel Margin="20">
        <!-- 비동기 명령 바인딩된 버튼 -->
        <Button Content="작업 시작"
                Command="{Binding StartTaskCommand}" Width="100"/>
        <!-- 진행률 표시 ProgressBar -->
        <ProgressBar Minimum="0" Maximum="100"
                     Value="{Binding ProgressValue}"
                     Height="20" Width="300" Margin="0,10,0,0"/>
    </StackPanel>
</Window>
```

위 XAML에서는 `Button`의 `Command` 속성에 뷰모델의 `StartTaskCommand`를 바인딩하였다. 이제 사용자가 이 버튼을 클릭하면 `LongTaskAsync` 메서드가 실행되고, `ProgressValue` 변수가 변화할 때마다 `INotifyPropertyChanged`를 통해 바인딩된 `ProgressBar`의 값이 업데이트된다. `ProgressBar`는 0부터 100까지의 범위를 가지며, 우리가 10번에 걸쳐 10씩 증가시키도록 구현했으므로 작업 시작 후 약 5초에 걸쳐 막대가 차오르게 된다. 이 동안에도 **UI 스레드는 멈추지 않고**, 사용자는 진행률이 업데이트되는 것을 실시간으로 볼 수 있다.

## 실행 결과 확인
이제 완성된 애플리케이션을 실행하여 동작을 확인해보자. 버튼을 클릭하면 5초 동안 가상의 작업이 진행되고, 그 사이 ProgressBar를 통해 진행률이 표시된다. 중요한 것은 **작업 도중에도 창이 응답하고 있다는 것**을 사용자가 느낄 수 있다는 점이다. 작업이 진행되는 동안에도 창을 드래그해서 움직일 수도 있고, ProgressBar 애니메이션이나 다른 UI 업데이트가 정상적으로 이루어진다.

 ([image]()) AsyncRelayCommand를 사용하여 비동기 작업을 처리하면 진행 상황이 UI에 즉시 반영되고 창이 멈추지 않는다. 예를 들어 위 그림처럼 작업 진행 중에도 ProgressBar가 자연스럽게 업데이트되며, UI 스레드가 계속 반응하기 때문에 창 이동이나 버튼 클릭 등의 **다른 상호작용도 처리 가능**하다. 작업이 완료되면 MessageBox를 통해 완료 메시지를 표시하도록 구현했으므로, 사용자는 작업 종료도 즉시 알 수 있다.

만약 동일한 작업을 `RelayCommand`로 동기 실행했다면 위와 같은 **원활한 진행 표시나 UI 반응은 불가능**했을 것이다. 사용자는 몇 초 동안 정지된 화면을 보게 되고, 작업이 끝난 뒤에야 한꺼번에 UI 변경이 반영되거나 결과를 확인하게 된다. 이처럼 **비동기 명령을 사용한 구현은 사용자 경험 측면에서 큰 차이**를 만든다.

## 결론
WPF에서 긴 처리 시간을 갖는 작업이라도 `async/await`와 `AsyncRelayCommand`를 활용하면 UI를 멈추지 않고 실행할 수 있다. 핵심은 **UI 스레드에서는 긴 작업을 직접 수행하지 않고 비동기로 넘기는 것**이다. `AsyncRelayCommand`는 MVVM 패턴에서 이러한 비동기 처리를 쉽게 구현하도록 도와주는 도구로서, 개발자는 마치 동기 메서드를 작성하듯이 비동기 메서드를 작성하고 `await`를 통해 결과를 이어받는 형태로 코드를 구성하면 된다. 

마지막으로 기억해야 할 것은, **절대로 UI 스레드를 블로킹하는 코드를 넣지 않는 것**이다. `Task.Wait()`이나 `.Result`를 사용한 잘못된 패턴은 피하고, 항상 `await`를 사용하여 **작업 중에도 UI 제어권이 유지되도록** 해야 한다. 이를 통해 사용자는 작업이 오래 걸려도 응답이 끊기지 않는 **부드러운 UI 경험**을 누릴 수 있다. AsyncRelayCommand와 같은 패턴은 처음 접하면 생소할 수 있지만, 한 번 익혀 두면 WPF 개발에서 안정적이고 효율적인 비동기 처리를 구현하는 데 큰 도움이 된다.
