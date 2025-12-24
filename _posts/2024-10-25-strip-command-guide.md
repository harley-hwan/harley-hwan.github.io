---
title: "Strip 명령어: ELF 파일 최적화의 핵심 도구"
description: "임베디드 시스템을 위한 실행 파일 용량 최적화에 대한 이론과 실제"
date: 2024-10-25 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, embedded, optimization, binary, elf, strip, linker]
---

# Strip 명령어: ELF 파일 최적화의 핵심 도구
- 최초 작성일: 2024년 10월 25일 (금)

<br/>

## 소개
Strip은 GNU Binutils의 핵심 구성 요소로, 실행 파일에서 불필요한 심볼과 섹션을 제거하여 파일 크기를 최적화하는 도구다. 특히 임베디드 시스템에서 중요한 역할을 하며, 실행 파일의 메모리 점유율을 최소화하는 데 결정적인 기여를 한다.

<br/>

## ELF 파일 구조와 이론적 배경

### ELF(Executable and Linkable Format) 파일의 구조
ELF 파일은 크게 다음과 같은 주요 섹션들로 구성된다:

```plaintext
ELF 파일 구조
├── ELF 헤더
│   ├── 매직 넘버 (0x7F ELF)
│   ├── 파일 클래스 (32/64비트)
│   ├── 데이터 인코딩
│   └── 버전 정보
│
├── 프로그램 헤더 테이블
│   ├── 세그먼트 정보
│   └── 메모리 매핑 정보
│
├── 섹션 영역
│   ├── .text (실행 코드)
│   │   └── 어셈블리 명령어
│   │
│   ├── .data (초기화된 데이터)
│   │   ├── 전역 변수
│   │   └── 정적 변수
│   │
│   ├── .bss (미초기화 데이터)
│   │   └── 제로로 초기화될 메모리
│   │
│   ├── .rodata (읽기 전용 데이터)
│   │   ├── 상수
│   │   └── 문자열 리터럴
│   │
│   ├── .symtab (심볼 테이블)
│   │   ├── 함수 심볼
│   │   └── 변수 심볼
│   │
│   ├── .strtab (문자열 테이블)
│   │   └── 심볼 이름 문자열
│   │
│   └── .debug (디버깅 정보)
│       ├── DWARF 정보
│       ├── 소스 코드 매핑
│       └── 타입 정보
│
└── 섹션 헤더 테이블
    └── 섹션 메타데이터
```

### 링커와 로더의 관점에서 본 ELF
1. **링커 관점**
   - 재배치 가능한 객체 파일들을 하나의 실행 파일로 결합
   - 심볼 해석과 주소 재배치 수행
   - 외부 라이브러리 연결

2. **로더 관점**
   - 프로그램 헤더를 통해 메모리 세그먼트 구성
   - 가상 메모리 매핑 설정
   - 동적 링커를 통한 런타임 링킹 처리

<br/>

## Strip의 동작 원리

### 1. 심볼 테이블 처리
Strip은 심볼 테이블(.symtab)을 분석하여 다음과 같은 작업을 수행한다:

```c
// 심볼 타입에 따른 처리
typedef enum {
    LOCAL_SYMBOL,    // 내부 심볼
    GLOBAL_SYMBOL,   // 전역 심볼
    WEAK_SYMBOL,     // 약한 심볼
    DEBUG_SYMBOL     // 디버그 심볼
} SymbolType;

// 심볼 처리 알고리즘 의사 코드
for (each symbol in symtab) {
    switch (symbol.type) {
        case DEBUG_SYMBOL:
            remove_symbol();  // 항상 제거
            break;
        case GLOBAL_SYMBOL:
            if (!symbol.used)
                remove_symbol();  // 미사용 심볼 제거
            break;
        case WEAK_SYMBOL:
            if (!symbol.referenced)
                remove_symbol();  // 참조되지 않은 심볼 제거
            break;
    }
}
```

### 2. 섹션 정리
불필요한 섹션을 식별하고 제거하는 과정은 다음과 같다:

1. **제거 대상 섹션**
   - .debug_*: 모든 디버깅 관련 섹션
   - .comment: 컴파일러 버전 등의 주석 정보
   - .note: 빌드 정보 등의 노트
   - 미사용 재배치 정보

