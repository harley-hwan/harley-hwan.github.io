---
title: 5-Queens Problem 머신러닝
description: 유전 알고리즘 (Genetic Algorithm)
date: 2021-10-20 10:00:00 +0900
categories: [Project]
tags: [machinelearning, 머신러닝, algorithm, genetic]
---



# 5-Queens Problem (Genetic Algorithm)

- 최초 작성일: 2021년 10월 20일(수)

## 목차



## 문제 설명

N-Queens Problem에서 n의 값을 5로 하고

(즉, 5x5 체스판에 5개의 퀸(상하좌우 대각선의 말들을 잡아먹음)을

서로 잡아먹지 않는 선에서 최대로 배치할 수 있는 방법을 구하는 문제)

Genetic Algorithm(유전 알고리즘)으로 풀어보자.

﻿


## 1) Chromosome design (염색체 디자인)

![image](https://user-images.githubusercontent.com/68185569/138053274-7e2a7fda-5ac3-48cb-91d6-c03583440d4a.png)


체스판 위에 놓인 퀸들의 형태를 표현한 모습을 구현해야 하는데, Vertical(세로)로 퀸이 하나만 반드시 존재하므로 체스판 위에 놓인 퀸의 수는 5개가 됨을 보장한다.

위의 그림은 체스판에 놓인 퀸의 위치를 표시한 것이다.

﻿

## 2) Initialization (초기화)

np.array([1, 2, 3, 4, 5] 와 같이

한 줄이 0~4까지 각각 5개의 y좌표에 Queen이 놓인 보드판을 랜덤으로 생성하여 반환한다.
인간의 인위적인 판단이나 개입으로 인해 모델의 성능을 정확하게 측정할 수 없게 되는 것을 방지하기 위해 랜덤으로 수행했다.


그 후 위의 작업을 100번 반복 수행한다.

아래의 실행 결과값은 100개의 결과값 중에 10개만을 test삼아 출력해본 것이다.

![image](https://user-images.githubusercontent.com/68185569/138053350-707e1f4b-30d3-4879-92e7-cc78cb2fe6d9.png)

﻿
 
## 3) Fitness (적합도)



나는 중복 체크의 기준점이 되는 퀸이 죽는 상황인지 아닌지를 판별하도록 코드를 짰다.
Queens-Problem의 조건 상 상하좌우 대각선으로 잡아먹는다는 Queen의 특성을 고려하여 대각선, 대각선 반대방향, horizon 방향에 대한 중복을 체크한다.



이때, vertical 방향에 대한 중복 체크는 불필요하다.
왜냐하면 Chromosome design에서도 설명했다시피
각 리스트마다 적힌 숫자는 x축 방향으로 왼쪽부터 0, 1, 2, 3, 4
각각 index에서 y축 방향으로 Queen의 위치를 숫자로 표시한 것이기 때문에
vertical 적으로 한 줄에는 Queen이 하나만 존재한다.



그렇게 체크된 중복들을 다 더해주고 중복 체크를 3번 진행을 하는데 자기 자신에 대한 중복이 일어나므로 3번의 체크된 중복을 제외해준다.

(처음에 -3을 안해줬는데 결과값이 죽은 퀸의 수치가 15와 같이 과장된 수치를 산출했는데 그것을 보고 디버깅을 하였다.)



이 과정에서 중복 체크가 1번이라도 일어났다면 자기 자신이 죽는 퀸이 된다.

그렇게 됐을 때 퀸이 죽은 횟수를 1을 더해준다.

그렇게 더해진 합계로 array를 만들어주는데, 이때 array 내에 index, 각 체스판 정보에 대한 list, 죽은 퀸의 개수를 하나로 합쳐 array로 저장했다.



아래의 실행 결과값은 임의로 10개만 보여준 것인데

index값인 0~9를 같이 저장해서 출력한 이유는 나중에 Selection을 할 건데 그때 잘 정렬이 되었는지 확인하기 위함이다.

![image](https://user-images.githubusercontent.com/68185569/138057062-a9af474d-9255-41cd-89ec-32efa30bf6f5.png)


﻿

## 4) Selection



이 단계를 위해서 Fitness 단계를 거친 것인데,

간단히 말하면 좋은 결과를 가진 것들을 선별해서 저장한다.



이때 Selected rate 선별율은 10%로 한다.

즉, 죽은 퀸의 개수를 기준으로 오름차순으로 sort 해서 상위 10%만을 선별해 저장하고 나머지를 버린다는 것이다.



결과적으로, 100개 중의 10%를 고르는 것이니 아래의 실행 결과값과 같이 10개가 저장이 된다.



그렇게 선별된 리스트들이 아래의 실행 결과값과 같고 이때는 index 값과 죽은 퀸의 수의 정보의 출력은 불필요하므로 list들만 array로 저장한다.

![image](https://user-images.githubusercontent.com/68185569/138053561-d302225c-aecb-483e-9285-5cb75405a5b3.png)

![image](https://user-images.githubusercontent.com/68185569/138053585-9e9a0aca-30d8-4cea-a351-b27fde577fb2.png)


Index값이 무작위로 섞인 모습이므로 죽은 퀸 수를 기준으로 잘 정렬 됐음을 확인할 수 있다.

(해당 출력 화면을 위해 다시 실행하여 데이터 값이 다르므로 참고만 한다.)

﻿

## 5) Crossover



간단히 말하면 절반을 쪼개서 쪼갠 것들끼리 재조합을 한다는 것이다.

좋은 자질들을 보존하면서 그 그룹 내에서 더 나은 결과값을 산출하기 위해서 교차를 시키는 작업을 하였다.

랜덤으로 index값을 구한 뒤 해당 index들의 두 개의 list를 그림과 같이 절반을 서로 바꿔 재조합 한다.

이렇게 재조합한 것들을 각각 10개씩 만들어 100개의 list들을 만들어 저장한다.

![image](https://user-images.githubusercontent.com/68185569/138053671-ca809040-cf74-44c1-a95d-dec4fb287db8.png)

(위의 그림 설명은 실제로 바뀐 것이 아니라 설명을 위해 나타낸 것이다.)

아래의 실행 결과값도 100개의 리스트를 만들었으나 임의로 10개만 출력해본 것이다.

![image](https://user-images.githubusercontent.com/68185569/138053704-957de6dd-4448-426e-afc5-f0ac87d20610.png)


﻿

## 6) Mutation (돌연변이 생성) & Update generation



위의 작업들을 통해 더 나은 값들의 집합들을 모아 해를 구할 수 있지만 그렇게 구해진 값들은 100% 완벽하다고 할 수 있는 해들이 아니기 때문에 위의 단계에서 생성된 100개의 리스트들에서 무작위로 선별된 리스트들의 숫자들을 바꾸어 돌연변이들을 만들어낸다.



이때 돌연변이 생성율(mutation rate)은 10%로 해보았다.

(50%로도 해보았는데 죽은 퀸의 수가 0으로 수렴하는 데에 너무 오랜 시간이 걸려 비효율적이었다.)


실제 실행 결과값들은 아래와 같이 출력이 되었는데,랜덤으로 array에서의 인덱스를 골라 해당 인덱스의 리스트에서 또 그 리스트의 인덱스를 랜덤으로 해당 인덱스에 랜덤으로 0~4 중의 숫자를 교체해서 넣는다.

![image](https://user-images.githubusercontent.com/68185569/138053795-6eefbd75-3aa9-49dc-a7e2-e3a2840f8f0b.png)

![image](https://user-images.githubusercontent.com/68185569/138053825-219612be-0ae1-4308-b6a1-d60926d09943.png)

![image](https://user-images.githubusercontent.com/68185569/138053848-776f1cfa-edb6-440f-ac03-41414a334527.png)

﻿
 
## 7) Go back to 3)

새로운 세대에 대한 Fitness를 다시 시행하고 Selection 하는 등의 과정을 반복한다.

이때 내가 원하는 target value에 도달할 때까지 반복 시행한다.

Target value를 0으로 설정을 했는데 모든 것들이 0이 되는 경우는 없었기 때문에 Target value를 특정 값으로 정하거나 반복 시행 시간을 제한해두어 종료하고 중간 결과를 반환하도록 했다.



﻿

## ⩥ 결론


Genetic Algorithm의 목적은 유일한 해를 찾기 보다는 적합한 값들을 찾는 것을 목적으로 하는 것이기 때문에 매 실행 때마다 모델이 적합하다고 생각하는 값들은 항상 변할 수밖에 없다.

이때 결과값은 시작점이 어디냐에 따라 큰 영향을 받는다.



Genetic Algorithm은 Local Search Algorithms처럼 탐욕적 알고리즘의 일부이므로 그때 그때 괜찮은 해를 선택하기 때문에 global maximum에 도달하지 못하고 local maximum에 도달하는 경우가 있다.

이때 global maximum과 local maximum은 여러 개가 존재할 수 있다.

![image](https://user-images.githubusercontent.com/68185569/138053904-8043566a-6261-4bba-a6c8-b577ad568b70.png)




기존의 내가 배웠던 알고리즘들은 정확하게 풀이방법을 컴퓨터에게 명령을 해야했다.

하지만 Genetic Algorithm(유전 알고리즘)은 해당 문제에 대해서 특정한 지식을 요구하진 않고 조건과 적합도(평가 지표)만 정해주기만 하면 모델이 알아서 답을 산출한다는 것이 특징이다.


예를 들어, 체스라는 게임을 플레이한다고 했을 때 단지 플레이 방법과 승리 조건을 알려주기만 해도 체스를 둘 수 있다는 것이다.


아래의 그림과 같이 Iasi에서 Fegaras로 가는 최적의 해를 구한다고 가정했을 때, 그리디 알고리즘의 일부인 Genetic 알고리즘을 이용한다했을 때 Selection을 통해 g(n) 즉, path cose from the start node to n 을 고려했을 때 Neamt으로 갈 것인데 막다른 길이라 계속 무한 루프에 갇혀 해를 구하지 끝까지 못 구할 수 있다.

하지만 그 이후에 Mutation작업을 통해 일부를 반대 방향인 Vaslui로 가는 것들을 만들어 여러 가지의 경우의 수를 수없이 반복해봐서 목적지까지 도달하는 적합한 해들을 산출할 수 있다.


![image](https://user-images.githubusercontent.com/68185569/138053937-c035d185-f673-4882-bcaf-634e662b5576.png)

﻿

### <실제 코드 실행 결과값 (1)>



아래의 실행 결과값들은 선별하는 비율(selected_rate)을 10% (0.1)로 했을 때의 결과이다.

아래와 같이 큰 폭의 변동을 보이는 이유는 Mutation의 폭이 크게 나타날 가능성이 있을 것이고 선별하는 비율을 비교적 적게 해서 살아 남는 경우의 다양성이 떨어지기 때문에 나타났을 가능성으로 보인다.

출력되는 Array 값들은 어느정도 수렴해서 비슷한 값들을 가지는 것을 확인할 수 있는데, Genetic 알고리즘 특성상 유일한 해를 찾아내는 것이 아니라 적합한 해들을 산출하는 것이 목적인 만큼 문제의 해답에 해당되는 해를 포함한 여러가지 가짓수를 보여준다.

그리고 2번의 시도가 각각 다른 산출값을 보인다. (매 시도마다 다른 값들을 산출)

![image](https://user-images.githubusercontent.com/68185569/138053992-663c1315-0faf-474c-b492-4e10a30a8848.png)

﻿

### <실제 코드 실행 결과값 (2)>



아래의 실행 결과값은 선별하는 비율(selected_rate)를 50% (0.5)로 했을 때의 결과이다.

1번 실행 결과에 비해 비교적으로 더 적게 변동하는 폭을 확인할 수 있는데 그 이유는 Selection 단계에서 절반을 남김으로써 더욱 더 다양성을 가지므로 그것을 섞었을 때 적합한 해를 구하기까지 적은 시간이 소요된 것으로 여겨진다.



출력되는 Array 값들 또한 1번 실행 결과에 비해 더욱 일관된 산출값을 보이는 것을 볼 수 있다.

마찬가지로 2번의 시도가 각각 다른 값들을 산출한다.



결과적으로 Genetic 알고리즘의 모든 경우의 수를 경험해보고 그 과정으로 인해 적합한 해를 찾아간다는 특성상 더욱 많은 다양성을 두면 적합한 해를 찾기 더 쉬운 모습을 확인할 수 있었다

![image](https://user-images.githubusercontent.com/68185569/138061485-d708acdd-6e2a-4070-8e48-f223261c9ffa.png)

    
﻿
    


```python
import matplotlib.pyplot as plt
import numpy as np
import random
import time

# 1 chromosome design
# np.array([1,2,3,4,5])
# 총 가짓수 5^5 => 25 125 625 3125가지

def initialization(n = 100):
    '''
    한 줄이 0~4까지 각각 5개의 Y좌표에 퀸이 놓인 보드판을 랜덤으로 생성하여 반환
    '''
    return np.random.randint(low = 0, high =4, size = (n,5))
test_boards = initialization(1)
print("< Chromosome >")
print(test_boards)
print("\n\n")
np.random.randint(low = 1, high =5, size = (100,5))[:10]

test_boards = initialization()
print("< Initialization >")
print(test_boards[:10])
print("\n\n")


#3) Fitness evaluation

def how_many_queens(chess_boards):
    result = []
    for n, chess_board in enumerate(chess_boards):
        nqueen = 0.0
        for x , y in enumerate(chess_board):
            test_arr_map = np.array([[4,3,2,1,0,-1,-2,-3,-4],[-4,-3,-2,-1,0,1,2,3,4]])[:,4-x:9-x] + y
            nplus = test_arr_map[0] == chess_board      # 대각선 중복 체크
            nminus = test_arr_map[1] == chess_board     # 대각선 반대방향 중복 체크
            n_hor = y == chess_board                    # horizon 방향에 대한 중복 체크
                        # vertical 은 중복 체크가 필요없음 -> vertical적으로 한 줄에는 하나만 존재함으로 설정했기 때문
            npm = (sum(nplus)+sum(nminus)+sum(n_hor)-3) # for문 반복시 자기 자신에 대한 죽음을 제외시킴 
            if npm > 0:
                nqueen += 1.0
        result.append((n, chess_board.tolist(), nqueen))
    dtype = [('index', int),('chess_board', list),('fit', float)]
    result_array = np.array(result, dtype = dtype) 
    
    return result_array

test_fitness= how_many_queens(test_boards)
print("< Fitness >")
print(test_fitness[:10])
print("\n\n")

#4) Selection
def select(fitness, selected_rate=0.1):
    n_survived = int(len(fitness)*selected_rate)    # n_survived = 10 ( 100 x 10% )
    survived_array = np.sort(fitness, order = 'fit')[:n_survived]
    return survived_array['chess_board']

test_survived = select(test_fitness)
print("< Selection >")
print(test_survived)
print("\n\n")

#5) Crossover

def crossover(survived, selected_rate=0.1):
    boards_a = np.random.randint(len(survived), size=int(((len(survived)/selected_rate))/2))
    boards_b = np.random.randint(len(survived), size=int(((len(survived)/selected_rate))/2))
    result = []
    for (board_a_index, board_b_index) in zip(boards_a, boards_b):
        copy_a = survived[board_a_index]
        copy_b = survived[board_b_index]
        copy_a[:2]= copy_b[:2]
        copy_b[3:]= survived[board_a_index][3:]

        result.append(copy_a)
        result.append(copy_b)
    return result

test_new_seeds = crossover(test_survived)
print("< Crossover >")
print(test_new_seeds[:10])
print("\n\n")


# 6) Mutation & 7) Update generation

def mutate(seeds, mutation_rate = 0.1):
    for n in range(int(len(seeds)*mutation_rate)):
        board_index = random.randint(0,len(seeds)-1)
        x_index = random.randint(0,4)
        seeds[board_index][x_index] = random.randint(0,4)
    return np.array(seeds)

test_new_generation = mutate(test_new_seeds)
print("< Mutation >")
print(test_new_generation[:10])
print("\n\n")

#8) Go back to 3)
def n_queens(chess_boards, target_value = 0,selected_rate = 0.5, mutation_rate=0.1):
    generation_now = chess_boards
    generation = 1
    fit_score = 5.0
    fit_scores = []
    stime = time.time()
    while fit_score > target_value:
        fitness = how_many_queens(generation_now)
        survived = select(fitness ,selected_rate = selected_rate)
        new_seeds = crossover(survived,selected_rate = selected_rate)
        generation_now = mutate(new_seeds, mutation_rate=mutation_rate)
        fit_score = fitness['fit'].mean()
        fit_scores.append(fit_score)
        
        # 5초가 지나면 종료
        if (time.time() -stime) > 5:
            break
    return generation_now, fit_scores, (time.time() - stime)


#그래프로 보여주기 위함

chess_boards = initialization(n = 100)
result_generation, fit_scores, spend_time = n_queens(chess_boards)
plt.plot(fit_scores)
plt.show()
print("< result1 >")
print(result_generation[::10]) # 결과값 10개만 출력
print("\n\n")


# 실행할 때마다 값이 다르게 나온다는걸 보여줌

chess_boards = initialization(n = 100)
result_generation2, fit_scores, spend_time = n_queens(chess_boards)
plt.plot(fit_scores)
plt.show()
print("< result2 >")
print(result_generation2[::10]) # 결과값 10개만 출력
```

﻿
