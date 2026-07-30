---
title: "(C++) iFFT & FFT 알고리즘 구현"
description: "센서가 내주는 스펙트럼을 iFFT로 시간축에 되돌리고, 프레임을 이어붙여 더 긴 FFT를 걸어 분해능을 높이려 했다. FFTW 사용에서 놓친 것들과, 관측 시간을 늘리는 데 따르는 조건을 정리했다."
date: 2023-11-21 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, visual-studio, fft, ifft, fftw, dsp, resolution]
math: true
---
## 하려던 것

센서는 프레임마다 512점짜리 스펙트럼을 실수부/허수부 로그로 내준다. 이걸 그대로 보면 빈 폭이 정해져 있어서 가까이 붙은 성분이 구분되지 않는다.

주파수 분해능은 코히어런트 관측 시간 $T$의 역수다.

$$
\Delta f = \frac{1}{T}
$$

관측 시간을 2배로 늘리면 분해능이 2배 좋아진다. 그런데 센서에서 나오는 건 이미 변환된 스펙트럼이라 시간축 데이터가 없다.

그래서 이렇게 했다. 스펙트럼에 **iFFT를 걸어 시간축으로 되돌리고**, 여러 프레임을 이어붙인 뒤, 더 긴 FFT를 다시 건다. 프레임 하나가 32 ms면 두 개를 붙여 64 ms, 네 개면 128 ms가 된다.

## 전체 코드

