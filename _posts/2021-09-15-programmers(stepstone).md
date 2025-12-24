---
title: Programmers 징검다리
description: Programmers KAKAO 개발자 겨울 인턴십 (c++)
date: 2021-09-15 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, kakao, algorithm, c++]
---

<https://programmers.co.kr/learn/courses/30/lessons/64062>


![image](https://user-images.githubusercontent.com/68185569/133344222-724d8ddc-01e5-4bfd-9813-fe440ba7ad10.png)

이 문제는 각각의 징검다리마다 밟을 수 있는 횟수가 주어지며, 한 번에 건너뛸 수 있는 징검다리 수를 k로 주어, 0을 가진 징검다리가 연속으로 k개를 넘어서면 그때까지 개울을 건너간 친구들의 수를 구하는 문제이다.

그림을 보고 엄청 단순하게 완전 탐색을 하면 되겠다 생각하여. stones의 사이즈만큼 계속 돌며 밟은 디딤돌이 0이 아니면 계속 -1을 해주어 밟았다라는 표시를 해주고, 0 이하(음수여도 0인 것과 동일)인 부분을 찾으면 그때부터 징검다리 간격을 카운팅하고, 다시 연속되지 않으면 0으로 초기화해준다. 이걸 쭉 반복하면 원하는 답을 얻을 수 있지만, 시간 초과로 풀이에 실패하게 된다.

---
~~~c++
// 완전 탐색 (시간 초과)

int solution(vector<int> stones, long long k) {
    long long answer = 0;
    int dif = 0;
    while(1){
        for (int i = 0; i < stones.size(); i++) {
            if (dif >= k) return answer;
            if (stones[i] == 0) {
                dif++;
                //cout << "dif: " << dif << endl;
                continue;
            }
            stones[i]--;
            dif = 0;
            //cout << "stones[" << i << "]: " << stones[i] << endl;
        }
        answer++;
    }
    return answer;
}
~~~

---

그래서 시간을 줄이기 위해 이분 탐색을 적용시켜주어 해결할 수 있었다.


~~~c++
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#define endl '\n'

using namespace std;

bool bs(vector<int> stones, int mid, int k) {
    int cnt = 0;

    // stones 순회
    for (int i = 0; i < stones.size(); i++) {
        // 결과가 0이하면 카운트
        if (stones[i] - mid <= 0)   cnt++;

        // 0이 아니면 다시 카운트 0으로 초기화하고 다시 연속된 다리 개수 카운트.
        else    cnt = 0;

        if (cnt >= k) return true;
    }
    return false;
}

int solution(vector<int> stones, int k) {
    int answer = 0;
    // start = 1, end = 배열에서 max값
    int start = 1, end = *max_element(stones.begin(), stones.end());

    while(start <= end) {   // 이분 탐색 진행
        int mid = (start + end) / 2;

        if (bs(stones, mid, k))     end = mid - 1;
        else                        start = mid + 1;
    }
    return start;   // 징검다리를 건널 수 있는 사람의 수
}
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    vector<int> stones = {2, 4, 5, 3, 2, 1, 4, 2, 5, 1};
    int k = 3;

    cout << solution(stones, k) << endl;

    return 0;
}
~~~
