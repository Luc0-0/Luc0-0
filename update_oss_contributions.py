import urllib.request
import json
import re
from datetime import datetime, timezone

USERNAME = "Luc0-0"
README_PATH = "README.md"


def _gh(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    data = _gh(f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr&per_page=100")
    items = data.get('items', [])

    counts = {}
    for item in items:
        owner = item['repository_url'].split('/repos/')[1].split('/')[0]
        if owner.lower() == USERNAME.lower():
            continue
        counts[owner] = counts.get(owner, 0) + 1

    orgs = []
    for owner, count in counts.items():
        try:
            user = _gh(f"https://api.github.com/users/{owner}")
        except Exception:
            continue
        if user.get('type') == 'Organization':
            orgs.append((owner, count))

    orgs.sort(key=lambda x: -x[1])

    badges = " ".join(
        f'<a href="https://github.com/{login}" title="{login} — {count} PR{"s" if count != 1 else ""}">'
        f'<img src="https://github.com/{login}.png" width="40" height="40" alt="{login}"/></a>'
        for login, count in orgs
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(
        r'(<!-- OSS_ORGS -->).*?(<!-- /OSS_ORGS -->)',
        lambda m: f"{m.group(1)}\n{badges}\n{m.group(2)}",
        content,
        flags=re.DOTALL,
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = re.sub(
        r'(<!-- LAST_UPDATED -->).*?(<!-- /LAST_UPDATED -->)',
        rf'\g<1>{today}\g<2>',
        content,
    )

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OSS orgs: {orgs}, last_updated: {today}")


if __name__ == "__main__":
    main()
