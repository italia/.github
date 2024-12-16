# Generates .md from JSON

import os, json
from slugify import slugify
from utils import auth_to_github, get_inactive_repos, write_inactive_repos_to_md

gh_connection = auth_to_github()

def generate_markdown(summary, repositories):
    final_markdown = f"""<!-- markdownlint-disable line-length no-inline-html -->
<!--
    line-length: Split up badges lines are busier than having long lines
    no-inline-html: We need that sweet center align
-->

<p align="center">
<br>
<img width="200" src="awesome-italia.png" alt="logo of awesome-italia">
<br>
</p>

{summary}

<p align="center">
<a href="https://developers.italia.it/en/to-do" title="Search issues in need for help" >
    <strong>Want to help?</strong>
</a>
•
<a href="https://come-partecipo.italia.it"
    title="Scopri come contribuire al miglioramento dei servizi pubblici digitali del Paese"
>
    <strong>Come partecipo?</strong>
</a>
</p>

# Awesome Italia

> The organized list of awesome @italia (and friends) projects

{repositories}
    """
    with open(os.path.join('README.md'), "w") as f:
        f.write(final_markdown)

def repo_to_json():
    groups = []
    repositories = {}
    with open(os.path.join('data', 'groups.json')) as f:
        groups = json.load(f)
    with open(os.path.join('data', 'repositories.json')) as f:
        repositories = json.load(f)
    inactive_repos = get_inactive_repos(gh_connection, 365, 'italia')
    write_inactive_repos_to_md(inactive_repos, 365)
    inactive_repos_urls = [repo['url'] for repo in inactive_repos]
    for repo in gh_connection.organization('italia').repositories():
        if repo.html_url not in inactive_repos_urls:
            if repo.archived or repo.private:
                if repo.html_url in repositories:
                    del repositories[repo.html_url]  
                continue              
            if not repo.html_url in repositories:
                repositories[repo.html_url] = ''
            else:
                if repositories[repo.html_url]:
                    group = [gr for gr in groups if gr['id'] == repositories[repo.html_url]][0]
                    if not "repos" in group:
                        group["repos"] = []
                    group["repos"].append(
                        {
                            'url' : repo.html_url,
                            'slug' : repo.name,
                            'description': repo.description or '',
                            'stars' : repo.stargazers_count
                        }
                    )
    with open(os.path.join('data', 'repositories.json'), 'w', encoding='utf-8') as f:
        json.dump(repositories, f, ensure_ascii=False, indent=4)
    return groups

def create_group_title(icon, group_name):
    return f'## {icon} {group_name}'

def create_group_list_item(icon, group_name):
    return f'• [{icon} {group_name}](#-{slugify(group_name)})'

def create_repo_list_item(slug, description):
    repo_item = f"""- [{slug}](https://github.com/italia/{slug})
  <img align="right" src="https://img.shields.io/github/stars/italia/{slug}?label=%E2%AD%90%EF%B8%8F&logo=github" alt="GitHub stars">
  <img align="right" src="https://img.shields.io/github/issues/italia/{slug}" alt="GitHub issues">\
  {description}
    """
    return repo_item


summary = ''
repositories = ''

groups = repo_to_json()

for group in groups:
    summary += f'{create_group_list_item(group['icon'], group['name'])}\n'

for group in groups:
    repositories += f'{create_group_title(group['icon'], group['name'])}\n\n'
    repositories += f'{group['description']}\n'
    if "repos" in group:
        for repo in sorted(group['repos'], key=lambda d: d['stars'], reverse=True):
            repositories += f'{create_repo_list_item(repo['slug'], repo['description'])}\n'

generate_markdown(summary, repositories)