```c++
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <complex>
#include "fftw3.h"
#pragma comment(lib,"libfftw3-3.lib")
#pragma comment(lib,"libfftw3f-3.lib")
#pragma comment(lib,"libfftw3l-3.lib")

const int FFT_POINT = 512; // FFT 포인트 수

std::vector<std::vector<double>> readTransposeAndReverseData(const std::string& filePath);
std::vector<std::vector<std::complex<double>>> reverseTransposeData(const std::vector<std::vector<std::complex<double>>>& data);
std::vector<std::complex<double>> combineRows(const std::vector<std::vector<std::complex<double>>>& data, int numLines);
std::vector<std::vector<double>> calculateAmplitude(const std::vector<std::vector<std::complex<double>>>& fftData);

int main()
{
    std::string realFilePath = "2023-11-01 15-03-51_output_real1.log";
    std::string imaginFilePath = "2023-11-01 15-03-51_output_imagin1.log";

    // 디렉토리 이름 추출
    std::size_t lastUnderscorePos = realFilePath.find_last_of('_');
    std::string directoryName = realFilePath.substr(0, lastUnderscorePos);

    std::cout << "directoryName: " << directoryName << std::endl;

    // 디렉토리 생성
    std::string mkdirCommand = "mkdir \"" + directoryName + "\"";
    system(mkdirCommand.c_str());

    std::vector<std::vector<double>> realData = readTransposeAndReverseData(realFilePath);
    std::vector<std::vector<double>> imaginData = readTransposeAndReverseData(imaginFilePath);

    fftw_complex* in, * out;
    fftw_plan p;
    in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * FFT_POINT);
    out = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * FFT_POINT);
    p = fftw_plan_dft_1d(FFT_POINT, in, out, FFTW_BACKWARD, FFTW_ESTIMATE);

    std::vector<std::vector<std::complex<double>>> fftResults; // 복소수 벡터

    for (size_t i = 0; i < realData.size(); ++i) {
        for (size_t j = 0; j < FFT_POINT; ++j) {
            in[j][0] = realData[i][j];
            in[j][1] = imaginData[i][j];
        }

        fftw_execute(p);    //iFFT

        std::vector<std::complex<double>> rowResult;
        for (int j = 0; j < FFT_POINT; ++j) {
            std::complex<double> value(out[j][0] / FFT_POINT, out[j][1] / FFT_POINT); // 정규화
            rowResult.push_back(value);
        }
        fftResults.push_back(rowResult);
    }

    // transpose & reverse for output
    std::vector<std::vector<std::complex<double>>> transposedResults = reverseTransposeData(fftResults);

    // 결과 파일을 새 디렉토리에 저장
    std::ofstream realFile(directoryName + "/output_real1_iFFT.log");
    std::ofstream imagFile(directoryName + "/output_imag1_iFFT.log");
    for (const auto& row : transposedResults) {
        for (const auto& value : row) {
            realFile << value.real() << "\t";
            imagFile << value.imag() << "\t";
        }
        realFile << "\n";
        imagFile << "\n";
    }
    realFile.close();
    imagFile.close();

    // FFT 설정 및 실행
    for (int period = 1; period <= 4; period *= 2) {
        std::vector<std::complex<double>> combinedData = combineRows(fftResults, period);
        int N = FFT_POINT * period;
        int numSegments = combinedData.size() / N;

        std::vector<std::vector<std::complex<double>>> segmentResults;

        for (int segment = 0; segment < numSegments; segment++) {
            fftw_complex* in_combined = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * N);
            fftw_complex* out_combined = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * N);
            fftw_plan fft_plan_combined = fftw_plan_dft_1d(N, in_combined, out_combined, FFTW_FORWARD, FFTW_ESTIMATE);

            // 입력 데이터 복사
            for (int i = 0; i < N; ++i) {
                int index = segment * N + i;
                in_combined[i][0] = combinedData[index].real();
                in_combined[i][1] = combinedData[index].imag();
            }

            // FFT 수행
            fftw_execute(fft_plan_combined);

            // 결과를 세그먼트 결과 벡터에 저장
            std::vector<std::complex<double>> segmentResult;
            for (int i = 0; i < N; ++i) {
                segmentResult.push_back(std::complex<double>(out_combined[i][0], out_combined[i][1]));
            }
            segmentResults.push_back(segmentResult);

            // 자원 해제
            fftw_destroy_plan(fft_plan_combined);
            fftw_free(in_combined);
            fftw_free(out_combined);
        }

        // 전치 및 역순 처리
        auto transposedReversedResults = reverseTransposeData(segmentResults);
        auto amplitudeResults = calculateAmplitude(transposedReversedResults);

        // 결과를 파일에 저장
        std::ofstream fftRealFile(directoryName + "/output_real1_FFT_" + std::to_string(period * 32) + "ms.log");
        std::ofstream fftImagFile(directoryName + "/output_imag1_FFT_" + std::to_string(period * 32) + "ms.log");
        std::ofstream fftAmpFile(directoryName + "/output_amplitude1_FFT_" + std::to_string(period * 32) + "ms.log");

        for (size_t i = 0; i < transposedReversedResults.size(); ++i) {
            for (size_t j = 0; j < transposedReversedResults[i].size(); ++j) {
                fftRealFile << transposedReversedResults[i][j].real() << "\t";
                fftImagFile << transposedReversedResults[i][j].imag() << "\t";
                fftAmpFile << amplitudeResults[i][j] << "\t";
            }
            fftRealFile << "\n";
            fftImagFile << "\n";
            fftAmpFile << "\n";
        }
        fftRealFile.close();
        fftImagFile.close();
        fftAmpFile.close();
    }

    return 0;
}
```

보조 함수들이다.

