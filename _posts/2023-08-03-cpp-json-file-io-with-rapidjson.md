---
title: "(C++) JSON 파일 입출력 (RapidJSON)"
description: "검사 결과를 JSON으로도 남기려고 RapidJSON을 붙였다. AddMember가 문자열을 복사하지 않는다는 것, 파싱 실패를 검사하지 않으면 Release에서 조용히 망가진다는 것, CT2CA로 변환한 한글이 UTF-8이 아니라는 것을 뒤늦게 알았다."
date: 2023-08-03 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, visual-studio, json, rapidjson, exception-handling, file-io, fopen-s, file-read-stream, file-write-stream, unicode]
---
## CSV 말고 JSON도 남긴 이유

검사 결과는 이미 [CSV](/posts/cpp-csv-file-io/)로 쌓고 있었다. 현장에서 Excel로 열어보기 좋으니까. 그런데 나중에 결과를 프로그램으로 집계하려니 CSV가 불편했다.

한 필드에 `Pass (0.3)`처럼 값과 판정이 섞여 있어서, 읽는 쪽에서 매번 괄호를 파싱해야 한다. 항목이 하나 추가되면 열 순서가 밀려서 기존 스크립트가 깨진다. 계층 구조도 표현이 안 된다.

그래서 사람이 보는 용도는 CSV로 두고, 프로그램이 읽는 용도로 JSON을 하나 더 만들었다. 라이브러리는 RapidJSON을 골랐다. 헤더 온리라 프로젝트에 끌어다 놓기만 하면 되고, MFC 프로젝트에 별도 빌드 설정을 안 건드려도 된다.

## 처음 짠 코드

```c++
void CMyDlg::UpdateJSON() {
	try {
		FILE* fp = nullptr;
		errno_t err = fopen_s(&fp, ".\\result\\All_results.json", "r");
		if (err != 0) {
			err = fopen_s(&fp, ".\\result\\All_results.json", "w");
			if (err != 0) {
				throw std::runtime_error("Failed to create JSON file for writing!");
			}
			fprintf(fp, "{ \"MyArray\": [] }");
			fclose(fp);
			err = fopen_s(&fp, ".\\result\\All_results.json", "r");
			if (err != 0) {
				throw std::runtime_error("Failed to create JSON file for reading!");
			}
		}

		char* readBuffer = new char[1000];
		FileReadStream is(fp, readBuffer, 1000);
		Document d;
		d.ParseStream(is);
		fclose(fp);

		Value newObj(kObjectType);
		Value strJson(kStringType);

		try {
			strJson.SetString(CT2CA(Field1.GetString()).m_psz, d.GetAllocator());
			newObj.AddMember("Field1", strJson, d.GetAllocator());

			strJson.SetString(Field2.c_str(), d.GetAllocator());
			newObj.AddMember("Field2", strJson, d.GetAllocator());

			// Continue adding fields...

			if (d.FindMember("MyArray") == d.MemberEnd()) {
				d.AddMember("MyArray", Value(kArrayType), d.GetAllocator());
			}

			d["MyArray"].PushBack(newObj, d.GetAllocator());

			err = fopen_s(&fp, ".\\result\\All_results.json", "w");
			if (err != 0) {
				throw std::runtime_error("Failed to open JSON file for writing!");
			}

			char* writeBuffer = new char[1000];
			FileWriteStream os(fp, writeBuffer, 1000);

			Writer<FileWriteStream> writer(os);
			d.Accept(writer);

			fclose(fp);

			delete[] readBuffer;
			delete[] writeBuffer;
		}
		catch (const std::exception& e) {
			std::cerr << "Caught an exception when updating JSON fields: " << e.what() << '\n';
		}
	}
	catch (const std::exception& e) {
		std::cerr << "Caught an exception: " << e.what() << '\n';
	}
}
```

흐름은 이렇다. 파일이 없으면 `{ "MyArray": [] }`로 하나 만들어두고 다시 읽는다. 읽은 걸 `Document`로 파싱하고, 새 객체를 만들어 필드를 채우고, `MyArray`에 밀어 넣고, 전체를 다시 쓴다.

