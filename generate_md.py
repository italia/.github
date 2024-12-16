import os, json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from slugify import slugify
from utils import auth_to_github, get_inactive_repos, write_inactive_repos_to_md


def load_groups_and_repos():
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
                            'stars' : repo.stargazers_count
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