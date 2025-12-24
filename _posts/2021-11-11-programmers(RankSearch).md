---
title: Programmers 순위 검색
description: 2021 KAKAO BLIND RECRUITMENT
date: 2021-11-11 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 순위 검색

- 최초 작성일: 2021년 11월 11일(수)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/72412>

## 목차



## 문제 설명

- **[본 문제는 정확성과 효율성 테스트 각각 점수가 있는 문제입니다.]**

  카카오는 하반기 경력 개발자 공개채용을 진행 중에 있으며 현재 지원서 접수와 코딩테스트가 종료되었습니다. 이번 채용에서 지원자는 지원서 작성 시 아래와 같이 4가지 항목을 반드시 선택하도록 하였습니다.

  - 코딩테스트 참여 개발언어 항목에 cpp, java, python 중 하나를 선택해야 합니다.
  - 지원 직군 항목에 backend와 frontend 중 하나를 선택해야 합니다.
  - 지원 경력구분 항목에 junior와 senior 중 하나를 선택해야 합니다.
  - 선호하는 소울푸드로 chicken과 pizza 중 하나를 선택해야 합니다.

  인재영입팀에 근무하고 있는 `니니즈`는 코딩테스트 결과를 분석하여 채용에 참여한 개발팀들에 제공하기 위해 지원자들의 지원 조건을 선택하면 해당 조건에 맞는 지원자가 몇 명인 지 쉽게 알 수 있는 도구를 만들고 있습니다.
  예를 들어, 개발팀에서 궁금해하는 문의사항은 다음과 같은 형태가 될 수 있습니다.
  `코딩테스트에 java로 참여했으며, backend 직군을 선택했고, junior 경력이면서, 소울푸드로 pizza를 선택한 사람 중 코딩테스트 점수를 50점 이상 받은 지원자는 몇 명인가?`

  물론 이 외에도 각 개발팀의 상황에 따라 아래와 같이 다양한 형태의 문의가 있을 수 있습니다.

  - 코딩테스트에 python으로 참여했으며, frontend 직군을 선택했고, senior 경력이면서, 소울푸드로 chicken을 선택한 사람 중 코딩테스트 점수를 100점 이상 받은 사람은 모두 몇 명인가?
  - 코딩테스트에 cpp로 참여했으며, senior 경력이면서, 소울푸드로 pizza를 선택한 사람 중 코딩테스트 점수를 100점 이상 받은 사람은 모두 몇 명인가?
  - backend 직군을 선택했고, senior 경력이면서 코딩테스트 점수를 200점 이상 받은 사람은 모두 몇 명인가?
  - 소울푸드로 chicken을 선택한 사람 중 코딩테스트 점수를 250점 이상 받은 사람은 모두 몇 명인가?
  - 코딩테스트 점수를 150점 이상 받은 사람은 모두 몇 명인가?

  즉, 개발팀에서 궁금해하는 내용은 다음과 같은 형태를 갖습니다.

  ```
  * [조건]을 만족하는 사람 중 코딩테스트 점수를 X점 이상 받은 사람은 모두 몇 명인가?
  ```

## 문제

- 지원자가 지원서에 입력한 4가지의 정보와 획득한 코딩테스트 점수를 하나의 문자열로 구성한 값의 배열 info, 개발팀이 궁금해하는 문의조건이 문자열 형태로 담긴 배열 query가 매개변수로 주어질 때,
  각 문의조건에 해당하는 사람들의 숫자를 순서대로 배열에 담아 return 하도록 solution 함수를 완성해 주세요.

## 제한 사항

- info 배열의 크기는 1 이상 50,000 이하입니다.
- info 배열 각 원소의 값은 지원자가 지원서에 입력한 4가지 값과 코딩테스트 점수를 합친 "개발언어 직군 경력 소울푸드 점수" 형식입니다.
  - 개발언어는 cpp, java, python 중 하나입니다.
  - 직군은 backend, frontend 중 하나입니다.
  - 경력은 junior, senior 중 하나입니다.
  - 소울푸드는 chicken, pizza 중 하나입니다.
  - 점수는 코딩테스트 점수를 의미하며, 1 이상 100,000 이하인 자연수입니다.
  - 각 단어는 공백문자(스페이스 바) 하나로 구분되어 있습니다.
- query 배열의 크기는 1 이상 100,000 이하입니다.
- query의 각 문자열은 "[조건] X" 형식입니다.
  - [조건]은 "개발언어 and 직군 and 경력 and 소울푸드" 형식의 문자열입니다.
  - 언어는 cpp, java, python, - 중 하나입니다.
  - 직군은 backend, frontend, - 중 하나입니다.
  - 경력은 junior, senior, - 중 하나입니다.
  - 소울푸드는 chicken, pizza, - 중 하나입니다.
  - '-' 표시는 해당 조건을 고려하지 않겠다는 의미입니다.
  - X는 코딩테스트 점수를 의미하며 조건을 만족하는 사람 중 X점 이상 받은 사람은 모두 몇 명인 지를 의미합니다.
  - 각 단어는 공백문자(스페이스 바) 하나로 구분되어 있습니다.
  - 예를 들면, "cpp and - and senior and pizza 500"은 "cpp로 코딩테스트를 봤으며, 경력은 senior 이면서 소울푸드로 pizza를 선택한 지원자 중 코딩테스트 점수를 500점 이상 받은 사람은 모두 몇 명인가?"를 의미합니다.