동작은 했다. 그런데 나중에 문제가 여러 개 나왔다.

## AddMember는 이름 문자열을 복사하지 않는다

이게 제일 먼저 걸린 것이다.

```c++
newObj.AddMember("Field1", strJson, d.GetAllocator());
```

이 형태는 `AddMember(StringRefType name, ...)` 오버로드로 잡히고, 이름 문자열을 **복사하지 않고 포인터만 들고 있는다**. 문자열 리터럴은 프로그램이 끝날 때까지 살아 있으니 이 코드는 우연히 안전하다.

문제는 필드 이름을 변수로 만들 때다. 항목이 늘면서 이름을 반복문으로 돌리려고 이렇게 바꿨다가 값이 깨졌다.

```c++
std::string key = "Field" + std::to_string(i);
newObj.AddMember(key.c_str(), v, alloc);   // key 가 사라지면 이름이 쓰레기가 된다
```

`key`는 반복문 안의 지역 변수라 다음 회차에 소멸한다. Document는 이미 사라진 메모리를 이름으로 들고 있다가, 나중에 쓸 때 엉뚱한 문자열을 뱉는다. 값이 아니라 **키가** 깨지는 거라 원인을 찾는 데 한참 걸렸다.

이름을 복사시키려면 `Value`로 만들어서 넘겨야 한다.

```c++
rapidjson::Value name;
name.SetString(key.c_str(), static_cast<rapidjson::SizeType>(key.size()), alloc);
newObj.AddMember(name, v, alloc);
```

값 쪽인 `SetString`도 마찬가지다. 할당자를 넘기는 오버로드만 복사를 하고, 안 넘기면 포인터만 들고 있는다. 리터럴이 아니면 항상 할당자를 넘겨야 한다.

> RapidJSON에서 "이 API가 복사를 하는가"는 오버로드마다 다르다. 값이 이상하면 우선 문자열 수명을 의심하는 게 빠르다.
{: .prompt-tip }

## 파싱 실패를 검사 안 하면 Release에서 조용히 망가진다

```c++
d.ParseStream(is);
```

반환값을 안 본다. 파일이 깨져 있거나 앞선 실행이 쓰다 말았으면 파싱이 실패하고, `d`는 Null 상태로 남는다. 그 상태에서 `d.FindMember("MyArray")`를 부르면 RapidJSON 내부의 `RAPIDJSON_ASSERT(IsObject())`에 걸린다.

여기가 함정이다. `RAPIDJSON_ASSERT`의 기본 정의가 `assert`인데, Release 빌드는 `NDEBUG`가 켜져 있어서 `assert`가 통째로 사라진다. Debug에서는 어설션 대화상자가 뜨면서 원인이 바로 보이는데, Release에서는 아무 검사 없이 Null 값을 객체로 취급해서 진행한다. 그 뒤 동작은 정의되지 않는다.

파싱 결과와 타입을 둘 다 확인해야 한다.

```c++
#include <rapidjson/error/en.h>

if (d.ParseStream(is).HasParseError()) {
    Log("JSON parse error at %zu: %s",
        d.GetErrorOffset(), rapidjson::GetParseError_En(d.GetParseError()));
    d.SetObject();                       // 빈 객체로 초기화하고 새로 시작
}
if (!d.IsObject()) d.SetObject();
```

깨진 파일을 만나면 그냥 새로 시작하도록 했다. 검사 결과를 잃는 것보다 못 읽는 파일을 붙들고 죽는 게 더 나쁘다. 원본은 지우지 말고 `.bak`으로 옮겨두면 나중에 볼 수 있다.

## 버퍼와 파일 핸들이 샌다

`new char[1000]` 두 개는 예외가 나면 그대로 샌다. 안쪽 `try`가 예외를 잡아서 로그만 찍고 넘어가니, 검사를 반복할수록 조금씩 쌓인다. `fp`도 마찬가지로 닫히지 않는다.

