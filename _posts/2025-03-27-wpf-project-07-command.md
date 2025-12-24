---
title: "(WPF) 7. Command 패턴을 활용한 버튼 이벤트 처리"
description: "커맨드(Command) 패턴을 이용한 이벤트 처리와 MVVM 활용"
date: 2025-03-27 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, command, relaycommand, mvvm, ui, xaml]
---

# Command 패턴을 활용한 버튼 이벤트 처리

- 최초 작성일: 2025년 3월 27일 (토)

## 1. Command 패턴이란

WPF에서 **Command 패턴**은 버튼과 같은 UI 요소의 클릭 이벤트 처리를 코드 비하인드가 아닌 ViewModel에서 처리하도록 해주는 방법이다. 이를 통해 UI와 로직을 깔끔하게 분리할 수 있으며, 코드의 유지보수와 확장성을 높일 수 있다.

---

## 2. ICommand 인터페이스의 역할

`ICommand` 인터페이스는 버튼 클릭 등의 명령을 처리할 때 사용되며, 다음 세 가지 멤버가 핵심이다.

- **Execute(object)**: 버튼 클릭 시 실제로 실행할 동작을 정의한다.
- **CanExecute(object)**: 버튼이 클릭 가능한 상태인지 여부를 판단한다.
- **CanExecuteChanged**: 버튼의 클릭 가능 상태가 변경될 때 UI에 알려주는 역할을 한다.

즉, 버튼 클릭이 실행 가능한지 판단하고, 클릭되었을 때 어떤 동작을 해야 하는지를 정리하는 역할을 수행한다.

---

## 3. RelayCommand 클래스 작성 방법 및 목적

`RelayCommand`는 `ICommand` 인터페이스를 구현하는 클래스 중 하나로, 특정 버튼의 클릭 이벤트에 대해 실행할 내용을 ViewModel로부터 받아 실행해주는 역할을 한다.

아래는 RelayCommand의 간단한 구현이다.

```csharp
public class RelayCommand<T> : ICommand
{
    private readonly Action<T> _execute;
    private readonly Predicate<T> _canExecute;

    public RelayCommand(Action<T> execute, Predicate<T> canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler CanExecuteChanged
    {
        add { CommandManager.RequerySuggested += value; }
        remove { CommandManager.RequerySuggested -= value; }
    }

    public bool CanExecute(object parameter)
    {
        return _canExecute == null || _canExecute((T)parameter);
    }

    public void Execute(object parameter)
    {
        _execute((T)parameter);
    }
}
```

- `_execute`: 실제 실행할 작업을 담고 있는 메서드이다.
- `_canExecute`: 작업을 실행할 수 있는지 여부를 판단하는 메서드이다.
- `CanExecuteChanged`: UI가 버튼의 활성화 상태를 자동으로 업데이트하도록 도와준다.

---

## 4. ViewModel에서 Command를 사용하는 이유

ViewModel에서 Command를 사용하면 버튼 클릭 시 일어날 작업을 UI(View)와 분리하여 명확하게 관리할 수 있다. 아래는 ViewModel에서 Command를 사용하는 예시 코드이다.

### ViewModel 예시

```csharp
public class MainViewModel
{
    public ICommand TestCommand { get; set; }

    public MainViewModel()
    {
        TestCommand = new RelayCommand<object>(ExecuteTestCommand, CanExecuteTestCommand);
    }

    private bool CanExecuteTestCommand(object parameter)
    {
        // 버튼 활성화 조건
        return parameter != null && parameter.ToString() == "abc";
    }

    private void ExecuteTestCommand(object parameter)
    {
        // 버튼 클릭 시 동작할 내용
        MessageBox.Show($"입력된 값: {parameter} aa");
    }
}
```

- **CanExecuteTestCommand**: 버튼이 활성화되는 조건을 설정해준다. 여기서는 입력된 값이 "abc"일 때만 버튼이 활성화된다.
- **ExecuteTestCommand**: 버튼 클릭 시 메시지 박스를 통해 입력된 값과 "aa"라는 문자를 함께 출력하는 작업을 수행한다.

### XAML에서 Command 바인딩

뷰(View)에서는 다음과 같이 Command와 연결한다.

```xml
<TextBox x:Name="TestBox" Width="200" Height="30"/>
<Button Content="실행" Command="{Binding TestCommand}"
        CommandParameter="{Binding ElementName=TestBox, Path=Text}" Width="100" Height="30"/>
```

- **Command**: 버튼 클릭 시 실행할 명령을 ViewModel로부터 가져온다.
- **CommandParameter**: 버튼 클릭 시 ViewModel로 전달할 값을 설정한다.

실행하면 텍스트 박스에 "abc"라고 입력했을 때만 버튼이 활성화되며, 클릭 시 입력한 값과 "aa"가 메시지 박스로 출력된다.

---
