---
title: (c++) json 파일 입출력 (RapidJson)
description: "C, C++, Visual Studio, JSON, RapidJSON, Exception Handling, File I/O, fopen_s, FileReadStream, FileWriteStream, RapidJSON Document, RapidJSON Value, RapidJSON Writer, String Manipulation"
date: 2023-08-03 10:00:00 +0900
categories: [Dev, C++]
tags: [C, C++, Visual Studio, JSON, RapidJSON, Exception Handling, File I/O, fopen_s, FileReadStream, FileWriteStream, RapidJSON Document, RapidJSON Value, RapidJSON Writer, String Manipulation]
---

# json 
- 최초 작성일: 2023년 8월 3일 (목)

## 

1. 파일을 읽기 모드("r")로 열려고 시도한다. 파일을 열 수 없는 경우, 새 파일을 작성 모드("w")로 열고 초기 객체를 작성한 다음 파일을 다시 읽기 모드로 열려고 시도.
2. 파일의 내용을 저장할 버퍼를 만든 다음, rapidjson::FileReadStream을 사용하여 파일의 내용을 읽는다.
3. 파일의 내용을 rapidjson::Document로 파싱한다. 이는 파일의 JSON 구조를 메모리에 로드한다.
4. 새 JSON 객체를 만들고 필요한 필드를 추가한다. 여기서 각 필드는 서로 다른 타입의 정보를 포함하며 이 정보들은 다른 부분의 코드에서 계산되거나 얻어진다.
5. Document에서 "WaveR1" 배열을 찾고, 배열이 없는 경우 새 배열을 추가한다.
6. "WaveR1" 배열에 새로 만든 객체를 추가한다.
7. 파일을 다시 쓰기 모드로 열고, rapidjson::FileWriteStream을 사용하여 JSON 구조를 파일에 다시 쓸 준비.
8. JSON Document를 파일에 쓰고, 파일을 닫음.
9. 읽기/쓰기에 사용한 버퍼 삭제.

<br/>

## 

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
		FileReadStream is(fp, readBuffer, sizeof(readBuffer));
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
			FileWriteStream os(fp, writeBuffer, sizeof(writeBuffer));

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