애초에 `new`를 쓸 이유가 없었다. 이 버퍼는 스트림이 한 번에 읽고 쓰는 덩어리 크기일 뿐이라 스택에 잡아도 된다.

```c++
char readBuffer[8192];      // 스택. 크기는 처리량에 맞춰 잡으면 된다
FileReadStream is(fp, readBuffer, sizeof(readBuffer));
```

`FILE*`는 RAII로 감쌌다.

```c++
struct FileCloser { void operator()(FILE* f) const { if (f) std::fclose(f); } };
using FilePtr = std::unique_ptr<FILE, FileCloser>;

FILE* raw = nullptr;
if (fopen_s(&raw, path, "rb") != 0) { /* ... */ }
FilePtr fp(raw);
// 어디서 빠져나가든 닫힌다
```

읽기/쓰기 모드를 `"r"`/`"w"`가 아니라 `"rb"`/`"wb"`로 바꾼 것도 이때다. 윈도우 텍스트 모드에서는 `\n`이 `\r\n`으로 변환되는데, JSON 문자열 안에 개행이 들어가면 바이트 수가 달라져서 오프셋 기반 에러 위치가 어긋난다.

## 한글이 UTF-8이 아니다

가장 늦게 발견한 문제다.

```c++
strJson.SetString(CT2CA(Field1.GetString()).m_psz, d.GetAllocator());
```

`CT2CA`는 와이드 문자열을 **시스템 기본 코드페이지**(한국어 윈도우면 CP949)의 narrow 문자열로 바꾼다. RapidJSON의 기본 인코딩은 UTF-8이다. 그러니까 CP949 바이트를 UTF-8 문서에 그대로 밀어 넣고 있었던 것이다.

영문과 숫자만 있을 때는 아스키라 둘이 같아서 아무 문제가 없다. 검사 항목명에 한글이 들어가는 순간 깨진다. 만들어진 파일을 파이썬 `json.load`로 읽으면 `UnicodeDecodeError`가 난다.

코드페이지를 명시해서 UTF-8로 변환해야 한다.

```c++
#include <atlconv.h>

CT2A utf8(Field1.GetString(), CP_UTF8);
strJson.SetString(utf8, static_cast<rapidjson::SizeType>(strlen(utf8)), d.GetAllocator());
```

`CT2A`는 두 번째 인자로 코드페이지를 받는다. `CT2CA`는 const 버전이지만 코드페이지 인자가 없어서 이 용도에 안 맞았다.

변환 결과를 `.m_psz`로 꺼내 쓰는 것도 조심해야 한다. `CT2A`가 만드는 임시 객체는 그 문장이 끝나면 소멸한다. `SetString`이 할당자를 받아 그 자리에서 복사하니까 위 코드는 안전하지만, 포인터를 변수에 담아 나중에 쓰면 이미 해제된 메모리다.

## 배열이 무한히 자란다

CSV 쪽은 ID를 키로 잡아서 재검사하면 기존 줄을 갈아끼웠다. JSON 쪽은 `PushBack`이라 그냥 계속 붙는다. 같은 장비를 세 번 검사하면 항목이 세 개 생긴다.

의도한 동작이면 상관없다. 나는 이력이 남는 게 오히려 나아서 그대로 뒀는데, CSV와 JSON의 내용이 달라진다는 걸 알고는 있어야 했다. 최신 것만 필요하면 ID로 찾아 지우고 넣는다.

```c++
auto& arr = d["MyArray"];
for (rapidjson::SizeType i = 0; i < arr.Size(); ++i) {
    if (arr[i].HasMember("ID") && arr[i]["ID"] == idValue) {
        arr.Erase(arr.Begin() + i);
        break;
    }
}
arr.PushBack(newObj, d.GetAllocator());
```

그리고 매번 전체를 읽고 전체를 쓰는 구조라 파일이 커지면 느려진다. 검사 결과 수천 건 정도로는 체감이 없었는데, 계속 쌓을 거라면 날짜별로 파일을 나누는 게 맞다.

## 읽을 수 있는 출력

