---
title: Excel 조건부 서식 매크로 적용하기
description: 조건부 서식을 다른 셀에 적용하는 매크로 작성법
date: 2024-05-14 10:00:00 +0900
categories: [Dev, ETC]
tags: [Excel, 매크로, 조건부 서식, vba, macro]
---

# Excel 조건부 서식 매크로 적용하기

- 최초 작성일: 2024년 5월 14일(화)

## 목차



<br/>

## 소개

이 글에서는 Excel에서 조건부 서식으로 설정(변경)된 셀 서식을 그대로 다른 셀들에도 똑같이 적용할 수 있는 매크로 기능을 설명한다. 매크로를 사용하면 반복적인 작업을 자동화하여 생산성을 높일 수 있다.

## 매크로 예제

아래는 조건부 서식을 포함한 셀 서식을 다른 범위로 복사하는 매크로 코드이다. 이 매크로는 셀의 배경색, 글꼴 색상, 그리고 조건부 서식으로 인해 변경된 테두리를 복사한다.

```vba
Sub CopyColorsAndBorders()
    Dim sourceRange As Range, destRange1 As Range, destRange2 As Range
    Dim i As Integer, j As Integer
    Dim sourceCell As Range, destCell1 As Range, destCell2 As Range
    
    Set sourceRange = Sheets("Sheet1").Range("B1:AQ2048") ' 1번 매트릭스 범위 설정
    Set destRange1 = Sheets("Sheet1").Range("AU1:CJ2048") ' 2번 매트릭스 첫 번째 대상 범위 설정
    Set destRange2 = Sheets("Sheet1").Range("CN1:EC2048") ' 2번 매트릭스 두 번째 대상 범위 설정
    
    For i = 1 To sourceRange.Rows.Count
        For j = 1 To sourceRange.Columns.Count
            Set sourceCell = sourceRange.Cells(i, j)
            Set destCell1 = destRange1.Cells(i, j)
            Set destCell2 = destRange2.Cells(i, j)
            
            ' 배경색 복사
            destCell1.Interior.Color = sourceCell.DisplayFormat.Interior.Color
            destCell2.Interior.Color = sourceCell.DisplayFormat.Interior.Color
            
            ' 글꼴 색상 복사
            destCell1.Font.Color = sourceCell.DisplayFormat.Font.Color
            destCell2.Font.Color = sourceCell.DisplayFormat.Font.Color
            
            ' 조건부 서식으로 인해 변경된 테두리가 있는 경우에만 테두리 복사
            CopyBordersIfChanged sourceCell, destCell1
            CopyBordersIfChanged sourceCell, destCell2
        Next j
    Next i
End Sub

Sub CopyBordersIfChanged(ByVal sourceCell As Range, ByRef destCell As Range)
    Dim borderIndex As Variant
    
    For Each borderIndex In Array(xlEdgeLeft, xlEdgeTop, xlEdgeBottom, xlEdgeRight, xlInsideVertical, xlInsideHorizontal)
        With sourceCell.DisplayFormat.Borders(borderIndex)
            ' 조건부 서식에 의해 스타일이 변경된 경우에만 복사
            If .LineStyle <> sourceCell.Borders(borderIndex).LineStyle Or _
               .Weight <> sourceCell.Borders(borderIndex).Weight Or _
               .Color <> sourceCell.Borders(borderIndex).Color Then
                
                destCell.Borders(borderIndex).LineStyle = .LineStyle
                destCell.Borders(borderIndex).Weight = .Weight
                destCell.Borders(borderIndex).Color = .Color
            End If
        End With
    Next borderIndex
End Sub
```

### 코드 설명

- `CopyColorsAndBorders` 매크로는 원본 범위(`sourceRange`)의 서식을 첫 번째 대상 범위(`destRange1`)와 두 번째 대상 범위(`destRange2`)에 복사한다.
- 셀의 배경색과 글꼴 색상을 복사하며, 조건부 서식으로 인해 변경된 테두리도 복사한다.
- `CopyBordersIfChanged` 함수는 셀의 각 테두리를 확인하여 조건부 서식으로 인해 변경된 경우에만 해당 테두리를 복사한다.

<br/>
