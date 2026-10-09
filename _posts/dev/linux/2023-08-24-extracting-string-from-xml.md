---
title: xml 파일에서 특정 문자열 포함하는 태그의 내용 출력
description: "cat, grep, gawk, XML parsing"
date: 2023-08-24 10:00:00 +0900
slug: 'extractingStringFromXML'
categories: [Dev, Linux]
tags: [linux, cat, grep, gawk, xml, parsing]
---
## 코드

```bash
IP1=`cat /Info.xml|grep -i "RFCH"|gawk -F"<" '{print $2}'|gawk -F">" '{print $2}'`
```

<br/>

## 설명

### `/Info.xml` 파일에서 "RFCH" 문자열 추출하기

1. `cat /Info.xml`
    - `cat`은 주어진 파일의 내용을 화면에 출력하는 명령어다. `/Info.xml`의 내용이 그대로 출력된다.

2. `grep -i "RFCH"`
    - `grep`은 텍스트에서 특정 패턴을 검색하는 명령어이고, `-i`는 대소문자를 구분하지 않는 옵션이다.
    - 여기까지 거치면 "RFCH" 문자열을 포함하는 라인만 남는다.

3. `gawk -F"<" '{print $2}'`
    - `gawk`는 텍스트 처리용 프로그래밍 언어 AWK의 GNU 버전이다.
    - `-F"<"`로 입력을 `<` 기준으로 나누고, `{print $2}`로 두 번째 부분을 출력한다.

4. `gawk -F">" '{print $2}'`
    - 같은 방식으로 이번에는 `>`를 구분자로 한 번 더 잘라, 태그 안의 내용만 남긴다.

<br/>

정리하면, 이 코드는 `/Info.xml` 파일에서 "RFCH" 문자열을 포함하는 태그의 내용을 출력한다.

<br/>

## 예시:

`/Info.xml`에 아래와 같은 내용이 있다면:

```xml
<info>
    <RFCH>12345</RFCH>
</info>
```

위의 코드 조합은 "12345"를 출력한다.
