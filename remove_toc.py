#!/usr/bin/env python3
"""
포스트에서 수동 목차 및 [TOC] 제거 스크립트

Chirpy 테마는 자동 TOC를 지원하므로 수동 목차가 필요 없습니다.
이 스크립트는 다음을 제거합니다:
1. [TOC] 마커
2. ## 목차 섹션 전체
3. 고아 앵커 링크 (내부 링크)

사용법:
    python remove_toc.py <_posts 폴더 경로>

예시:
    python remove_toc.py ./_posts
"""

import os
import re
import sys
from pathlib import Path

def remove_toc_section(content):
    """목차 섹션과 [TOC] 제거"""
    
    original_content = content
    
    # 1. [TOC] 제거
    content = re.sub(r'\[TOC\]\s*\n?', '', content, flags=re.IGNORECASE)
    
    # 2. ## 목차 섹션 제거 (목차 헤더부터 다음 ## 헤더 전까지)
    # 패턴: ## 목차 로 시작하고, 다음 ## 이 나오기 전까지의 내용
    content = re.sub(
        r'^##\s*목차\s*\n(.*?)(?=^##\s+[^#]|\Z)',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 3. 빈 줄이 3개 이상 연속되면 2개로 줄이기
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    changed = (content != original_content)
    return content, changed

def process_file(filepath):
    """단일 파일 처리"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, changed = remove_toc_section(content)
        
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
        print("  python remove_toc.py ./_posts")
        sys.exit(1)
    
    posts_dir = Path(sys.argv[1])
    
    if not posts_dir.exists():
        print(f"❌ 폴더를 찾을 수 없습니다: {posts_dir}")
        sys.exit(1)
    
    print(f"🔧 수동 목차 및 [TOC] 제거 시작")
    print(f"   대상 폴더: {posts_dir}")
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
        print('   git commit -m "Remove manual TOC sections"')
        print("   git push origin main")

if __name__ == '__main__':
    main()
