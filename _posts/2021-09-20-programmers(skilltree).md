---
title: Programmers 스킬트리
description: "Summer, Winter Coding(~2018) (c++)"
date: 2021-09-20 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 스킬트리

- 최초 작성일: 2021년 9월 20일(월)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/49993>

## 문제 설명
![image](https://user-images.githubusercontent.com/68185569/133917563-09ad9064-6a6b-4035-964c-af102048d8c7.png)

- 선행 스킬이란 어떤 스킬을 배우기 전에 먼저 배워야 하는 스킬을 뜻합니다.
- 예를 들어 선행 스킬 순서가 `스파크 → 라이트닝 볼트 → 썬더`일때, 썬더를 배우려면 먼저 라이트닝 볼트를 배워야 하고, 라이트닝 볼트를 배우려면 먼저 스파크를 배워야 합니다.
- 위 순서에 없는 다른 스킬(힐링 등)은 순서에 상관없이 배울 수 있습니다. 따라서 `스파크 → 힐링 → 라이트닝 볼트 → 썬더`와 같은 스킬트리는 가능하지만, `썬더 → 스파크`나 `라이트닝 볼트 → 스파크 → 힐링 → 썬더`와 같은 스킬트리는 불가능합니다.
- 선행 스킬 순서 skill과 유저들이 만든 스킬트리[1](https://programmers.co.kr/learn/courses/30/lessons/49993#fn1)를 담은 배열 skill_trees가 매개변수로 주어질 때, 가능한 스킬트리 개수를 return 하는 solution 함수를 작성해주세요.

## 제한 조건
- 스킬은 알파벳 대문자로 표기하며, 모든 문자열은 알파벳 대문자로만 이루어져 있습니다.
- 스킬 순서와 스킬트리는 문자열로 표기합니다.
  - 예를 들어, `C → B → D` 라면 "CBD"로 표기합니다
- 선행 스킬 순서 skill의 길이는 1 이상 26 이하이며, 스킬은 중복해 주어지지 않습니다.
- skill_trees는 길이 1 이상 20 이하인 배열입니다.
- skill_trees의 원소는 스킬을 나타내는 문자열입니다.
  - skill_trees의 원소는 길이가 2 이상 26 이하인 문자열이며, 스킬이 중복해 주어지지 않습니다.

## 입출력 예
![image](https://user-images.githubusercontent.com/68185569/133933238-8ea1b1a2-c89d-4b93-8d8c-40cc419b32b7.png)

## 입출력 예 설명

- "BACDE": B 스킬을 배우기 전에 C 스킬을 먼저 배워야 합니다. 불가능한 스킬트립니다.
- "CBADF": 가능한 스킬트리입니다.
- "AECB": 가능한 스킬트리입니다.
- "BDA": B 스킬을 배우기 전에 C 스킬을 먼저 배워야 합니다. 불가능한 스킬트리입니다.

## 풀이 방법

- 이 문제는, 만약 string으로 주어지는 입력인 skill이 CBD라면 스킬 순서가 무조건 C->B->D 순이어야 하므로, 일단 가장 처음이 C가 나와야 한다. C가 없으면 C->D 순서가 맞아도 틀린 것이 된다.
- 그렇기 때문에, 두번째로 주어지는 skill_trees 입력 벡터에서 CBD를 제외한 나머지 skill은 논외이기 때문에, 나 지워줘도 무방하다.
- 예를 들면, 영어 문장에서 주어 + 동사 + 목적어가 나와야하는데, 중간 중간에 수식어가 들어간들 생략해줘도 무방한 것과 같은 원리이다.
-  그런 후, 참 혹은 거짓만을 나타낼 수 있는, bool 자료형의 ans를 하나 우선 true로 선언해주고, 입력 스트링 skill인 CBD와 앞에서부터 일치하는지 확인하며 일치하면 출력값(answer)을 1 증가해주고, 틀리면 false를 선언해주고 바로 빠져나와 다음 skill_trees를 확인하는 것을 반복한다.

```c++
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

int solution(string skill, vector<string> skill_trees) {
    int answer = 0;

    for (int k = 0; k < skill_trees.size(); k++) {
        string str;
        for (int i = 0; i < skill_trees[k].length(); i++) {
            for (int j = 0; j < skill.length(); j++) {
                if (skill[j] == skill_trees[k][i]) {
                    str += skill_trees[k][i];
                }
            }
        }
        bool ans = true;

        for (int i = 0; i < str.length(); i++) {
            if (str[i] != skill[i]) {
                ans = false;
                break;
            }
        }
        if (ans) answer++;
    }   
    return answer;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    string skill = "CBD";
    vector<string >skill_trees = {"BACDE", "CBADF", "AECB", "BDA"};

    cout << solution(skill, skill_trees) << "\n";
    return 0;
}
```

