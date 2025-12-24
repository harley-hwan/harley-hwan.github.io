---
title: "(WPF) 5. WPF에서 GML 리소스 활용하기"
description: "GML 리소스를 활용한 스타일 재사용 및 유지보수 방법"
date: 2025-03-14 10:00:00 +0900
categories: [Dev, WPF]
tags: [c#, wpf, styles, gml, xaml, ui]
---

# GML 리소스 활용하기

- 최초 작성일: 2025년 3월 14일 (금)

## 목차

1. [GML 리소스 개요](#gml-리소스-개요)
2. [스타일 리소스 정의하기](#스타일-리소스-정의하기)
3. [정의된 스타일을 컨트롤에 적용하기](#정의된-스타일을-컨트롤에-적용하기)

---

## GML 리소스 개요

GML 리소스는 WPF에서 스타일을 정의하여 재사용할 수 있게 지원하는 기능이다. GML 리소스를 활용하면 반복되는 스타일을 일관성 있게 관리하고 변경 사항을 쉽게 반영할 수 있다.

---

## 스타일 리소스 정의하기

스타일 리소스는 주로 `Window.Resources`에 정의하여 애플리케이션 전체에서 사용할 수 있다. 예시로 그라데이션 배경 스타일을 정의하는 방법을 살펴본다.

### 스타일 리소스 정의 예제

다음은 라벨 배경에 적용할 그라데이션 스타일을 정의하는 예제이다.

```xml
<Window.Resources>
    <Style x:Key="GradientLabelStyle" TargetType="Label">
        <Setter Property="Background">
            <Setter.Value>
                <LinearGradientBrush>
                    <GradientStop Color="White" Offset="0"/>
                    <GradientStop Color="LightGreen" Offset="0.5"/>
                    <GradientStop Color="White" Offset="1"/>
                </LinearGradientBrush>
            </Setter.Value>
        </Setter>
    </Style>
</Window.Resources>
```

위 코드에서는 `TestStyle`이라는 이름의 스타일을 정의하고, 배경에 초록색과 흰색의 그라데이션 효과를 설정했다.

---

## 정의된 스타일을 컨트롤에 적용하기

위에서 정의한 스타일을 컨트롤에 적용하려면, 각 컨트롤의 `Style` 속성에 설정하면 된다.

```xml
<Label Content="Label" Style="{StaticResource TestStyle}"/>
```

위의 방식대로 설정하면 라벨에 간단하게 정의된 스타일을 적용할 수 있다. 또한 다른 라벨이나 컨트롤에도 동일하게 적용하여 손쉽게 재사용할 수 있다.

추가적으로 스타일을 변경하고 싶다면, 리소스에 정의된 스타일만 수정하면 모든 컨트롤에 자동으로 반영된다.

---

## GML 리소스 활용의 장점

- **유지 보수 용이성**: 스타일 변경이 간편하며, 유지보수가 용이하다.
- **재사용성**: 한 번 정의된 스타일을 여러 UI 컨트롤에서 공통으로 사용하여 일관된 UI를 구현할 수 있다.
- **편리한 관리**: 스타일을 중앙에서 관리하므로 디자인 변경이나 테마 적용 시 효과적이다.

이러한 장점을 활용하여 WPF에서 보다 생산적이고 효율적인 UI 개발이 가능하다.

---

이 글에서는 WPF의 GML 리소스를 이용해 스타일을 정의하고 컨트롤에 적용하여 UI를 관리하는 방법을 살펴보았다.