```c++
// FFT 데이터로부터 진폭 계산
std::vector<std::vector<double>> calculateAmplitude(const std::vector<std::vector<std::complex<double>>>& fftData) {
    std::vector<std::vector<double>> amplitudeData(fftData.size(), std::vector<double>(fftData[0].size()));
    for (size_t i = 0; i < fftData.size(); ++i) {
        for (size_t j = 0; j < fftData[i].size(); ++j) {
            amplitudeData[i][j] = std::abs(fftData[i][j]);
        }
    }
    return amplitudeData;
}

// 여러 줄의 데이터를 하나의 긴 데이터로 결합
std::vector<std::complex<double>> combineRows(const std::vector<std::vector<std::complex<double>>>& data, int period) {
    std::vector<std::complex<double>> combined;
    for (size_t i = 0; i < data.size(); i += period) {
        for (int line = 0; line < period; ++line) {
            if (i + line < data.size()) {
                combined.insert(combined.end(), data[i + line].begin(), data[i + line].end());
            }
        }
    }
    return combined;
}

std::vector<std::vector<double>> readTransposeAndReverseData(const std::string& filePath) {
    std::ifstream file(filePath);
    std::vector<std::vector<double>> data, transposedData;
    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string value;
        std::vector<double> row;

        while (std::getline(ss, value, '\t')) {
            row.push_back(std::stod(value));
        }

        data.push_back(row);
    }

    size_t rows = data.size();
    if (!data.empty()) {
        size_t cols = data[0].size();
        transposedData.resize(cols);

        for (size_t i = 0; i < cols; ++i) {
            transposedData[i].resize(rows);
            for (size_t j = 0; j < rows; ++j) {
                transposedData[i][j] = data[rows - 1 - j][i];
            }
        }
    }

    return transposedData;
}

std::vector<std::vector<std::complex<double>>> reverseTransposeData(const std::vector<std::vector<std::complex<double>>>& data) {
    size_t rows = data.size();
    size_t cols = data[0].size();
    std::vector<std::vector<std::complex<double>>> reversedData(cols, std::vector<std::complex<double>>(rows));

    for (size_t i = 0; i < rows; ++i) {
        for (size_t j = 0; j < cols; ++j) {
            reversedData[cols - 1 - j][i] = data[i][j]; // 전치 후 각 열을 역순으로 처리
        }
    }
    return reversedData;
}
```

## combineRows의 period가 아무 일도 안 한다

정리하면서 제일 먼저 눈에 띈 부분이다.

```c++
for (size_t i = 0; i < data.size(); i += period) {
    for (int line = 0; line < period; ++line) {
        if (i + line < data.size())
            combined.insert(combined.end(), data[i + line].begin(), data[i + line].end());
    }
}
```

`i`가 `period`씩 늘고 안쪽에서 `i`부터 `i+period-1`까지를 붙인다. 결과는 행 0, 1, 2, ... 순서 그대로다. **`period`가 무엇이든 결과가 같다.** 그냥 전체를 이어 붙이는 것과 동일하다.

`period`가 실제로 쓰이는 곳은 `N = FFT_POINT * period` 한 군데뿐이다. 즉 데이터는 항상 같고 자르는 길이만 달라진다. 의도가 그거였다면 이 함수는 인자를 받을 이유가 없다.

```c++
std::vector<std::complex<double>> flatten(const std::vector<std::vector<std::complex<double>>>& data)
{
    std::vector<std::complex<double>> out;
    size_t total = 0;
    for (const auto& r : data) total += r.size();
    out.reserve(total);                       // 재할당 방지
    for (const auto& r : data) out.insert(out.end(), r.begin(), r.end());
    return out;
}
```

인자 이름도 안 맞는다. 선언은 `numLines`, 정의는 `period`다. 선언과 정의에서 인자 이름이 다르면 컴파일은 되지만 나중에 읽을 때 헷갈린다.

## FFTW에서 놓친 것들

### plan을 루프 안에서 만든다

```c++
for (int segment = 0; segment < numSegments; segment++) {
    fftw_complex* in_combined = (fftw_complex*)fftw_malloc(...);
    fftw_plan fft_plan_combined = fftw_plan_dft_1d(N, ..., FFTW_ESTIMATE);
    // ...
    fftw_destroy_plan(fft_plan_combined);
}
```

세그먼트마다 버퍼를 잡고 plan을 만들고 부수기를 반복한다. plan 생성은 `FFTW_ESTIMATE`라도 공짜가 아니다. 크기가 같은 변환을 반복하는 상황이면 plan은 한 번만 만들어야 한다.

```c++
fftw_complex* in  = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * N);
fftw_complex* out = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * N);
fftw_plan p = fftw_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_ESTIMATE);

for (int seg = 0; seg < numSegments; ++seg) {
    // in 을 채우고
    fftw_execute(p);
    // out 을 읽는다
}

fftw_destroy_plan(p);
fftw_free(in);
fftw_free(out);
```

