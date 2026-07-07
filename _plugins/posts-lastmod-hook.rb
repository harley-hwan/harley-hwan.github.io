#!/usr/bin/env ruby
#
# Check for changed posts

require "open3"

module PostsLastmodHook
  def self.cache_for(site)
    @cache ||= {}
    @cache[site.source] ||= build_cache(site)
  end

  def self.build_cache(site)
    output, status = Open3.capture2e(
      "git",
      "-C",
      site.source,
      "log",
      "--name-only",
      "--pretty=format:%H%x09%ad",
      "--date=iso",
      "--",
      "_posts"
    )

    return {} unless status.success?

    cache = Hash.new { |hash, path| hash[path] = { count: 0, lastmod: nil } }
    current_date = nil

    output.each_line do |line|
      line = line.chomp

      if line.match?(/\A[0-9a-f]{40}\t/)
        current_date = line.split("\t", 2).last
      elsif current_date && line.start_with?("_posts/")
        path = File.expand_path(line, site.source)
        cache[path][:count] += 1
        cache[path][:lastmod] ||= current_date
      end
    end

    cache
  end
end

Jekyll::Hooks.register :posts, :post_init do |post|
  info = PostsLastmodHook.cache_for(post.site)[File.expand_path(post.path)]

  post.data["last_modified_at"] = info[:lastmod] if info && info[:count] > 1
end
