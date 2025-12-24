---
title: EQTransformer model
description: Earthquake transformer - deap learning model
date: 2021-09-19 10:00:00 +0900
categories: [Project]
tags: [eqtransformer, deap learning, machine learning, python, big data science]
---


# EQTransformer 코드 실행 및 설명
- 최초 작성일: 2021년 7월 29일(목)
- 논문: <https://rdcu.be/b58li>
- github 주소: <https://github.com/smousavi05/EQTransformer>


## 목차


## 코드 실행
- colab 위치: <https://colab.research.google.com/drive/1hmBsEhi4hozDsI6aCdfL1t6FBR69WXRc?usp=sharing>
- colab 런타임 gpu 설정

## 논문 설명
### 소개
- 본 논문은 full wavelength 지진파에서 지진검출과 P/S파 검출을 동시에 학습하는 딥러닝 모델을 hierarchical attention 기법을 이용하여 설계하였고, 이를 통해 지진검출과 P/S파 검출 정확도가 높은 예측 모델을 만들었다.  모델 학습에는 STEAD(STanford Earthquake Dataset)을 사용하여 학습을 했다. STEAD 데이터는 전세계 여러 지역의 seismic signal 데이터로 해당 지진 발생 여부도 라벨링 되어 있는 데이터이다. 모델 검증에는 STEAD test 데이터도 사용을 했고, 2000년 일본의 Tottori 지역의 데이터로도 모델 성능을 테스트했다. 일본 Tottori 데이터로 모델을 테스트한 이유는 STEAD는 전세계적인 지진파 데이터를 포함하고 있지만, 일본 데이터가 없어, 학습에 등장하지 않은 데이터에서도 모델이 정상 동작하는지 테스트가 가능하기 때문이다. 이렇게 디자인되고, 학습된 모델은 앞서 다른 논문들에서 제시된 예측 모델들 보다 정확도가 뛰어났다. 그리고 본 논문에서 제안한 모델은 지진 검출과 S/V파 검출을 동시에 할 수 있다는 장점도 있다.

### 목적
- 지진 검출 task
    - 지진검출은 여러 지진 관측 센서들로부터 노이즈 값과 함께 수집된 많은 seismic signal 로부터 지진인지 아닌지를 판단하는 task이다.
- P/S파 검출 (phase picking) task
    - P/S파 검출은 지진이 발새한 지역을 추측하기 위해 지진파로부터 S/V파를 판단하여 task이다. 
- 모델 설계 아이디어
    - 이전 모델들은 지진파 검출과 P/S파 검출을 각기 다른 네트워크를 통해 수행을 했지만, 본 논문의 모델은 1개의 모델로 2가지 task를 한번에 수행한다.
    - 그 이유는 실제로 사람이 일을 할 때, 전체 데이터를 보고 그리고 phase를 분석하여 어떤 부분이 P/S파인지 분서한다. 이것은 두 task가 실제로는 연관이 있다는 것을 의미한다. 그래서 본 논문은 이 점을 착안하여, 인간이 실제로 수행하는 방식을 모방하는 딥러닝 모델을 만들었다. 본 논문에 설계한 딥러닝 모델은 encoder를 통해 전체 데이터로부터 context 정보를 얻은 후, decoder에서 세부 task를 진행하는 방식으로 모델을 설계하였다. 상세한 모델 구조는 아래와 같다.

