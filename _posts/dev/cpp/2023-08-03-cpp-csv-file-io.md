---
title: "(C++) CSV 파일 입출력"
description: "검사 결과를 ID 키로 갱신하는 CSV 누적 파일을 만들었다. vector 순회에서 map으로 바꾼 이유, 필드 조각마다 이스케이프를 걸면 안 되는 이유, Excel이 값을 멋대로 바꿔놓는 문제까지 정리했다."
date: 2023-08-03 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, visual-studio, csv, excel, ifstream, ofstream, std-ifstream, std-ofstream, map, lambda, rfc4180]
---
## 하려던 것

검사 지그에서 장비 한 대를 검사할 때마다 결과 한 줄이 나온다. 이걸 `All_results.csv` 한 파일에 계속 쌓되, **같은 장비를 재검사하면 새 줄을 추가하는 게 아니라 기존 줄을 갈아끼워야** 한다. 재검사 이력이 여러 줄로 남으면 나중에 최종 결과를 집계할 때 어느 줄을 봐야 하는지 알 수 없다.

CSV로 간 이유는 단순하다. 현장에서 결과를 확인하는 사람이 Excel로 연다.

## 처음 구현 — vector 순회

```c++
void CRadarCalibrationDlg::UpdateCSV() {
	CString fileName;
	fileName.Format(_T(".\\result\\All_results.csv"));

	std::vector<std::string> lines;
	bool addHeader = false;

	// Check if the file exists
	std::ifstream testFile(fileName);
	if (!testFile) {
		// File does not exist, add header
		addHeader = true;
	}
	testFile.close();

	std::ifstream inFile(fileName);
	std::string strCsv;

	if (addHeader) {
		lines.push_back("ID,Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9,Field10,Field11,Field12,Field13,Field14\n");
	}

	while (std::getline(inFile, strCsv)) {
		if (!strCsv.empty()) {
			lines.push_back(strCsv + '\n');
		}
	}
	inFile.close();

	std::string idStr = CT2CA(IdField.GetString());

	std::string newLine = idStr + ","
		+ Field1 + ","
		+ Field2 + " (" + ResField2 + ")" + ","
		// ... 이하 생략
		+ ResField17 + "\n";

	// Check each line to see if the ID is already present.
	auto it = std::find_if(lines.begin(), lines.end(), [&](const std::string& line) {
		return line.substr(0, idStr.length()) == idStr;
		});

	if (it != lines.end()) {
		// If the ID is found, overwrite the line.
		*it = newLine;
	}
	else {
		// If the ID was not found, add a new line.
		lines.push_back(newLine);
	}

	// Write the updated data to the file.
	std::ofstream outFile(fileName);
	for (const auto& line : lines) {
		outFile << line;
	}
	outFile.close();
}
```

돌아가긴 했는데 문제가 몇 개 있었다.

**앞부분만 비교한다.** `line.substr(0, idStr.length()) == idStr`은 접두사 비교다. ID가 `A100`인 장비를 검사하는데 파일에 `A1000`인 줄이 이미 있으면, `A1000`의 앞 네 글자가 `A100`과 같아서 엉뚱한 줄을 덮어쓴다. 검사한 적 없는 장비의 결과가 사라지는 셈이라 알아채기도 어렵다.

**헤더도 매칭될 수 있다.** 헤더는 `ID,`로 시작하는데, 어쩌다 `ID`로 시작하는 시리얼이 있으면 헤더 줄이 결과로 덮어써진다. 그러면 그다음부터 Excel에서 열 이름이 사라진다.

**개행을 문자열에 붙여서 관리한다.** `lines`의 각 원소가 `\n`을 달고 있어서 마지막 줄에만 개행이 없는 경우, 파일 끝에 개행이 있는 경우 등을 따로 신경 써야 한다. 읽을 때는 `getline`이 개행을 떼고 주는데 쓸 때는 다시 붙이니 앞뒤가 안 맞는다.

## map으로 바꾸기

ID로 찾는 일이라 애초에 map이 맞았다.

