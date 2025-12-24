---
title: (MFC) 메시지 박스 프로그램 -1
description: MessageBox 프로그램 작성
date: 2022-02-23 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, serialport, registry]
---

# [MFC] 메시지 박스 프로그램 작성 -1

- 최초 작성일: 2022년 2월 23일 (수)

## 목적

2개의 버튼을 생성하고, 생성된 버튼을 클릭하면 새로운 창이 표시된다.

<br/>

## 구현

### 프로젝트 생성

아래와 같이 MFC Application을 생성해준다. 프로젝트명은 MsgBox1로 정했다.

![image](https://user-images.githubusercontent.com/68185569/155261077-834c6322-a5d9-4d02-ac9e-fd97b8704bc7.png)

<br/>

그리고, Application type (응용 프로그램 종류)는 'Dialog based (대화 상자 기반)'를 선택하고 [Finish] 버튼을 클릭한다.

![image](https://user-images.githubusercontent.com/68185569/155261120-68dfaad7-09d3-41fb-b396-e9569d0b5c86.png)

<br/>

### 다이얼로그 생성 및 설정

그러면 아래와 같은 창이 나오는데, 안 나온다면 [Ctrl]-[Shift]-[R] 혹은 [메뉴]-[보기]-[다른 창]-[리소스 뷰]를 클릭하면 된다.

![image](https://user-images.githubusercontent.com/68185569/155261424-cbb0d2e8-080d-4e1e-ba5e-0e45e5241bca.png)

<br/>

그러면, 가운데 Dialog에 있는 모든 컨트롤들을 삭제해준다. ( [Ctrl + A] + [Delete] )

![image](https://user-images.githubusercontent.com/68185569/155261482-becf4476-1e49-46b6-9ea6-c98f1c5a58c2.png)

<br/>

그런 다음, Toolbox(도구상자) 내의 Button을 끌어와 Dialog에 넣어준다. 

![image](https://user-images.githubusercontent.com/68185569/155261654-e123aaf9-8e59-4b66-b493-b46ef98d6f2c.png)

<br/>

버튼이 생성됐다면, 우측 마우스 클릭한 후 Properties(속성)을 눌러보자.

![image](https://user-images.githubusercontent.com/68185569/155261899-7b2ad79b-cea5-4314-9d43-21399928a782.png)

<br/>

그러면 오른쪽 아래의 창이 뜰텐데, 거기서 해당 컨트롤의 속성을 변경할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/155261995-65cb3746-613b-45fe-912b-6c1cdb482739.png)

<br/>

버튼을 추가로 하나 더 생성하여, 다음과 같이 ID와 Caption을 변경하여 설정하자.

![image](https://user-images.githubusercontent.com/68185569/155262471-510b1ad5-735f-4b3a-87ca-ed5de9b14ba6.png)

![image](https://user-images.githubusercontent.com/68185569/155262129-ce335587-acf1-4336-b9b5-c48c513784d7.png)
![image](https://user-images.githubusercontent.com/68185569/155262222-e91af810-1719-4212-a987-2cad414a783f.png)

<br/>

### 함수 추가

멤버 함수를 추가하기 위해서 [메뉴]-[프로젝트]-[클래스 마법사] 또는, [Ctrl + Shift + X] 키를 눌러 [클래스 마법사]를 실행시킨다.

그럼, 아래의 창이 뜨는데 거기서 [Commands(명령)] 탭에서 Object IDs(개체ID)는 'IDC_BUTTON_HELLO', Messages(메시지) 는 'BN_CLICKED'를 클릭한 후 Add Handler(처리기 추가)를 클릭하면 다음과 같이 [Add Member Function(멤버 함수 추가)] 창이 표시된다. 그러면 OK 버튼을 누르자.

![image](https://user-images.githubusercontent.com/68185569/155262755-5980bfe1-277a-40ef-9ddb-5b7ce6dac929.png)

<br/>

그러면 보통, MsgBox1Dlg.cpp에 void CMsgBox1Dlg::OnClickedButtonHello() 함수가 생성된 곳으로 이동하여 바로 확인할 수 있는데, 아니라면 다음과 같이 [클래스 뷰]-[MsgBox1]-[CMsgBox1Dlg] 에서 OnClickedButtonHello() 찾아 더블클릭하면, 해당 코드로 이동할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/155263246-d8158094-0d8a-42ce-afa9-49bfd8b4adcf.png)

<br/>

위와 동일하게, Close 버튼도 똑같이 생성해주고, 아래의 코드를 각각 삽입하고 프로그램을 빌드하고 실행해보자.

![image](https://user-images.githubusercontent.com/68185569/155263600-415a4558-d131-4f71-91ac-c013c3e0d40a.png)

<br/>

### 실행 결과

![image](https://user-images.githubusercontent.com/68185569/155263405-10d47d72-3d13-4fc8-8d9b-9cd1955139bb.png)
![image](https://user-images.githubusercontent.com/68185569/155263426-e6a9ea45-2b21-4baa-8e25-9e23923da6f4.png)

<br/>
