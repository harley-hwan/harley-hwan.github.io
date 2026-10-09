#!/usr/bin/env ruby
#
# Check for changed posts

require "open3"

module PostsLastmodHook
  def self.cache_for(site)
    @cache ||= {}
    @cache[site.source] ||= build_cache(site)
  end

  # 이름 변경(-M)을 따라가며 센다. 글을 _posts 아래 다른 폴더로 옮기면 git 에는
  # 새 경로의 커밋 하나만 남으므로, 경로 그대로 세면 옮긴 글이 수정 이력을 잃는다.
  # git 이 유사도 100% 로 판정한 이동(R100)은 수정으로 치지 않는다.
  def self.build_cache(site)
    output, status = Open3.capture2e(
      "git",
      "-C",
      site.source,
      "log",
      "--name-status",
      "-M",
      "--pretty=format:%H%x09%ad",
      "--date=iso",
      "--",
      "_posts"
    )

    return {} unless status.success?

    cache = Hash.new { |hash, path| hash[path] = { count: 0, lastmod: nil } }
    renamed_to = {}
    current_date = nil

    output.each_line do |line|
      line = line.chomp

      if line.match?(/\A[0-9a-f]{40}\t/)
        current_date = line.split("\t", 2).last
        next
      end

      # "M\t경로", "A\t경로", "D\t경로" 또는 "R<유사도>\t옛 경로\t새 경로"
      change, *paths = line.split("\t")
      next unless current_date && paths.last&.start_with?("_posts/")

      # 로그는 최신 커밋부터 나오므로, 이름 변경을 만나면 옛 경로를 지금 경로에 잇는다.
      current_path = renamed_to.fetch(paths.last, paths.last)
      if change.start_with?("R")
        renamed_to[paths.first] = current_path
        next if change == "R100"
      end

      path = File.expand_path(current_path, site.source)
      cache[path][:count] += 1
      cache[path][:lastmod] ||= current_date
    end

    cache
  end
end

Jekyll::Hooks.register :posts, :post_init do |post|
  info = PostsLastmodHook.cache_for(post.site)[File.expand_path(post.path)]

  post.data["last_modified_at"] = info[:lastmod] if info && info[:count] > 1
end
