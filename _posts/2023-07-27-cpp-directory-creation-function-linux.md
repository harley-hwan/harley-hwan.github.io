---
title: (c++) 리눅스 환경에서 디렉토리 생성을 보장하는 함수
description: "c, c++, vs, linux, inotify, inotify_init, IN_CREATE, IN_ISDIR, inotify_rm_watch"
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, linux, inotify, inotify_init, IN_CREATE, IN_ISDIR, inotify_rm_watch]
---

# 원하는 파일 생성 이벤트 모니터링
- 최초 작성일: 2023년 7월 27일 (수)

## 목차



<br/>

## 내용

이 함수는 주로 리눅스 기반의 시스템에서 파일 시스템 작업을 수행하기 전에 특정 디렉토리의 존재를 보장하는 용도로 사용된다. 

파일을 생성하거나, 디렉토리 내의 파일 목록을 조회하거나, 다른 파일 시스템 작업을 수행하기 전에 먼저 디렉토리가 있는지 확인하고, 없다면 생성한다.

<br/>

## 설명

ensure_directory_exists() 함수는 주어진 경로에 디렉토리가 존재하는지 확인하고, 만약 없다면 그 디렉토리를 생성한다. 함수는 두 개의 인자를 받는다.
- path: 디렉토리의 경로를 나타내는 문자열
- mode: 새로 생성할 디렉토리의 접근 권한을 나타내는 값. 이 값은 표준 Unix 권한 표기법에 따름.

<br/>

## 구현

1. 파일 상태 확인: stat 함수를 사용해 경로에 해당하는 파일의 상태를 확인. stat 함수는 성공할 경우 0을 반환하고, 실패할 경우 -1을 반환. 디렉토리나 파일이 존재하지 않을 경우 stat은 -1을 반환. 이 경우, 함수는 다음 단계로 넘어간다.
2. 디렉토리 생성: stat 함수가 -1을 반환했다면, mkdir 함수를 사용해 디렉토리를 생성. mkdir 역시 성공할 경우 0을 반환하고, 실패할 경우 -1을 반환. 만약 디렉토리 생성에 실패했고, 그 이유가 이미 같은 이름의 디렉토리가 존재해서가 아니라면(errno != EEXIST), 오류 메시지를 출력하고 프로그램을 종료.
3. 디렉토리 여부 확인: 만약 stat 함수가 성공했다면, 해당 경로에는 어떠한 파일이나 디렉토리가 존재한다. 이 경우, S_ISDIR 매크로를 사용해 이것이 디렉토리인지 확인. 만약 디렉토리가 아니라면, 오류 메시지를 출력하고 프로그램을 종료.
4. 따라서 이 함수는 주어진 경로에 디렉토리가 존재하게 하는 역할을 한다. 디렉토리가 이미 존재하면 아무 작업도 수행하지 않고, 존재하지 않으면 디렉토리를 생성. 하지만, 해당 경로에 디렉토리 대신 다른 종류의 파일이 존재하는 경우에는 에러 반환.

<br/>

## 코드

```c++
    void ensure_directory_exists(const std::string& path, mode_t mode)
    {
        struct stat st;
        if(stat(path.c_str(), &st) != 0) {
            if (mkdir(path.c_str(), mode) != 0 && errno != EEXIST) {
                std::cerr << "Could not create directory: " << path << std::endl;
                exit(EXIT_FAILURE);
            }
        } else if (!S_ISDIR(st.st_mode)) {
            errno = ENOTDIR;
            std::cerr << "Path exists but is not a directory: " << path << std::endl;
            exit(EXIT_FAILURE);
        }
    }
```

<br/>

```c++
    // Check if log directory exists, if not, create it
    ensure_directory_exists("../log", 0777);
```
