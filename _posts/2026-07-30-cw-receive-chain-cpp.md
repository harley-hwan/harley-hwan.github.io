---
title: "(Radar) 7. CW 수신 체인 구현 — IQ 신호에서 속도와 각도 구하기"
description: "6장에서 정리한 CW 체인 여섯 단계를 그림과 코드로 확인한다. I–Q 궤적으로 결함을 구분하는 법, 불균형이 반대쪽 주파수에 이미지를 만드는 이유, 창이 필요한 이유, 세 점으로 피크 위치를 보간하는 법, 위상차를 켤레곱으로 구해야 하는 이유를 다룬다."
date: 2026-07-30 10:00:00 +0900
slug: 'cw-receive-chain-cpp'
categories: [Dev, Radar]
series: radar
series_order: 7
tags: [radar, cw-radar, cpp, python, fft, dsp, doppler, windowing, signal-processing, radar-sensor]
math: true
---

[6장](/posts/cw-vs-fmcw-radar/)에서 CW 수신 체인을 여섯 단계로 정리했다. DC 제거, I/Q 보정, 윈도잉, 복소 FFT, 검출, 각도. 각 단계마다 왜 필요한지가 있는데, 그걸 모르고 짜면 코드는 돌아가지만 결과가 이상해진다.

그 여섯 단계를 그림, 식, 코드로 하나씩 확인한다.

구현은 C++이지만, 개념을 적을 때는 표현이 간결한 Python을 함께 쓴다.

