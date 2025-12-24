---
title: Programmers 크레인 인형뽑기 게임
description: 2019 카카오 개발자 겨울 인턴십
date: 2021-10-21 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 크레인 인형뽑기 게임

- 최초 작성일: 2021년 10월 21일(목)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/64061>

## 풀이 방법 1

- moves 벡터는 어떤 인덱스의 가장 위에 위치한 인형을 하나씩 꺼낼지를 나타낸다.
- 그러므로, board의 size만큼 돌며 해당 인덱스의 가장 위 인형을 하나씩 꺼내며 지워주고, 새로운 빈 벡터에 하나씩 넣어준다.
- 그러던 중, 새로운 벡터에 연속으로 같은 숫자의 인형이 쌓이면 pop_back()을 통해 제거해주고, answer를 2 증가한다. 지워진 숫자를 제외한 마지막 숫자를 before로 지정해주어, 다음 번에 같은 숫자가 나왔을 시 지울 수 있도록 해준다.
- 예를 들어, 4 3 1 1 3 2 3 4 순으로 인형을 꺼냈다고 했을 때, 1 1 을 먼저 지워주면 4 3 3 2 3 4 순서가 되므로, 또 3 3을 지워줘야 한다. 
- 그렇게 마지막 answer를 출력해준다.

---

```c++
#include <iostream>
#include <string>
#include <vector>

using namespace std;

int solution(vector<vector<int>> board, vector<int> moves) {
    int answer = 0;
    int before = 0;
    vector<int> v;

    for (int i = 0; i < moves.size(); i++) {
        for (int j = 0; j < board.size(); j++) {
            if (board[j][moves[i]-1] != 0) {
            
                if (before == board[j][moves[i]-1]) {
                    v.pop_back();

                    answer = answer + 2;
                    before = v.back();
                    board[j][moves[i]-1] = 0;
                    break;
                }
                v.push_back(board[j][moves[i]-1]);
                before = board[j][moves[i]-1];

                board[j][moves[i]-1] = 0;
                break;
            }
        }
    }
    return answer;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    vector<vector<int>> board = { {0, 0, 0, 0, 0}, {0, 0, 1, 0, 3}, {0, 2, 5, 0, 1}, {4, 2, 4, 4, 2}, {3, 5, 1, 3, 1} };
    vector<int> moves = {1, 5, 3, 5, 1, 2, 1, 4};

    cout << solution(board, moves) << "\n";

    return 0;
}

```

---