## 입출력 예

##### **[입출력 예]**

| info                                                         | query                                                        | result        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------- |
| `["java backend junior pizza 150","python frontend senior chicken 210","python frontend senior chicken 150","cpp backend senior pizza 260","java backend junior chicken 80","python backend senior chicken 50"]` | `["java and backend and junior and pizza 100","python and frontend and senior and chicken 200","cpp and - and senior and pizza 250","- and backend and senior and - 150","- and - and - and chicken 100","- and - and - and - 150"]` | [1,1,1,1,2,4] |

##### **입출력 예에 대한 설명**

지원자 정보를 표로 나타내면 다음과 같습니다.

| 언어   | 직군     | 경력   | 소울 푸드 | 점수 |
| ------ | -------- | ------ | --------- | ---- |
| java   | backend  | junior | pizza     | 150  |
| python | frontend | senior | chicken   | 210  |
| python | frontend | senior | chicken   | 150  |
| cpp    | backend  | senior | pizza     | 260  |
| java   | backend  | junior | chicken   | 80   |
| python | backend  | senior | chicken   | 50   |

- `"java and backend and junior and pizza 100"` : java로 코딩테스트를 봤으며, backend 직군을 선택했고 junior 경력이면서 소울푸드로 pizza를 선택한 지원자 중 코딩테스트 점수를 100점 이상 받은 지원자는 1명 입니다.
- `"python and frontend and senior and chicken 200"` : python으로 코딩테스트를 봤으며, frontend 직군을 선택했고, senior 경력이면서 소울 푸드로 chicken을 선택한 지원자 중 코딩테스트 점수를 200점 이상 받은 지원자는 1명 입니다.
- `"cpp and - and senior and pizza 250"` : cpp로 코딩테스트를 봤으며, senior 경력이면서 소울푸드로 pizza를 선택한 지원자 중 코딩테스트 점수를 250점 이상 받은 지원자는 1명 입니다.
- `"- and backend and senior and - 150"` : backend 직군을 선택했고, senior 경력인 지원자 중 코딩테스트 점수를 150점 이상 받은 지원자는 1명 입니다.
- `"- and - and - and chicken 100"` : 소울푸드로 chicken을 선택한 지원자 중 코딩테스트 점수를 100점 이상을 받은 지원자는 2명 입니다.
- `"- and - and - and - 150"` : 코딩테스트 점수를 150점 이상 받은 지원자는 4명 입니다.

## 풀이 방법

- 나는 이 문제를 차근차근 한 단계씩 풀었던 기억이 난다. Python에서는 split과 같은 명령어로 간단하게 공백을 제거할 수 있는 기능을 나는 c++로 직접 구현했다.

- 첫번재 문자열 벡터인 info string은 공백을 기준으로 string을 잘라 v1 벡터에 저장하고, 두번째 문자열 벡터인 query string은 "and"를 기준으로 잘라 v2 벡터에 저장해줬다.

- 그렇게 각각 저장된 vector를 돌면서 서로 일치하는지 비교하고 일치하면 count를 하나 증가해주고, 혹시나 "-" 인경우에도 count를 더해줘야하므로 해당 경우도 추가해주었다.

- 그렇게 구해진 count를 answer 벡터에 push_back해주고, v1과 v2는 clear하여 새로 쓴다.

- 위의 과정을 반복하여, answer 벡터를 전부 출력한다.

---

하지만 이렇게 정확성은 다 통과했지만, 효율성 면에서 모두 시간 초과가 발생했다.
더 효율적인 알고리즘이 필요한 것 같다. 언제든지 지적은 환영합니다.

![image](https://user-images.githubusercontent.com/68185569/141248125-068d176b-519d-4f0d-b6a6-a98c32355d37.png)

---

```c++
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

using namespace std;

vector<string> info;
vector<string> query;
vector<string> v1;
vector<string> v2;

void removeSpace(string str) {
    istringstream ss1(str);
    string stringBuffer;

    string tmp_string;

    while (getline(ss1, stringBuffer, ' ')) {
        v1.push_back(stringBuffer);
    }
}

void removeAnd(string str) {
    istringstream ss1(str);
    string stringBuffer;

    string tmp_string;

    while (getline(ss1, stringBuffer, ' ')) {
        if (stringBuffer != "and") v2.push_back(stringBuffer);            
        else continue;
    }
}

vector<int> solution(vector<string> info, vector<string> query) {
    vector<int> answer;
    
    for (int i = 0; i < query.size(); i++) {
        int count = 0;
        for (int j = 0; j < info.size(); j++) {
            removeAnd(query[i]);
            removeSpace(info[j]);

            if (( (v1[0] == v2[0]) || (v2[0] == "-") )
                && ( (v1[1] == v2[1]) || (v2[1] =="-") )
                && ( (v1[2] == v2[2]) || (v2[2] =="-") )
                && ( (v1[3] == v2[3]) || (v2[3] =="-") )
                && ( (stoi(v1[4]) >= stoi(v2[4])) ) ) count++;

            v1.clear();
            v2.clear();
        }
        
        //cout << count << "\n";
        answer.push_back(count);
    }
    
    
    return answer;
}
```
