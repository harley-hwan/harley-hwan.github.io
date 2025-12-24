---
title: "(c++) iFFT & FFT algorithm"
description: "C++, Visual Studio, FFT, iFFT, inverse FFT, 고속 푸리에 변환, Fast Fourier Transform"
date: 2023-11-21 10:00:00 +0900
categories: [Dev, C++]
tags: [C++, Visual Studio, FFT, iFFT, inverse FFT, 고속 푸리에 변환, Fast Fourier Transform]
---

# inverse FFT 한 후, 다시 FFT 연산

해당 작업은 분해능을 높이고, 노이즈를 제거하여 높은 해상도의 신호를 추출하기 위함.

<br/>

## 소스

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

    // 파일에 저장
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


std::vector<std::vector<double>> calculateAmplitude(const std::vector<std::vector<double>>& realData,
    const std::vector<std::vector<double>>& imaginData) {
    std::vector<std::vector<double>> amplitudeData(realData.size(), std::vector<double>(realData[0].size()));

    for (size_t i = 0; i < realData.size(); ++i) {
        for (size_t j = 0; j < realData[i].size(); ++j) {
            double realPart = realData[i][j];
            double imaginaryPart = imaginData[i][j];
            amplitudeData[i][j] = sqrt(realPart * realPart + imaginaryPart * imaginaryPart);
        }
    }
    return amplitudeData;
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
