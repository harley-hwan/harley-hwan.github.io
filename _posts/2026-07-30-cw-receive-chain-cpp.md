---
title: "(Radar) 3. CW 수신 체인을 C++로 — 여섯 단계에 숨은 함정들"
description: "2편이 여섯 줄로 적은 CW 체인을 실제로 돌아가는 C++ 코드로 내린다 — 트위들 표, DC 노치의 진짜 모양, 유령 표적을 28 dB 눌러 앉히는 보정, 창과 추정기를 짝지어야 하는 이유, 그리고 켤레곱으로 뽑는 위상차까지."
date: 2026-07-30 10:00:00 +0900
slug: 'cw-receive-chain-cpp'
categories: [Dev, Radar]
series: radar
series_order: 3
tags: [radar, cw-radar, cpp, fft, dsp, doppler, windowing, cfar, signal-processing, radar-sensor]
math: true
---

[2편](/posts/cw-vs-fmcw-radar/)은 CW 체인을 여섯 단계로 적어 두고 끝났다. DC 제거, I/Q 보정, 윈도잉, 복소 FFT 한 번, 검출, 각도. 문장으로는 여섯 줄이지만 코드로 내리면 각 줄마다 결정해야 할 것이 생기고, 그 결정 몇 개가 최종 정밀도를 통째로 정한다.

이 글은 그 여섯 단계를 C++17로 구현한다. 외부 라이브러리는 쓰지 않는다. FFT까지 직접 짜는 이유는 성능이 아니라, 트위들을 어떻게 들고 있느냐 같은 사소해 보이는 선택이 뒤쪽 위상 정확도로 흘러나오기 때문이다.

미리 밝혀 둘 것이 하나 있다. **이 글에 나오는 숫자는 전부 아래 코드를 실제로 컴파일해 돌린 실측값**이고, 합성한 표적으로 잰 것이라 참값을 알고 있어 오차를 그대로 뽑을 수 있다. 실제 센서에서 나오는 숫자는 아니다.

* * *

## 1. 무엇을 만드는가

입력은 3채널 복소 IQ 스트림이고, 출력은 프레임마다 나오는 표적 목록이다. 표적 하나는 시선 속도, SNR, 방위각을 갖는다.

![CW 수신 체인 파이프라인](/assets/img/posts/cw-receive-chain-cpp/fig1-pipeline.svg){: width="860"}
_그림 1. 프레임 하나가 지나가는 길. 파란색이 FFT 앞의 전처리, 주황색이 스펙트럼 영역, 초록색이 추정이다._

상수부터 한곳에 모은다. 2편에서 세운 24 GHz 골프 설정을 그대로 쓴다.

```cpp
struct Config {
    double fs     = 50000.0;  // ADC 표본화 주파수 [Hz]
    int    n_fft  = 512;      // 프레임 길이 = FFT 길이
    int    hop    = 128;      // STFT 이동 간격 (75% 겹침)
    double lambda = 0.0125;   // 24 GHz 파장 [m]
    double d_ant  = 0.00625;  // 안테나 간격 [m] (= λ/2)

    double frame_time() const { return n_fft / fs; }
    double bin_hz()     const { return fs / n_fft; }
    double dv()         const { return lambda / (2 * frame_time()); }
    double v_max()      const { return lambda * fs / 4; }
};
```

이 네 줄에서 나머지가 전부 따라 나온다.

| 값 | 식 | 결과 |
| :--- | :--- | ---: |
| 코히어런트 관측 시간 $T$ | $N/f_s$ | 10.24 ms |
| 빈 폭 | $1/T$ | 97.66 Hz |
| 속도 분해능 $\Delta v$ | $\lambda/2T$ | 0.610 m/s |
| 비모호 속도 | $\lambda f_s/4$ | ±156.25 m/s |
| 프레임 간격 | $\text{hop}/f_s$ | 2.56 ms |

2편에서 관측 시간의 상한을 17 ms로 잡았다. 표적이 감속하면서 도플러가 흐르기 때문이다. 512 샘플은 그 상한 아래에 있으면서 스핀 측대역을 가르는 하한 1 ms 위에 있는, 위아래로 묶인 구간 안의 선택이다.

* * *

## 2. FFT — 트위들은 표로 들고 있어야 한다

기수-2 Cooley-Tukey는 짧다. 다만 트위들 인자를 어떻게 만드느냐에서 한 번 갈린다.

