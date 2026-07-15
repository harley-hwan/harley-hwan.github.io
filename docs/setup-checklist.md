# 사이트 설정 마무리 체크리스트

코드/설정 인프라는 모두 준비된 상태이며, 아래 항목은 **각 서비스 대시보드에서 값을 발급받아
`_config.yml`에 붙여넣는 작업**만 남아 있다. 항목당 5~10분 소요.
값을 채운 뒤 push 하면 GitHub Actions 가 자동 배포한다.

> 이 폴더(`docs/`)는 `_config.yml`의 `exclude` 목록에 있어 사이트에 게시되지 않는다.

---

## 1. Google AdSense 광고 단위 (수익화)

현재 상태: `adsense.client` 는 설정되어 있으나 slot 3개가 비어 있어 **광고가 하나도 렌더링되지 않는다**
(스크립트 로드 비용만 지불 중). 자동 광고는 대시보드에서 꺼둔 상태를 유지할 것.

1. [AdSense 대시보드](https://adsense.google.com) → **광고 → 광고 단위 기준** 이동.
2. 광고 단위 3개 생성:
   | 용도 | 권장 유형 | `_config.yml` 키 |
   |---|---|---|
   | 글 하단 (태그 아래) | 디스플레이 광고 (반응형) | `adsense.slot_post_bottom` |
   | 홈 피드 5번째 카드 아래 | 인피드 광고 또는 디스플레이 | `adsense.slot_home_feed` |
   | 글 상단 (제목 아래, 선택) | 디스플레이 광고 (반응형) | `adsense.slot_post_top` |
3. 각 단위의 `data-ad-slot` 숫자만 복사해 해당 키에 입력.
4. 인피드 광고로 만든 경우 `data-ad-layout-key` 값을 `adsense.home_feed_layout_key` 에 입력
   (디스플레이 광고면 비워둠).

> 글 상단(post_top)은 노출은 많지만 읽기 시작을 늦추므로, 우선 하단+피드 2개만 운영하고
> 반응을 본 뒤 결정하는 것을 권장.

## 2. Google Search Console (구글 검색 등록)

1. [Search Console](https://search.google.com/search-console) → 속성 추가 → **URL 접두어** 방식으로
   `https://harley-hwan.github.io` 입력.
2. 확인 방법 중 **HTML 태그** 선택 → `<meta name="google-site-verification" content="여기값">` 의
   **content 값만** 복사.
3. `_config.yml` → `webmaster_verifications.google` 에 붙여넣고 push → 배포 완료 후 Search Console 에서 "확인" 클릭.
4. 확인 후: **Sitemaps** 메뉴에 `sitemap.xml` 제출.

## 3. 네이버 서치어드바이저 (네이버 검색 등록)

한국어 기술 블로그이므로 네이버 유입 효과가 크다.

1. [서치어드바이저](https://searchadvisor.naver.com) → 웹마스터 도구 → 사이트 등록:
   `https://harley-hwan.github.io`
2. 소유 확인 중 **HTML 태그** 방식 선택 → content 값만 복사.
3. `_config.yml` → `webmaster_verifications.naver` 에 붙여넣고 push → 배포 후 소유 확인 클릭.
   (렌더링은 `_includes/metadata-hook.html` 이 처리한다.)
4. 확인 후: **요청 → 사이트맵 제출**에 `sitemap.xml`, **RSS 제출**에 `rss.xml` 제출.
   > 주의: Chirpy 기본 피드(`feed.xml`)는 Atom 형식이라 네이버 RSS 제출에서
   > "올바른 RSS가 아닙니다"로 거부된다. 이를 위해 RSS 2.0 형식의 `/rss.xml` 을
   > 저장소 루트에 별도로 두었다 (일반 구독기는 계속 `feed.xml` 사용).

## 4. giscus 댓글

`_config.yml` 의 `comments.giscus` 에 `repo`, `repo_id`, `category` 는 이미 채워져 있다.
남은 것은 아래 3단계 + `category_id` 입력.

1. GitHub 저장소 → **Settings → General → Features → Discussions 체크박스 활성화**.
2. <https://github.com/apps/giscus> → Install → `harley-hwan.github.io` 저장소 선택.
3. <https://giscus.app> 접속 → 저장소에 `harley-hwan/harley-hwan.github.io` 입력 →
   Discussion 카테고리에서 **Announcements** 선택 → 하단 생성된 스크립트에서
   `data-category-id` 값 복사.
4. `_config.yml` 수정 2곳:
   - `comments.giscus.category_id` 에 복사한 값 입력
   - `comments.provider` 를 `giscus` 로 변경 ← **category_id 입력 전에 켜면 안 됨**

## 5. Google Analytics 4 (방문자 분석)

1. [Google Analytics](https://analytics.google.com) → 관리 → 계정/속성 만들기 (속성 이름 예: harley's dev note).
2. 데이터 스트림 → 웹 → `https://harley-hwan.github.io` 등록 → **측정 ID (G-XXXXXXXXXX)** 복사.
3. `_config.yml` → `analytics.google.id` 에 입력.
   (Chirpy 가 production 빌드에서만 gtag 를 로드하므로 로컬 개발에는 영향 없음.)

---

## 배포 후 확인 방법

- **og:image**: 카카오톡/슬랙에 글 URL 붙여넣기 → 미리보기 카드에 `social-preview.png` 가 떠야 함.
  카카오톡 캐시가 남으면 <https://developers.kakao.com/tool/debugger/sharing> 에서 초기화.
- **AdSense**: 광고 반영까지 수 분~수 시간 걸릴 수 있음. 미채움(unfilled) 시 영역이 자동으로 숨겨짐.
- **giscus**: 아무 글 하단에 댓글 위젯이 뜨고, 댓글 작성 시 저장소 Discussions 에 스레드가 생성됨.
- **GA4**: 실시간 보고서에서 본인 접속이 잡히는지 확인.
- **검색 등록**: 색인 반영까지 며칠 걸림. Search Console/서치어드바이저에서 색인 현황 확인.