plan은 특정 버퍼 주소에 묶여 있어서 `fftw_execute(p)`는 항상 그 버퍼를 쓴다. 다른 버퍼에 같은 plan을 적용하려면 `fftw_execute_dft(p, other_in, other_out)`를 쓴다.

### 첫 번째 plan이 정리되지 않는다

iFFT용으로 만든 `p`, `in`, `out`은 `fftw_destroy_plan`도 `fftw_free`도 안 한다. 한 번 실행하고 끝나는 프로그램이라 티가 안 나지만, 이걸 함수로 만들어 반복 호출하면 계속 쌓인다.

### FFTW_MEASURE로 바꾸면 데이터가 날아간다

성능이 아쉬워서 `FFTW_ESTIMATE`를 `FFTW_MEASURE`로 바꾸려 한 적이 있다. 문서를 보고 그만뒀다.

`FFTW_MEASURE`는 여러 알고리즘을 실제로 돌려보고 제일 빠른 걸 고른다. 그 과정에서 **입력 버퍼를 덮어쓴다**. 데이터를 채운 다음 plan을 만들면 데이터가 사라진다.

plan을 먼저 만들고 나서 데이터를 채우면 된다. 위처럼 루프 밖에서 plan을 만드는 구조로 바꾸면 자연스럽게 그 순서가 된다.

### 정규화 관례

FFTW는 정규화를 하지 않는다. iFFT 다음에 FFT를 하면 원래 값의 $N$배가 나온다. 이 코드는 iFFT 결과를 `FFT_POINT`로 나눠서 맞추고 있다.

그런데 뒤의 긴 FFT에는 정규화가 없다. 진폭을 절대값으로 해석해야 한다면 이 스케일을 알고 있어야 한다. 진폭 비교나 피크 위치만 본다면 상관없다.

`libfftw3f-3.lib`(float)과 `libfftw3l-3.lib`(long double)까지 링크되어 있는데, 코드는 `double` API만 쓴다. 필요한 건 `libfftw3-3.lib` 하나다.

## 범위 검사가 없다

```c++
for (size_t j = 0; j < FFT_POINT; ++j) {
    in[j][0] = realData[i][j];
    in[j][1] = imaginData[i][j];
}
```

`realData[i]`의 크기가 512보다 작으면 그대로 범위 밖 접근이다. 로그 파일의 줄 수가 512가 아니면 이렇게 된다.

`readTransposeAndReverseData`가 전치를 하기 때문에, 여기서 필요한 건 파일의 **줄 수**가 512여야 한다는 조건이다. 열 수가 아니다. 이게 코드만 봐서는 잘 안 보인다.

그리고 `size_t j`와 `int FFT_POINT`를 비교해서 부호 경고가 난다. 실수부와 허수부 파일의 크기가 같은지도 확인하지 않는다.

```c++
if (realData.size() != imaginData.size())
    throw std::runtime_error("real/imag row count mismatch");
for (size_t i = 0; i < realData.size(); ++i)
    if (realData[i].size() < FFT_POINT || imaginData[i].size() < FFT_POINT)
        throw std::runtime_error("row too short at " + std::to_string(i));
```

`std::stod`도 예외를 던진다. 로그에 빈 줄이나 숫자가 아닌 값이 하나만 있어도 프로그램이 그대로 끝난다. 어느 줄에서 실패했는지 알려주는 처리가 있으면 원인을 바로 찾을 수 있다.

## 디렉토리 생성

```c++
std::string mkdirCommand = "mkdir \"" + directoryName + "\"";
system(mkdirCommand.c_str());
```

프로세스를 하나 띄운다. 경로에 특수문자가 있으면 셸이 다르게 해석하고, 이미 있으면 에러 메시지가 콘솔에 찍힌다. 반환값도 안 본다.

```c++
#include <filesystem>
std::filesystem::create_directories(directoryName);
```

한 줄이고, 이미 있으면 아무 일도 안 하고, 중간 경로까지 만든다.