```c++
void UpdateCSV() {
	try {
		CString fileName;
		fileName.Format(_T(".\\result\\All_results.csv"));

		// Map for lines
		std::map<std::string, std::string> lines;

		// CSV Escape Function as a lambda expression
		auto escapeCSV = [](const std::string& field) -> std::string {
			if (field.find(',') != std::string::npos || field.find('\n') != std::string::npos || field.find('\"') != std::string::npos) {
				return "\"" + std::regex_replace(field, std::regex("\""), "\"\"") + "\"";
			}
			return field;
		};

		// File input (skip if the file does not exist yet)
		std::ifstream inFile(fileName);
		if (inFile) {
			std::string strCsv;
			while (std::getline(inFile, strCsv)) {
				if (!strCsv.empty()) {
					// Extract ID
					std::string id = strCsv.substr(0, strCsv.find(','));

					// Skip header line
					if (id == "ID") {
						continue;
					}
					lines[id] = strCsv;
				}
			}
			inFile.close();
		}

		// Convert CString to string
		std::string idStr = CT2CA(IdField.GetString());

		// Construct new line
		std::string newLine = escapeCSV(idStr) + ","
			+ escapeCSV(Field1) + ","
			+ escapeCSV(Field2) + " (" + escapeCSV(ResField2) + ")" + ","
			+ escapeCSV(Field3) + " (" + escapeCSV(ResField3) + ")" + ","
			// ... 이하 생략
			+ "=\"" + escapeCSV(Field10) + " " + escapeCSV(Field11) + "\"" + ","
			+ escapeCSV(ResField16) + ","
			+ escapeCSV(ResField17);

		// Replace or add line
		lines[idStr] = newLine;

		// File output
		std::ofstream outFile(fileName);
		if (outFile.fail()) {
			throw std::runtime_error("File could not be written.\n");
		}

		// Write header (the whole file is rewritten every time)
		outFile << "ID,Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9,Field10,Field11,Field12,Field13,Field14\n";

		// Write lines
		for (const auto& line : lines) {
			outFile << line.second << '\n';
		}
		outFile.close();
	}
	catch (const std::exception& e) {
		std::cerr << "Caught an exception: " << e.what() << '\n';
	}
}
```

`lines[idStr] = newLine;` 한 줄로 "있으면 갱신, 없으면 추가"가 끝난다. 접두사 문제도 같이 사라진다. 헤더는 읽을 때 걸러내고 쓸 때 항상 새로 찍는다.

한 가지 부수 효과가 있다. `std::map`은 키 순으로 정렬되므로 결과 줄의 순서가 **검사한 순서가 아니라 ID 사전순**이 된다. 게다가 문자열 비교라 `ID10`이 `ID9`보다 앞에 온다. 검사 순서를 유지해야 하면 `std::map` 대신 `std::vector` + `std::unordered_map<ID, index>` 조합을 쓰거나, 행에 타임스탬프 열을 넣고 Excel에서 정렬하는 쪽이 낫다. 나는 어차피 Excel에서 정렬해 보길래 그냥 뒀다.

## 이스케이프를 조각마다 걸면 안 된다

위 코드에서 나중에 고친 부분이다. 처음엔 이렇게 썼다.

```c++
escapeCSV(Field2) + " (" + escapeCSV(ResField2) + ")"
```

`Field2`에 쉼표가 없으면 아무 일도 안 일어나니 평소엔 문제가 안 보인다. 그런데 `Field2`에 쉼표가 들어오면 이렇게 된다.

```text
"a,b" (c)
```

CSV에서 따옴표는 **필드 전체**를 감싸야 의미가 있다. 위처럼 필드 중간에 따옴표가 열리고 닫히면 파서가 어떻게 읽을지 모른다. Excel은 대충 읽어주기도 하는데, 다른 도구로 읽으면 열이 어긋난다.

조각을 다 합친 뒤 마지막에 한 번만 이스케이프하는 게 맞다.

```c++
auto field = [&](const std::string& v, const std::string& res) {
    return escapeCSV(v + " (" + res + ")");    // 합치고 나서 한 번
};

std::string newLine = escapeCSV(idStr) + ","
    + escapeCSV(Field1) + ","
    + field(Field2, ResField2) + ","
    + field(Field3, ResField3) + ",";
```

