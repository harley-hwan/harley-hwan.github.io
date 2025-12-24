---
title: "(BOJ) 1031. 스타 대결 문제 풀이 (C++)"
description: "최대 유량을 활용한 사전순 최소 대진표 구성 방법"
date: 2025-04-09 10:00:00 +0900
categories: [Algorithm, Baekjoon]
tags: [c++, baekjoon, network-flow, maxflow, bfs, algorithm]
toc: false
---

# 스타 대결 (C++)

- 최초 작성일: 2025년 4월 9일 (수)

<br>

## 문제 설명
백준 1031번 **스타 대결** 문제는 두 팀(지민팀과 한수팀) 간의 1대1 경기 대진표를 구성하는 문제다. 각 팀원의 경기 수(필요한 매치 수)가 주어지며, 이를 만족하는 **N×M** 크기의 0-1 행렬(대진표)을 찾아야 한다. 행렬의 각 행은 지민팀 선수의 경기 목록, 각 열은 한수팀 선수의 경기 목록을 나타내며, 1은 해당 두 선수가 경기함을 의미한다. 모든 팀원은 **정해진 수의 경기**를 해야 하며, 같은 두 선수의 대결은 **한 번만** 가능하다. 가능한 대진표가 여러 개라면 **사전순(lexicographical order)**으로 가장 앞서는 것을 출력하고, 불가능하면 `-1`을 출력해야 한다.

## 접근 방법
이 문제는 주어진 각 행과 열의 합(경기 수) 조건을 만족하는 **0-1 행렬**을 구성하는 것으로 볼 수 있다. 이는 **이분 그래프의 각 정점의 차수가 주어진 경우에 그 그래프를 구성**하는 문제로 환원되며, 효율적인 해결을 위해 **네트워크 플로우(최대 유량)** 알고리즘을 사용한다. 핵심 접근 방식은 다음과 같다:

1. **네트워크 플로우 모델링**
지민팀의 각 선수와 한수팀의 각 선수를 이분 그래프의 좌우 정점으로 생각한다. 각 지민팀 선수 정점에서 **소스(source)**로 향하는 간선 용량을 해당 선수의 경기 수로 설정하고, 각 한수팀 선수 정점에서 **싱크(sink)**로 향하는 간선 용량을 그 선수의 경기 수로 설정한다. 지민팀 정점과 한수팀 정점 사이의 간선 용량은 **1**로 두어, 한 쌍의 선수는 최대 한 번의 경기를 할 수 있게 한다. 이렇게 하면 최대 유량 알고리즘을 통해 **각 선수의 경기 수 조건을 만족하는 경기 매칭**을 찾을 수 있다.

2. **최대 유량 계산**
에드몬즈-카프(Edmonds-Karp) 또는 디닉(Dinic) 알고리즘으로 위 그래프의 최대 유량을 계산한다. 만약 계산된 최대 유량이 **소스에서 흘려보낸 총 용량(= 모든 경기 수의 합)**과 일치하지 않으면, 주어진 조건을 만족하는 대진표는 존재하지 않으므로 `-1`을 출력한다. 최대 유량이 충분히 확보되었다면, 이는 하나의 가능한 경기 대진표에 해당한다.

3. **사전순 최소 대진표 구성**
얻어진 대진표(유량 결과)가 여러 경우 중 사전순 최소가 아닐 수 있으므로, 추가 단계를 통해 **사전순으로 가장 앞서는 형태로 조정**한다. 이를 위해 **현재 대진표에서 좌상단부터 차례로** 확인하면서, 각 매치(1로 표시된 자리)를 **필요하면 뒤쪽으로 미루는 작업**을 수행한다. 구체적인 방법은 다음과 같다:
   - 대진표를 첫 번째 행부터 검사하면서, 각 행의 왼쪽부터 오른쪽으로 이동한다. 현재 위치 `(i, j)`에 `1`(경기 매치)이 있다면, 이를 `0`으로 변경할 수 있는지 확인한다. **`0`으로 변경 가능**하다는 뜻은, 해당 경기를 삭제해도 남은 경기 수 요구를 만족할 수 있다는 의미다.
   - 이 확인은 **잔여 유량(residual flow)** 그래프를 이용하여 수행한다. `(i, j)` 위치의 경기를 제외하고도 지민팀 `i`와 한수팀 `j`의 남은 경기 수를 충족하는 **대체 경로**가 존재하는지 BFS로 탐색한다. 이때 **사전순 조건**을 유지하기 위해, BFS에서는 이미 결정된 이전 행보다 앞서는 선수나 더 이른 열로의 흐름은 고려하지 않는다. 예를 들어, 현재 처리 중인 지민팀 `i` 선수보다 번호가 작은 선수 쪽으로 흐르거나, 현재 열 `j`보다 작은 번호의 열로 가는 경로는 배제한다.
   - 만약 `(i, j)` 경기를 제거해도 대체 경로로 **모든 경기 수를 맞출 수 있다면**, 해당 자리를 `0`으로 확정하고 유량을 재조정한다. 반대로, 해당 경기가 반드시 필요하여 제거할 수 없는 경우에는 `1`을 유지한다. 이러한 과정을 모든 행과 열에 대해 수행하면, 가능한 범위에서 최대한 왼쪽 부분이 `0`으로 채워진, **사전순 가장 작은 대진표**가 완성된다.

