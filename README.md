# harley's dev note

Jekyll + Chirpy 기반 개인 기술 블로그입니다.

## Structure

- `_posts`: Markdown posts.
- `_layouts`, `_includes`: Chirpy layout overrides and AdSense includes.
- `_plugins`: build-time helpers such as Git-based `last_modified_at`.
- `_tabs`, `_data`: sidebar tabs and contact/share metadata.
- `assets/img`, `assets/video`: site-owned media.
- `assets/lib`: Chirpy static-assets submodule kept for reference/offline use, excluded from the generated site while CDN assets are used.
- `docs/setup-checklist.md`: dashboard-side setup checklist (AdSense units, Search Console, Naver Search Advisor, giscus, GA4). Not published to the site.

## Local Development

```shell
bundle install
bundle exec jekyll serve --livereload
```

The VS Code task `Run Jekyll Server` runs `tools/run.sh`.

## Build

```shell
JEKYLL_ENV=production bundle exec jekyll build
```

## Test

```shell
bundle exec htmlproofer _site \
  --disable-external \
  --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
```

On Windows, `html-proofer` requires `libcurl.dll` on `PATH`. The most reliable local test environment is the devcontainer or WSL.

## Content Notes

- Post filenames use lowercase kebab-case.
- If an old filename had a legacy URL, keep it with front matter `slug`.
- Use slug-safe tags such as `cpp`, `csharp`, `c-language`, `visual-studio`, and `deep-learning`.
- Prefer local images under `assets/img/posts/<post-slug>/` instead of external image hosts.
- Use `pwsh tools/migrate-external-images.ps1` to download external Markdown images and rewrite them to local asset paths.

## Deploy

GitHub Actions builds and deploys the site to GitHub Pages on pushes to `main` or `master`.
