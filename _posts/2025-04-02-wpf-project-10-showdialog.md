---
title: "(WPF) 10. ShowDialog를 활용한 다른 창 호출하기"
description: ""MVVM 패턴에서 새 창 호출 및 ViewModel 바인딩 방법""
date: 2025-04-02 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, showdialog, mvvm, asyncRelayCommand, window, ui]
---

# ShowDialog를 활용한 다른 창 호출하기

- 최초 작성일: 2025년 3월 30일 (일)

## 목차

1. [ShowDialog와 Modal 창 개념](#1-showdialog와-modal-창-개념)
2. [MVVM 패턴에서 새 창 호출 흐름](#2-mvvm-패턴에서-새-창-호출-흐름)
3. [예제 구현: ProgressBar가 있는 Modal 창 열기](#3-예제-구현-progressbar가-있는-modal-창-열기)
   - [MainWindow.xaml – 메인 창 UI 구성](#mainwindowxaml--메인-창-ui-구성)
   - [MainViewModel.cs – 메인 ViewModel과 명령 정의](#mainviewmodelcs--메인-viewmodel과-명령-정의)
   - [SecondView.xaml – 두 번째 창 UI (ProgressBar 포함)](#secondviewxaml--두-번째-창-ui-progressbar-포함)
   - [SecondViewModel.cs – ProgressBar 업데이트 ViewModel](#secondviewmodelcs--progressbar-업데이트-viewmodel)
4. [AsyncRelayCommand를 사용한 ICommand 구현](#4-asyncrelaycommand를-사용한-icommand-구현)
5. [실행 결과: 동작 과정 정리](#5-실행-결과-동작-과정-정리)
6. [정리 및 결론](#6-정리-및-결론)

---

## 1. ShowDialog와 Modal 창 개념
WPF에서 `Window.ShowDialog()` 메서드는 새 윈도우를 **모달 창**으로 표시한다. 모달 창이 뜨면 **사용자가 그 창을 닫기 전까지** 부모 창을 조작할 수 없고, `ShowDialog()`를 호출한 코드 실행도 창이 닫힐 때까지 멈춘다. 예를 들어 확인/취소를 받는 대화상자, 진행 상황을 표시하는 Progress 창 등이 모달 창으로 구현된다. 반면 `Window.Show()`는 **모달이 아닌(non-modal)** 창을 띄워 부모 창과 독립적으로 동작하게 한다.

모달 창을 사용할 때 **데이터 바인딩**을 위해 **DataContext** 설정이 중요하다. 새 창을 열 때 해당 창의 `DataContext`에 **ViewModel 인스턴스**를 할당하면, XAML에서 ViewModel 속성을 바인딩한 컨트롤들이 제대로 값을 표시하고 업데이트한다. 이제 MVVM 패턴에서 ViewModel을 통해 모달 창을 여는 일반적인 흐름을 알아보자.

## 2. MVVM 패턴에서 새 창 호출 흐름
MVVM에서 **ViewModel은 UI 요소에 직접 접근하지 않는 것**이 원칙이지만, **새 창 열기** 같은 동작은 보통 다음 두 가지 방법으로 구현한다:

- **View의 코드비하인드에서 처리**: 메인 View(XAML 코드비하인드)에서 버튼 클릭 이벤트 등으로 `ShowDialog()`를 호출하고, 필요한 ViewModel을 DataContext로 설정한다. 이 방법은 간단하지만 View 코드비하인드에 로직이 들어간다.
- **ViewModel의 커맨드에서 처리**: ViewModel에서 `ICommand`를 구현한 커맨드를 노출하고, View(XAML)에서 버튼 등을 그 커맨드에 바인딩한다. 커맨드 실행 시 ViewModel에서 새 Window와 ViewModel을 생성하고 `ShowDialog()`를 호출한다. MVVM 순수성을 위해 **Dialog Service**를 사용하기도 하지만, 여기서는 이해를 돕기 위해 **직접 ViewModel에서 Window를 생성**하는 방법을 사용할 것이다.

**핵심 흐름:** 사용자 버튼 클릭 → **MainViewModel의 Command 실행** → 새로운 **SecondView 창과 SecondViewModel 생성** → **SecondView.DataContext에 SecondViewModel 주입** → `SecondView.ShowDialog()`로 모달 표시 → SecondView 내 UI가 SecondViewModel에 바인딩되어 동작.

## 3. 예제 구현: ProgressBar가 있는 Modal 창 열기
예제 시나리오: 메인 창에 "Open Progress Window" 버튼이 있고, 이를 누르면 모달 대화창(Progress 창)이 뜬다. 이 SecondView 창에는 ProgressBar와 "Start" 버튼이 있으며, Start를 누르면 백그라운드 작업을 **비동기 처리**하면서 ProgressBar가 0%부터 100%까지 올라간다. 이 모든 동작을 **MVVM 데이터 바인딩**으로 구현한다.

### MainWindow.xaml – 메인 창 UI 구성
먼저 메인 창 XAML을 설정한다. **DataContext**로 `MainViewModel`을 지정하고, 버튼의 `Command`를 MainViewModel의 커맨드에 바인딩한다.

```xml
<Window x:Class="WpfModalExample.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:local="clr-namespace:WpfModalExample"
        Title="MainWindow" Height="200" Width="300">
    <!-- MainWindow에 ViewModel을 연결 -->
    <Window.DataContext>
        <local:MainViewModel />
    </Window.DataContext>

    <Grid VerticalAlignment="Center" HorizontalAlignment="Center">
        <!-- 모달 Progress 창을 여는 버튼 -->
        <Button Content="Open Progress Window"
                Command="{Binding OpenDialogCommand}"
                Width="150" Height="30" />
    </Grid>
</Window>
```

- `Window.DataContext`에 `<local:MainViewModel />`을 설정하여 **MainViewModel 인스턴스**를 연결했다. 이렇게 하면 XAML에서 `{Binding ...}`으로 MainViewModel의 속성이나 ICommand에 접근할 수 있다.
- `<Button>`의 `Command="{Binding OpenDialogCommand}"`는 MainViewModel에 정의된 `OpenDialogCommand`에 바인딩된다. 이제 버튼 클릭 시 해당 커맨드가 실행된다.

### MainViewModel.cs – 메인 ViewModel과 명령 정의
이제 MainViewModel 클래스를 구현하자. 버튼과 바인딩된 `OpenDialogCommand`를 정의하고, 이 커맨드가 실행되면 새로운 창을 띄우도록 한다. **AsyncRelayCommand**를 사용하여 ICommand를 쉽게 구현할 수 있다.

```csharp
using CommunityToolkit.Mvvm.Input;
using System.Threading.Tasks;
using System.Windows;  // Window 사용을 위해

namespace WpfModalExample
{
    public class MainViewModel
    {
        public IAsyncRelayCommand OpenDialogCommand { get; }

        public MainViewModel()
        {
            // 커맨드 초기화: 버튼 클릭 시 OpenDialogAsync 실행
            OpenDialogCommand = new AsyncRelayCommand(OpenDialogAsync);
        }

        // Progress 창을 여는 메서드 (비동기 커맨드 대상)
        private async Task OpenDialogAsync()
        {
            // 새 SecondView의 ViewModel 생성
            var secondVM = new SecondViewModel();
            // SecondView 창 생성 및 DataContext에 ViewModel 주입
            var secondWindow = new SecondView();
            secondWindow.DataContext = secondVM;

            // 모달 창 표시 (이 줄에서 창이 닫힐 때까지 대기)
            secondWindow.ShowDialog();
        }
    }
}
```

- `OpenDialogCommand` 속성은 `AsyncRelayCommand`로 생성했다. 이 커맨드는 `OpenDialogAsync` 메서드를 실행한다. `AsyncRelayCommand`는 **CommunityToolkit.Mvvm**에서 제공하는 `ICommand` 구현체로, 비동기 메서드를 손쉽게 커맨드로 만들 수 있다.
- `OpenDialogAsync` 메서드 안에서 **SecondViewModel 인스턴스**를 만들고, **SecondView 윈도우**를 생성한 뒤 `DataContext`에 방금 만든 SecondViewModel을 할당한다. 이로써 SecondView 창의 모든 바인딩은 SecondViewModel을 향하게 된다.
- 마지막으로 `secondWindow.ShowDialog()`를 호출하여 SecondView 창을 **모달**로 띄운다. 이 메서드가 호출되면 MainWindow는 비활성화되고, 이 코드의 다음 줄은 SecondView 창이 닫힌 후에야 실행된다. (`ShowDialog()`는 `bool?` 값을 반환하지만 여기서는 사용하지 않았다.)

> **Note:** 엄밀히 따지면 ViewModel에서 View (`SecondView`)를 직접 생성하는 것은 MVVM 원칙상 권장되지 않는다. 그러나 작은 예제이므로 간단히 이 방법을 사용했다. 규모가 커지면 **Dialog 서비스** 등을 통해 ViewModel이 창 표시를 요청하고 View 쪽에서 열도록 구현할 수 있다.

### SecondView.xaml – 두 번째 창 UI (ProgressBar 포함)
다음으로 모달로 표시될 두 번째 창 (`SecondView`)의 XAML을 작성한다. ProgressBar와 이를 제어할 UI를 배치하고, 나중에 주입될 SecondViewModel의 속성/커맨드에 바인딩한다.

```xml
<Window x:Class="WpfModalExample.SecondView"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Progress" Height="150" Width="300">
    <Grid Margin="20">
        <StackPanel>
            <!-- 설명 텍스트 -->
            <TextBlock Text="Processing..." FontWeight="Bold" FontSize="14" />
            
            <!-- 진행률 바: ProgressValue 속성에 바인딩 -->
            <ProgressBar Minimum="0" Maximum="100" Height="20" Margin="0,10,0,0"
                         Value="{Binding ProgressValue}" />

            <!-- 퍼센트 텍스트 표시 -->
            <TextBlock Text="{Binding ProgressValue, StringFormat={}{0}%}" 
                       Margin="0,5,0,0" HorizontalAlignment="Center" />

            <!-- 시작 버튼: StartWorkCommand 커맨드에 바인딩 -->
            <Button Content="Start" Command="{Binding StartWorkCommand}" 
                    Width="80" Margin="0,10,0,0" HorizontalAlignment="Center"/>
        </StackPanel>
    </Grid>
</Window>
```

- `ProgressBar`의 `Value`를 `{Binding ProgressValue}`로 지정했다. 나중에 `SecondViewModel.ProgressValue` 속성과 연결될 바인딩 경로이다. `Minimum`은 0, `Maximum`은 100으로 설정하여 `%` 진행률로 사용한다.
- 그 아래 `TextBlock`에는 `Text="{Binding ProgressValue, StringFormat={}{0}%}"`를 사용해 현재 진행률 값을 퍼센트 문자와 함께 표시했다. (예: 50이면 "50%")
- `"Start"` 버튼의 `Command`를 `{Binding StartWorkCommand}`로 바인딩했다. 이것은 SecondViewModel에 정의될 ICommand로, ProgressBar 증가 작업을 수행한다.
- **중요:** `SecondView` XAML에는 **DataContext를 설정하지 않았다.** 대신 MainViewModel에서 `SecondView.DataContext = new SecondViewModel()`로 주입할 것이므로, XAML 바인딩 경로만 맞게 적어두면 된다. (디자인 타임 지원을 원한다면 XAML에 d:DataContext 등을 지정할 수도 있다.)

### SecondViewModel.cs – ProgressBar 업데이트 ViewModel
마지막으로 SecondViewModel 클래스를 구현한다. 이 ViewModel은 ProgressBar와 상호작용하므로 **진행률 값 속성**과 **시작 커맨드**를 가진다. ProgressBar를 업데이트하는 작업은 시간이 걸릴 수 있으므로, **AsyncRelayCommand**를 사용하여 UI스레드를 막지 않고 비동기로 진행한다.

```csharp
using CommunityToolkit.Mvvm.Input;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace WpfModalExample
{
    public class SecondViewModel : INotifyPropertyChanged
    {
        private int _progressValue;
        public int ProgressValue
        {
            get => _progressValue;
            set 
            { 
                _progressValue = value;
                OnPropertyChanged();
            }
        }

        public IAsyncRelayCommand StartWorkCommand { get; }

        public SecondViewModel()
        {
            ProgressValue = 0;  // 초기값 0%
            // AsyncRelayCommand로 StartWorkAsync 메서드를 커맨드로 연결
            StartWorkCommand = new AsyncRelayCommand(StartWorkAsync);
        }

        // ProgressBar를 0부터 100까지 증가시키는 비동기 작업
        private async Task StartWorkAsync()
        {
            // 1부터 100까지 루프 돌면서 ProgressValue 증가
            for (int i = 1; i <= 100; i++)
            {
                ProgressValue = i;
                // 50ms 지연 주어 UI 업데이트 표시 (작업 시뮬레이션)
                await Task.Delay(50);
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
```

- `ProgressValue` 속성: `int` 타입의 진행률 값이며, `INotifyPropertyChanged` 구현을 통해 값이 변경될 때 UI에 통보한다. (`OnPropertyChanged()` 호출) 이 값에 ProgressBar의 Value와 퍼센트 TextBlock이 바인딩되어 있다.
- `StartWorkCommand`: `AsyncRelayCommand`를 사용하여 `StartWorkAsync` 메서드를 커맨드로 노출했다. SecondView의 "Start" 버튼에 바인딩되어 있어서, 사용자가 클릭하면 `StartWorkAsync`가 실행된다.
- `StartWorkAsync` 메서드: 1부터 100까지 `ProgressValue`를 변경하면서 `Task.Delay(50)`로 약간의 지연을 준다. `await`를 사용하므로 UI 스레드를 블로킹하지 않고도 ProgressValue 변경 시마다 UI의 ProgressBar가 업데이트된다. 이 루프가 끝나면 ProgressValue가 100이 되어 작업 완료 상태를 나타낸다.
- `INotifyPropertyChanged` 구현: `OnPropertyChanged` 메서드는 `PropertyChanged` 이벤트를 발생시켜 WPF 바인딩에 현재 ViewModel의 속성 값이 변했음을 알린다. 덕분에 ProgressValue가 변할 때마다 ProgressBar와 TextBlock이 자동으로 새 값을 반영하게 된다.

## 4. AsyncRelayCommand를 사용한 ICommand 구현
위 예제에서 **AsyncRelayCommand**를 사용하여 MainViewModel과 SecondViewModel의 ICommand를 구현했다. `AsyncRelayCommand`는 **Microsoft CommunityToolkit.Mvvm** 라이브러리의 기능으로, `Task` 반환형의 메서드를 손쉽게 ICommand로 바꿔 준다. 일반 `RelayCommand`와 달리 작업이 **비동기 처리**되는 동안 UI 응답을 유지하고, 작업 완료 후 UI 스레드로 돌아와 결과를 처리한다. 

이 예제에서:
- `MainViewModel.OpenDialogCommand`는 AsyncRelayCommand를 통해 `OpenDialogAsync`를 실행한다. 비록 `OpenDialogAsync` 내부에서 비동기 작업(`await`)은 없지만, AsyncRelayCommand를 사용함으로써 메서드를 async로 작성하고 필요하면 `await`를 사용할 수 있는 유연성이 생긴다. (예를 들어, 두 번째 창이 닫힌 후 결과를 받거나 후속 처리를 비동기로 할 수 있다.)
- `SecondViewModel.StartWorkCommand`는 `StartWorkAsync`를 async로 실행하여 루프마다 `await Task.Delay(...)`를 호출한다. AsyncRelayCommand는 실행 중 상태를 관리(`IsRunning` 등)할 수 있고, 예제처럼 UI 차단 없이 진행률을 업데이트할 수 있게 한다.

> **참고:** AsyncRelayCommand 등을 사용하려면 프로젝트에 **CommunityToolkit.Mvvm** NuGet 패키지를 설치하고, `using CommunityToolkit.Mvvm.Input;` 지시어를 추가해야 한다. 해당 Toolkit의 `ObservableRecipient`나 `ObservableObject`를 상속하면 INotifyPropertyChanged를 쉽게 구현할 수도 있지만, 이해를 돕기 위해 여기서는 수동으로 `INotifyPropertyChanged`를 구현했다.

## 5. 실행 결과: 동작 과정 정리
이제 모든 구현을 마쳤다. 전체 흐름을 정리하며, 실제 실행 시 어떤 일이 일어나는지 단계별로 알아보겠다.

- **메인 창 표시:** MainWindow가 뜨면 DataContext로 연결된 MainViewModel이 로드되어 있다. 메인 창의 버튼은 `OpenDialogCommand`에 바인딩되어 있으므로 현재 활성화되어 있다.
- **버튼 클릭:** 사용자가 "Open Progress Window" 버튼을 클릭하면, MainViewModel의 `OpenDialogCommand`가 실행된다. 이는 내부적으로 `OpenDialogAsync` 메서드를 호출한다.
- **SecondView 생성:** `OpenDialogAsync` 메서드에서 새로운 SecondViewModel 객체를 만들고 SecondView 창을 생성한다. 곧바로 `secondWindow.DataContext = secondVM;`로 **ViewModel을 창에 주입**하므로, SecondView의 모든 바인딩(ProgressBar Value, TextBlock Text, Button Command)이 이제 secondVM을 참고하게 된다.
- **모달 창 열기:** `secondWindow.ShowDialog()` 호출로 SecondView 창이 모달로 나타난다. 이때 MainWindow는 비활성화되고, SecondView 창을 닫을 때까지 `OpenDialogAsync` 메서드는 일시 정지된 상태로 기다린다.
- **ProgressBar 동작:** SecondView 창이 나타나면, 사용자는 창 내부의 "Start" 버튼을 클릭할 수 있다. Start 버튼이 `StartWorkCommand`에 묶여 있으므로, 클릭 시 SecondViewModel의 `StartWorkAsync`가 실행된다.  
  - 이 메서드는 별도의 쓰레드가 아니라 **UI 스레드에서 비동기적으로** 실행된다. `for` 루프에서 `ProgressValue`를 1씩 증가시키고 매 반복마다 `await Task.Delay(50)`로 잠깐씩 쉬어 준다. `await` 덕분에 UI 스레드는 각 지연 동안 다른 작업(예: UI 업데이트)을 처리할 수 있다. 
  - `ProgressValue`가 변경될 때마다 SecondView의 ProgressBar 값이 갱신되고 퍼센트 텍스트도 변한다. 이는 데이터 바인딩과 `INotifyPropertyChanged`로 인해 자동으로 일어난다. UI는 멈추지 않고 부드럽게 ProgressBar가 채워지는 모습을 보여준다.
- **작업 완료 및 창 닫기:** 루프가 끝나면 `ProgressValue == 100`이 되고 ProgressBar는 꽉 찬 상태가 된다. 이제 SecondView 창에서 할 일은 끝났으므로 사용자가 창을 **닫기 버튼 (X)**으로 닫거나, 필요하다면 추가로 구현된 닫기 버튼이 있다면 그것을 눌러 창을 닫는다. 창이 닫히면 `ShowDialog()` 호출이 반환되고 MainWindow가 다시 활성화된다.
- **메인 창으로 복귀:** SecondView 창이 닫히면서 `OpenDialogAsync` 메서드의 나머지 부분이 이어서 실행되지만, 현재 예제에서는 `ShowDialog()` 다음에 별도 코드는 없다. 따라서 `OpenDialogAsync`가 완료되고, MainViewModel의 커맨드 실행이 끝납니다. MainWindow는 여전히 떠 있으며, 필요하면 사용자는 다시 버튼을 눌러 Progress 창을 띄울 수 있다.

요약하면, **MainWindow → (커맨드) → SecondView + SecondViewModel 생성 → (ShowDialog) → SecondView에서 작업 실행 (Progress 업데이트) → 창 닫힘 → MainWindow로 복귀** 순서이다. 모든 데이터 전달과 UI 업데이트는 **DataContext를 통한 바인딩**으로 이루어지므로, 코드 상으로 View와 ViewModel이 깔끔하게 분리되어 유지된다.

## 6. 정리 및 결론
이번 예제에서는 WPF에서 **ShowDialog**를 사용해 모달 창을 열고, **ViewModel을 DataContext로 주입**하여 ProgressBar 값을 바인딩하는 방법을 살펴봤다. MVVM 패턴에 따라 **ViewModel의 ICommand** (여기서는 AsyncRelayCommand 활용)로 새 창을 띄우고, **View-ViewModel 간 데이터 바인딩**을 설정하면 별도의 UI 업데이트 코드 없이도 ViewModel 속성 변화가 즉시 UI에 반영됨을 확인했다.

초보자 입장에서도 따라하기 쉽게 **단계별 구현**을 진행해 보았는데, 요점을 다시 한 번 정리하면 다음과 같다:

- **DataContext 설정:** 메인 창에서 새로운 창을 열 때, 새로운 Window의 `DataContext`에 대응되는 ViewModel 인스턴스를 넣어준다. 이렇게 해야 XAML 바인딩이 올바르게 동작한다.
- **ShowDialog 호출:** ViewModel 쪽에서 `Window.ShowDialog()`를 호출하면 모달 창이 뜨고, 해당 창이 닫힐 때까지 호출한 측의 실행이 멈춘다. 사용자와의 상호작용은 새 창에서 진행된다.
- **커맨드 바인딩:** 버튼 등의 UI 요소에 `ICommand`를 바인딩하여, UI 이벤트를 ViewModel의 메서드로 처리한다. **AsyncRelayCommand**를 사용하면 긴 작업도 UI 멈춤 없이 처리할 수 있다.
- **ProgressBar 업데이트:** ViewModel에서 `INotifyPropertyChanged`를 구현하고 Progress 값을 변경함으로써, 별도 스레드 작업이나 `Dispatcher` 호출 없이도 ProgressBar와 같은 바인딩된 UI 컨트롤이 자동으로 갱신된다 (async/await 사용 시 컨텍스트 전환에 유의).

위 예제를 직접 따라 해 보면, **"Open Progress Window"** 버튼을 눌렀을 때 새 창이 뜨고, **"Start"** 버튼 클릭 시 ProgressBar가 서서히 채워지는 것을 확인할 수 있을 것이다. 이처럼 WPF MVVM 패턴을 활용하면 깔끔한 구조로 **모달 대화창** 기능을 구현할 수 있다. 초보자라도 본 예제의 흐름을 이해하고 응용하면, 자신의 WPF 프로젝트에서 **다양한 대화창과 진행 표시 기능**을 손쉽게 구현할 수 있을 것이다.
