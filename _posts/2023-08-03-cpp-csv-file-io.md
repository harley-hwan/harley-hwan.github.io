---
title: (c++) csv 파일 입출력
description: "c, c++, vs, csv, excel, ifstream, ofstream, std::ifstream, std::ofstream, tellp, map, lambda function"
date: 2023-08-03 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, csv, excel, ifstream, ofstream, std::ifstream, std::ofstream, tellp, map, lambda function]
---

# csv 
- 최초 작성일: 2023년 8월 3일 (목)

## 

1. __std::map<std::string, std::string> lines__ : CSV 파일의 각 행을 저장. 키는 시리얼 번호이고, 값은 해당 시리얼 번호에 해당하는 전체 행이다.
2. __auto escapeCSV 람다 함수__ : 특정 필드(데이터 값)가 CSV 파일에서 제대로 처리되도록 이스케이프한다. 예를 들어, 데이터 값에 쉼표가 포함되어 있으면, 이것은 CSV에서 새로운 필드를 생성하는 데 사용되는 구분자로 해석될 수 있으므로, 이스케이프 처리가 필요.
3. __파일 읽기__ : ifstream을 사용하여 CSV 파일을 열고, 각 행을 읽어서 시리얼 번호와 행을 map에 저장.
4. __새로운 행 구성__ : 각각의 변수(예: SerialNumber, MacWifi, SWVer 등)는 escapeCSV 함수를 통해 안전하게 이스케이프 처리되고, 이들은 쉼표로 구분되어 새로운 CSV 행을 생성한다.
5. __행 업데이트 또는 추가__ : 새로 생성된 행은 map에 추가됩니다. 이미 같은 시리얼 번호를 가진 행이 있다면, 그 행은 새로운 행으로 업데이트되고, 그렇지 않다면 새 행이 추가된다.
6. __파일 쓰기__ : map에 있는 모든 행을 다시 CSV 파일에 쓴다. 파일이 처음 생성되는 경우에는 헤더도 추가.

<br/>

이 함수의 주요 목적은 특정 시리얼 번호에 대한 행을 CSV 파일에서 업데이트 하는 것. 만약 해당 시리얼 번호에 대한 행이 없다면 새로운 행을 추가하고, 있다면 기존 행을 업데이트 한다.

<br/>

## 

```c++
void UpdateCSV() {
	try {
		CString fileName;
		fileName.Format(_T(".\\result\\All_results.csv"));

		// Map for lines
		std::map<std::string, std::string> lines;

		// CSV Escape Function as a lambda expression
		auto escapeCSV = [](const std::string& field) {
			if (field.find(',') != std::string::npos || field.find('\n') != std::string::npos || field.find('\"') != std::string::npos) {
				return "\"" + std::regex_replace(field, std::regex("\""), "\"\"") + "\"";
			}
			return field;
		};

		// File input
		std::ifstream inFile(fileName);
		if (inFile.fail()) {
			throw std::runtime_error("File could not be opened.\n");
		}

		std::string strCsv;
		while (std::getline(inFile, strCsv)) {
			if (!strCsv.empty()) {
				// Extract ID
				std::string id = strCsv.substr(0, strCsv.find(','));
				lines[id] = strCsv;
			}
		}
		inFile.close();

		// Convert CString to string
		std::string idStr = CT2CA(IdField.GetString());

		// Construct new line
		std::string newLine = escapeCSV(idStr) + ","
			+ escapeCSV(Field1) + ","
			+ escapeCSV(Field2) + " (" + escapeCSV(ResField2) + ")" + ","
			+ escapeCSV(Field3) + " (" + escapeCSV(ResField3) + ")" + ","
			+ escapeCSV(Field4) + " (" + escapeCSV(ResField4) + ")" + ","
			+ escapeCSV(Field5) + " (" + escapeCSV(ResField5) + ")" + ","
			+ escapeCSV(Field6) + " (" + escapeCSV(ResField6) + ")" + ","
			+ escapeCSV(Field7) + " (" + escapeCSV(ResField7) + ")" + ","
			+ escapeCSV(Field8) + " " + escapeCSV(ResField8) + " (" + escapeCSV(ResField9) + ")" + ","
			+ escapeCSV(Field9) + " (" + escapeCSV(ResField10) + ")" + ","
			+ escapeCSV(ResField11) + "/" + escapeCSV(ResField12) + "(" + escapeCSV(ResField13) + " " + escapeCSV(ResField14) + ")" + " (" + escapeCSV(ResField15) + ")" + ","
			+ "=\"" + escapeCSV(Field10) + " " + escapeCSV(Field11) + "\"" + ","
			+ escapeCSV(ResField16) + ","
			+ escapeCSV(ResField17) + "\n";

		// Replace or add line
		lines[idStr] = newLine;

		// File output
		std::ofstream outFile(fileName);
		if (outFile.fail()) {
			throw std::runtime_error("File could not be written.\n");
		}

		// Write header if new file
		if (outFile.tellp() == 0) {
			outFile << "ID,Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9,Field10,Field11,Field12,Field13,Field14\n";
		}

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

<br/>

<br/>

## 

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
		+ Field3 + " (" + ResField3 + ")" + ","
		+ Field4 + " (" + ResField4 + ")" + ","
		+ Field5 + " (" + ResField5 + ")" + ","
		+ Field6 + " (" + ResField6 + ")" + ","
		+ Field7 + " (" + ResField7 + ")" + ","
		+ Field8 + " " + ResField8 + " (" + ResField9 + ")" + ","
		+ Field9 + " (" + ResField10 + ")" + ","
		+ ResField11 + "/" + ResField12 + "(" + ResField13 + " " + ResField14 + ")" + " (" + ResField15 + ")" + ","
		+ "=\"" + Field10 + " " + Field11 + "\"" + ","
		+ ResField16 + ","
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