`Writer`는 공백 없이 한 줄로 쓴다. 파일이 몇 MB짜리 한 줄이 되면 에디터로 열어보기가 어렵다.

```c++
#include <rapidjson/prettywriter.h>

rapidjson::PrettyWriter<rapidjson::FileWriteStream> writer(os);
writer.SetIndent(' ', 2);
d.Accept(writer);
```

용량은 늘지만 사람이 직접 열어볼 파일이면 이쪽이 낫다. 통신으로 주고받는 데이터면 `Writer`가 맞다.

## 정리한 형태

```c++
void CMyDlg::UpdateJSON()
{
    namespace rj = rapidjson;
    const char* kPath = ".\\result\\All_results.json";
    const char* kTmp  = ".\\result\\All_results.json.tmp";

    rj::Document d;
    d.SetObject();

    // 1) 읽기 — 없거나 깨졌으면 빈 문서로 시작
    {
        FILE* raw = nullptr;
        if (fopen_s(&raw, kPath, "rb") == 0 && raw) {
            FilePtr fp(raw);
            char buf[8192];
            rj::FileReadStream is(fp.get(), buf, sizeof(buf));
            if (d.ParseStream(is).HasParseError() || !d.IsObject()) {
                Log("JSON 손상, 새로 시작한다");
                d.SetObject();
            }
        }
    }

    auto& alloc = d.GetAllocator();
    if (!d.HasMember("MyArray") || !d["MyArray"].IsArray())
        d.AddMember("MyArray", rj::Value(rj::kArrayType), alloc);

    // 2) 새 레코드
    rj::Value obj(rj::kObjectType);
    auto put = [&](const char* key, const CString& v) {
        CT2A utf8(v.GetString(), CP_UTF8);
        rj::Value s;
        s.SetString(utf8, static_cast<rj::SizeType>(strlen(utf8)), alloc);
        obj.AddMember(rj::StringRef(key), s, alloc);   // key 는 리터럴만
    };
    put("Field1", Field1);
    put("Field2", Field2);

    d["MyArray"].PushBack(obj, alloc);

    // 3) 임시 파일에 쓰고 교체
    {
        FILE* raw = nullptr;
        if (fopen_s(&raw, kTmp, "wb") != 0 || !raw) {
            Log("JSON 임시 파일 생성 실패");
            return;
        }
        FilePtr fp(raw);
        char buf[8192];
        rj::FileWriteStream os(fp.get(), buf, sizeof(buf));
        rj::PrettyWriter<rj::FileWriteStream> w(os);
        w.SetIndent(' ', 2);
        d.Accept(w);
    }
    std::remove(kPath);
    std::rename(kTmp, kPath);
}
```

CSV 때와 같은 이유로 임시 파일에 쓰고 바꿔치기한다. 쓰는 도중에 죽어도 원본이 남는다. 윈도우 `std::rename`은 대상이 있으면 실패하기 때문에 `std::remove`를 먼저 부르는데, 그 사이에 죽으면 원본이 없는 순간이 생긴다. 완전히 원자적으로 하려면 `MoveFileEx`에 `MOVEFILE_REPLACE_EXISTING`을 준다.

## 정리하면

- `AddMember`/`SetString`에 할당자를 안 넘기면 문자열을 복사하지 않는다. 리터럴이 아니면 반드시 넘긴다
- `ParseStream`의 결과와 `IsObject()`를 확인한다. RapidJSON의 어설션은 Release에서 사라진다
- `CT2CA`는 시스템 코드페이지로 변환한다. UTF-8이 필요하면 `CT2A(..., CP_UTF8)`
- 파일은 `"rb"`/`"wb"`로 열고, 쓸 때는 임시 파일 + 교체로 간다
- 사람이 볼 파일이면 `PrettyWriter`

## 참고

- [RapidJSON — Tutorial](https://rapidjson.org/md_doc_tutorial.html)
- [RapidJSON — DOM: Move Semantics](https://rapidjson.org/md_doc_tutorial.html#MoveSemantics)
