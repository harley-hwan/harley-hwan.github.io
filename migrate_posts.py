#!/usr/bin/env python3
"""
Beautiful Jekyll → Chirpy 포스트 마이그레이션 스크립트

사용법:
    python migrate_posts.py <백업폴더경로> <새블로그_posts경로>
    
예시:
    python migrate_posts.py ./blog-backup ./harley-hwan.github.io/_posts
"""

import os
import re
import sys
import shutil
from pathlib import Path

# 카테고리 매핑 테이블 (폴더명 → Chirpy categories)
CATEGORY_MAP = {
    # Algorithm
    'baekjoon': '[Algorithm, Baekjoon]',
    'programmers': '[Algorithm, Programmers]',
    # Dev
    'cdbplus': '[Dev, C++]',
    'csharp': '[Dev, CSharp]',
    'cuda': '[Dev, CUDA]',
    'linux': '[Dev, Linux]',
    'docker': '[Dev, Docker]',
    'mfc': '[Dev, MFC]',
    'wpf': '[Dev, WPF]',
    'opencv': '[Dev, OpenCV]',
    'cnn': '[Dev, CNN]',
    'dev_etc': '[Dev, ETC]',
    # Project
    'project': '[Project]',
}

def extract_date_from_filename(filename):
    """파일명에서 날짜 추출 (YYYY-MM-DD-title.md 형식)"""
    match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def convert_front_matter(content, category_folder, filename):
    """Front matter를 Chirpy 형식으로 변환"""
    
    # front matter 추출
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        print(f"  ⚠️  Front matter를 찾을 수 없음: {filename}")
        return content
    
    front_matter = match.group(1)
    body = match.group(2)
    
    # 기존 값들 추출
    title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
    subtitle_match = re.search(r'^subtitle:\s*(.+)$', front_matter, re.MULTILINE)
    tags_match = re.search(r'^tags:\s*\[(.+)\]$', front_matter, re.MULTILINE)
    
    title = title_match.group(1).strip() if title_match else filename
    subtitle = subtitle_match.group(1).strip() if subtitle_match else ""
    tags = tags_match.group(1).strip() if tags_match else ""
    
    # 제목에 따옴표가 없으면 추가
    if not (title.startswith('"') or title.startswith("'")):
        # 특수문자가 있으면 따옴표로 감싸기
        if any(c in title for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', "'", '"']):
            title = f'"{title}"'
    
    # 파일명에서 날짜 추출
    date_str = extract_date_from_filename(filename)
    if not date_str:
        date_str = "2024-01-01"  # 기본값
    
    # 카테고리 매핑
    categories = CATEGORY_MAP.get(category_folder.lower(), '[ETC]')
    
    # 새 front matter 생성
    new_front_matter_lines = [
        f'title: {title}',
    ]
    
    if subtitle:
        # description도 특수문자 처리
        if any(c in subtitle for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', "'", '"']):
            subtitle = f'"{subtitle}"'
        new_front_matter_lines.append(f'description: {subtitle}')
    
    new_front_matter_lines.append(f'date: {date_str} 10:00:00 +0900')
    new_front_matter_lines.append(f'categories: {categories}')
    
    if tags:
        new_front_matter_lines.append(f'tags: [{tags}]')
    
    new_front_matter = '\n'.join(new_front_matter_lines)
    
    return f'---\n{new_front_matter}\n---\n{body}'

def find_category_folders(backup_path):
    """백업 폴더에서 카테고리 폴더들 찾기"""
    categories = []
    backup = Path(backup_path)
    
    for item in backup.iterdir():
        if item.is_dir():
            posts_dir = item / '_posts'
            if posts_dir.exists():
                categories.append(item.name)
    
    return categories

def migrate_posts(backup_path, output_path):
    """모든 포스트 마이그레이션"""
    backup = Path(backup_path)
    output = Path(output_path)
    
    # 출력 폴더 생성
    output.mkdir(parents=True, exist_ok=True)
    
    # 카테고리 폴더 찾기
    categories = find_category_folders(backup_path)
    print(f"\n📁 발견된 카테고리 폴더: {len(categories)}개")
    for cat in categories:
        print(f"   - {cat}")
    
    total_files = 0
    converted_files = 0
    errors = []
    
    for category in categories:
        posts_dir = backup / category / '_posts'
        if not posts_dir.exists():
            continue
        
        md_files = list(posts_dir.glob('*.md'))
        print(f"\n📂 {category}/ ({len(md_files)}개 파일)")
        
        for md_file in md_files:
            total_files += 1
            try:
                # 파일 읽기
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 변환
                new_content = convert_front_matter(content, category, md_file.name)
                
                # 새 파일로 저장
                output_file = output / md_file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                converted_files += 1
                print(f"   ✅ {md_file.name}")
                
            except Exception as e:
                errors.append((md_file.name, str(e)))
                print(f"   ❌ {md_file.name}: {e}")
    
    # 결과 출력
    print(f"\n{'='*50}")
    print(f"📊 마이그레이션 완료!")
    print(f"   - 전체 파일: {total_files}개")
    print(f"   - 변환 성공: {converted_files}개")
    print(f"   - 변환 실패: {len(errors)}개")
    
    if errors:
        print(f"\n⚠️  실패한 파일들:")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    
    print(f"\n📁 변환된 파일 위치: {output}")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\n사용 예시:")
        print("  python migrate_posts.py ./blog-backup ./harley-hwan.github.io/_posts")
        sys.exit(1)
    
    backup_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(backup_path):
        print(f"❌ 백업 폴더를 찾을 수 없습니다: {backup_path}")
        sys.exit(1)
    
    print(f"🚀 Beautiful Jekyll → Chirpy 마이그레이션 시작")
    print(f"   백업 폴더: {backup_path}")
    print(f"   출력 폴더: {output_path}")
    
    migrate_posts(backup_path, output_path)

if __name__ == '__main__':
    main()
