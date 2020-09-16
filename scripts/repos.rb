#!/usr/bin/env ruby

# frozen_string_literal: true

require 'rubygems'
require 'bundler/setup'

require 'httparty'

ORGS = %w[italia teamdigitale].freeze
EXCLUDED_MEMBERS = %w[rasky ruphy gunzip gvarisco biancini umbros jenkin cloudify matteodesanti pdavide].freeze

class GitHub
  include HTTParty

  # debug_output $stdout
  base_uri 'https://api.github.com'

  def repos
    ORGS.map do |org|
      paginated_get("https://api.github.com/orgs/#{org}/repos")
    end.flatten
  end

  def members(org)
    paginated_get("https://api.github.com/orgs/#{org}/members").map { |m| m['login'] }
  end

  def contributors(repo)
    commits = paginated_get("https://api.github.com/repos/#{repo}/commits?per_page=100&since=2020-01-09T00:00:00Z")
    # commits = paginated_get("https://api.github.com/repos/#{repo}/commits?per_page=100")

    commits.group_by { |c| c.dig('author', 'login') }
           .map { |login, c| { login => c.length } }
           .inject(:merge) || []
  end

  private

  def paginated_get(link)
    res = []
    while link
      warn "Getting #{link}..."
      r = HTTParty.get(link, {
        headers: {
          'Authorization' => "token #{ENV['GITHUB_TOKEN']}",
          'User-Agent' => 'repos.rb'
        }
      })
      # Empty repo
      return res if r.code == 409

      raise "HTTP code: #{r.code}. Response #{r.body}. URL: #{link}" if r.code != 200

      res += r.parsed_response

      link_header = r.headers['link']
      break if link_header.nil?

      matches = link_header.match(/<(https:[^\s]+?)>; rel="next"/)
      break if matches.nil?

      link = matches[1]
    end

    res
  end
end

def sort_contribs(contributors)
  place = -1
  sorted = []
  current_count = nil

  loop do
    max = contributors.max { |a, b| a[1] <=> b[1] }
    return sorted if max.nil?

    if max[1] != current_count
      return sorted if place == 2

      place += 1
      sorted[place] = []
    end

    current_count = max[1]

    sorted[place] << max
    contributors.delete(max[0])
  end
end

gh = GitHub.new

excluded_members = gh.members('teamdigitale') + gh.members('pagopa') + EXCLUDED_MEMBERS

repos = gh.repos
          .reject { |r| r['archived'] || r['disabled'] }
          .sort_by { |r| -r['stargazers_count'] }

medals = %w[🥇 🥈 🥉]

puts "# Contributions\n"

repos.each do |repo|
  name = repo['full_name']

  warn name
  contributors = gh.contributors(name)
                   .reject { |login, _| excluded_members.include?(login) || login.nil? || login =~ /\[bot\]/ }
                   .sort_by { |_, count| -count }
                   .to_h

  sorted = sort_contribs(contributors)

  puts "- [#{repo['name']}](#{repo['html_url']})"
  puts "  <img align='right' src='https://img.shields.io/github/stars/#{name}?label=%E2%AD%90%EF%B8%8F&logo=github' alt='GitHub stars'>"
  print "  <img align='right' src='https://img.shields.io/github/issues/#{name}' alt='GitHub issues'>"
  puts "\\\n  #{repo['description']}"
  puts

  medals.each_with_index do |medal, i|
    next if sorted[i].nil? || sorted[i].empty?

    sorted[i].each { |user| print "  #{medal} **[#{user[0]}](https://github.com/#{user[0]})** (#{user[1]}) " }
    puts
  end

  puts
end
