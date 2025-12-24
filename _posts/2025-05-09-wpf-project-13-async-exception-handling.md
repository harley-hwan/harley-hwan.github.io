---
title: "(WPF) 13. 비동기 함수의 예외 처리"
description: "async/await 패턴과 예외 처리 방법"
date: 2025-05-09 10:00:00 +0900
categories: [Dev, WPF]
tags: [WPF, C#, Async, Await, Exception Handling, Task]
---

# 비동기 함수의 예외 처리: async/await 패턴 이해하기

## 비동기 프로그래밍 기초

C#에서 비동기 프로그래밍은 `async`와 `await` 키워드를 통해 구현한다. 이 패턴은 I/O 작업이나 시간이 오래 걸리는 작업을 수행할 때 애플리케이션의 응답성을 유지하는 데 중요하다.

```csharp
// 기본적인 비동기 메서드 구조
public async Task DoSomethingAsync()
{
    await SomeAsyncOperation();
}
```

비동기 메서드는 일반적으로 `Task` 또는 `Task<T>`를 반환하며, 이는 작업의 완료 상태와 결과를 나타낸다. `async void`는 이벤트 핸들러에서만 권장한다.

## async/await에서의 예외 처리 방식

비동기 코드에서 예외 처리는 동기 코드와 다르다. 이 차이점을 이해하는 것이 중요하다.

### 핵심 원칙: 예외는 await 지점에서 전파된다

```csharp
public async void ConnCall()
{
    try
    {
        // await 키워드를 사용하면 비동기 함수에서 발생한 예외가 호출자에게 전파된다
        await IsSampleRun();
    }
    catch (Exception ex)
    {
        // 이 catch 블록이 IsSampleRun()에서 발생한 예외를 잡을 수 있다
    }
}
```

비동기 메서드에서 예외가 발생하면, 해당 예외는 `Task` 객체 내에 캡슐화된다. `await` 키워드를 사용할 때만 이 예외가 호출 스택으로 다시 전파되어 `catch` 블록으로 잡힌다.

## 예외 처리의 두 가지 접근법: await vs Wait()

### 1. await 키워드 사용 (권장)

```csharp
try
{
    // 권장 방식: await 키워드 사용
    await IsSampleRun();
}
catch (Exception ex)
{
    // 예외가 정상적으로 잡힌다
}
```

**장점:**
- 호출 스레드를 차단하지 않음
- 자연스러운 예외 전파
- UI 응답성 유지
- 비동기 컨텍스트 유지

### 2. Wait() 메서드 사용

```csharp
try
{
    // 대체 방식: Wait() 메서드 사용
    IsSampleRun().Wait();
}
catch (Exception ex)
{
    // 예외가 AggregateException으로 감싸져서 전달됨
}
```

**특징:**
- 호출 스레드를 차단(blocking)
- 예외가 `AggregateException`으로 감싸짐
- 데드락 가능성 있음
- UI 스레드에서 사용 시 응답성 저하

### 중요 차이점

`Wait()`를 사용하면 원래 예외가 `AggregateException`으로 감싸져서 전달된다. 이 경우 원래 예외에 접근하려면 `AggregateException.InnerException` 속성을 확인해야 한다:

```csharp
try
{
    IsSampleRun().Wait();
}
catch (AggregateException ex)
{
    // 내부 예외에 접근
    var innerException = ex.InnerException;
    // 내부 예외 처리
}
```

## 비동기 코드에서의 모범 사례

### 1. async void 대신 async Task 사용하기

```csharp
// 피해야 할 패턴
public async void BadMethod() { ... }

// 권장 패턴
public async Task GoodMethod() { ... }
```

`async void`는 예외를 호출자에게 전파할 수 없어 예외 처리가 어렵다. 이벤트 핸들러를 제외하고는 사용을 피해야 한다.

### 2. 비동기 라이브러리 함수 호출 시 await 사용하기

```csharp
// SQL 명령 실행 시 권장 방식
await sqlCommand.ExecuteScalarAsync();

// 파일 작업 시 권장 방식
await File.ReadAllTextAsync(path);
```

.NET에서 제공하는 비동기 라이브러리 함수를 호출할 때는 항상 `await` 키워드를 사용해야 예외 처리가 정상적으로 작동한다.

### 3. Thread.Sleep 대신 Task.Delay 사용하기

```csharp
// 피해야 할 패턴
Thread.Sleep(1000); // 스레드 차단됨

// 권장 패턴
await Task.Delay(1000); // 스레드 차단 없음
```

`Thread.Sleep`은 현재 스레드를 차단하여 리소스를 낭비하지만, `await Task.Delay`는 비차단 방식으로 대기한다.

## 실제 응용 예시

### 데이터베이스 연결 예제

```csharp
public async Task<DataTable> GetDataAsync()
{
    try
    {
        using (SqlConnection connection = new SqlConnection(connectionString))
        {
            // 비동기 연결 열기
            await connection.OpenAsync();
            
            SqlCommand command = new SqlCommand("SELECT * FROM Users", connection);
            
            // 비동기 SQL 명령 실행
            using (SqlDataReader reader = await command.ExecuteReaderAsync())
            {
                DataTable dataTable = new DataTable();
                dataTable.Load(reader);
                return dataTable;
            }
        }
    }
    catch (SqlException ex)
    {
        // 데이터베이스 관련 예외 처리
        LogError("데이터베이스 오류: " + ex.Message);
        throw; // 선택적으로 예외를 다시 던짐
    }
    catch (Exception ex)
    {
        // 일반 예외 처리
        LogError("예상치 못한 오류: " + ex.Message);
        throw;
    }
}
```

이 예제는 데이터베이스 연결, 명령 실행, 예외 처리를 모두 비동기적으로 수행하는 패턴을 보여준다.

### 요약

비동기 함수에서 예외를 올바르게 처리하려면:

1. 비동기 메서드에는 `async Task` 또는 `async Task<T>` 반환 타입을 사용한다.
2. 비동기 작업을 기다릴 때는 `await` 키워드를 사용한다.
3. `.Wait()` 메서드는 특별한 경우에만 제한적으로 사용한다.
4. 비동기 컨텍스트에서는 `Thread.Sleep` 대신 `await Task.Delay`를 사용한다.
5. 비동기 메서드 체인에서 모든 호출에 `async`/`await` 패턴을 일관되게 적용한다.

이러한 원칙을 따르면 비동기 코드에서도 예외를 효과적으로 처리하고 애플리케이션의 안정성을 향상시킬 수 있다.
