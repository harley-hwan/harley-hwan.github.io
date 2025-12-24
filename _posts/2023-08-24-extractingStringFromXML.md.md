---
title: xml 파일에서 특정 문자열 포함하는 태그의 내용 출력
description: "cat, grep, gawk, XML parsing"
date: 2023-08-24 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, cat, grep, gawk, XML, parsing]
---

# Ethernet Configuration Check via Script

- 최초 작성일: 2023년 8월 23일(수)

## 

```bash
IP1=`cat /Info.xml|grep -i "RFCH"|gawk -F"<" '{print $2}'|gawk -F">" '{print $2}'`
```

<br/>

## 

### `/Info.xml` "RFCH" 

1. **`cat /Info.xml`**:
    - `cat`: 주어진 파일의 내용을 화면에 출력하는 명령어.
    - `/Info.xml`: `cat`에 전달된 파일 경로.
    - 결과: `/Info.xml`의 내용이 출력됨.

2. **`grep -i "RFCH"`**:
    - `grep`: 텍스트에서 특정 패턴을 검색하는 명령어.
    - `-i`: 대소문자 구분 없이 검색하는 옵션.
    - 결과: `/Info.xml`에서 "RFCH" 문자열(대소문자 구분 없이)을 포함하는 모든 라인이 출력됨.

3. **`gawk -F"<" '{print $2}'`**:
    - `gawk`: 텍스트 처리용 프로그래밍 언어 AWK의 GNU 버전.
    - `-F"<"`: 입력 텍스트를 "<"로 구분.
    - `{print $2}`: 나눈 텍스트 중 두 번째 부분을 출력.
    - 결과: `<` 문자를 기준으로 구분된 텍스트의 두 번째 부분이 출력됨.

4. **`gawk -F">" '{print $2}'`**:
    - `gawk`: 동일한 명령어, 이번에는 ">"로 텍스트를 구분.
    - 결과: `>` 문자로 구분된 텍스트의 두 번째 부분이 출력됨.

<br/>

**총결**: 이 코드 `/Info.xml` 파일에서 "RFCH" 문자열을 포함하는 태그의 내용을 출력.

<br/>

## :

`/Info.xml`에 아래와 같은 내용이 있다면:

```xml
<info>
    <RFCH>12345</RFCH>
</info>
```

위의 코드 조합의 결과는 "12345"를 출력합니다.