```cpp
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

교과서 예제는 보통 안쪽 루프에서 `w *= wl` 로 트위들을 굴린다. 짧고 곱셈도 아낀다. 문제는 그 곱이 512번 누적되면서 위상 오차가 쌓인다는 것이다. 진폭 스펙트럼만 볼 거라면 티가 잘 안 나지만, 이 체인의 마지막 단계는 **채널 간 위상차를 0.1° 수준에서 읽는 일**이다. 미리 계산한 표를 들고 있으면 그 항이 아예 없어지고, 객체 하나를 프레임마다 재사용하므로 비용도 초기화 한 번뿐이다.

한 가지 더. 복소 FFT의 빈 번호는 절반 위에서 음의 주파수를 뜻한다. 실수 신호만 다루다 오면 반드시 한 번 걸리는 지점이다.

```cpp
inline double bin_to_hz(double bin, int n, double fs) {
    if (bin >= n / 2.0) bin -= n;
    return bin * fs / n;
}
```

CW에서 도플러의 부호는 접근과 이탈을 가르는 정보다. 이 다섯 줄을 빠뜨리면 멀어지는 표적이 전부 초고속으로 다가오는 표적으로 읽힌다.

* * *

## 3. DC·클러터 제거 — 노치는 브릭월이 아니다

거리 게이트가 없으니 벽, 삼각대, 바닥, TX 누설이 전부 0 Hz에 쌓인다. 프레임 평균을 빼는 것이 가장 싼 방법이다.

```cpp
inline void remove_dc(std::vector<cf>& x) {
    const cf mean = std::accumulate(x.begin(), x.end(), cf{}) / double(x.size());
    for (auto& s : x) s -= mean;
}
```

2편은 이것을 "폭이 $\approx 1/T$인 DC 노치"라고 적고 그 아래 구간이 죽는다고 했다. 코드로 재 보면 그 진술은 방향은 맞지만 모양은 더 부드럽다. 같은 표적을 DC 제거 전후로 재서 손실만 뽑으면 이렇다.

| 표적 속도 | 빈 위치 | 손실 |
| ---: | ---: | ---: |
| 0.10 m/s | 0.16 | −16.6 dB |
| 0.20 m/s | 0.33 | −9.2 dB |
| 0.30 m/s | 0.49 | −4.3 dB |
| 0.40 m/s | 0.66 | −2.3 dB |
| 0.50 m/s | 0.82 | −1.0 dB |
| 0.61 m/s | 1.00 | 0.0 dB |

−3 dB 지점은 약 0.35 m/s이고, **빈 1개(0.61 m/s)에 도달하면 손실이 정확히 0이 된다.** 평균을 빼는 것은 DC 빈 하나를 지우는 일이라, 표적이 정수 빈에 정확히 앉으면 DC로 새는 성분이 없어 아무것도 잃지 않기 때문이다. 즉 $\lambda/2T$는 노치의 **폭 스케일**이지 그 아래가 통째로 죽는 경계가 아니다.

실무에서 더 중요한 것은 따로 있다. 아날로그 HPF의 코너가 300 Hz면 최소 측정 속도가 1.875 m/s이고, 이쪽이 훨씬 단단한 벽이다. 디지털 노치를 아무리 다듬어도 아날로그에서 이미 잘린 신호는 돌아오지 않는다.

> **남은 DC는 유령 표적으로 검출된다**: 평균 차감 뒤에도 클러터가 완전히 사라지지는 않는다. 뒤에 나올 전체 실행에서 0 Hz 근처에 SNR 12.3 dB짜리 검출이 하나 잡히는데, 표적이 아니라 잔재다. 검출 단계에서 DC 주변 몇 빈을 아예 게이팅하지 않으면 이것이 "0.12 m/s로 다가오는 표적"으로 보고된다.
{: .prompt-warning }

* * *

## 4. I/Q 불균형 보정 — 유령을 28 dB 아래로

2편은 CW에서 I/Q 불균형이 특히 치명적이라고 했다. 이미지가 $-f_d$에 서는데 그 자리가 "같은 속도로 멀어지는 표적"이라는, 물리적으로 완벽히 그럴듯한 위치이기 때문이다.

보정은 복소 정현파의 I와 Q가 등전력이고 서로 무상관이라는 성질을 쓴다. 블록에서 세 개의 통계량만 모으면 된다.

```cpp
struct IqGain {
    double gain    = 1.0;  // Q 채널 이득 보정 계수
    double sin_psi = 0.0;  // 직교 오차 sin ψ
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
    const double cos_psi = std::sqrt(1.0 - k.sin_psi * k.sin_psi);
    for (auto& s : x) {
        const double i = s.real();
        const double q = s.imag() * k.gain;
        s = cf{i, (q - k.sin_psi * i) / cos_psi};
    }
}
```

`estimate_iq`는 반드시 DC를 제거한 뒤에 불러야 한다. 상주하는 누설이 남아 있으면 그 DC가 $E[I^2]$와 $E[IQ]$를 통째로 지배해서 추정이 클러터를 따라간다.

이득 0.5 dB, 위상 3°를 주입하고 재 보면 2편의 예측과 맞아떨어진다.

![I/Q 불균형이 만드는 유령 표적](/assets/img/posts/cw-receive-chain-cpp/fig2-iq-image.svg){: width="860"}
_그림 2. 보정 없이는 −67, −45 m/s 자리에 유령이 선다. 실제 표적은 +67(공), +45(클럽)뿐이다._

| 항목 | 보정 없음 | 보정 적용 |
| :--- | ---: | ---: |
| 공 (+67 m/s) | 58.6 dB | 58.6 dB |
| 유령 (−67 m/s) | 30.7 dB | 검출 안 됨 |
| 유령 (−45 m/s) | 22.7 dB | 검출 안 됨 |

억압비가 $58.6 - 30.7 = 27.9$ dB다. 2편이 $\mathrm{IRR} \approx -20\log_{10}(\sqrt{\epsilon^2+\psi^2}/2)$로 계산한 값이 28.1 dB였으니 0.2 dB 안에서 맞는다. 식이 맞다는 확인이자, 구현이 그 식대로 동작한다는 확인이다.

> **이 추정기가 기대는 가정**: 블록 안의 신호가 원점 대칭이어야 한다. 표적이 하나뿐이고 SNR이 충분하면 잘 맞지만, 강한 정지 클러터가 남아 있거나 표적이 없는 프레임에서는 추정이 흔들린다. 실제 장비에서는 프레임마다 새로 추정하기보다 **알려진 조건에서 한 번 재서 상수로 굳히고**, 온도가 크게 변할 때만 갱신하는 편이 안정적이다.
{: .prompt-tip }

* * *

## 5. 창 — 사이드로브가 약한 표적의 진폭을 먹는다

2편은 윈도잉의 이유를 한 줄로 적었다. 강한 표적의 사이드로브가 약한 표적을 덮는다는 것이다. 코드로 재면 "덮는다"가 정확히 무엇인지 나온다.

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

두 가지가 들어 있다. 하나는 분모의 $N$이다. 대칭형($N-1$로 나누는 쪽)이 아니라 **주기형 Hann**을 써야 스펙트럼 해석에서 편향이 생기지 않는다. 다른 하나는 코히어런트 이득 `cg`로 나누는 것이다. Hann의 평균은 0.5라 그냥 곱하면 모든 진폭이 6 dB 내려앉는다.

강한 표적 옆에 40 dB 약한 표적을 두고 그 진폭을 재 봤다.

| 간격 | 창 | 참 진폭 | 측정값 | 오차 |
| ---: | :--- | ---: | ---: | ---: |
| 3 빈 | 직사각 | −40 dB | −20.5 dB | +19.5 dB |
| 3 빈 | Hann | −40 dB | −30.2 dB | +9.8 dB |
| 6 빈 | 직사각 | −40 dB | −27.1 dB | +12.9 dB |
| 6 빈 | Hann | −40 dB | −41.2 dB | −1.2 dB |
| 12 빈 | 직사각 | −40 dB | −31.4 dB | +8.6 dB |
| 12 빈 | Hann | −40 dB | −40.4 dB | −0.4 dB |

직사각 창에서는 12 빈이나 떨어져도 8.6 dB를 틀린다. 약한 표적을 재는 게 아니라 **강한 표적의 사이드로브 바닥을 재고 있는 것**이다. Hann은 6 빈부터 1 dB 안으로 들어온다. 다만 3 빈에서는 Hann도 9.8 dB를 틀리는데, 이건 사이드로브가 아니라 메인로브가 겹치는 영역이라 창을 바꿔서 풀 문제가 아니다.

대가도 있다. Hann은 메인로브가 넓어진 만큼 표적이 빈 사이에 있으면 피크가 내려앉는다.

| 빈 소수부 | 피크 |
| ---: | ---: |
| 0.00 | 0.00 dB |
| 0.25 | −0.35 dB |
| 0.50 | −1.42 dB |

교과서 값인 1.42 dB가 그대로 나온다. 진폭을 절대적으로 써야 한다면(RCS 추정 같은) 이 스캘롭 손실을 보간해서 되돌려야 한다. 속도만 필요하다면 무시해도 된다.

**순서가 중요하다.** DC 제거를 창보다 먼저 해야 한다. 창을 먼저 걸면 상주하던 DC가 창의 스펙트럼 모양대로 번져서, 그다음에 평균을 빼도 이미 퍼진 것은 돌아오지 않는다.

* * *

## 6. 피크 보간 — 창을 골랐으면 추정기도 그에 맞춰야 한다

빈 폭이 0.61 m/s인데 2편은 정밀도를 7.5 mm/s로 이야기했다. 그 80배 차이를 만드는 것이 보간이다. 세 점만 있으면 된다.

```cpp
const double denom = db[km] - 2 * db[k] + db[kp];
const double delta = (std::abs(denom) < 1e-12) ? 0.0
                                               : 0.5 * (db[km] - db[kp]) / denom;
