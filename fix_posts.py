#!/usr/bin/env python3
"""
포스트 HTML Proofer 에러 수정 스크립트

수정 내용:
1. 헤더에서 이모지 제거 (## 📚 개요 → ## 개요)
2. 이미지에 alt 속성 추가 (![](url) → ![image](url))
3. 빈 링크 제거 ([text]() → text)
4. 잘못된 내부 링크 제거

사용법:
    python fix_posts.py <_posts 폴더 경로>

예시:
    python fix_posts.py ./_posts
"""

import os
import re
import sys
from pathlib import Path

# 이모지 패턴 (일반적인 이모지 범위)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # 이모티콘
    "\U0001F300-\U0001F5FF"  # 기호 & 픽토그램
    "\U0001F680-\U0001F6FF"  # 교통 & 지도
    "\U0001F1E0-\U0001F1FF"  # 플래그
    "\U00002702-\U000027B0"  # 딩뱃
    "\U000024C2-\U0001F251"  # 기타
    "\U0001F900-\U0001F9FF"  # 보조 기호
    "\U0001FA00-\U0001FA6F"  # 체스 기호
    "\U0001FA70-\U0001FAFF"  # 기호 확장
    "\U00002600-\U000026FF"  # 기타 기호
    "\U00002700-\U000027BF"  # 딩뱃
    "\U0001F000-\U0001F02F"  # 마작
    "\U0001F0A0-\U0001F0FF"  # 카드
    "]+", 
    flags=re.UNICODE
)

def remove_emoji_from_headers(content):
    """헤더에서 이모지 제거"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 헤더 라인인지 확인 (## 또는 ### 등)
        if re.match(r'^#{1,6}\s+', line):
            # 이모지 제거
            original_line = line
            line = EMOJI_PATTERN.sub('', line)
            # 이모지 제거 후 남은 공백 정리
            line = re.sub(r'\s+', ' ', line)
            line = re.sub(r'^(#{1,6})\s+', r'\1 ', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_image_alt(content):
    """이미지에 alt 속성 추가"""
    # ![](url) → ![image](url)
    content = re.sub(r'!\[\]\(([^)]+)\)', r'![image](\1)', content)
    return content

def fix_empty_links(content):
    """빈 링크 수정"""
    # [text]() → text
    content = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', content)
    
    # [text](#) → text (# 만 있는 경우)
    content = re.sub(r'\[([^\]]+)\]\(#\s*\)', r'\1', content)
    
    return content

def remove_toc_section(content):
    """목차 섹션 제거"""
    # [TOC] 제거
    content = re.sub(r'\[TOC\]\s*\n?', '', content, flags=re.IGNORECASE)
    
    # ## 목차 섹션 제거 (목차 헤더부터 다음 ## 헤더 전까지)
    content = re.sub(
        r'^##\s*목차\s*\n(.*?)(?=^##\s+[^#]|\Z)',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    return content

def fix_broken_internal_links(content):
    """잘못된 내부 링크 수정"""
    # 패턴: [텍스트](#한글-링크) 에서 링크가 작동하지 않을 수 있는 것들
    # 특수문자가 포함된 내부 링크를 텍스트로 변환
    
    # 한글이 포함된 내부 링크 중 복잡한 것들 제거
    # [텍스트](#복잡한-한글-링크) → 텍스트
    # 단, 간단한 영문 링크는 유지
    
    def replace_korean_anchor(match):
        text = match.group(1)
        anchor = match.group(2)
        # 앵커에 한글이 포함되어 있으면 텍스트만 남김
        if re.search(r'[가-힣]', anchor):
            return text
        return match.group(0)  # 영문 앵커는 유지
    
    content = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', replace_korean_anchor, content)
    
    return content

def fix_post(content):
    """모든 수정 적용"""
    original = content
    
    # 1. 목차 섹션 제거
    content = remove_toc_section(content)
    
    # 2. 헤더에서 이모지 제거
    content = remove_emoji_from_headers(content)
    
    # 3. 이미지 alt 추가
    content = fix_image_alt(content)
    
    # 4. 빈 링크 수정
    content = fix_empty_links(content)
    
    # 5. 잘못된 내부 링크 수정
    content = fix_broken_internal_links(content)
    
    # 6. 연속된 빈 줄 정리
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    changed = (content != original)
    return content, changed

def process_file(filepath):
    """단일 파일 처리"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, changed = fix_post(content)
        
        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
        
    except Exception as e:
        print(f"   ❌ 오류: {filepath}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n사용 예시:")
        print("  python fix_posts.py ./_posts")
        sys.exit(1)
    
    posts_dir = Path(sys.argv[1])
    
    if not posts_dir.exists():
        print(f"❌ 폴더를 찾을 수 없습니다: {posts_dir}")
        sys.exit(1)
    
    print(f"🔧 포스트 에러 수정 시작")
    print(f"   대상 폴더: {posts_dir}")
    print()
    print("수정 내용:")
    print("   1. 헤더에서 이모지 제거")
    print("   2. 이미지 alt 속성 추가")
    print("   3. 빈 링크 수정")
    print("   4. 잘못된 내부 링크 수정")
    print("   5. [TOC] 및 목차 섹션 제거")
    print()
    
    md_files = list(posts_dir.glob('*.md'))
    print(f"📁 발견된 마크다운 파일: {len(md_files)}개")
    print()
    
    fixed_count = 0
    
    for md_file in md_files:
        if process_file(md_file):
            print(f"   ✅ 수정됨: {md_file.name}")
            fixed_count += 1
    
    print()
    print(f"{'='*50}")
    print(f"📊 완료!")
    print(f"   - 전체 파일: {len(md_files)}개")
    print(f"   - 수정된 파일: {fixed_count}개")
    
    if fixed_count > 0:
        print()
        print("💡 이제 다시 배포하세요:")
        print("   git add .")
        print('   git commit -m "Fix HTML proofer errors"')
        print("   git push origin main")

if __name__ == '__main__':
    main()