4. **결과 출력**
위의 과정을 거쳐 얻은 최종 매치 대진표를 출력한다. 출력은 지민팀 선수 순서대로 각 행에 한수팀과의 경기 여부를 나타내는 `0`과 `1`의 문자열로 구성된다. 모든 조건을 만족하는 대진표가 없다면 `-1`을 출력한다.

## 시간 복잡도 분석
주어진 문제 조건에서 팀원 수는 최대 50명이므로, 플로우 네트워크의 정점 수는 약 100개 내외(소스/싱크 포함)이고 가능한 간선은 최대 2500개 수준이다. **최대 유량 알고리즘**의 시간 복잡도는 일반적으로 `O(V * E^2)` 혹은 `O(\sqrt{V} * E)` 정도이며, 본 문제의 그래프 규모에서는 충분히 효율적이다. 실제로 모든 선수의 경기 수 합을 `F`라고 할 때, 유량을 `F`만큼 보내야 하므로 에드몬즈-카프 알고리즘으로도 `O(F * E)` 정도의 수행이 이뤄진다. 최악의 경우 `F`는 2500(50×50) 이하이며, `E`도 약 2600 이하이므로 최대 유량 계산은 **수백만 회 이하의 연산**으로 완료될 수 있다. 

사전순 정렬을 위한 3단계 과정에서도, 각 `(i,j)` 위치에 대해 **BFS 탐색**을 한 번씩 수행한다. 위치의 개수가 최대 2500개이고, 한 번의 BFS가 `O(V+E)`에 수행되므로 이 또한 대략 수백만 회 이내의 연산량이다. 따라서 전체 알고리즘은 충분히 빠르며, **시간 복잡도 측면에서 안전한 해결 방법**이다. (단순한 Greedy로는 해결할 수 없으므로, 이러한 네트워크 유량 기반 접근이 필요하다.)

## C++ 전체 코드
코드 실행 시 입력에 맞춰 **정확히 N개의 행**으로 구성된 대진표를 출력하고, 조건을 만족하는 대진표가 없을 경우 `-1`을 출력한다.