```

`db`라는 이름이 핵심이다. 선형 진폭이 아니라 **로그 진폭에 포물선을 맞춰야** 한다. Hann 창의 메인로브는 로그 영역에서 포물선에 매우 가깝기 때문이다.

여기서 흔한 함정이 하나 있다. 주파수 추정 문헌에서 자주 인용되는 Jacobsen 추정기는 복소값 세 개를 그대로 쓰는 더 세련된 식이라 그냥 가져다 쓰기 쉽다.

![보간기별 오차](/assets/img/posts/cw-receive-chain-cpp/fig3-interpolation.svg){: width="860"}
_그림 3. 표적을 빈 사이에서 훑으며 잰 보간 오차. 초록이 Hann + 포물선(dB), 보라가 Hann + Jacobsen이다._

| 창 + 추정기 | 최대 오차 |
| :--- | ---: |
| Hann + 포물선(dB) | 0.016 bin |
| 직사각 + 포물선(dB) | 0.167 bin |
| Hann + Jacobsen | 0.250 bin |

Jacobsen 추정기는 **직사각 창을 전제로 유도된 것**이라 Hann에 그대로 쓰면 포물선보다 16배 나쁘다. 창과 추정기는 짝으로 골라야 한다는 이야기이고, 창을 바꾸면 보간식도 다시 확인해야 한다는 뜻이다.

0.016 bin을 속도로 바꾸면 9.8 mm/s다. 2편이 계산한 CRLB 7.5 mm/s와 같은 자릿수다. 이게 실무적으로 중요한 결론을 하나 준다 — **정밀도의 천장은 잡음이 아니라 보간 편향이다.** SNR을 30 dB에서 60 dB로 올려도 이 항은 그대로 남는다. 더 필요하면 SNR이 아니라 보간식을 손봐야 한다.

* * *

## 7. 검출 — 잡음 바닥을 먼저 눕히고 CFAR

2편은 이 순서를 분명히 했다. 1/f 치마는 프레임마다 같은 모양으로 서는 정적 기울기라 빈 상태에서 미리 재어 나눠 버리는 쪽이 맞고, 적응 문턱은 그 위에 얹는다.

```cpp
inline std::vector<Detection> cfar_detect(const std::vector<double>& db,
                                          const Config& cfg,
                                          int guard = 4, int ref = 16,
                                          double threshold_db = 11.0) {
    std::vector<Detection> out;
    const int n = int(db.size());
    for (int k = 0; k < n; ++k) {
        const int km = (k - 1 + n) % n, kp = (k + 1) % n;
        if (!(db[k] > db[km] && db[k] >= db[kp])) continue;  // 국소 최대만

        double sum = 0; int cnt = 0;
        for (int j = guard + 1; j <= guard + ref; ++j) {
            sum += db[(k - j + n) % n] + db[(k + j) % n];
            cnt += 2;
        }
        const double noise = sum / cnt;
        if (db[k] - noise < threshold_db) continue;
        // ... 포물선 보간 뒤 Detection 채우기
    }
    return out;
}
```

보호 셀(guard)이 있는 이유는 표적 자신의 메인로브가 참조 셀에 섞이면 문턱이 표적을 따라 올라가 스스로를 지우기 때문이다. Hann의 메인로브가 약 4 빈을 차지하니 보호 셀도 그만큼 잡는다. 인덱스가 `% n`으로 감기는 것은 복소 스펙트럼이 원형이라 그렇다. 0 Hz의 왼쪽은 음의 최대 속도다.

문턱 11 dB는 2편의 계산과 붙는다. 참조 셀 32개에 $P_{fa} = 10^{-4}$면 $\alpha = N_{ref}(P_{fa}^{-1/N_{ref}} - 1)$이 10.6 dB 근처다.

* * *

## 8. 각도 — 위상차는 켤레곱으로 구한다

마지막 단계다. 같은 도플러 빈의 복소값을 채널마다 뽑아 위상차를 취한다.

```cpp
inline double phase_diff(cf a, cf b) { return std::arg(a * std::conj(b)); }

