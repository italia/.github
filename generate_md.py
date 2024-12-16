import os, json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from slugify import slugify
from utils import auth_to_github, get_inactive_repos, write_inactive_repos_to_md

ORGANIZATIONS = ['italia', 'teamdigitale']
INACTIVE_DAYS_TRESHOLD = 365

def load_groups_and_repos():
    groups = []
    repositories = {}
    with open(os.path.join('data', 'groups.json')) as f:
        groups = json.load(f)
    with open(os.path.join('data', 'repositories.json')) as f:
        repositories = json.load(f)
    inactive_repos = []
    all_repos = []

    for organization in ORGANIZATIONS:
        inactive_repos.extend(get_inactive_repos(gh_connection, INACTIVE_DAYS_TRESHOLD, organization))
        all_repos.extend(gh_connection.organization(organization).repositories())

    write_inactive_repos_to_md(inactive_repos, INACTIVE_DAYS_TRESHOLD)
    inactive_repos_urls = [repo['url'] for repo in inactive_repos]

    for repo in all_repos:
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
                    ## Init group
                    if not "repos" in group:
                        group["repos"] = []
                    if not "slug" in group:
                        group["slug"] = slugify(group["name"])
                    group["repos"].append(
                        {
                            'url' : repo.html_url,
                            'slug' : repo.name,
                            'description': repo.description or '',
                            'stars' : repo.stargazers_count,
                            'organization': repo.html_url.replace('https://github.com/', '').split('/')[0]
                        }
                    )
    with open(os.path.join('data', 'repositories.json'), 'w', encoding='utf-8') as f:
        json.dump(repositories, f, ensure_ascii=False, indent=4)
    return groups


if __name__ == '__main__':
    gh_connection = auth_to_github()

    groups = load_groups_and_repos()

    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join('templates')),
        autoescape=select_autoescape()
    )

    template = env.get_template(os.path.join('main.md'))

    with open(os.path.join('README.md'), "w") as f:
        f.write(template.render(groups=groups))