```cpp
#include <bits/stdc++.h>
using namespace std;

const int MAXN = 105;  // 최대 노드 수 (N+M+2 정도)
int N, M;
int capacity[MAXN][MAXN];  // 용량
int flow[MAXN][MAXN];      // 흐른 유량 (양수: 정방향, 음수: 역방향)

// BFS로 최대 유량 증가 경로 찾기 (에드몬즈-카프 사용)
bool findAugmentingPath(int source, int sink, vector<int>& parent) {
    fill(parent.begin(), parent.end(), -1);
    parent[source] = source;
    queue<int> q;
    q.push(source);
    while (!q.empty() && parent[sink] == -1) {
        int u = q.front();
        q.pop();
        for (int v = 0; v <= N + M + 1; ++v) {
            // 남은 용량이 있고 방문하지 않은 노드
            if (parent[v] == -1 && capacity[u][v] - flow[u][v] > 0) {
                parent[v] = u;
                q.push(v);
                if (v == sink) break;
            }
        }
    }
    return parent[sink] != -1;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N >> M)) {
        return 0;
    }
    vector<int> rowMatches(N+1), colMatches(M+1);
    for (int i = 1; i <= N; ++i) {
        cin >> rowMatches[i];
    }
    for (int j = 1; j <= M; ++j) {
        cin >> colMatches[j];
    }

    // 소스, 싱크 노드 번호 설정
    int source = 0;
    int sink = N + M + 1;

    // 용량 초기화
    memset(capacity, 0, sizeof(capacity));
    memset(flow, 0, sizeof(flow));

    // 소스->지민팀 노드 용량 설정
    long long totalRow = 0, totalCol = 0;
    for (int i = 1; i <= N; ++i) {
        capacity[source][i] = rowMatches[i];
        totalRow += rowMatches[i];
    }
    // 한수팀 노드->싱크 용량 설정
    for (int j = 1; j <= M; ++j) {
        capacity[N + j][sink] = colMatches[j];
        totalCol += colMatches[j];
    }
    // 만약 요구 경기 수 총합이 다르면 불가능
    if (totalRow != totalCol) {
        cout << "-1";
        return 0;
    }
    // 지민팀->한수팀 노드 용량 1 (모든 가능한 대결 간선 추가)
    for (int i = 1; i <= N; ++i) {
        for (int j = 1; j <= M; ++j) {
            capacity[i][N + j] = 1;
        }
    }

    // 최대 유량 계산 (Edmonds-Karp)
    int maxFlow = 0;
    vector<int> parent(N + M + 2);
    while (findAugmentingPath(source, sink, parent)) {
        // 증강 경로가 발견되면 가능한 유량만큼(여기서는 1 단위씩) 보냄
        int increment = INT_MAX;
        for (int v = sink; v != source; v = parent[v]) {
            int u = parent[v];
            increment = min(increment, capacity[u][v] - flow[u][v]);
        }
        for (int v = sink; v != source; v = parent[v]) {
            int u = parent[v];
            flow[u][v] += increment;
            flow[v][u] -= increment;
        }
        maxFlow += increment;
    }

    // 최대 유량이 총 필요한 경기 수와 다르면 -1 출력 후 종료
    if (maxFlow != totalRow) {
        cout << "-1";
        return 0;
    }

    // 사전순으로 대진표 조정: 각 지민팀 i, 한수팀 j 순회
    for (int i = 1; i <= N; ++i) {
        for (int j = 1; j <= M; ++j) {
            int colNode = N + j;
            if (flow[i][colNode] == 1) {  // 현재 i번째 선수와 j번째 선수 간 경기 있음
                // 해당 경기(flow)를 제거해보고 대체 가능 여부 확인
                flow[source][i] -= 1;
                flow[i][source] += 1;
                flow[i][colNode] -= 1;
                flow[colNode][i] += 1;
                flow[colNode][sink] -= 1;
                flow[sink][colNode] += 1;
                // BFS로 i에서 sink까지 새로운 경로 찾기 (제한 조건 적용)
                vector<int> prev(N + M + 2, -1);
                queue<int>q;
                q.push(i);
                prev[i] = source;
                bool canReplace = false;
                while (!q.empty() && !canReplace) {
                    int u = q.front();
                    q.pop();
                    // 인접 노드 순회 (0~N+M+1 전체를 확인)
                    for (int v = 0; v <= N + M + 1; ++v) {
                        if (prev[v] != -1) continue;
                        // **제한 조건 적용** 
                        // 1) 시작 행 i로부터 이동할 때, j보다 작은(혹은 같은) 열은 제외
                        if (u == i && v <= N + j) continue;
                        // 2) 어떤 정점으로든 i보다 작은 번호의 지민팀 선수 노드는 방문 불가
                        if (v <= i && v != source) continue;
                        // 유량을 더 보낼 수 있는 간선인지 확인
                        if (capacity[u][v] - flow[u][v] > 0) {
                            prev[v] = u;
                            q.push(v);
                            if (v == sink) {  // sink에 도달하면 경로 찾음
                                canReplace = true;
                                break;
                            }
                        }
                    }
                }
                if (!canReplace) {
                    // 대체 경로 못 찾았으면 제거 실패 -> 원래 흐름 복구
                    flow[source][i] += 1;
                    flow[i][source] -= 1;
                    flow[i][colNode] += 1;
                    flow[colNode][i] -= 1;
                    flow[colNode][sink] += 1;
                    flow[sink][colNode] -= 1;
                } else {
                    // 대체 경로 찾았으면 경로 따라 유량 1 보충
                    int v = sink;
                    while (v != i) {
                        int u = prev[v];
                        flow[u][v] += 1;
                        flow[v][u] -= 1;
                        v = u;
                    }
                    // (i->colNode 경기는 0으로 유지되고, 유량은 다른 경로로 채워짐)
                }
            }
        }
    }

    // 최종 대진표 출력
    for (int i = 1; i <= N; ++i) {
        string line = "";
        for (int j = 1; j <= M; ++j) {
            int colNode = N + j;
            line.push_back(flow[i][colNode] > 0 ? '1' : '0');
        }
        cout << line << "\n";
    }

    return 0;
}
``` 

각 팀원의 경기 수 제약을 만족하면서도 사전순으로 가장 이른 대진표를 생성하기 위해, 위 코드는 **최대 유량을 통한 매칭**과 **잔여 유량 그래프를 통한 사전순 조정** 기법을 활용한다. 이러한 접근은 **필요한 경우에만** 경기를 왼쪽에서 오른쪽으로 미루므로 불필요한 연산을 최소화하고, 결과적으로 요구한 시간 내에 효율적으로 동작한다.