inline double aoa_rad(double dphi, double lambda, double d) {
    return std::asin(std::clamp(dphi * lambda / (2.0 * kPi * d), -1.0, 1.0));
}
```

`std::arg(a) - std::arg(b)`로 빼면 안 된다. 두 위상이 각각 $(-\pi, \pi]$로 감겨 있어서, 참 위상차가 그 경계를 넘으면 결과가 $2\pi$만큼 튄다. 켤레곱을 먼저 하고 한 번만 `arg`를 취하면 그 문제가 아예 생기지 않는다. 한 줄 차이지만 튀는 각도값을 며칠씩 쫓게 만드는 종류의 버그다.

`std::clamp`도 장식이 아니다. 잡음이나 캘리브레이션 오차 때문에 `asin`의 인자가 1을 아주 조금 넘으면 NaN이 나오고, 그 NaN은 조용히 뒷단으로 흘러간다.

복소값을 어느 빈에서 뽑을지도 결정해야 한다. 피크가 빈 사이에 있으면 정수 빈의 복소값은 창 누설 때문에 이미 회전해 있다.

```cpp
inline cf bin_value(const std::vector<cf>& X, double bin_refined) {
    const int n = int(X.size());
    const int k = int(std::floor(bin_refined));
    const double f = bin_refined - k;
    const cf a = X[(k + n) % n], b = X[(k + 1 + n) % n];
    return a * (1.0 - f) + b * f;
}
```

세 채널 모두 **같은 실수 빈 위치**에서 뽑는 것이 중요하다. 채널마다 각자 피크를 찾아 각자의 정수 빈을 쓰면, 두 채널이 서로 다른 빈을 고르는 순간 위상차에 빈 하나만큼의 가짜 회전이 들어간다. 기준 채널에서 한 번 찾은 `bin_refined`를 세 채널에 공통으로 적용해야 한다.

### 캘리브레이션 — 각도 정확도의 진짜 한계

2편에서 각도 정밀도의 실제 한계는 열잡음이 아니라 채널 간 오프셋이고 그 값이 온도에 따라 흐른다고 적었다. 구현에서는 상수 하나를 빼는 것으로 끝나지만, 그 상수를 어떻게 얻느냐가 전부다.

```cpp
struct ChannelCal { double phase_offset[3] = {0, 0, 0}; };

