---
layout: post 
title: "(WPF) 7. Command 패턴을 활용한 버튼 이벤트 처리" 
subtitle: "커맨드(Command) 패턴을 이용한 이벤트 처리와 MVVM 활용" 
gh-repo: harley-hwan/harley-hwan.github.io 
gh-badge: [star, fork, follow] 
tags: [c#, wpf, command, relaycommand, mvvm, ui, xaml] 
comments: true 
filename: "2025-03-15-wpf-project-07-command.md"
---

# (WPF) 7. Command 패턴을 활용한 버튼 이벤트 처리

- 최초 작성일: 2025년 3월 15일 (토)

## 목차

1. [Command 패턴 개요](#command-패턴-개요)
2. [ICommand 인터페이스 이해하기](#icommand-인터페이스-이해하기)
3. [RelayCommand 클래스 구현 및 활용](#relaycommand-클래스-구현-및-활용)
4. [ViewModel에서 Command 사용하기](#viewmodel에서-command-사용하기)

---

## 1. Command 패턴 개요

WPF에서 Command(커맨드) 패턴은 MVVM 아키텍처에서 뷰와 비즈니스 로직을 분리하는 데 주로 사용된다. 이벤트 처리를 직접 뷰(View)에 연결하지 않고 ViewModel에서 명령(Command)을 정의하여 사용하는 방식으로, UI와 비즈니스 로직 간의 의존성을 낮추는 것이 주요 목적이다.



---

## 2. ICommand 인터페이스 이해하기

커맨드를 구현하기 위해서는 `ICommand` 인터페이스를 구현한 클래스를 작성해야 한다. `ICommand`는 아래와 같은 주요 멤버로 구성되어 있다.

- **Execute(object)**: 커맨드가 실행될 때 호출되는 메서드.
- **CanExecute(object)**: 커맨드 실행 가능 여부를 반환하는 메서드.
- **CanExecuteChanged**: CanExecute 상태가 변경되었을 때 이를 알리는 이벤트.

---

## 3. RelayCommand 클래스 구현 및 활용

`RelayCommand`는 일반적인 명령 처리를 위해 자주 사용되는 클래스로, 사용자가 정의한 실행 로직과 실행 조건을 전달받아 동작한다.

아래는 `RelayCommand` 클래스의 기본적인 구현 예시이다.

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



---

## 4. ViewModel에서 Command 사용하기

ViewModel에서 정의한 Command를 View의 버튼과 바인딩하여 사용하는 방법을 알아보자.

### ViewModel 코드 작성 예시

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
        return parameter != null && parameter.ToString() == "abc";
    }

    private void ExecuteTestCommand(object parameter)
    {
        MessageBox.Show($"입력된 값: {parameter} aa");
    }
}
```



### XAML 뷰에서 Command 바인딩

뷰(View)에서 버튼에 Command를 연결하는 방법은 다음과 같다.

```xml
<TextBox x:Name="TestBox" Width="200" Height="30"/>
<Button Content="실행" Command="{Binding TestCommand}" 
        CommandParameter="{Binding ElementName=TestBox, Path=Text}" Width="100" Height="30"/>
```

실행하면 텍스트 박스에 'abc'가 입력되었을 때만 버튼이 활성화되며, 버튼 클릭 시 입력된 값과 추가 문자열이 출력된다.

---

