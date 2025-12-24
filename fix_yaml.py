#!/usr/bin/env python3
"""
포스트 Front Matter YAML 오류 수정 스크립트

문제 해결:
1. 중첩된 따옴표: ""text"" → "text"
2. 콜론이 포함된 값 따옴표 처리
3. 대괄호가 포함된 값 따옴표 처리

사용법:
    python fix_yaml.py <_posts 폴더 경로>
    
예시:
    python fix_yaml.py ./_posts
"""

import os
import re
import sys
from pathlib import Path

def fix_front_matter(content):
    """Front matter의 YAML 오류 수정"""
    
    # front matter 추출
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return content, False
    
    front_matter = match.group(1)
    body = match.group(2)
    
    original_front_matter = front_matter
    
    # 1. 중첩된 따옴표 수정: ""text"" → "text"
    front_matter = re.sub(r'""([^"]*?)""', r'"\1"', front_matter)
    
    # 2. 빈 중첩 따옴표 수정: """" → ""
    front_matter = re.sub(r'""""', '""', front_matter)
    
    # 3. title/description 라인에서 따옴표가 없고 특수문자가 있는 경우 처리
    lines = front_matter.split('\n')
    fixed_lines = []
    
    for line in lines:
        # title: 또는 description: 라인 처리
        for field in ['title', 'description']:
            pattern = rf'^({field}:\s*)(.+)$'
            match = re.match(pattern, line)
            if match:
                prefix = match.group(1)
                value = match.group(2).strip()
                
                # 이미 따옴표로 감싸져 있는지 확인
                if value.startswith('"') and value.endswith('"'):
                    # 중첩 따옴표 제거
                    if value.startswith('""') and value.endswith('""'):
                        value = '"' + value[2:-2] + '"'
                elif value.startswith("'") and value.endswith("'"):
                    pass  # 이미 처리됨
                else:
                    # 특수문자가 있으면 따옴표로 감싸기
                    special_chars = [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', '%', '@', '`']
                    if any(c in value for c in special_chars):
                        # 내부 따옴표 이스케이프
                        if '"' in value:
                            value = "'" + value + "'"
                        else:
                            value = '"' + value + '"'
                
                line = prefix + value
                break
        
        fixed_lines.append(line)
    
    front_matter = '\n'.join(fixed_lines)
    
    # 변경 여부 확인
    changed = (front_matter != original_front_matter)
    
    return f'---\n{front_matter}\n---\n{body}', changed

def process_file(filepath):
    """단일 파일 처리"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, changed = fix_front_matter(content)
        
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
        print("  python fix_yaml.py ./_posts")
        sys.exit(1)
    
    posts_dir = Path(sys.argv[1])
    
    if not posts_dir.exists():
        print(f"❌ 폴더를 찾을 수 없습니다: {posts_dir}")
        sys.exit(1)
    
    print(f"🔧 YAML 오류 수정 시작")
    print(f"   대상 폴더: {posts_dir}")
    print()
    
    md_files = list(posts_dir.glob('*.md'))
    print(f"📁 발견된 마크다운 파일: {len(md_files)}개")
    print()
    
    fixed_count = 0
    error_count = 0
    
    for md_file in md_files:
        try:
            if process_file(md_file):
                print(f"   ✅ 수정됨: {md_file.name}")
                fixed_count += 1
        except Exception as e:
            print(f"   ❌ 오류: {md_file.name}: {e}")
            error_count += 1
    
    print()
    print(f"{'='*50}")
    print(f"📊 완료!")
    print(f"   - 전체 파일: {len(md_files)}개")
    print(f"   - 수정된 파일: {fixed_count}개")
    print(f"   - 오류 발생: {error_count}개")

if __name__ == '__main__':
    main()
