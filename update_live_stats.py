import urllib.request
import json
import re
import os

USERNAME = "Luc0-0"
SVG_PATH = "header/live_stats.svg"


def _gh(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def replace_marker(content, tag, value):
    pattern = rf'(<!-- {tag} -->).*?(<!-- /{tag} -->)'
    return re.sub(pattern, rf'\g<1>{value}\g<2>', content)


def main():
    user = _gh(f"https://api.github.com/users/{USERNAME}")
    followers = user.get('followers', 0)

    repos = _gh(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    owned = [r for r in repos if not r.get('fork')]

    total_stars = sum(r.get('stargazers_count', 0) for r in owned)
    repo_count = len(owned)

    languages = {}
    for r in owned:
        lang = r.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    top_languages = " · ".join(l for l, _ in sorted(languages.items(), key=lambda x: -x[1])[:3])

    with open(SVG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    content = replace_marker(content, 'REPOS_COUNT', repo_count)
    content = replace_marker(content, 'STARS_COUNT_TOTAL', total_stars)
    content = replace_marker(content, 'FOLLOWERS_COUNT', followers)
    content = replace_marker(content, 'TOP_LANGUAGES', top_languages)

    with open(SVG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated {SVG_PATH}: repos={repo_count} stars={total_stars} followers={followers} top={top_languages}")


if __name__ == "__main__":
    main()
