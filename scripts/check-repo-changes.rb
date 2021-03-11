#!/usr/bin/env ruby
# frozen_string_literal: true

require 'rubygems'
require 'bundler/setup'

require 'json'
require 'octokit'

ORGS = %w[teamdigitale italia].freeze
AWESOME_ITALIA_REPO = 'italia/awesome-italia'
STATE_REPO = 'developers-italia-droid/awesome-italia-state'
STATE_FILE = 'repos.json'

GITHUB_TOKEN = ENV.fetch('GITHUB_TOKEN', '')
abort 'Set GITHUB_TOKEN first.' if GITHUB_TOKEN.empty?

client = Octokit::Client.new(auto_paginate: true, access_token: GITHUB_TOKEN)
client.user.login

resp = client.contents(STATE_REPO, path: STATE_FILE)
previous_state_decoded = Base64.decode64(resp.content)
previous_state = JSON.parse(previous_state_decoded)

current_state = {}
added_repos = {}
removed_repos = {}
ORGS.each do |org|
  current_state[org] = client.org_repos(org, { type: 'public' })
                             .reject { |r| r['archived'] }
                             .map(&:full_name)

  removed_repos[org] = previous_state[org] - current_state[org]
  added_repos[org] = current_state[org] - previous_state[org]
end

added_count = added_repos.values.flatten.length
removed_count = removed_repos.values.flatten.length

added = added_count.positive?
removed = removed_count.positive?

if added || removed

  issue_body = ''

  info = "added repos #{added_count}, removed repos: #{removed_count}"
  puts info

  if added
    issue_body += "\n### The following repos were added\n"
    issue_body += added_repos.values.flatten.map { |r| "* [#{r}](https://github.com/#{r})\n" }.join
  end

  if removed
    issue_body += "\n### The following repos were removed or archived\n"
    issue_body += removed_repos.values.flatten.map { |r| "* [#{r}](https://github.com/#{r})\n" }.join
  end

  puts "Creating issue in #{AWESOME_ITALIA_REPO}"
  client.create_issue(AWESOME_ITALIA_REPO, "New or removed repositories (#{info})", issue_body)

  puts "Updating state file '#{STATE_FILE}' in #{STATE_REPO}"
  client.create_contents(STATE_REPO,
                         STATE_FILE,
                         ":robot: Update repos.json (added #{added_count}, removed: #{removed_count})",
                         current_state.to_json,
                         sha: resp.sha,
                         branch: 'main')
end
