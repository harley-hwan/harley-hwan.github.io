---
title: Programmers 숫자 문자열과 영단어
description: 2021 카카오 채용연계형 인턴십
date: 2021-10-06 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 

- 최초 작성일: 2021년 10월 06일(수)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/81301>

## 

- 네오와 프로도가 숫자놀이를 하고 있습니다. 네오가 프로도에게 숫자를 건넬 때 일부 자릿수를 영단어로 바꾼 카드를 건네주면 프로도는 원래 숫자를 찾는 게임입니다.
- 다음은 숫자의 일부 자릿수를 영단어로 바꾸는 예시입니다.
  - 1478 → "one4seveneight"
  - 234567 → "23four5six7"
  - 10203 → "1zerotwozero3"
- 이렇게 숫자의 일부 자릿수가 영단어로 바뀌어졌거나, 혹은 바뀌지 않고 그대로인 문자열 `s`가 매개변수로 주어집니다. `s`가 의미하는 원래 숫자를 return 하도록 solution 함수를 완성해주세요.

- 참고로 각 숫자에 대응되는 영단어는 다음 표와 같습니다.

| 숫자 | 영단어 |
| ---- | :----- |
| 0    | zero   |
| 1    | one    |
| 2    | two    |
| 3    | three  |
| 4    | four   |
| 5    | five   |
| 6    | six    |
| 7    | seven  |
| 8    | eight  |
| 9    | nine   |

## 

- 1 ≤ `s`의 길이 ≤ 50
- `s`가 "zero" 또는 "0"으로 시작하는 경우는 주어지지 않습니다.
- return 값이 1 이상 2,000,000,000 이하의 정수가 되는 올바른 입력만 `s`로 주어집니다.

## 

| s                    | result |
| -------------------- | ------ |
| `"one4seveneight"`   | 1478   |
| `"23four5six7"`      | 234567 |
| `"2three45sixseven"` | 234567 |
| `"123"`              | 123    |

## 1

- 주어지는 문자열을 하나씩 돌면서 일치하는 영단어와 대응되는 숫자를 찾기 위해 map<string, string> 형태의 words라는 0~9, zero~nine 을 매칭치켜 저장해둔다.
- 그리고 정답을 저장하기 위한 answer와 중간중간 영단어를 저장해 map의 원소들과 비교하기 위한 temp라는 빈 문자열을 선언해준다.
- 그럼 이제 주어진 문자열을 하나씩 차례대로 비교해봐야하는데, 해당 문자열이 숫자일 경우 answer에 그대로 더해서 저장해주면되고, 숫자가 아니면 그 문자를 하나씩 temp에 저장하며 words map에 일치하는 게 나올 때까지 찾아간다.
- 일치하는 게 나오면 answer에 더해준 후, 다시 temp를 비워주고 위의 과정을 반복한다.
- 그렇게 문자열의 모든 문자를 비교하면, answer에 저장된 결과를 정수형으로 변환 후 출력한다.

---

```c++
#include <iostream>
#include <string>
#include <map>
using namespace std;

map <string, string> words= { {"zero", "0"},
                            {"one", "1"},
                            {"two", "2"},
                            {"three", "3"},
                            {"four", "4"},
                            {"five", "5"},
                            {"six", "6"},
                            {"seven", "7"},
                            {"eight", "8"},
                            {"nine", "9"} };

int solution(string s) {
    string answer = "";
    string temp = "";

    for (int i = 0; i < s.size(); i++) {
       if (!isdigit(s[i])) {
           temp += s[i];
           if (words[temp] != "") {
               answer += words[temp];
               temp = "";
           }
       }
       else answer += s[i];
    }
    return stoi(answer);
}
```

---

## 2

- 구글링하다가 찾은 방법인데, regex를 이용하면 아래의 풀이와 같이 간단하게 풀이할 수 있다.
- 주어지는 문자열에서 일치하는 문자가 발견했을 경우, 뒤의 숫자로 replace(대체)할 수 있다.
- 마지막으로, stoi로 정수형으로 반환하면 된다.

---

    #include <iostream>
    #include <regex>
    
    using namespace std;
    
    int solution(string s) {
        s = regex_replace(s, regex("zero"), "0");
        s = regex_replace(s, regex("one"), "1");
        s = regex_replace(s, regex("two"), "2");
        s = regex_replace(s, regex("three"), "3");
        s = regex_replace(s, regex("four"), "4");
        s = regex_replace(s, regex("five"), "5");
        s = regex_replace(s, regex("six"), "6");
        s = regex_replace(s, regex("seven"), "7");
        s = regex_replace(s, regex("eight"), "8");
        s = regex_replace(s, regex("nine"), "9");    
        return stoi(s);
    }
