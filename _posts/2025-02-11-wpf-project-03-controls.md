---
title: "(WPF) 3. WPF에서 컨트롤 사용하기"
description: "라벨(Label), 체크 박스(CheckBox), 라디오 버튼(RadioButton), 텍스트 박스(TextBox), 버튼(Button), 패스워드 박스(PasswordBox), 리스트 뷰(ListView) 활용"
date: 2025-02-11 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, controls, ui, xaml]
---

# WPF에서 컨트롤 사용하기

- 최초 작성일: 2025년 2월 11일 (화)

## 목차
1. [WPF 컨트롤 개요](#wpf-컨트롤-개요)
2. [라벨(Label) 사용하기](#라벨label-사용하기)
3. [체크 박스(CheckBox)와 라디오 버튼(RadioButton)](#체크-박스checkbox와-라디오-버튼radiobutton)
4. [텍스트 박스(TextBox)와 패스워드 박스(PasswordBox)](#텍스트-박스textbox와-패스워드-박스passwordbox)
5. [버튼(Button)과 이벤트 핸들러](#버튼button과-이벤트-핸들러)
6. [리스트 뷰(ListView)와 데이터 바인딩](#리스트-뷰listview와-데이터-바인딩)
7. [스택 패널(StackPanel) 활용](#스택-패널stackpanel-활용)

---

## WPF 컨트롤 개요

WPF(Windows Presentation Foundation)에서는 다양한 UI 컨트롤을 제공하며, 이를 활용하여 사용자 인터페이스를 직관적으로 구성할 수 있다. 이번 글에서는 **라벨(Label), 체크 박스(CheckBox), 라디오 버튼(RadioButton), 텍스트 박스(TextBox), 버튼(Button), 패스워드 박스(PasswordBox), 리스트 뷰(ListView)** 등을 사용하는 방법을 설명한다.

각 컨트롤의 동작 방식과 기본적인 사용법을 예제 코드와 함께 학습해보자.

---

## 라벨(Label) 사용하기

### 라벨(Label)이란?
라벨(Label)은 사용자가 UI에서 정보를 쉽게 확인할 수 있도록 **텍스트를 출력하는 컨트롤**이다. 주로 제목, 설명, 상태 표시 등을 위해 사용된다.

### 라벨 추가하기
```xml
<Label x:Name="LabelTest1" Content="기본 텍스트" Width="200" Height="30"/>
```

### 주요 속성
- `Content`: 표시할 텍스트를 지정한다.
- `FontSize`: 글자 크기를 지정한다.
- `Foreground`: 글자 색상을 변경한다.
- `Background`: 라벨의 배경색을 변경한다.

C# 코드에서 Label의 텍스트를 동적으로 변경할 수 있다.
```csharp
LabelTest1.Content = "변경된 텍스트";
```

라벨은 UI에서 **설명을 제공하거나 동적 메시지를 출력하는 데** 유용하게 사용된다.

---

## 체크 박스(CheckBox)와 라디오 버튼(RadioButton)

### 체크 박스(CheckBox)란?
체크 박스는 사용자가 **다중 선택이 가능한 항목을 선택할 때** 사용한다.

#### 체크 박스 추가하기
```xml
<CheckBox x:Name="CheckBox1" Content="CheckBox" HorizontalAlignment="Left" Margin="37,160,0,0" VerticalAlignment="Top" Height="30" Width="103"/>
```

#### 체크 상태 확인하기
```csharp
private void btnTest1_Click(object sender, RoutedEventArgs e)
{
    labelTest1.Content = "내용변경완료";
    MessageBox.Show(CheckBox1.IsChecked + "");
}
```

<img width="311" alt="image" src="https://github.com/user-attachments/assets/02c583ed-1a4b-4102-907e-8ada977a3caa" />

### 라디오 버튼(RadioButton)이란?
라디오 버튼은 사용자가 **여러 개의 옵션 중 하나만 선택하도록** 할 때 사용한다. 같은 `GroupName`을 지정하면 **그룹 내에서 하나의 옵션만 선택할 수 있다.** 이는 성별 선택, 결제 옵션 선택 등 **배타적인 옵션을 제공할 때 유용**하다.

### 라디오 버튼 추가하기
라디오 버튼을 **Toolbox에서 가져와서 추가**한 후, 복사 & 붙여넣기로 2개를 더 생성한다. 이후 **각 라디오 버튼을 선택한 후 속성 창에서 `GroupName`을 `MyGroup`으로 설정**하면 해당 라디오 버튼들은 하나의 그룹으로 묶이게 된다. 이렇게 설정하면 **같은 그룹 내에서는 하나의 옵션만 선택할 수 있게 된다.**

```xml
<StackPanel>
    <RadioButton x:Name="Radio1" Content="옵션 1" HorizontalAlignment="Left" Margin="37,195,0,0" VerticalAlignment="Top" GroupName="MyGroup"/>
    <RadioButton x:Name="Radio2" Content="옵션 2" HorizontalAlignment="Left" Margin="37,234,0,0" VerticalAlignment="Top" GroupName="MyGroup"/>
    <RadioButton x:Name="Radio3" Content="옵션 3" HorizontalAlignment="Left" Margin="37,271,0,0" VerticalAlignment="Top" GroupName="MyGroup"/>
</StackPanel>
```

위 코드에서는 `GroupName="MyGroup"`을 설정하여 **세 개의 라디오 버튼 중 하나만 선택할 수 있도록 제한**했다.

### 선택된 라디오 버튼 확인하기
사용자가 선택한 옵션을 확인하려면 다음과 같이 C# 코드를 작성하면 된다.

```csharp
private void CheckSelectedRadioButton()
{
    if (Radio1.IsChecked == true)
    {
        MessageBox.Show("옵션 1이 선택되었습니다.");
    }
    else if (Radio2.IsChecked == true)
    {
        MessageBox.Show("옵션 2이 선택되었습니다.");
    }
    else if (Radio3.IsChecked == true)
    {
        MessageBox.Show("옵션 3이 선택되었습니다.");
    }
}
```

### 라디오 버튼의 활용 예시
- **설문 조사**: 사용자에게 하나의 답변만 선택하도록 할 때 사용.
- **성별 선택**: "남성", "여성", "기타" 옵션 중 하나만 선택할 경우.
- **배송 옵션 선택**: "일반 배송", "빠른 배송", "특급 배송" 중 하나 선택.

라디오 버튼을 활용하면 **사용자가 실수로 여러 개의 옵션을 선택하는 문제를 방지**할 수 있으며, UX(User Experience) 측면에서도 깔끔하고 직관적인 인터페이스를 제공할 수 있다.

<img width="518" alt="image" src="https://github.com/user-attachments/assets/9836c2b2-3ef5-4cdf-b55f-90dbf783bf1b" />

---

## 텍스트 박스(TextBox)와 패스워드 박스(PasswordBox)

### 텍스트 박스(TextBox)란?
텍스트 박스는 사용자가 **문자를 입력할 수 있는 필드**를 제공하는 컨트롤이다. 사용자 입력을 받을 수 있으며, 폼(Form)과 같은 입력 UI에 필수적으로 사용된다.

### 텍스트 박스 추가하기
```xml
<TextBox x:Name="TextBox1" Width="200" Height="30"/>
```

### 주요 속성
- **Text**: 입력된 텍스트를 가져오거나 설정할 수 있음.
- **MaxLength**: 입력할 수 있는 최대 문자 수 지정.
- **AcceptsReturn**: 여러 줄 입력을 허용할지 여부 설정.
- **IsReadOnly**: 읽기 전용 모드 활성화.

### 사용 예제 (C# 코드)
```csharp
string userInput = TextBox1.Text;
```
이 코드를 통해 사용자가 입력한 값을 변수에 저장할 수 있다.

### 패스워드 박스(PasswordBox)란?
패스워드 박스는 **보안이 필요한 입력(예: 비밀번호 입력)** 시 사용되는 컨트롤이다. 텍스트 박스와 달리 입력된 문자를 화면에 표시하지 않는다.

### 패스워드 박스 추가하기
```xml
<PasswordBox x:Name="PasswordBox1" Width="200" Height="30"/>
```

### 주요 속성
- **Password**: 입력된 비밀번호를 가져오거나 설정할 수 있음.
- **MaxLength**: 입력할 수 있는 최대 문자 수 지정.
- **Foreground**: 글자 색상을 설정.

### 사용 예제 (C# 코드)
```csharp
string password = PasswordBox1.Password;
```
이 코드를 사용하여 비밀번호 입력을 변수에 저장할 수 있다.

---

## 버튼(Button)과 이벤트 핸들러

### 버튼(Button)이란?
버튼은 사용자가 클릭하여 특정 동작을 수행할 수 있도록 하는 컨트롤이다. **폼 제출, 이벤트 실행, UI 상호작용** 등의 기능을 수행할 수 있다.

### 버튼 추가하기
```xml
<Button x:Name="BtnClick" Content="클릭" Click="BtnClick_Click"/>
```

### 주요 속성
- **Content**: 버튼에 표시될 텍스트 설정.
- **IsEnabled**: 버튼을 활성화 또는 비활성화.
- **Background**: 버튼의 배경색 지정.

### 클릭 이벤트 핸들러 추가하기
```csharp
private void BtnClick_Click(object sender, RoutedEventArgs e)
{
    MessageBox.Show("버튼이 클릭되었습니다!");
}
```
버튼이 클릭되면 `MessageBox.Show`를 통해 메시지를 표시하는 동작을 수행한다.

버튼 컨트롤은 WPF UI에서 가장 많이 사용되는 요소 중 하나이며, **사용자 입력을 받거나 특정 동작을 실행하는 데 필수적**이다.

---

## 리스트 뷰(ListView)와 데이터 바인딩

### 리스트 뷰(ListView)란?
리스트 뷰는 **데이터를 표 형태로 정리하여 보여주는 컨트롤**입니다. 사용자가 여러 개의 데이터를 한 번에 확인할 수 있도록 설계되었습니다. WPF(Windows Presentation Foundation)에서는 `GridView`와 함께 사용하여 표 형식의 데이터를 쉽게 표시할 수 있습니다.

### 리스트 뷰 추가하기
```xml
<ListView Margin="228,61,228,185" x:Name="listView1">
    <ListView.View>
        <GridView>
            <GridViewColumn Header="이미지" Width="300"/>
            <GridViewColumn Header="이름" DisplayMemberBinding="{Binding Name}"/>
            <GridViewColumn Header="나이" DisplayMemberBinding="{Binding UserAge}"/>
        </GridView>
    </ListView.View>
</ListView>
```

위 코드에서 `DisplayMemberBinding` 속성을 사용하여 **데이터 바인딩을 통해 UI에 데이터를 동적으로 표시할 수 있습니다.**

### 데이터 모델 생성 및 바인딩

먼저, `Model`이라는 폴더를 만들고 해당 폴더 내에 `User`라는 클래스를 생성합니다. 그리고 `User.cs`에 아래와 같이 작성합니다.

```csharp
namespace WpfAppProject.Models
{
    class User
    {
        public string Name { get; set; }
        public string UserImg { get; set; }
        public int UserAge { get; set; }
    }
}
```

위 모델 클래스를 통해 **사용자 데이터를 관리할 수 있으며, 이후 ListView에 바인딩하여 출력할 수 있습니다.**

### 리스트 뷰에 데이터 바인딩하기
아래 코드를 `MainWindow.xaml.cs`에서 버튼 클릭 이벤트에 추가하여 리스트 뷰에 데이터를 동적으로 로드할 수 있도록 합니다.

```csharp
private void btnTest1_Click(object sender, RoutedEventArgs e)
{
    labelTest1.Content = "내용변경완료";
    
    List<User> myList1 = new List<User>();

    User userA = new User();
    userA.Name = "Noah";
    userA.UserAge = 15;

    User userB = new User();
    userB.Name = "Liam";
    userB.UserAge = 15;

    myList1.Add(userA);
    myList1.Add(userB);

    listView1.ItemsSource = myList1;
}
```

이제 버튼을 클릭하면 `listView1`에 사용자의 이름과 나이가 표시됩니다.

### 리스트 뷰에서 이미지 추가하기

이미지를 표시하려면 `DataTemplate`을 사용하여 특정 열에 이미지를 추가해야 합니다.

```xml
<ListView Margin="228,61,165,185" x:Name="listView1">
    <ListView.View>
        <GridView>
            <GridViewColumn Header="이미지" Width="300">
                <GridViewColumn.CellTemplate>
                    <DataTemplate>
                        <Image Width="60" Height="60" Source="{Binding UserImg}"/>
                    </DataTemplate>
                </GridViewColumn.CellTemplate>
            </GridViewColumn>
            <GridViewColumn Header="이름" DisplayMemberBinding="{Binding Name}"/>
            <GridViewColumn Header="나이" DisplayMemberBinding="{Binding UserAge}"/>
        </GridView>
    </ListView.View>
</ListView>
```

그리고 `User` 모델에 이미지 경로를 추가합니다.

```csharp
private void btnTest1_Click(object sender, RoutedEventArgs e)
{
    labelTest1.Content = "내용변경완료";
    
    List<User> myList1 = new List<User>();

    User userA = new User();
    userA.UserImg = @"D:\\Documents\\GitHub\\WpfAppProject\\Resources\\photo1.jpg";
    userA.Name = "Noah";
    userA.UserAge = 15;

    User userB = new User();
    userB.UserImg = @"D:\\Documents\\GitHub\\WpfAppProject\\Resources\\photo2.jpg";
    userB.Name = "Liam";
    userB.UserAge = 15;

    myList1.Add(userA);
    myList1.Add(userB);

    listView1.ItemsSource = myList1;
}
```

이렇게 설정하면 **리스트 뷰에서 사용자 이미지도 함께 표시할 수 있습니다.**

리스트 뷰를 사용하면 UI에서 **데이터를 표 형태로 쉽게 출력**할 수 있으며, 데이터 바인딩을 활용하면 코드에서 동적으로 데이터를 변경할 수 있습니다.

---

## 스택 패널(StackPanel) 활용

### 스택 패널(StackPanel)이란?
스택 패널(StackPanel)은 WPF에서 **컨트롤을 수직 또는 수평 방향으로 정렬**하는 데 사용되는 컨테이너이다. 여러 UI 요소를 균일하게 정렬할 때 유용하며, 간단한 레이아웃 구성을 쉽게 할 수 있다.

### 스택 패널 추가하기
```xml
<StackPanel Orientation="Vertical">
    <Button Content="버튼 1" Width="100" Height="30"/>
    <Button Content="버튼 2" Width="100" Height="30"/>
</StackPanel>
```

위 코드에서는 `StackPanel`이 **세로 방향(Vertical)**으로 설정되어 있어, 버튼이 위에서 아래로 정렬된다. 

#### 주요 속성
- **Orientation**: `Horizontal`(가로 정렬), `Vertical`(세로 정렬) 설정 가능
- **Margin**: 컨트롤 간 여백을 설정
- **HorizontalAlignment / VerticalAlignment**: 정렬 방식 지정

### 스택 패널을 활용한 UI 배치 예제
```xml
<StackPanel Orientation="Horizontal" Margin="10">
    <Label Content="이름:" VerticalAlignment="Center"/>
    <TextBox Width="200" Height="25"/>
    <Button Content="확인" Width="75" Height="25"/>
</StackPanel>
```

위 코드는 **가로 방향(Horizontal)으로 컨트롤을 정렬**하는 예제이다. 라벨, 텍스트 박스, 버튼이 한 줄에 배치되며, `Margin`을 활용하여 여백을 조정할 수 있다.

### 스택 패널이 사용되는 경우
1. **폼(Form) 레이아웃 구성** - 입력 필드와 버튼을 정렬할 때 유용
2. **내비게이션 메뉴** - 버튼을 세로로 배치하여 메뉴 구성 가능
3. **설정 창** - 여러 옵션을 그룹화하여 정렬할 때 사용

스택 패널을 활용하면 레이아웃 구성을 쉽게 할 수 있으며, 복잡한 UI 구성에서도 정렬을 효과적으로 관리할 수 있다.

---

이 문서에서는 WPF에서 다양한 컨트롤을 사용하는 방법을 살펴보았다. 이를 활용하여 보다 직관적인 UI를 개발할 수 있다.