이스케이프 규칙 자체는 RFC 4180이 정의한 대로 간단하다. 쉼표, 큰따옴표, 개행 중 하나라도 들어 있으면 필드 전체를 큰따옴표로 감싸고, 내부의 큰따옴표는 두 개로 늘린다. 위 람다가 그걸 하고 있다.

`std::regex`를 쓴 게 좀 과하긴 하다. 문자 하나 치환이라 직접 도는 게 훨씬 빠르고 의존성도 없다.

```c++
std::string escape_csv(const std::string& s)
{
    if (s.find_first_of(",\"\n\r") == std::string::npos) return s;
    std::string out = "\"";
    for (char c : s) {
        if (c == '"') out += "\"\"";
        else          out += c;
    }
    out += '"';
    return out;
}
```

`\r`도 판정에 넣었다. 장비에서 읽은 값 끝에 `\r`이 붙어 오는 경우가 있는데, 이게 CSV 필드 안에 들어가면 Excel에서 셀 안 줄바꿈으로 보인다.

## Excel이 값을 바꿔놓는다

CSV의 진짜 문제는 파싱이 아니라 Excel이다.

가장 자주 겪은 건 **앞자리 0이 사라지는 것**이다. 시리얼이 `007123`인데 Excel로 열면 `7123`이 된다. 숫자로 해석해버리기 때문이다. 원본 파일은 멀쩡한데 사람이 열어서 보는 값이 다르다.

원 코드의 `"=\"" + ... + "\""`이 그 대응이다. 필드를 `="007123"`처럼 만들면 Excel이 문자열 상수 수식으로 보고 원래 값을 유지한다. 다만 이건 CSV 표준이 아니라 Excel 전용 꼼수라, 같은 파일을 파이썬이나 다른 도구로 읽으면 `="007123"`이라는 글자 그대로 나온다. 나중에 집계 스크립트를 짜면서 이 부분을 다시 벗겨내야 했다.

비슷한 사고가 몇 개 더 있다.

| 값 | Excel이 보여주는 것 | 이유 |
| :--- | :--- | :--- |
| `007123` | `7123` | 숫자로 해석 |
| `1-2` | `1월 2일` | 날짜로 해석 |
| `3E5` | `300000` | 지수 표기로 해석 |
| `00123456789012345678` | `1.23457E+19` | 15자리 넘는 수는 정밀도 손실 |

그리고 **한글이 깨지는 문제**. UTF-8로 저장한 CSV를 Excel이 시스템 코드페이지로 읽어서 글자가 다 깨진다. 파일 맨 앞에 UTF-8 BOM을 찍어주면 Excel이 알아본다.

```c++
std::ofstream outFile(fileName, std::ios::binary);
outFile << "\xEF\xBB\xBF";      // UTF-8 BOM
```

`std::ios::binary`를 같이 준 이유는, 텍스트 모드에서는 윈도우가 `\n`을 `\r\n`으로 바꿔주기 때문에 개행을 직접 통제하려면 바이너리가 편해서다. RFC 4180은 줄 구분자를 CRLF로 정의하고 있으니 `outFile << "\r\n"`으로 명시하면 어느 환경에서 만들든 같은 파일이 나온다.

> **`=`로 시작하는 값은 그냥 두면 안 된다.** 필드 값이 `=`, `+`, `-`, `@` 중 하나로 시작하면 Excel이 수식으로 해석한다. 장비에서 읽은 값이 `-12dB` 같은 형태였을 때 Excel에서 오류 셀로 표시된 적이 있다. 값 앞에 작은따옴표를 붙이거나 `="..."` 형태로 감싸면 막을 수 있다. 외부 입력을 그대로 넣는 CSV에서는 명령 실행까지 이어지는 알려진 취약점이기도 하다.
{: .prompt-warning }

## 통째로 다시 쓰는 방식의 위험

이 코드는 매번 파일 전체를 읽고, 메모리에서 고치고, 전체를 다시 쓴다. 검사 결과가 수백 줄이니 성능은 문제가 안 된다. 문제는 다른 데 있다.

`std::ofstream outFile(fileName);`이 실행되는 순간 파일이 0바이트로 잘린다. 그 뒤 쓰는 도중에 프로그램이 죽거나 전원이 나가면 **누적된 결과 전체가 날아간다**. 하루치 검사 결과를 통째로 잃는 상황이다.