### 모델
- 구조
    - 모델은 하나의 encode와 세개의 decoder로 구성이 되어있다. encoder는 전체 인풋에서 지진과 관련된 feature를 강조시키는 역할을 하고, decoder는 지진 검출, P파 검출, S파 검출 등 특정 task를 수행한다. 네트워크 구조 설계는 인간이 해당 일을 수행하는 것을 모방하여 설계하였고, 설계한 네트워크의 parameter 최적화 작업은 계속 실험을 하면서 최적화해 나갔다.
    - one deep encoder
        - encoder는 시간에따른 seismic signal을 인풋으로 받아, high-level representation과 context 정보를 생성해낸다. 들어오는 인풋의 길이가 길어지면 메모리가 많이 필요지므로 Conv 1D와 maxpooling을 이용하여 down sampling 해준다. 그리고 이렇게 down sampling 된 feature는 Res CNN과 LSTM을 통해 transform된 이후, encoder의 마지막에 위치한 global attention에 의해 지진과 연관된 feature가 커지게 된다.
        ![](https://i.imgur.com/dv3kc10.png)
        - 위 이미지는 encoder의 마지막 global attention을 시각화한 것인데, 지진과 관련된 부분만 attention이 수행된 것을 볼 수 있다.
    - three decoders
        - 먼저 첫번째 decoder는 encoder의 입력 값을 받아, 지진 발생확률을 계산한다. 해당 decoder는 Conv 1D를 이용하여 down sampling된 데이터를 up sampling하고, sigmoid를 통해 결과 값을 도출한다.
        - 남은 2가지 decoder는 특정구간에서 P/S파일 확률을 계산한다. 네트워크 구성은 처음에는 lstm과 local attention을 이용하여 global attention보다 더 지엽적인 특징을 추출한다.
        ![](https://i.imgur.com/dPpiVBj.png)
        - 위 이미지는 decoder의 local attention을 시각화한 것이다. 첫 번째는 P파 검출 task에서 수행한 local attention인데 P파 검출에 필요한 부분에 attention이 수행된 것을 볼 수 있다. 두번째 이미지는 S파 검출 task에서 수행한 local attentiond으로 P파와는 또다르게 S파에 주요하게 사용될 feature에 대해서 attention을 수행하는 것을 볼 수 있다.그리고 이렇게 local attention을 거치고 나면 Conv 1D로 up sampling을 진행하게 되고, 최종적으로 sigmoid를 거쳐 최종 결과 값을 도출한다.
    - 그리고 모델의 각 block에 residual connection network-in-network 기법을 사용하여, 더 깊은 네트워크를 쌓을 수 있었다. 최종적으로 56개의 레이어와 약 37만 2천개의 파라미터를 가지는 딥러닝 모델을 설계했다.
    ![](https://i.imgur.com/fimHmto.png)

### 학습 방식
- convolution이나 LSTM 등의 초기값은 Xavier normal initialzer를 사용해서 세팅하고, bias 값은 0으로 초기값을 세팅한다. 그리고 학습 과정의 learning rate는 ADAM optimizer를 이용하여 learning rate를 설정해준다.
- 모델 학습시간에는 4개의 Nvidia Tesla-V100 gpu를 병렬로 사용했을 때, 약 89시간이 걸렸다. 학습은 validation loss가 연속해서 12 epoch동안 개선되지 않으면, 학습을 종료했다.
- 학습 과정에서 data augmentation도 발생하는데, 지진파 데이터에 Gaussian 노이즈를 덧씌워거나 random shift, randomly adding gap, randomly dropping channels와 같은 방식으로 학습 데이터를 augmentation한다.
- 그리고 학습/테스트 과정에서 drop out은 동일하게 0.1로 사용했다.

### 학습/테스트 데이터
- 학습에는 STEAD 데이터를 하고 학습에 데이터를 넣을 때는 사용 비율은 train 85%, validation 5%, test 10%로 사용했다.
    ![](https://i.imgur.com/6Ypp0W2.jpg)
- 위 이미지는 본 논문에서 사용한 STEAD 데이터의 station 위치를 시각화한 것이다.
- 본 논문은 STEAD에 포함되지 않은 지역에 대해서도, 모델이 task를 잘 수행하는지 추가 테스트를 진행하였고, 2000년 일본 Tottori에서 일어난 지진 데이터를 이용하여 모델의 성능을 추가로 검증하였다. 

### 결과
- 본 논문은 앞서 제시된 지진검출, phase picking 모델들과 성능을 비교하였다. 테스트에는 STEAD 테스트 모델을 사용했다. Tottori 데이터를 이용한 성능 테스트에서는 사람이 분석한 데이터와 EQtransformer가 추론한 데이터를 비교하였다.
- 모델별 지진검출 성능
    - 지진검출 성능은 지진 발생 여부를 precision, recall, f1으로 계산하였고, EQTransformer가 세개의 지표에서 모두 타 모델보다 우수했다.
    ![](https://i.imgur.com/D6KHqE9.png)
- 모델별 P파 검출 성능
    - 모델별 P파 검출 성능 precision, recall, f1에 더불어 평균과 표준편차, MAE, MAPE 지표를 추가하여 비교하였다. 그리고 모든 지표에서 EQTransformer가 모두 타 모델 대비 우수했다.
    ![](https://i.imgur.com/W8bXX8K.png)
- 모델별 S파 검출 성능
    - 모델 S파 검출은 P파 검출과 동일한 성능 지표로 평가했고, precision을 제외한 모든 지표에서 EQTransformer가 우수했다.
    ![](https://i.imgur.com/LERYIZc.png)

- 학습 데이터에서 본적 없는 지역에 경우도, 본 논문의 모델이 동작하는지 확인하기 위해 일본 Tottori 지역의 지진 데이터를 사용하여 테스트하였고, 테스트에서 성능 비교에는 일본 JMA(Japan Meteorological Agency)에서 사람이 측정한 분석 데이터와 EQTransformer가 자동으로 분석한 데이터를 서로 비교하였다.
    ![](https://i.imgur.com/HL7jRNP.jpg)
    - a는 사람이 phase picking을 분석한 데이터이고, b는 EQTransformer가 분석한 데이터이다.
    - c는 JMA에서 판단한 57개 지진 대상 지역이고, d는 EQTransformer가 판단한 18개 지진 지역이다.

