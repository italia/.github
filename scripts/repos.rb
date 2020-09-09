#!/usr/bin/env ruby

# frozen_string_literal: true

require 'rubygems'
require 'bundler/setup'

require 'httparty'

class Repos
  include HTTParty

  # debug_output $stdout
  base_uri 'https://api.github.com'

  def all
    repos = []

    orgs = [
      'https://api.github.com/orgs/italia/repos',
      'https://api.github.com/orgs/teamdigitale/repos'
    ]

    orgs.each do |link|
      while link
        r = HTTParty.get(link, {
          headers: {
            'Authorization' => "token #{ENV['GITHUB_TOKEN']}",
            'User-Agent' => 'repos.rb'
          }
        })
        raise "HTTP code: #{r.code}. Response #{r.body}. URL: #{link}" if r.code != 200

        repos += r.parsed_response

        link_header = r.headers['link']
        break if link_header.nil?

        matches = link_header.match(/<(https:[^\s]+?)>; rel="next"/)
        break if matches.nil?

        link = matches[1]
      end
    end

    repos
  end
end

repos = Repos.new.all
             .reject { |r| r['archived'] || r['disabled'] }
             .sort_by { |r| -r['stargazers_count'] }

repos.each do |p|
  name = p['full_name']

  puts "- [#{p['name']}](#{p['html_url']})"
  puts "  <img align='right' src='https://img.shields.io/github/stars/#{name}?label=%E2%AD%90%EF%B8%8F&logo=github' alt='GitHub stars'>"
  print "  <img align='right' src='https://img.shields.io/github/issues/#{name}' alt='GitHub issues'>"
  puts "\\\n  #{p['description']}"
  puts
end