inline double calibrated_diff(const std::vector<cf>& Xa, const std::vector<cf>& Xb,
                              double bin_refined, double offset) {
    return std::remainder(phase_diff(bin_value(Xa, bin_refined),
                                     bin_value(Xb, bin_refined)) - offset,
                          2.0 * kPi);
}
```

`std::remainder`를 쓰는 이유는 오프셋을 뺀 뒤에도 결과를 $(-\pi, \pi]$로 되접어야 하기 때문이다. 오프셋 자체는 알려진 방위에 기준 표적을 두고 재며, 세션 시작과 한 시간 뒤의 값을 로그로 남겨야 각도 사양을 온도 조건과 함께 적을 수 있다.

세 채널을 'ㄴ' 자로 놓고 수평·수직 위상차에서 스핀축까지 가는 기하는 [3채널 레이더 센서로 스핀축 계산하기](/posts/cpp-3-channel-radar-sensor-spin-axis-calculation/)에 따로 정리해 두었다.

* * *

## 9. 전부 통과시키면

프레임 하나에 클럽(45 m/s, 방위 −4°)과 공(67 m/s, 방위 +6°)을 넣고, TX 누설과 정지 클러터를 DC로 얹고, 이득 0.5 dB와 위상 3°의 불균형까지 주입한 뒤 체인을 돌린다.

```cpp
auto x = ch[c];
remove_dc(x);
apply_iq(x, estimate_iq(x));
apply_window(x, w);
fft(x);
```

| 표적 | 참 속도 | 추정 속도 | 오차 | SNR | 추정 방위각 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 공 | 67.00 m/s | 66.991 m/s | −9 mm/s | 58.6 dB | 6.00° (참 6.0°) |
| 클럽 | 45.00 m/s | 44.990 m/s | −10 mm/s | 50.6 dB | −4.05° (참 −4.0°) |

두 표적의 속도 오차가 −9, −10 mm/s로 거의 같다. 잡음이 만든 오차라면 두 값이 SNR에 따라 달라야 하는데(공이 클럽보다 8 dB 높다) 그렇지 않다. **6절에서 잰 보간 편향 9.8 mm/s가 그대로 나타난 것**이고, 계통 오차라는 뜻이다. 잡음을 줄여서는 없앨 수 없고, 보간식을 바꿔야 없어진다.

각도 오차는 공 0.00°, 클럽 0.05°다. 클럽 쪽이 조금 나쁜 것은 SNR이 8 dB 낮아서인데, 위상 추정 오차가 SNR에 반비례한다는 것과 방향이 맞는다.

* * *

## 10. 정리, 그리고 코드가 말해주지 않는 것

여섯 단계를 코드로 내리면서 나온 결정들을 모으면 이렇다.

1. 트위들은 표로 들고 있는다 — 위상차를 읽을 거라면 누적 오차를 만들지 않는다
2. 복소 FFT의 상위 절반은 음의 주파수다 — CW에서 이 부호가 접근과 이탈을 가른다
3. DC 제거를 창보다 먼저 — 순서를 바꾸면 되돌릴 수 없다
4. I/Q 보정은 DC 제거 뒤에 — 누설이 통계량을 지배하지 않도록
5. Hann과 포물선(dB)은 짝이다 — 창을 바꾸면 보간식도 다시 본다
6. 위상차는 켤레곱으로 — 뺄셈은 경계에서 튄다
7. 세 채널은 같은 실수 빈에서 뽑는다 — 채널마다 피크를 찾으면 가짜 회전이 들어간다

그리고 이 코드로는 확인할 수 없는 것들을 정직하게 적어 둔다. 합성 신호에는 실제 믹서의 1/f 잡음도, 프레임마다 모양이 달라지는 이동 클러터도, 온도에 따라 흐르는 채널 오프셋도 없다. 2편의 마지막 절에서 잡음 바닥·I–Q 궤적·채널 간 위상 오프셋 셋을 실측으로 잡아야 한다고 적은 이유가 그것이고, 그 셋은 코드가 아니라 장비 앞에서만 나온다.

여기까지가 한 프레임이다. 다음 글에서는 프레임을 시간축으로 이어 붙이는 쪽 — STFT로 뽑은 추정치 스무 개를 궤적으로 묶고, 임팩트 시점으로 역외삽하며, 프레임 사이에서 표적을 잃지 않고 따라가는 추적 문제를 다룰 예정이다.

* * *

## 참고 자료

- M. A. Richards, *Fundamentals of Radar Signal Processing*, McGraw-Hill — 검출 이론과 CFAR의 표준 레퍼런스
- F. J. Harris, "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform," *Proc. IEEE*, 1978 — 창 함수의 코히어런트 이득·스캘롭 손실·사이드로브를 한 표에 정리한 고전
- E. Jacobsen, P. Kaiser, "Fast, Accurate Frequency Estimators," *IEEE Signal Processing Magazine*, 2007 — 보간 추정기들의 비교와 각각의 전제
- B.-K. Park et al., "Arctangent Demodulation With DC Offset Compensation in Quadrature Doppler Radar Receiver Systems," *IEEE Trans. MTT*, 2007 — I/Q 불균형과 DC 오프셋 보상
