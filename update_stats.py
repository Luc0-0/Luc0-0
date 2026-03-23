import urllib.request
import json
import re
import os

REPOS = {
    "Serenity-Multi-Modal-Mental-Assistant-System": ("header/pinned_serenity.svg", "SERENITY"),
    "Smart-notes-by-Nipun": ("header/pinned_notes.svg", "NOTES"),
    "Samarth": ("header/pinned_samarth.svg", "SAMARTH"),
    "xlnet-emotion-classifier": ("header/pinned_xlnet.svg", "XLNET"),
    "StudyPath": ("header/pinned_studypath.svg", "STUDYPATH")
}

def update_svg(file_path, tag, stars, forks):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace stars
    stars_pattern = rf'(<!-- STARS_COUNT_{tag} -->).*?(<!-- /STARS_COUNT_{tag} -->)'
    content = re.sub(stars_pattern, rf'\g<1>{stars}\g<2>', content)

    # Replace forks
    forks_pattern = rf'(<!-- FORKS_COUNT_{tag} -->).*?(<!-- /FORKS_COUNT_{tag} -->)'
    content = re.sub(forks_pattern, rf'\g<1>{forks}\g<2>', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {file_path}")

def main():
    for repo, (file_path, tag) in REPOS.items():
        url = f"https://api.github.com/repos/Luc0-0/{repo}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Use GITHUB_TOKEN if available to avoid rate limits
        if os.getenv('GITHUB_TOKEN'):
            headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                stars = data.get('stargazers_count', 0)
                forks = data.get('forks_count', 0)
                
                update_svg(file_path, tag, stars, forks)
        except Exception as e:
            print(f"Error fetching {repo}: {e}")

if __name__ == "__main__":
    main()
