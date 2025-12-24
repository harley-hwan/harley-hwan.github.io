---
title: "(WPF) 9. UserControl과 Custom Control 활용하기"
description: "UserControl과 Custom Control의 차이점과 구현 방법"
date: 2025-04-02 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, usercontrol, customcontrol, mvvm, xaml, ui]
---

# UserControl과 Custom Control 활용하기

- 최초 작성일: 2025년 3월 29일 (토)

## 목차

1. [UserControl](#usercontrol)
   - [정의](#정의)
   - [생성 방법](#생성-방법)
   - [XAML 예제](#xaml-예제)
   - [코드 비하인드 설명](#코드-비하인드-설명)
   - [ViewModel 바인딩 예시](#viewmodel-바인딩-예시)
   - [사용 결과](#사용-결과)

2. [Custom Control](#custom-control)
   - [정의](#정의-1)
   - [생성 방법](#생성-방법-1)
   - [XAML 예제](#xaml-예제-1)
   - [코드 비하인드 설명](#코드-비하인드-설명-1)
   - [ViewModel 바인딩 예시](#viewmodel-바인딩-예시-1)
   - [사용 결과](#사용-결과-1)

3. [정리: UserControl과 Custom Control의 차이](#정리-usercontrol과-custom-control의-차이)

---

WPF에서 UI를 재사용하거나 확장하기 위해 **사용자 컨트롤(UserControl)**과 **커스텀 컨트롤(Custom Control)**을 만들 수 있다. 두 방식은 목적과 구현 방식이 다르다. 이 문서는 UserControl과 Custom Control이 무엇인지, 어떻게 만들며 어떤 차이가 있는지를 설명한다.

## UserControl

### 정의  
**UserControl**은 기존의 여러 컨트롤을 조합하여 하나의 재사용 가능한 UI 조각으로 만드는 컨트롤이다. 즉, XAML로 필요한 버튼, 텍스트 박스, 레이블 등의 기본 컨트롤을 모아 **사용자 지정 컨트롤**을 구성하고, 이를 하나의 컨트롤처럼 사용할 수 있게 해준다. 사용자 컨트롤은 **복잡한 테마나 스타일 변경이 필요 없고**, 주로 특정 화면 또는 어플리케이션 내에서만 사용할 UI를 만들 때 적합하다. 간단히 말해 **여러 기본 컨트롤의 조합**을 캡슐화하는 용도로 사용된다.

### 생성 방법  
Visual Studio에서 UserControl을 만드는 방법은 다음과 같다:

1. **프로젝트에 UserControl 추가:** 솔루션 탐색기에서 프로젝트를 마우스 오른쪽 클릭하고 **추가 > 새 항목**을 선택한 후 **WPF 사용자 컨트롤** 항목을 선택한다. 이름을 지정하여 (예: `ThreeControls`) 추가하면 XAML과 코드비하인드 파일이 생성된다.  
2. **XAML 디자인:** 생성된 `<UserControl>` XAML 파일에 원하는 UI 요소들을 배치한다. 이때 UserControl은 하나의 컨테이너 역할을 하며, Grid나 StackPanel 등을 사용해 내부 레이아웃을 잡는다.  
3. **코드 비하인드 작성:** 필요하면 코드비하인드(.xaml.cs 파일)에서 의존 속성(DependencyProperty) 등을 정의하여 외부에서 바인딩할 수 있는 속성을 추가한다.

### XAML 예제  
아래는 `ThreeControls.xaml` 파일의 예시이다. 이 UserControl에는 **Label**과 **Button** 두 가지 기본 컨트롤이 들어 있으며, Label은 사용자 컨트롤의 커스텀 의존 속성인 `MyText`를 표시하고, Button은 `MyCommand`라는 ICommand를 실행한다.

```xml
<UserControl x:Class="FirstWPFProjects.UserControls.ThreeControls"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Name="root"
             d:DesignHeight="150" d:DesignWidth="300">
    <StackPanel>
        <!-- UserControl의 MyText 속성을 표시하는 레이블 -->
        <Label Content="{Binding MyText, ElementName=root}" />
        <!-- UserControl의 MyCommand 속성에 바인딩된 ICommand를 실행하는 버튼 -->
        <Button Content="클릭" Command="{Binding MyCommand, ElementName=root}" />
    </StackPanel>
</UserControl>
```

위 XAML에서 `x:Name="root"`는 UserControl 자신에게 이름을 부여한 것이다. 이렇게 하면 내부 요소가 `ElementName="root"` 바인딩을 통해 UserControl 자신의 속성에 접근할 수 있다. Label의 `Content`는 `root` UserControl의 `MyText` 속성과 바인딩되고, Button의 `Command`는 `MyCommand` 속성과 연결된다. 이로써 외부에서 `MyText`와 `MyCommand`를 설정하면 UserControl 내부의 Label과 Button에 값이 전달된다.

### 코드 비하인드 설명  
다음은 `ThreeControls.xaml.cs` 코드 비하인드 파일의 핵심 부분이다. UserControl에 **의존 속성(DependencyProperty)** 두 개를 정의하고 있다: 하나는 문자열을 위한 `MyText` 속성이고, 다른 하나는 ICommand를 위한 `MyCommand` 속성이다.

```csharp
public partial class ThreeControls : UserControl
{
    // MyText 의존 속성 등록
    public static readonly DependencyProperty MyTextProperty =
        DependencyProperty.Register("MyText", typeof(string), typeof(ThreeControls), new PropertyMetadata(""));
    public string MyText
    {
        get => (string)GetValue(MyTextProperty);
        set => SetValue(MyTextProperty, value);
    }

    // MyCommand 의존 속성 등록
    public static readonly DependencyProperty MyCommandProperty =
        DependencyProperty.Register("MyCommand", typeof(System.Windows.Input.ICommand), typeof(ThreeControls), new PropertyMetadata(null));
    public System.Windows.Input.ICommand MyCommand
    {
        get => (System.Windows.Input.ICommand)GetValue(MyCommandProperty);
        set => SetValue(MyCommandProperty, value);
    }

    public ThreeControls()
    {
        InitializeComponent();
    }
}
```

위 코드에서 `DependencyProperty.Register`를 사용하여 의존 속성을 정의한다. 이렇게 만든 속성들은 XAML에서 `<local:ThreeControls MyText="..." MyCommand="...">` 형태로 사용할 수 있고, 데이터 바인딩도 지원된다. `MyText` 속성은 문자열을 받아 Label의 내용으로 표시되며, `MyCommand` 속성은 ICommand 개체를 받아 Button 클릭 시 실행된다. **의존 속성**을 사용함으로써 이 UserControl은 WPF의 바인딩, 스타일링, 애니메이션 등의 기능을 활용할 수 있다.

### ViewModel 바인딩 예시  
UserControl을 실제 화면에서 사용하려면 주로 Window(XAML)에서 해당 컨트롤을 선언하고 속성을 지정한다. MVVM 패턴을 사용한다면 ViewModel의 속성과 명령을 UserControl의 의존 속성에 바인딩한다. 예를 들어, `MainWindow.xaml`에서 `ThreeControls` UserControl을 사용하는 코드는 다음과 같다.

```xml
<Window x:Class="FirstWPFProjects.MainWindow" ... 
        xmlns:local="clr-namespace:FirstWPFProjects.UserControls;assembly=FirstWPFProjects">
    <Grid>
        <!-- 사용자 컨트롤 사용 예시 -->
        <local:ThreeControls MyText="{Binding LabelText}"
                              MyCommand="{Binding ClickCommand}" />
    </Grid>
</Window>
```

위 XAML에서는 Window에 DataContext로 설정된 뷰 모델(ViewModel)의 `LabelText` 속성과 `ClickCommand` 명령(ICommand)이 `ThreeControls`의 `MyText` 및 `MyCommand`에 각각 바인딩되어 있다. 이렇게 설정하면, ViewModel에서 `LabelText`에 제공한 문자열이 UserControl 내부 Label에 표시되고, ViewModel의 `ClickCommand`에 연결된 동작이 Button 클릭 시 실행된다.

> **Note:** DataContext는 `MainWindow.xaml.cs` 등에서 `MainWindow.DataContext = new MainViewModel();` 형태로 뷰 모델 인스턴스를 할당하여 설정한다고 가정한다. `LabelText`와 `ClickCommand`는 MainViewModel에 정의된 `string` 속성과 `ICommand` 속성이다.

### 사용 결과  
이 UserControl을 적용한 결과 화면에서는, `ThreeControls` 컨트롤 내부의 레이블에 원하는 텍스트가 표시되고 버튼이 배치된다. 예를 들어 `MyText="안녕하세요"`로 설정하면 화면에 **"안녕하세요"** 라는 글자의 레이블이 나타난다. 버튼을 클릭하면 `MyCommand`에 연결된 동작이 실행된다. 만약 `MyCommand`를 뷰 모델의 ICommand로 바인딩하고 그 명령에서 `MessageBox.Show` 등을 수행하도록 구현했다면, 버튼 클릭 시 해당 메시지 박스가 표시되는 식으로 동작한다. 이처럼 UserControl은 내부에 배치된 여러 컨트롤을 하나로 묶어주며, 복잡한 UI 구성 요소를 손쉽게 재사용할 수 있게 해준다.

## Custom Control

### 정의  
**Custom Control**은 기존 WPF 컨트롤을 서브클래싱(subclassing)하거나 새로운 컨트롤을 만들어 **기능이나 모양을 확장**한 컨트롤이다. 커스텀 컨트롤은 일반적으로 **Control 기반 클래스**를 상속하여 만들며, 고유한 스타일과 컨트롤 템플릿을 가질 수 있다. 즉, **테마 및 스타일을 지원**하고 다른 어플리케이션에서도 재사용하기 좋은 형태의 컨트롤이다. Custom Control은 **재사용 범위가 넓고 유연하게 테마를 적용**해야 하는 시나리오, 또는 **기존에 없는 완전히 새로운 기능의 컨트롤을 만들 때** 주로 사용된다.

### 생성 방법  
WPF에서 Custom Control을 만드는 일반적인 방법은 **새 클래스 파일을 만들어 Control을 상속**하고, Themes\Generic.xaml에 기본 스타일을 정의하는 것이다. Visual Studio에서는 **WPF 사용자 지정 컨트롤** 항목을 추가하면 이러한 구조가 자동으로 생성된다.  

본 예제에서는 간단히 **기존 Label 컨트롤을 상속**하여 Custom Control을 만드는 방법을 시연한다:

1. **컨트롤 클래스 생성:** 프로젝트에 새로운 WPF UserControl을 추가하고 이름을 `MyLabel`로 지정한다. 생성된 `MyLabel.xaml`의 루트 태그를 `<UserControl>`에서 `<Label>`로 변경하고, 코드비하인드 클래스가 `Label`을 상속하도록 수정한다. (Alternatively, XAML 없이 C# 코드만으로 `public class MyLabel : Label`을 작성하고 `DefaultStyleKey`를 설정하는 방법도 있다. 하지만 여기서는 XAML을 통해 간단히 기본 속성을 설정한다.)  
2. **기본 속성 설정:** `MyLabel.xaml` 파일 내 `<Label>` 태그에 미리 원하는 속성을 설정한다. 예제로 배경색(Background)을 검정색, 전경색(Foreground)을 흰색으로 하고 기본 Content를 `"mytext"`로 설정한다. 이 값들은 MyLabel 컨트롤을 사용할 때 초기 기본값으로 적용된다.  
3. **빌드 및 사용 준비:** Custom Control은 별도의 XAML 디자인 파일 없이도 동작하며, Toolbox(도구 상자)에는 나타나지 않을 수 있다. 사용하려면 수동으로 XAML에 `<local:MyLabel>`을 추가하거나 필요한 경우 에셈블리 정보를 지정해준다. 이번 예에서는 같은 프로젝트 내에 있으므로 바로 사용이 가능하다.

### XAML 예제  
`MyLabel.xaml` 파일에서 Label을 정의한 예시는 다음과 같다. (XAML을 사용하지 않고 코드로 컨트롤을 정의할 수도 있지만, 여기서는 이해를 위해 XAML에 기본 속성을 설정한다.)

```xml
<Label x:Class="FirstWPFProjects.MyLabel"
       xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
       xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
       Background="Black"
       Foreground="White"
       Content="mytext" />
```

위 XAML은 MyLabel 컨트롤의 기본 모양과 속성을 정의한다. `Background="Black"`과 `Foreground="White"`를 지정하여 **검은 배경에 흰 글자**를 갖도록 했고, `Content="mytext"`로 기본 표시 텍스트를 정했다. 이 XAML을 통해 MyLabel은 Label을 상속한 커스텀 컨트롤이면서, 기본적으로 Label과 동일한 동작을 하지만 시각적으로 구분되는 스타일을 갖게 된다.

### 코드 비하인드 설명  
Custom Control의 코드비하인드(`MyLabel.xaml.cs`)는 매우 간단하다. Label을 상속받아 partial 클래스로 정의하고 `InitializeComponent()`를 호출하여 XAML에 지정된 내용을 적용한다:

```csharp
public partial class MyLabel : System.Windows.Controls.Label
{
    public MyLabel()
    {
        InitializeComponent();
    }
}
```

위 코드에서 특별한 의존 속성을 추가로 정의하지는 않았다. MyLabel은 기본 Label의 모든 속성과 기능을 그대로 상속하므로, Label의 `Content`, `Foreground`, `Background` 등의 **기존 의존 속성**을 그대로 사용할 수 있다. 필요한 경우 UserControl과 마찬가지로 `DependencyProperty.Register`를 통해 새로운 속성을 추가할 수도 있다. (예를 들어 Label에 없는 새로운 커스텀 속성을 만들 경우)

### ViewModel 바인딩 예시  
MyLabel은 Label을 상속받았으므로 **Content 속성**을 통해 데이터 표시 및 바인딩을 할 수 있다. 사용법은 일반 Label과 동일하다. Window XAML에서 MyLabel을 사용하고, Content를 ViewModel에 바인딩하는 예시는 아래와 같다.

```xml
<Window ... xmlns:local="clr-namespace:FirstWPFProjects;assembly=FirstWPFProjects">
    <StackPanel>
        <!-- 커스텀 컨트롤 사용 예시 -->
        <local:MyLabel Content="{Binding LabelText}" />
    </StackPanel>
</Window>
```

위와 같이 사용하면, ViewModel의 `LabelText` 속성 값이 MyLabel 컨트롤에 표시된다. MyLabel 자체에 명령(ICommand)을 직접 포함하고 있지는 않지만, 필요한 경우 Label 기반의 컨트롤에서도 이벤트를 Command로 노출시키는 패턴을 구현할 수 있다. (예를 들어 Button을 상속한 Custom Control을 만들면 Command 속성을 가질 수 있다.) 이처럼 Custom Control도 WPF의 의존 속성을 활용하여 데이터 바인딩에 참여할 수 있다.

### 사용 결과  
MyLabel 커스텀 컨트롤을 화면에 배치하면 기본적으로 **검은 배경에 흰색 글자**로 된 Label이 보인다. 별도로 Content를 지정하지 않으면 `"mytext"`라는 기본 문구가 표시된다. 만약 XAML에서 `<local:MyLabel Content="Hello" />`처럼 Content를 지정하거나 바인딩하면 그 값으로 내용이 표시된다. 이 Custom Control은 내부적으로 Label이기 때문에 Label과 동일한 동작을 하며, 여러 곳에서 일관된 스타일의 레이블이 필요할 때 재사용할 수 있다. 또한 필요에 따라 Style이나 Template를 추가로 정의하여 MyLabel의 모양을 한 곳에서 수정할 수도 있다. (예: Generic.xaml에 기본 스타일 지정)

## 정리: UserControl과 Custom Control의 차이  
마지막으로 **UserControl과 Custom Control의 주요 차이점**을 정리하면 다음과 같다:

- **구현 방식:**  
  - UserControl은 **XAML과 코드비하인드**로 여러 컨트롤을 합쳐 새로운 UI를 만든다. Visual Studio 디자이너를 통해 쉽게 구성할 수 있다.  
  - Custom Control은 **기존 컨트롤을 상속**하여 새로운 컨트롤 클래스를 만든다. 주로 템플릿과 스타일을 통해 모양을 정의하며, 코드로 로직을 확장한다.  

- **재사용성과 배포:**  
  - UserControl은 특정 어플리케이션 내에서 재사용하기 좋으며, 다른 프로젝트에서 쓰려면 XAML과 코드를 함께 공유해야 한다. Control Template으로 디자인을 크게 바꾸는 것은 어렵다.  
  - Custom Control은 컨트롤 라이브러리 형태로 만들어 여러 어플리케이션에서 재사용하거나 배포하기에 적합하다. 외부 Resource Dictionary를 통해 테마를 변경하거나 스타일을 적용하기 쉽다.

- **스타일과 테마:**  
  - UserControl은 내부 구조가 고정되어 있어 **사용자가 ControlTemplate을 바꿀 수 없다**. 따라서 전체 테마 적용이나 스킨 변경에는 한계가 있다.  
  - Custom Control은 **ControlTemplate**을 제공하여 사용자가 컨트롤의 모양을 완전히 바꿀 수 있고, WPF 테마(예: Light/Dark 모드 등)에 자동으로 반응하도록 설계할 수 있다.

- **사용 난이도:**  
  - UserControl은 초보자도 손쉽게 만들 수 있고, 필요한 기능을 빠르게 묶을 때 적합하다.  
  - Custom Control은 보다 **고급 기능**으로, 구현에 더 많은 코드 작업이 필요하지만 그만큼 **유연하고 강력**하다.  

요약하면, **UserControl은 빠르게 UI 조합을 만들어 재사용할 때**, **Custom Control은 새로운 동작이나 광범위한 재사용을 위한 컨트롤을 개발할 때** 사용한다. 프로젝트 요구사항에 따라 둘 중 알맞은 방식을 선택하여 WPF UI를 구성하면 된다.