디렉토리 이름을 `realFilePath.find_last_of('_')`로 뽑는 것도 파일명 규칙에 의존한다. 파일명에 `_`가 없으면 `npos`가 나오고 `substr(0, npos)`는 전체 문자열이라, 파일명 그대로 디렉토리를 만들려고 한다.

## 전치와 역순은 주석이 필요하다

`readTransposeAndReverseData`와 `reverseTransposeData`는 전치와 역순을 동시에 한다. 왜 그렇게 하는지가 코드에 없다.

```c++
transposedData[i][j] = data[rows - 1 - j][i];
```

이 한 줄에 두 가지 변환이 겹쳐 있다. 로그가 어떤 축 순서로 저장되어 있고 어떤 순서가 필요한지를 아는 사람만 읽을 수 있다. 몇 달 뒤에 다시 보면 자기도 모른다.

이런 코드일수록 주석에 "입력은 [시간][빈], 출력은 [빈][시간], 시간축은 최신이 먼저" 같은 걸 적어둬야 한다. 함수 이름에 `Reverse`가 있어도 무엇을 뒤집는지는 안 나온다.

## 관측 시간을 늘리면 항상 좋아지나

코드 얘기는 여기까지고, 이 방법 자체의 조건이 있다.

$\Delta f = 1/T$는 신호가 그 시간 동안 **같은 주파수를 유지할 때** 성립한다. 표적이 가속하면 관측 구간 안에서 주파수가 변하고, 스펙트럼이 한 점에 모이지 않고 퍼진다. 관측 시간을 늘릴수록 퍼짐이 커져서, 어느 지점을 넘으면 오히려 나빠진다.

가속도 $a$인 표적을 시간 $T$ 동안 관측하면 도플러가 이만큼 이동한다.

$$
\Delta f_d = \frac{2 a T}{\lambda}
$$

이 값이 빈 폭 $1/T$를 넘지 않아야 한다는 조건에서 $T$의 상한이 나온다.

$$
T < \sqrt{\frac{\lambda}{2a}}
$$

즉 관측 시간에는 표적의 운동이 정하는 천장이 있고, 그 위로 올리면 분해능이 좋아지는 게 아니라 피크가 뭉개진다. 32 → 64 → 128 ms로 늘려가며 비교한 게 사실 이 천장을 찾는 실험이었던 셈이다. 어느 길이에서 피크가 가장 뾰족한지 보면 된다.

같은 이야기를 [CW와 FMCW 비교](/posts/cw-vs-fmcw-radar/) 쪽에 더 정리해뒀다.

한 가지 더, 긴 FFT를 직사각 창으로 돌리면 누설이 크다. 약한 표적이 강한 표적의 사이드로브에 묻힌다. Hann 창을 걸면 그 부분이 개선되는데, 대신 메인로브가 넓어져서 분해능 이득의 일부를 도로 내준다. 이 맞바꿈은 [CW 수신 체인](/posts/cw-receive-chain-cpp/) 5절에 실제 측정값과 같이 적었다.

## 정리하면

- `combineRows`의 `period`는 결과에 영향을 주지 않는다. 그냥 이어붙이는 함수였다
- 같은 크기 변환을 반복하면 plan을 루프 밖에서 한 번만 만든다. 다른 버퍼에 쓰려면 `fftw_execute_dft`
- `FFTW_MEASURE`는 plan 생성 중 입력 버퍼를 덮어쓴다. plan을 먼저 만들고 데이터를 채운다
- FFTW는 정규화를 안 한다. 왕복하면 $N$배가 된다
- 파일에서 읽은 데이터는 크기를 검사하고 들어가야 한다. 로그 한 줄이 짧으면 범위 밖 접근이다
- 관측 시간을 늘리면 분해능이 좋아지지만, 표적이 가속하면 상한이 생긴다

## 참고

- [FFTW 3 매뉴얼](https://www.fftw.org/fftw3_doc/)
- [FFTW: Planner Flags](https://www.fftw.org/fftw3_doc/Planner-Flags.html)
