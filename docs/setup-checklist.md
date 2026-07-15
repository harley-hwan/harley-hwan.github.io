# 사이트 설정 마무리 체크리스트

## 진행 상태 (2026-07-16 기준)

- ✅ **giscus**: 완료 (Discussions + 앱 설치 + category_id + provider 활성화)
- ✅ **GA4**: 측정 ID 입력 완료 (G-1TB5XCP1T3) — 배포 후 실시간 보고서로 확인
- 🔶 **Search Console**: 인증값 입력 완료 — 배포 후 대시보드에서 "확인" 클릭 + sitemap.xml 제출 필요
- 🔶 **네이버**: 인증값 입력 완료 — 배포 후 "소유확인" 클릭 + sitemap.xml/rss.xml 제출 필요
- 🔶 **AdSense**: post_bottom만 가동 — slot_post_mid(인아티클) 등 단위 추가 생성 권장 (섹션 1)

---

코드/설정 인프라는 모두 준비된 상태이며, 아래 항목은 **각 서비스 대시보드에서 값을 발급받아
`_config.yml`에 붙여넣는 작업**만 남아 있다. 항목당 5~10분 소요.
값을 채운 뒤 push 하면 GitHub Actions 가 자동 배포한다.

> 이 폴더(`docs/`)는 `_config.yml`의 `exclude` 목록에 있어 사이트에 게시되지 않는다.

---

## 1. Google AdSense 광고 단위 (수익화)

현재 상태: post_bottom(5813890411)만 가동 중. 나머지 슬롯을 채우면 배치가 완성된다.
자동 광고(페이지 자동 삽입)는 대시보드에서 꺼둔 상태를 유지할 것 — 단, 아래 "앵커 광고" 예외 참고.

1. [AdSense 대시보드](https://adsense.google.com) → **광고 → 광고 단위 기준** 이동.
2. 광고 단위 생성 (수익 효율 우선순위 순):
   | 우선순위 | 용도 | 권장 유형 | `_config.yml` 키 |
   |---|---|---|---|
   | 1 | 본문 중간 (기본: 3번째 h2 섹션 뒤, 섹션 5개↑ 글만) | **인아티클(In-article) 광고** | `adsense.slot_post_mid` ✅ 완료 |
   | 2 | 글 하단 (태그 아래) | 디스플레이 광고 (반응형) | `adsense.slot_post_bottom` ✅ 완료 |
   | 3 | 홈 피드 5번째 카드 아래 | 인피드 광고 또는 디스플레이 | `adsense.slot_home_feed` |
   | 4 | 글 상단 (제목 아래, 선택) | 디스플레이 광고 (반응형) | `adsense.slot_post_top` |
3. 각 단위의 `data-ad-slot` 숫자만 복사해 해당 키에 입력.
4. 인피드 광고로 만든 경우 `data-ad-layout-key` 값을 `adsense.home_feed_layout_key` 에 입력
   (디스플레이 광고면 비워둠).

> - **본문 중간(post_mid)이 통상 RPM이 가장 높다.** 독자가 글을 읽는 중간에 자연스럽게 노출되기
>   때문. 읽기 방해 최소화를 위해 `post_mid_min_sections`(기본 5) 개 이상 섹션을 가진 긴 글에만,
>   `post_mid_after_section`(기본 3) 번째 섹션 뒤에 삽입된다 — _config.yml 숫자로 조정 가능.
>   광고가 채워지면 위아래 경계선 + "광고" 라벨로 본문과 구분 표시된다. 끄려면 slot 값만 비우면 됨.
> - 글 상단(post_top)은 노출은 많지만 읽기 시작을 늦추므로 마지막에 고려.
> - **앵커 광고(모바일 하단 고정)를 원하면**: 대시보드 → 광고 → 사이트별 → 자동 광고 켬 →
>   광고 형식에서 **앵커만 켜고** "페이지 내 광고(In-page)"는 꺼둘 것. 이러면 본문 레이아웃은
>   그대로 두고 모바일 하단 고정 광고만 추가된다 (수익 기여 큼, 취향에 따라 선택).

### 광고가 안 보일 때 점검 순서

1. **사이트 승인 상태**: 대시보드 → 사이트 → `harley-hwan.github.io` 가 "준비됨"인지 확인.
   "요검토/승인 대기"면 광고가 아예 서빙되지 않는다 (신규 사이트는 승인에 며칠~2주).
2. **신규 광고 단위 지연**: 단위 생성 후 서빙까지 보통 수 시간, 최대 하루.
3. 페이지 소스에 `data-ad-slot` 태그가 있는데 영역이 안 보이면 → 미채움(unfilled)으로
   자동 숨김된 것 (정상 동작). AdSense 보고서에서 "광고 요청 수"가 잡히는지 확인.
4. 광고 차단 확장 프로그램이 켜진 브라우저에서는 당연히 안 보인다.

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