임시 파일에 쓰고 나서 바꿔치기하면 이 위험이 없어진다.

```c++
#include <filesystem>
namespace fs = std::filesystem;

const fs::path target = "./result/All_results.csv";
const fs::path tmp    = "./result/All_results.csv.tmp";

{
    std::ofstream out(tmp, std::ios::binary);
    if (!out) throw std::runtime_error("temp file open failed");
    out << "\xEF\xBB\xBF";
    out << header << "\r\n";
    for (const auto& [id, row] : lines) out << row << "\r\n";
    out.flush();
    if (!out) throw std::runtime_error("write failed");
}   // 여기서 닫힌다

fs::rename(tmp, target);    // 같은 볼륨이면 교체가 한 번에 끝난다
```

중간에 죽으면 임시 파일만 남고 원본은 그대로다. 블록을 하나 열어서 `ofstream`의 수명을 명시적으로 끊은 이유는, 닫히기 전에 `rename`을 하면 윈도우에서 실패하기 때문이다.

## 읽을 때 걸리는 것

`getline`으로 읽으면 CRLF로 저장된 파일에서 `\r`이 마지막 필드에 남는다. 윈도우에서 텍스트 모드로 읽으면 알아서 벗겨지지만, 바이너리 모드로 열었거나 리눅스에서 읽으면 그대로 붙어 있다.

```c++
while (std::getline(inFile, line)) {
    if (!line.empty() && line.back() == '\r') line.pop_back();
    // ...
}
```

그리고 이 코드는 ID를 `line.substr(0, line.find(','))`로 뽑는데, ID 자체에 쉼표가 있어서 따옴표로 감싸진 경우에는 틀린 값이 나온다. 내 경우 ID는 영숫자로 제한되어 있어서 문제가 없었지만, 필드에 뭐가 들어올지 모르면 제대로 된 파서가 필요하다. 따옴표 상태를 들고 한 글자씩 도는 정도로 충분하다.

```c++
std::vector<std::string> parse_csv_line(const std::string& line)
{
    std::vector<std::string> out;
    std::string cur;
    bool in_quotes = false;

    for (size_t i = 0; i < line.size(); ++i) {
        const char c = line[i];
        if (in_quotes) {
            if (c == '"') {
                if (i + 1 < line.size() && line[i + 1] == '"') { cur += '"'; ++i; }
                else in_quotes = false;
            } else cur += c;
        } else {
            if (c == '"')      in_quotes = true;
            else if (c == ',') { out.push_back(cur); cur.clear(); }
            else               cur += c;
        }
    }
    out.push_back(cur);
    return out;
}
```

필드 안에 개행이 들어간 경우(따옴표 안의 `\n`)는 이걸로도 부족하다. 한 줄이 한 레코드라는 가정이 깨지기 때문에, 그런 데이터를 다뤄야 하면 줄 단위가 아니라 스트림 단위로 파싱해야 한다. 검사 결과에는 개행이 들어갈 일이 없어서 여기까지만 했다.

## 정리하면

- ID로 찾아 갱신하는 구조면 `map`이 맞다. 접두사 비교 버그가 애초에 안 생긴다
- `map`은 키 사전순으로 재배열한다. 순서가 중요하면 다른 자료구조를 쓴다
- CSV 이스케이프는 필드 조각이 아니라 완성된 필드 전체에 한 번만 건다
- Excel은 앞자리 0을 지우고, `1-2`를 날짜로 바꾸고, BOM이 없으면 한글을 깬다. `="..."`와 BOM이 대응책이지만 둘 다 Excel 전용 꼼수다
- 파일을 통째로 다시 쓰는 방식은 임시 파일 + rename으로 바꿔야 사고가 안 난다

같은 데이터를 JSON으로도 남긴 얘기는 [JSON 파일 입출력 (RapidJSON)](/posts/cpp-json-file-io-with-rapidjson/)에 있다.

## 참고

- [RFC 4180 — Common Format and MIME Type for CSV Files](https://datatracker.ietf.org/doc/html/rfc4180)