> 이 글의 숫자는 모두 아래 코드를 실행해서 얻은 값이다. 참값을 아는 합성 신호로 측정했기 때문에 오차를 그대로 확인할 수 있다. 실제 센서 측정치는 아니다. 신호를 만드는 코드는 [부록](#부록-합성-신호-만들기)에 있으니 표를 직접 재현해 볼 수 있다.
{: .prompt-tip }

* * *

## 1. 입력과 출력

입력은 3채널 복소 IQ 스트림이고, 출력은 프레임마다 나오는 표적 목록이다. 표적 하나는 시선 속도, SNR, 방위각을 갖는다.

6장에서 사용한 24 GHz 골프 설정을 그대로 쓴다.

```cpp
struct Config {
    double fs     = 50000.0;  // ADC 표본화 주파수 [Hz]
    int    n_fft  = 512;      // 프레임 길이 = FFT 길이
    int    hop    = 128;      // STFT 이동 간격 (75% 겹침)
    double lambda = 0.0125;   // 24 GHz 파장 [m]
    double d_ant  = 0.00625;  // 안테나 간격 [m] (= λ/2)
};
```

나머지 값은 여기서 계산된다.

| 값 | 식 | 결과 |
| :--- | :--- | ---: |
| 코히어런트 관측 시간 $T$ | $N_\mathrm{FFT}/f_s$ | 10.24 ms |
| 빈 폭 | $1/T$ | 97.66 Hz |
| 속도 분해능 $\Delta v$ | $\lambda/2T$ | 0.610 m/s |
| 비모호 속도 | $\lambda f_s/4$ | ±156.25 m/s |
| 프레임 간격 | hop$/f_s$ | 2.56 ms |

512 샘플은 임의로 고른 값이 아니다. 6장에서 공의 감속으로 관측 시간 상한이 17 ms가 되고, 스핀 측대역을 구분하려면 1 ms 이상이 필요하다고 했다. 10.24 ms는 그 사이에 들어가는 길이다.

> **기호 하나만 짚고 간다**: 여기서 $N_\mathrm{FFT}$는 프레임 길이, 곧 FFT 길이 512다. 6장에서 $N$은 **chirp 하나당 샘플 수**를 뜻했는데, CW에는 chirp가 없으므로 같은 글자라도 가리키는 대상이 다르다. 6장의 $N$에 해당하는 것은 아예 없다 — 접지 않기 때문이다.
{: .prompt-warning }

체인 전체는 이 순서로 돌아간다. 이후 절이 각 줄을 하나씩 설명한다.

```cpp
remove_dc(x);                     // 3절 — 거리 게이트가 없으니 0 Hz 부터 지운다
apply_iq(x, estimate_iq(x));      // 4절 — 찌그러진 궤적을 원으로 되돌린다
apply_window(x, w);               // 5절 — 잘린 양 끝을 0 으로 만든다
fft(x);                           // 2절 — 복소 FFT 한 번이 곧 도플러 스펙트럼
// 이후: magnitude_db -> 검출(7절) -> 포물선 보간(6절) -> 채널 위상차(8절)
```

앞의 세 줄은 순서를 바꾸면 안 된다. 이유는 뒤에서 하나씩 나온다.

* * *

## 2. FFT와 빈 번호 읽기

체인의 중심에 복소 FFT가 있다. 파이썬으로는 한 줄이다.

```python
X = np.fft.fft(x)          # x 는 길이 512 의 복소 배열
```

여기서 복소 FFT의 빈 번호를 읽는 방법이 CW에서 중요하다. 절반 위쪽 빈은 큰 양의 주파수가 아니라 음의 주파수를 뜻한다.

```python
def bin_to_hz(b, n, fs):
    return (b - n if b >= n / 2 else b) * fs / n
```

이 처리를 빠뜨리면 멀어지는 표적이 전부 초고속으로 다가오는 표적으로 읽힌다. CW는 거리를 재지 못하는 대신 도플러의 부호로 접근과 이탈을 구분하는데, 그 부호가 통째로 뒤집힌다.

속도는 6장의 $f_d = 2v/\lambda$를 뒤집어서 구한다.

$$
v = \frac{f_d\,\lambda}{2}
$$

C++ FFT 구현은 [부록](#부록-c-구현)에 두었다. 한 가지만 미리 적으면, 트위들 인자는 표로 미리 계산해 두는 편이 좋다. 교과서 예제처럼 안쪽 루프에서 `w *= wl`로 계산하면 512번 곱하는 동안 위상 오차가 누적되는데, 이 체인의 마지막 단계가 채널 간 위상차를 0.1° 수준에서 읽는 작업이다.

* * *

## 3. DC·클러터 제거

거리 게이트가 없으므로 벽, 삼각대, 바닥, TX 누설이 모두 0 Hz에 쌓인다. 스펙트럼을 보기 전에 I–Q 평면에 궤적을 그려보는 편이 빠르다.

![I–Q 궤적으로 보는 전처리 두 단계](/assets/img/posts/cw-receive-chain-cpp/fig1-iq-trajectory.svg){: width="860"}
_그림 1. 표적이 하나면 궤적은 원점을 도는 원이 된다. 중심이 밀렸으면 DC가 남은 것이고, 찌그러졌으면 I/Q 불균형이 남은 것이다._

표적이 하나면 기저대역은 복소 정현파 하나이므로 궤적은 원점 중심의 원이다. 클러터가 상수로 더해지면 그 원이 옆으로 밀린다. 밀린 만큼 빼면 된다.

```python
x -= x.mean()              # 프레임 평균 = 그 프레임의 DC
```

```cpp
inline void remove_dc(std::vector<cf>& x) {
    const cf mean = std::accumulate(x.begin(), x.end(), cf{}) / double(x.size());
    for (auto& s : x) s -= mean;
}
```

6장에서는 이것을 폭이 $\approx 1/T$인 DC 노치라고 적고 그 아래 속도가 죽는다고 했다. 실제로 측정해보면 방향은 맞지만 경계가 뚜렷하지는 않다. 같은 표적을 DC 제거 전후로 측정해서 손실만 뽑으면 다음과 같다.

| 표적 속도 | 빈 위치 | 손실 |
| ---: | ---: | ---: |
| 0.10 m/s | 0.16 | −16.6 dB |
| 0.20 m/s | 0.33 | −9.2 dB |
| 0.30 m/s | 0.49 | −4.3 dB |
| 0.40 m/s | 0.66 | −2.3 dB |
| 0.50 m/s | 0.82 | −1.0 dB |
| 0.61 m/s | 1.00 | 0.0 dB |

−3 dB 지점이 약 0.35 m/s이고, 빈 1개(0.61 m/s)에서는 손실이 0이다. 평균을 빼는 것은 DC 빈 하나를 지우는 연산이라, 표적이 정수 빈에 정확히 놓이면 DC로 새는 성분이 없어서 손실도 없다. 즉 $\lambda/2T$는 노치의 폭을 나타내는 값이지 그 아래가 모두 죽는 경계는 아니다.

실무에서는 아날로그 쪽 제약이 더 크다. HPF 코너가 300 Hz면 최소 측정 속도가 1.875 m/s이고, 거기서 이미 잘린 신호는 디지털에서 되살릴 수 없다.

> **남은 DC는 표적으로 검출된다**: 평균을 빼도 클러터가 완전히 사라지지는 않는다. 뒤에 나올 전체 실행에서 0 Hz 근처에 SNR 12.3 dB짜리 검출이 하나 잡히는데, 표적이 아니라 잔재다. 검출 단계에서 DC 주변 몇 빈을 게이팅하지 않으면 "0.12 m/s로 다가오는 표적"으로 보고된다.
{: .prompt-warning }

* * *

## 4. I/Q 불균형 보정

궤적이 원점으로 왔는데도 찌그러져 있다면 I와 Q의 이득이 다르거나 두 채널이 정확히 90°가 아니다. 6장에서 이것이 CW에서 특히 문제가 된다고 했다. 이미지가 $-f_d$에 생기는데, 그 위치가 "같은 속도로 멀어지는 표적"이라는 그럴듯한 값이다.

이미지가 반대쪽에 생기는 이유는 다음과 같다.

![불균형이 이미지를 만드는 원리](/assets/img/posts/cw-receive-chain-cpp/fig2-imbalance-mechanism.svg){: width="860"}
_그림 2. 타원은 서로 반대 방향으로 도는 두 원으로 분해된다. 역방향으로 도는 성분이 $-f_d$의 이미지가 된다._

반지름이 $a$, $b$인 타원은 다음과 같이 분해된다.

$$
a\cos\theta + jb\sin\theta = \underbrace{\frac{a+b}{2}e^{j\theta}}_{\text{정방향}} + \underbrace{\frac{a-b}{2}e^{-j\theta}}_{\text{역방향}}
$$

균형이 맞아 $a = b$이면 두 번째 항이 0이라 원 하나만 남는다. 불균형이 있으면 $a \ne b$가 되어 반대 방향으로 도는 작은 원이 생기고, 이 성분은 주파수 축에서 $-f_d$에 나타난다.

보정은 타원을 다시 원으로 만드는 작업이다. 복소 정현파의 I와 Q가 등전력이고 서로 무상관이라는 성질을 이용하면 통계량 세 개로 충분하다.

```python
i, q = x.real, x.imag
gain    = np.sqrt((i**2).mean() / (q**2).mean())     # 이득비
sin_psi = (i*q).mean() / np.sqrt((i**2).mean() * (q**2).mean())   # 직교 오차
q_fixed = (q*gain - sin_psi*i) / np.sqrt(1 - sin_psi**2)
x = i + 1j*q_fixed
```

```cpp
struct IqGain {
    double gain    = 1.0;   // I 대비 Q 의 이득비
    double sin_psi = 0.0;   // 직교 오차 sin ψ
};

inline IqGain estimate_iq(const std::vector<cf>& x) {
    double pii = 0, pqq = 0, piq = 0;
    for (const auto& s : x) {
        pii += s.real() * s.real();
        pqq += s.imag() * s.imag();
        piq += s.real() * s.imag();
    }
    const double n = double(x.size());
    pii /= n; pqq /= n; piq /= n;

    IqGain k;
    if (pqq > 0 && pii > 0) {
        k.gain    = std::sqrt(pii / pqq);
        k.sin_psi = std::clamp(piq / std::sqrt(pii * pqq), -0.9, 0.9);
    }
    return k;
}

inline void apply_iq(std::vector<cf>& x, const IqGain& k) {
    const double norm = std::sqrt(1.0 - k.sin_psi * k.sin_psi);   // 위에서 ±0.9 로 clamp 했다
    for (auto& s : x)
        s = cf{ s.real(), (s.imag() * k.gain - k.sin_psi * s.real()) / norm };
}
```

`gain`은 상관계수의 척도 불변성 덕분에 먼저 곱해도 `sin_psi` 추정값을 흔들지 않는다. 그래서 두 보정을 한 줄에 이어 붙일 수 있다.

이 추정은 DC를 제거한 뒤에 해야 한다. 누설이 남아 있으면 그 DC가 $E[I^2]$와 $E[IQ]$를 지배해서 추정값이 표적이 아니라 클러터를 따라간다.

이득 0.5 dB, 위상 3°를 주입하고 측정한 결과다.

| 항목 | 보정 없음 | 보정 적용 |
| :--- | ---: | ---: |
| 공 (+67 m/s) | 58.6 dB | 58.6 dB |
| 이미지 (−67 m/s) | 30.7 dB | 검출 안 됨 |
| 이미지 (−45 m/s) | 22.7 dB | 검출 안 됨 |

억압비가 $58.6 - 30.7 = 27.9$ dB다. 6장에서 $\mathrm{IRR} \approx -20\log_{10}(\sqrt{\epsilon^2+\psi^2}/2)$로 계산한 값이 28.1 dB였으니 0.2 dB 차이로 일치한다. 위 분해식으로 보면 작은 원의 반지름이 큰 원의 4%에 해당한다.

> **이 추정기의 전제**: 블록 안의 신호가 원점 대칭이어야 한다. 표적이 하나이고 SNR이 충분하면 잘 맞지만, 강한 정지 클러터가 남아 있거나 표적이 없는 프레임에서는 추정값이 흔들린다. 실제 장비에서는 프레임마다 추정하기보다 알려진 조건에서 한 번 측정해 상수로 두고, 온도가 크게 변할 때만 갱신하는 편이 안정적이다.
{: .prompt-tip }

* * *

## 5. 윈도잉

프레임은 연속된 신호를 512 샘플만큼 잘라낸 조각이다. FFT는 그 조각이 무한히 반복된다고 가정하는데, 잘린 양 끝의 값이 맞지 않으면 이어지는 지점에 불연속이 생긴다. 이 불연속이 스펙트럼 전체로 퍼진다.

![창이 필요한 이유](/assets/img/posts/cw-receive-chain-cpp/fig3-window-leakage.svg){: width="860"}
_그림 3. 왼쪽은 시간축, 오른쪽은 그 결과 스펙트럼. 직사각 창에서는 누설 때문에 약한 표적이 보이지 않는다._

양 끝을 0으로 만들어 불연속을 없애면 된다.

```python
w = np.hanning(N + 1)[:-1]        # 주기형 Hann
X = np.fft.fft(x * w / w.mean())  # 코히어런트 이득 보정 포함
```

```cpp
inline std::vector<double> hann(size_t n) {
    std::vector<double> w(n);
    for (size_t i = 0; i < n; ++i)
        w[i] = 0.5 - 0.5 * std::cos(2.0 * kPi * double(i) / double(n));
    return w;
}

inline void apply_window(std::vector<cf>& x, const std::vector<double>& w) {
    const double cg = std::accumulate(w.begin(), w.end(), 0.0) / double(w.size());
    for (size_t i = 0; i < x.size(); ++i) x[i] *= w[i] / cg;
}
```

두 가지가 들어 있다. 분모의 $N$은 주기형 Hann을 만들기 위한 것이다. $N-1$로 나누는 대칭형은 스펙트럼 해석에서 편향이 생긴다. `cg`로 나누는 것은 코히어런트 이득 보정인데, Hann의 평균이 0.5라서 그냥 곱하면 진폭이 6 dB 낮아진다.

효과는 다음과 같다. 강한 표적 옆에 40 dB 약한 표적을 두고 진폭을 측정했다.

| 간격 | 창 | 참 진폭 | 측정값 | 오차 |
| ---: | :--- | ---: | ---: | ---: |
| 3 빈 | 직사각 | −40 dB | −20.5 dB | +19.5 dB |
| 3 빈 | Hann | −40 dB | −30.2 dB | +9.8 dB |
| 6 빈 | 직사각 | −40 dB | −27.1 dB | +12.9 dB |
| 6 빈 | Hann | −40 dB | −41.2 dB | −1.2 dB |
| 12 빈 | 직사각 | −40 dB | −31.4 dB | +8.6 dB |
| 12 빈 | Hann | −40 dB | −40.4 dB | −0.4 dB |

직사각 창은 12 빈 떨어져도 8.6 dB 오차가 난다. 약한 표적이 아니라 강한 표적의 누설을 측정하고 있다. 3 빈에서는 Hann도 9.8 dB 오차가 나는데, 이건 사이드로브가 아니라 메인로브가 겹치는 영역이라 창으로 해결할 수 없다.

3 빈 행만은 숫자를 그대로 믿으면 안 된다. Hann의 메인로브가 약 4 빈이라 두 표적이 겹쳐 있고, 겹친 자리에서는 두 성분이 **벡터로** 더해지므로 측정값이 상대 위상에 따라 오르내린다. 같은 조건에서 위상만 한 바퀴 돌려 보면 −51 dB에서 −36 dB까지 15 dB가 움직인다. 반면 12 빈 Hann은 같은 스윕에서 0.2 dB밖에 안 흔들린다. 3 빈 행은 "창으로는 안 된다"는 방향만 읽고, 값은 12 빈 쪽을 믿는 것이 맞다.

대가도 있다. Hann은 메인로브가 넓어서 표적이 빈 사이에 있으면 피크가 낮아진다. 빈 정중앙에서 1.42 dB이고, 스캘롭 손실이라고 부른다. 진폭을 절대값으로 써야 한다면 이 손실을 보정해야 하고, 속도만 필요하면 무시해도 된다.

순서를 정리하면, DC 제거가 창보다 먼저다. 창을 먼저 걸면 DC가 창의 모양대로 퍼져서, 그다음에 평균을 빼도 이미 퍼진 성분은 되돌릴 수 없다.

* * *

## 6. 피크 보간

빈 폭이 0.61 m/s인데 6장에서는 정밀도를 7.5 mm/s로 계산했다. 약 80배 차이이고, 그 차이를 만드는 것이 보간이다.

![포물선 보간](/assets/img/posts/cw-receive-chain-cpp/fig4-interpolation.svg){: width="860"}
_그림 4. 피크 주변 세 빈에 포물선을 맞추고 꼭짓점 위치를 읽는다. dB 값으로 맞춰야 한다._

```python
k = np.argmax(db)
d = 0.5*(db[k-1] - db[k+1]) / (db[k-1] - 2*db[k] + db[k+1])
peak_bin = k + d
```

```cpp
const double denom = db[km] - 2 * db[k] + db[kp];
const double delta = (std::abs(denom) < 1e-12) ? 0.0
                                               : 0.5 * (db[km] - db[kp]) / denom;
```

변수 이름이 `db`인 것이 중요하다. 선형 진폭이 아니라 로그 진폭에 포물선을 맞춰야 한다. Hann 창의 메인로브는 로그 영역에서 포물선과 거의 일치한다.

주파수 추정 문헌에서 자주 인용되는 Jacobsen 추정기는 dB로 바꿀 것도 없이 복소값을 그대로 넣는 한 줄이라 가져다 쓰기 쉽다.

$$
\delta = -\,\mathrm{Re}\!\left[\frac{X_{k+1} - X_{k-1}}{2X_k - X_{k-1} - X_{k+1}}\right]
$$

그런데 창에 따라 결과가 달라진다.

| 창 + 추정기 | 최대 오차 |
| :--- | ---: |
| Hann + 포물선(dB) | 0.016 bin |
| 직사각 + 포물선(dB) | 0.167 bin |
| Hann + Jacobsen | 0.250 bin |

Jacobsen 추정기는 직사각 창을 전제로 유도된 식이라 Hann에 쓰면 포물선보다 16배 나쁘다. 창을 바꾸면 보간식도 다시 확인해야 한다.

0.016 bin을 속도로 바꾸면 9.8 mm/s다. 6장에서 계산한 CRLB 7.5 mm/s와 같은 자릿수인데, 여기서 한 가지를 알 수 있다. 정밀도의 한계는 잡음이 아니라 보간 편향이다. SNR을 30 dB에서 60 dB로 올려도 이 항은 남는다.

* * *

## 7. 검출

6장에서 순서를 정리했다. 1/f 잡음은 프레임마다 같은 모양으로 나타나는 정적 성분이라 빈 상태에서 미리 측정해 나누고, 적응 문턱은 그 위에 적용한다.

```cpp
struct Detection {
    double bin;        // 보간된 실수 빈 위치
    double velocity;   // [m/s]
    double snr_db;     // 참조 셀 평균 대비
};

// db    : magnitude_db() 출력, 길이 n_fft
// guard : 보호 셀 수 (Hann 메인로브 폭), ref : 한쪽 참조 셀 수
std::vector<Detection> detect(const std::vector<double>& db, const Config& cfg,
                              int guard, int ref, double threshold_db) {
    std::vector<Detection> out;
    const int n = int(db.size());

    for (int k = 0; k < n; ++k) {
        const int km = (k - 1 + n) % n, kp = (k + 1) % n;
        if (!(db[k] > db[km] && db[k] >= db[kp])) continue;   // 국소 최대만

        double sum = 0; int cnt = 0;
        for (int j = guard + 1; j <= guard + ref; ++j) {      // 보호 셀은 건너뛴다
            sum += db[(k - j + n) % n] + db[(k + j) % n];
            cnt += 2;
        }
        const double floor_db = sum / cnt;
        if (db[k] - floor_db < threshold_db) continue;

        const double denom = db[km] - 2 * db[k] + db[kp];     // 6절 포물선 보간
        const double delta = (std::abs(denom) < 1e-12) ? 0.0
                                                       : 0.5 * (db[km] - db[kp]) / denom;
        const double bin = k + delta;
        const double hz  = (bin >= n / 2.0 ? bin - n : bin) * cfg.fs / n;   // 2절 빈 매핑
        out.push_back({ bin, hz * cfg.lambda / 2.0, db[k] - floor_db });
    }
    return out;
}
```

표적 자신의 메인로브가 참조 셀에 섞이면 문턱이 표적을 따라 올라가서 스스로를 지운다. 보호 셀은 그것을 막는다. Hann의 메인로브가 약 4 빈이므로 보호 셀도 그만큼 잡는다.

복소 스펙트럼은 원형이라 인덱스를 `% n`으로 순환시킨다. 0 Hz의 왼쪽은 음의 최대 속도이고, 앞의 빈 매핑과 같은 이야기다.

> **이 검출기는 참조 셀을 dB로 평균한다.** 선형 전력으로 평균하는 교과서의 셀 평균(CA) CFAR와는 다른 물건이고, log-CFAR 계열에 속한다. 레일리 잡음에서 dB 평균 바닥은 선형 평균보다 $10\gamma/\ln 10 \approx 2.5$ dB 낮게 잡히므로($\gamma$는 오일러 상수), [6장](/posts/cw-vs-fmcw-radar/)의 문턱 계수 $\alpha = N_{ref}(P_{fa}^{-1/N_{ref}}-1)$는 선형 평균 전제라 `threshold_db`에 그대로 넣으면 $P_{fa}$가 설계값보다 커진다. 같은 이유로 이 코드가 보고하는 SNR도 잡음 전력 대비보다 그만큼 높게 읽힌다. $P_{fa}$를 사양으로 보증해야 한다면 참조 평균은 선형 전력으로 하고 dB는 표시에만 쓰는 것이 맞다.
{: .prompt-warning }

* * *

## 8. 각도 계산

같은 도플러 빈의 복소값을 채널마다 뽑아 위상차를 구하고, 각도로 변환한다.

$$
\Delta\phi = \frac{2\pi d\sin\theta}{\lambda} \quad\Longrightarrow\quad \theta = \arcsin\!\left(\frac{\Delta\phi\,\lambda}{2\pi d}\right)
$$

위상차를 구하는 방법에서 자주 나오는 실수가 있다.

![위상차는 켤레곱으로](/assets/img/posts/cw-receive-chain-cpp/fig5-phase-wrap.svg){: width="860"}
_그림 5. 두 위상이 ±180° 경계에 걸치면 뺄셈은 20°를 340°로 만든다. 켤레곱에는 이 문제가 없다._

```python
dphi  = np.angle(a * np.conj(b))          # 항상 (−π, π]
theta = np.arcsin(np.clip(dphi*lam/(2*np.pi*d), -1, 1))
```

```cpp
inline double phase_diff(cf a, cf b) { return std::arg(a * std::conj(b)); }

inline double aoa_rad(double dphi, double lambda, double d) {
    return std::asin(std::clamp(dphi * lambda / (2.0 * kPi * d), -1.0, 1.0));
}
```

`arg(a) - arg(b)`로 빼면 안 된다. 두 위상은 각각 $(-\pi, \pi]$ 안에서만 표현되므로, 참 위상차가 그 경계를 넘으면 결과가 $2\pi$만큼 틀어진다. 그림 5의 경우 실제로는 20° 차이인데 뺄셈은 340°를 준다. 켤레곱을 먼저 하고 `arg`를 한 번만 취하면 곱셈 과정에서 위상이 자동으로 접힌다.

각도가 가끔씩만 튄다면 이 경우일 가능성이 높다. 표적이 정면 근처에 있을 때만 경계를 넘기 때문에 재현이 어렵다.

`clamp`도 필요하다. 잡음이나 캘리브레이션 오차로 `asin`의 인자가 1을 조금 넘으면 NaN이 나오고, 이후 계산으로 그대로 전파된다.

### 세 채널은 같은 빈에서 뽑는다

피크가 빈 사이에 있으면 정수 빈의 복소값은 창 누설 때문에 회전해 있다. 이 회전은 세 채널에 공통이라 위상차에서는 소거된다. 이웃 빈과 섞는 보간은 그 회전을 고치는 것이 아니라, 빈 경계 근처에서 신호 성분을 더 모아 위상에 실리는 잡음을 줄이는 쪽이다.

```cpp
inline cf bin_value(const std::vector<cf>& X, double bin_refined) {
    const int n = int(X.size());
    const int k = int(std::floor(bin_refined));
    const double f = bin_refined - k;
    return X[(k + n) % n] * (1.0 - f) + X[(k + 1 + n) % n] * f;
}
```

채널마다 각자 피크를 찾아 각자의 정수 빈을 쓰면, 두 채널이 서로 다른 빈을 고르는 순간 위상차에 빈 하나만큼의 오차가 들어간다. 기준 채널에서 찾은 실수 빈 위치를 세 채널에 공통으로 적용해야 한다.

### 캘리브레이션

6장에서 각도 정확도의 한계는 열잡음이 아니라 채널 간 오프셋이고 그 값이 온도에 따라 변한다고 했다. 구현은 상수 하나를 빼는 것으로 끝나지만, 그 상수를 어떻게 얻느냐가 중요하다.

```cpp
// 오프셋을 뺀 뒤에도 (−π, π] 로 접어야 한다
inline double calibrated_diff(cf a, cf b, double offset) {
    return std::remainder(phase_diff(a, b) - offset, 2.0 * kPi);
}
```

오프셋은 알려진 방위에 기준 표적을 두고 측정한다. 세션 시작과 한 시간 뒤의 값을 기록해두면 각도 사양을 온도 조건과 함께 적을 수 있다.

세 채널을 'ㄴ' 자로 배치하고 수평·수직 위상차에서 스핀축을 구하는 방법은 [3채널 레이다 센서로 스핀축 계산하기](/posts/cpp-3-channel-radar-sensor-spin-axis-calculation/)에 정리해두었다.

* * *

## 9. 전체 실행 결과

프레임 하나에 클럽(45 m/s, 방위 −4°)과 공(67 m/s, 방위 +6°)을 넣고, TX 누설과 정지 클러터를 DC로 더하고, 이득 0.5 dB와 위상 3°의 불균형을 주입한 뒤 체인을 실행했다.

```cpp
auto x = ch[c];
remove_dc(x);                     // 3절
apply_iq(x, estimate_iq(x));      // 4절
apply_window(x, w);               // 5절
fft(x);                           // 2절
```

| 표적 | 참 속도 | 추정 속도 | 오차 | SNR | 추정 방위각 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 공 | 67.00 m/s | 66.991 m/s | −9 mm/s | 58.6 dB | 6.00° (참 6.0°) |
| 클럽 | 45.00 m/s | 44.990 m/s | −10 mm/s | 50.6 dB | −4.05° (참 −4.0°) |

두 표적의 속도 오차가 −9, −10 mm/s로 거의 같다. 잡음 때문이라면 SNR이 8 dB 차이 나는 만큼 값도 달라야 하는데 그렇지 않다. 6절에서 측정한 보간 편향 9.8 mm/s가 그대로 나타났다. 잡음이 아니라 계통 오차이므로, 잡음을 줄여서는 없앨 수 없고 보간식을 바꿔야 한다.

* * *

## 10. 정리

여섯 단계에서 확인한 내용을 정리하면 다음과 같다.

1. I–Q 궤적을 먼저 본다. 중심이 밀렸으면 DC, 찌그러졌으면 불균형이다. 두 결함이 서로 다른 모양이라 원인을 구분할 수 있다
2. DC 노치는 경계가 뚜렷하지 않다. $\lambda/2T$는 폭을 나타내는 값이고, 정수 빈에서는 손실이 0이다
3. 이미지가 $-f_d$에 생기는 이유는 타원 분해로 설명된다. 역방향으로 도는 작은 원이 이미지다
4. DC 제거 → I/Q 보정 → 창 순서를 지킨다. 순서를 바꾸면 되돌릴 수 없다
5. Hann과 포물선(dB)은 짝이다. 창을 바꾸면 보간식도 다시 확인한다
6. 위상차는 켤레곱으로 구한다. 뺄셈은 경계에서만 틀려서 재현이 어렵다
7. 세 채널은 같은 실수 빈에서 뽑는다. 채널마다 피크를 찾으면 오차가 들어간다

이 코드로 확인할 수 없는 것도 있다. 합성 신호에는 실제 믹서의 1/f 잡음도, 프레임마다 모양이 달라지는 이동 클러터도, 온도에 따라 변하는 채널 오프셋도 없다. 6장 마지막 절에서 잡음 바닥, I–Q 궤적, 채널 간 위상 오프셋 세 가지를 실측해야 한다고 적은 이유가 이것이고, 이 셋은 장비에서만 측정할 수 있다.

여기까지가 한 프레임이다. 프레임을 시간축으로 이어 붙이는 문제 — STFT로 얻은 추정치를 궤적으로 묶고, 임팩트 시점으로 역외삽하는 일 — 는 [20장](/posts/radar-tracking/)으로 넘긴다. 다만 거기서 보듯, 60 ms 짜리 짧은 궤적은 재귀 필터보다 전체 구간을 한꺼번에 맞추는 일괄 적합 쪽이 맞다. 필터가 답인 경우와 아닌 경우도 거기서 갈라 두었다.

여기서 짠 체인은 펄스 도플러에서 거의 그대로 반복된다. 축 하나가 늘어 거리축이 붙는 것만 다르다([8장](/posts/pw-radar/)).

* * *

## 부록: C++ 구현

FFT는 기수-2 Cooley-Tukey다. 트위들과 비트 역순 인덱스를 미리 계산해두고 프레임마다 재사용한다.

```cpp
using cf = std::complex<double>;
constexpr double kPi = 3.14159265358979323846;

class Fft {
public:
    explicit Fft(size_t n) : n_(n), rev_(n), tw_(n / 2) {
        size_t bits = 0;
        while ((size_t{1} << bits) < n) ++bits;
        for (size_t i = 0; i < n; ++i) {
            size_t r = 0;
            for (size_t b = 0; b < bits; ++b)
                if (i & (size_t{1} << b)) r |= size_t{1} << (bits - 1 - b);
            rev_[i] = r;
        }
        for (size_t k = 0; k < n / 2; ++k)
            tw_[k] = std::polar(1.0, -2.0 * kPi * double(k) / double(n));
    }

    void operator()(std::vector<cf>& x) const {
        for (size_t i = 0; i < n_; ++i)
            if (i < rev_[i]) std::swap(x[i], x[rev_[i]]);
        for (size_t len = 2; len <= n_; len <<= 1) {
            const size_t half = len / 2, step = n_ / len;
            for (size_t i = 0; i < n_; i += len)
                for (size_t k = 0; k < half; ++k) {
                    const cf u = x[i + k];
                    const cf t = tw_[k * step] * x[i + k + half];
                    x[i + k]        = u + t;
                    x[i + k + half] = u - t;
                }
        }
    }

private:
    size_t n_;
    std::vector<size_t> rev_;
    std::vector<cf> tw_;
};
```

`M_PI`는 표준이 아니라서 `kPi`를 직접 정의했다. Visual Studio에서는 `_USE_MATH_DEFINES`를 먼저 정의해야 쓸 수 있다.

스펙트럼은 창의 코히어런트 이득까지 보정한 dB 값으로 만든다.

```cpp
inline std::vector<double> magnitude_db(const std::vector<cf>& X) {
    std::vector<double> m(X.size());
    for (size_t i = 0; i < X.size(); ++i)
        m[i] = 20.0 * std::log10(std::max(std::abs(X[i]) / double(X.size()), 1e-20));
    return m;
}
```

* * *

## 부록: 합성 신호 만들기

본문의 표를 직접 재현하려면 입력 신호가 있어야 한다. 참값을 아는 신호를 만드는 코드가 이것이다.

```python
import numpy as np

FS, N, LAM, D = 50_000.0, 512, 0.0125, 0.00625
n = np.arange(N)

def synth(targets, gain_db=0.5, psi_deg=3.0, dc=30.0, noise=1e-3, ch=0, seed=0):
    """targets: [(속도[m/s], 진폭, 방위각[deg]), ...],  ch: 채널 번호 (0 이 기준)"""
    rng = np.random.default_rng(seed)
    x = np.zeros(N, dtype=complex)
    for v, amp, az in targets:
        fd   = 2 * v / LAM                                        # 도플러
        dphi = ch * 2 * np.pi * D * np.sin(np.deg2rad(az)) / LAM   # 채널 간 위상차
        x += amp * np.exp(1j * (2 * np.pi * fd * n / FS + dphi))

    x += dc                                                        # TX 누설 + 정지 클러터
    x += noise * (rng.normal(size=N) + 1j * rng.normal(size=N)) / np.sqrt(2)

    g, psi = 10 ** (gain_db / 20), np.deg2rad(psi_deg)             # I/Q 불균형 주입
    i0, q0 = x.real, x.imag
    return i0 + 1j * g * (q0 * np.cos(psi) + i0 * np.sin(psi))

# 9절의 프레임 — 공 67 m/s @ +6°, 클럽 45 m/s @ −4° (공보다 8 dB 약하게)
targets = [(67.0, 1.0, 6.0), (45.0, 10 ** (-8 / 20), -4.0)]
chans   = [synth(targets, ch=c, seed=7) for c in range(3)]
```

불균형 주입식이 4절 보정식의 정확한 역이다. $q = g\,(q_0\cos\psi + i_0\sin\psi)$로 넣으면 `estimate_iq`가 $1/g$와 $\sin\psi$를 되찾고, `apply_iq`가 $q_0$를 복원한다. 그래서 "보정이 듣는다"는 것이 우연이 아니라는 것까지 확인할 수 있다.

3절의 DC 노치 손실표는 표적 하나만 넣고 `dc=0`, `noise=0`, `gain_db=0`, `psi_deg=0`으로 두면 그대로 나온다. 6절의 보간 오차표는 톤 하나를 정수 빈에서 −0.5부터 +0.5까지 밀면서 최대 오차를 재면 된다.

> **한 가지만 주의**: 5절의 누설 표에서 3 빈 행은 이 코드로도 그대로 나오지 않는다. 메인로브가 겹치는 영역이라 두 톤의 상대 위상에 따라 값이 15 dB까지 움직이기 때문이다. 6 빈과 12 빈 행은 위상을 어떻게 두어도 0.2 dB 안에서 재현된다.
{: .prompt-warning }

* * *

## 참고 자료

- M. A. Richards, *Fundamentals of Radar Signal Processing*, McGraw-Hill — 검출 이론과 CFAR
- F. J. Harris, "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform," *Proc. IEEE*, 1978 — 창 함수의 코히어런트 이득, 스캘롭 손실, 사이드로브 정리
- E. Jacobsen, P. Kaiser, "Fast, Accurate Frequency Estimators," *IEEE Signal Processing Magazine*, 2007 — 보간 추정기 비교
- B.-K. Park et al., "Arctangent Demodulation With DC Offset Compensation in Quadrature Doppler Radar Receiver Systems," *IEEE Trans. MTT*, 2007 — I/Q 불균형과 DC 오프셋 보상
