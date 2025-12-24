---
title: (c++) RANSAC 알고리즘 구현 (Eigen 사용)
description: "c, c++, vs, ransac, algorithm, eigen"
date: 2023-06-09 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, ransac, algorithm, eigen]
---

# Eigen 라이브러리를 이용하여 RANSAC 구현
- 최초 작성일: 2023년 6월 9일 (금)

## 코드1

```c++
#include <iostream>
#include <vector>
#include <Eigen/Dense>

struct LineModel {
    double a, b;

    LineModel(double a = 0, double b = 0) : a(a), b(b) {}

    // Fit the line model using two points
    void fit(const Eigen::Vector2d& pt1, const Eigen::Vector2d& pt2) {
        a = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0]);
        b = pt1[1] - a * pt1[0];
    }

    // Evaluate the line model for a given x
    double eval(double x) const {
        return a * x + b;
    }

    // Calculate the error of the point to the line model
    double error(const Eigen::Vector2d& pt) const {
        return std::abs(pt[1] - eval(pt[0]));
    }
};

int main() {
    // Create synthetic data
    std::vector<Eigen::Vector2d> data;
    for (double x = -1; x <= 1; x += 0.01) {
        double y = 2 * x + 1 + 0.1 * ((double)rand() / (RAND_MAX));
        data.push_back(Eigen::Vector2d(x, y));
    }

    // RANSAC parameters
    int max_iterations = 1000;
    double inlier_threshold = 0.1;
    int min_inliers = data.size() * 0.8;

    LineModel best_model;
    int best_inlier_count = 0;

    for (int i = 0; i < max_iterations; i++) {
        // Randomly select 2 data points and fit the model
        int idx1 = rand() % data.size();
        int idx2 = rand() % data.size();
        LineModel model;
        model.fit(data[idx1], data[idx2]);

        // Count the inliers for the current model
        int inlier_count = 0;
        for (const auto& pt : data) {
            if (model.error(pt) < inlier_threshold)
                inlier_count++;
        }

        // Update the best model if current model is better
        if (inlier_count > best_inlier_count) {
            best_model = model;
            best_inlier_count = inlier_count;
        }

        // If we already have enough inliers, stop early
        if (best_inlier_count >= min_inliers)
            break;
    }

    std::cout << "Best model: y = " << best_model.a << " * x + " << best_model.b << std::endl;
    std::cout << "Inlier count: " << best_inlier_count << std::endl;

    return 0;
}

```

<br/>

## 결과1

```c++
Best model: y = 2.06363 * x + 1.06259
Inlier count: 193
```

<br/>

<br/>

## 코드2

```c++
#include <Eigen/Dense>
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>

// Define random generator
std::random_device rd;
std::mt19937 gen(rd());

double computeResidual(Eigen::MatrixXd A, Eigen::VectorXd B, Eigen::VectorXd X) {
    Eigen::VectorXd residual = B - A * X;
    return residual.norm();
}

Eigen::VectorXd ransac(const Eigen::MatrixXd& A, const Eigen::VectorXd& B, int N, double T) {
    int n_data = A.rows();
    int n_sample = 3;

    int max_cnt = 0;
    Eigen::VectorXd best_model = Eigen::VectorXd::Zero(A.cols());

    std::uniform_int_distribution<> dis(0, n_data - 1);
    for (int itr = 0; itr < N; ++itr) {
        std::vector<int> k(n_sample);
        for (int i = 0; i < n_sample; ++i) {
            k[i] = dis(gen);
        }

        Eigen::MatrixXd AA(n_sample, A.cols());
        Eigen::VectorXd BB(n_sample);
        for (int i = 0; i < n_sample; ++i) {
            AA.row(i) = A.row(k[i]);
            BB(i) = B(k[i]);
        }

        Eigen::VectorXd X = AA.colPivHouseholderQr().solve(BB);

        Eigen::VectorXd residual = B - A * X;
        int cnt = (residual.array().abs() < T).count();
        if (cnt > max_cnt) {
            best_model = X;
            max_cnt = cnt;
        }
    }

    Eigen::VectorXd residual = B - A * best_model;
    std::vector<int> in_k;
    for (int i = 0; i < n_data; ++i) {
        if (std::abs(residual(i)) < T) {
            in_k.push_back(i);
        }
    }

    Eigen::MatrixXd A2(in_k.size(), A.cols());
    Eigen::VectorXd B2(in_k.size());
    for (size_t i = 0; i < in_k.size(); ++i) {
        A2.row(i) = A.row(in_k[i]);
        B2(i) = B(in_k[i]);
    }

    return A2.colPivHouseholderQr().solve(B2);
}

int main() {
    std::ifstream file1("maxAmplitudePhasesH.log");
    std::ifstream file2("maxAmplitudePhasesW.log");
    if (!file1.is_open() || !file2.is_open()) {
        std::cout << "Failed to open the file.\n";
        return 1;
    }

    std::vector<double> data1;
    std::vector<double> data2;
    double value;
    while (file1 >> value) {
        data1.push_back(value);
    }   
    while (file2 >> value) {
        data2.push_back(value);
    }
    file1.close();
    file2.close();

    int n_data1 = data1.size();
    int n_data2 = data2.size();

    Eigen::MatrixXd A1(n_data1, 3);
    Eigen::VectorXd B1(n_data1);
    for (int i = 0; i < n_data1; ++i) {
        A1(i, 0) = i * i;
        A1(i, 1) = i;
        A1(i, 2) = 1;
        B1(i) = data1[i];
    }
    
    Eigen::MatrixXd A2(n_data2, 3);
    Eigen::VectorXd B2(n_data2);
    for (int i = 0; i < n_data2; ++i) {
        A2(i, 0) = i * i;
        A2(i, 1) = i;
        A2(i, 2) = 1;
        B2(i) = data2[i];
    }

    int N = 100;
    double T = 3 * 100; // 3 * noise_sigma
    Eigen::VectorXd X1 = ransac(A1, B1, N, T);
    Eigen::VectorXd X2 = ransac(A2, B2, N, T);

    Eigen::VectorXd F1 = A1 * X1;
    Eigen::VectorXd F2 = A2 * X2;

    std::ofstream outfile1("outputH.log");
    std::ofstream outfile2("outputW.log");
    if (!outfile1.is_open() || !outfile2.is_open()) {
        std::cout << "Failed to open the output file.\n";
        return 1;
    }

    for (int i = 0; i < F1.size(); ++i) {
        outfile1 << F1(i) << std::endl;
    }
    for (int i = 0; i < F2.size(); ++i) {
        outfile2 << F2(i) << std::endl;
    }
    outfile1.close();
    outfile2.close();

    std::cout << "Result H: " << X1.transpose() << std::endl;
    std::cout << "Result W: " << X2.transpose() << std::endl;

    return 0;
}
```

<br/>

## 결과2

```c++
Result H: 0.00547198   0.292524   -80.6625
Result W: -0.00291597     1.01354    -70.4702
```

<br/>

첨부한 input파일을 이용해 output파일을 기록하고, 그 값들을 그래프로 표현해보았다.

내가 원하는 답이 아니다.

![image](https://github.com/harley-hwan/harley-hwan.github.io/assets/68185569/49c2cc66-0c50-4f78-98aa-809735706328)

<br/>

#### input log files

[maxAmplitudePhasesH.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705761/maxAmplitudePhasesH.log)

[maxAmplitudePhasesW.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705762/maxAmplitudePhasesW.log)

<br/>

#### output log files

[outputH.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705756/outputH.log)

[outputW.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705758/outputW.log)
