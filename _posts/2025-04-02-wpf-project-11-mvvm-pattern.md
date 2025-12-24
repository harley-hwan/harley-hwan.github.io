---
title: "(WPF) 11. MVVM 패턴 복습 및 이론, 실습"
description: "MVVM 패턴 이론과 폴더 구조 실습"
date: 2025-04-02 10:00:00 +0900
categories: [Dev, WPF]
tags: [WPF, MVVM, C#, XAML, ViewModel]
---

# MVVM , 

## MVVM 

- **Model**: 애플리케이션에서 사용되는 **데이터**와 그 데이터를 처리하는 **비즈니스 로직**을 담당한다.  
- **View**: 사용자에게 보이는 **UI 화면**으로, XAML 등의 **디자인 요소**를 포함한다. (예: Window, UserControl)  
- **ViewModel**: View와 Model 사이에서 **중간자 역할**을 한다. View의 데이터 바인딩 대상이 되는 **속성(Property)**과 **명령(Command)**을 제공하여, 화면 동작을 처리한다. (주로 `INotifyPropertyChanged` 구현과 `ICommand` 등을 사용한다)

---

## MVVM 

- **UI와 로직 분리:** 화면 코드(XAML)와 데이터 로직(C#)을 분리하여 **관심사 분리**를 달성한다. View와 Model이 직접 의존하지 않으므로, 한쪽을 변경해도 다른 쪽에 미치는 영향이 적다.  
- **유지보수 및 확장 용이:** 역할별로 코드가 나뉘어 있어 구조가 **깔끔**해지고, 기능 추가나 수정이 쉬워진다. 팀 작업 시에도 **분업**이 수월하다.  
- **테스트 용이:** ViewModel에 애플리케이션 로직을 모으기 때문에 **UI 없이도** 로직을 독립적으로 테스트할 수 있다. 즉, 단위 테스트 등으로 비즈니스 로직 검증이 가능하다.  
- **WPF 기능과 시너지:** WPF의 **데이터 바인딩**과 **커맨드** 기능을 활용하여 최소한의 코드로 UI와 데이터 동기화가 가능하다. MVVM은 WPF 디자인에 잘 맞는 패턴이므로 WPF 개발에서 사실상 표준처럼 쓰인다.

---

## 

WPF 프로젝트에 MVVM 패턴을 적용할 때는 보통 폴더를 나눠 파일들을 관리한다. 예를 들어 **Views**, **ViewModels**, **Models** 폴더를 만들어 각 역할별 파일을 넣는다:

```plaintext
MyWpfApp/
├── Models/           ← 모델 클래스 폴더
│   └── User.cs           (예: 데이터 구조 및 비즈니스 로직 클래스)
├── ViewModels/       ← 뷰모델 클래스 폴더 
│   └── MainViewModel.cs  (예: MainWindow에 대응하는 뷰모델 클래스)
├── Views/            ← 뷰(XAML) 폴더 
│   ├── MainWindow.xaml    (메인 화면 XAML)
│   └── MainWindow.xaml.cs (메인 화면 코드비하인드)
│   └── SecondView.xaml    (두 번째 화면 XAML)
│   └── SecondView.xaml.cs (두 번째 화면 코드비하인드)
└── App.xaml          (응용 프로그램 진입점 설정 파일, StartupUri 등)
```

위와 같이 폴더를 구성하면 파일 역할이 명확해진다.  
- **Views 폴더:** 화면에 해당하는 XAML 파일들과 그 코드비하인드(.xaml.cs).  
- **ViewModels 폴더:** 화면과 모델을 연결하는 로직이 담긴 클래스들 (뷰모델).  
- **Models 폴더:** 애플리케이션의 데이터 구조 및 비즈니스 로직을 담은 클래스들.

---

## MainWindow.xaml Views 

기존에 프로젝트 루트에 있던 `MainWindow.xaml` 파일을 **Views 폴더**로 옮겨 MVVM 구조를 적용해보자. Visual Studio를 사용한다면 다음 순서로 진행한다:

1. **Views 폴더 생성:** 프로젝트에 `Views` 폴더를 추가한다. (솔루션 탐색기에서 프로젝트명 우클릭 → 새 폴더)  
2. **MainWindow.xaml 이동:** 기존 `MainWindow.xaml`과 `MainWindow.xaml.cs` 파일을 Views 폴더로 **드래그**하여 이동시킨다.  
3. **네임스페이스 확인:** 파일 이동 후 `MainWindow.xaml` 상단의 `x:Class` 값과 코드비하인드의 `namespace`가 `...Views`로 올바르게 변경됐는지 확인한다.  
   - (Visual Studio에서 자동으로 변경해주지만, 혹시 안 되어 있다면 수동으로 고쳐준다.)  
4. **프로젝트 빌드:** 이동 후 프로젝트를 **빌드**하여 오류가 없는지 확인한다. 이 상태로는 `App.xaml`이 여전히 옮기기 전 경로를 참조하고 있어 **시작 시 오류**가 발생한다. 다음 단계에서 `StartupUri` 설정을 수정할 것이다.

---

## App.xaml StartupUri 

마지막으로, 애플리케이션이 시작할 때 참조하는 경로인 `App.xaml`의 **StartupUri**를 수정해야 한다. `MainWindow.xaml`을 Views 폴더로 옮겼으므로, `App.xaml`에서 StartupUri에 폴더 경로를 추가해준다:

변경 전 (`App.xaml`):
```xml
<Application x:Class="MyApp.App"
             StartupUri="MainWindow.xaml">
    <!-- ... 기타 설정 ... -->
</Application>
```

변경 후 (`App.xaml`):
```xml
<Application x:Class="MyApp.App"
             StartupUri="Views/MainWindow.xaml">
    <!-- ... 기타 설정 ... -->
</Application>
```

위와 같이 `StartupUri`를 **`Views/MainWindow.xaml`**로 변경하면, 애플리케이션 실행 시 올바른 MainWindow를 찾아 열게 된다. 이제 프로젝트가 MVVM 폴더 구조에 맞게 정리되었으며, 이 구조를 바탕으로 개발을 진행하면 된다.