2. **보존 대상 섹션**
   - .text: 실행 코드
   - .data: 초기화된 데이터
   - .rodata: 상수 데이터
   - .dynamic: 동적 링킹 정보

<br/>

<br/>

## Strip이 제거하는 정보의 상세 분석

### 1. 디버깅 정보 (DWARF 포맷)
DWARF(Debugging With Attributed Record Formats) 디버깅 정보는 다음과 같은 요소들을 포함한다:

```plaintext
DWARF 구조
├── .debug_info (기본 디버깅 정보)
│   ├── 컴파일 단위 정보
│   ├── 타입 정의
│   └── 변수 위치
├── .debug_line (소스 라인 매핑)
├── .debug_abbrev (약어 테이블)
└── .debug_str (디버그 문자열)
```

### 2. 심볼 정보의 분류
심볼 정보는 다음과 같이 분류되어 처리된다:

1. **필수 심볼**
   - 동적 링킹에 필요한 심볼
   - 프로그램 시작점(_start, main)
   - 외부 참조 심볼

2. **제거 가능 심볼**
   - 정적 함수 심볼
   - 디버깅용 타입 정보
   - 지역 변수 심볼
   - 소스 파일 정보

<br/>

## Strip 사용법과 고급 기능

### 1. 기본 명령어와 옵션

```bash
# 기본 사용법
strip [옵션] <파일명>

# 주요 옵션
--strip-all        # 모든 심볼 제거
--strip-debug      # 디버그 심볼만 제거
--strip-unneeded   # 재배치에 불필요한 심볼 제거
-K symbolname      # 특정 심볼 보존
--keep-file-symbols # 파일 심볼 보존
```

### 2. 고급 사용 예제

```bash
# 1. 특정 섹션만 제거
strip --remove-section=.note.ABI-tag --remove-section=.comment binary

# 2. 디버그 정보를 별도 파일로 분리
objcopy --only-keep-debug binary binary.debug
strip --strip-debug binary
objcopy --add-gnu-debuglink=binary.debug binary

# 3. 선택적 심볼 보존
strip -K main -K _init -K _fini binary
```

<br/>

## 성능과 트레이드오프

### 1. 메모리 사용량 분석

```text
일반적인 크기 감소 비율:
- 실행 파일: 40-70% 감소
- 공유 라이브러리: 20-50% 감소
- 정적 라이브러리: 60-80% 감소
```

### 2. 성능 영향
1. **긍정적 효과**
   - 파일 로딩 시간 단축
   - 메모리 캐시 효율성 증가
   - 페이지 폴트 감소

2. **부정적 효과**
   - 크래시 분석 어려움
   - 런타임 디버깅 불가능
   - 프로파일링 정보 손실

<br/>

## 실전 최적화 전략

### 1. 단계별 최적화 프로세스

```bash
# 1. 원본 백업
cp binary binary.full

# 2. 불필요 섹션 제거
strip --remove-section=.comment --remove-section=.note binary

# 3. 디버그 정보 분리
objcopy --only-keep-debug binary binary.debug
strip --strip-debug binary

# 4. 디버그 링크 설정
objcopy --add-gnu-debuglink=binary.debug binary
```

### 2. 보안 고려사항
1. **심볼 스트리핑과 보안**
   - 리버스 엔지니어링 난이도 증가
   - 취약점 분석 복잡도 증가
   - 바이너리 크기 감소로 인한 공격 표면 축소

2. **권장 보안 설정**
   
```bash
# 모든 불필요 정보 제거
strip --strip-all --remove-section=.note --remove-section=.comment binary

# 중요 심볼만 보존
strip -K main -K _start --strip-unneeded binary
```

<br/>

## 결론
Strip은 단순한 바이너리 축소 도구를 넘어서, 임베디드 시스템과 제한된 환경에서의 소프트웨어 최적화에 핵심적인 역할을 한다. ELF 파일 구조에 대한 깊은 이해를 바탕으로 Strip을 효과적으로 활용하면, 실행 파일의 크기를 최적화하면서도 필요한 기능은 모두 보존할 수 있다.

효과적인 Strip 활용을 위해서는:
- ELF 파일 구조의 이해
- 심볼과 섹션의 역할 파악
- 최적화와 디버깅 간의 균형
- 보안 측면의 고려

이러한 요소들을 종합적으로 고려해야 한다.
