"""
generate_assets.py — Auto-generate all GodProfile SVG assets for Luc0-0.
Fetches live GitHub stats via the GitHub API. Run locally or via GitHub Actions.
"""
import json
import os
import sys
import urllib.request

# ── Import godprofile_mcp (PyPI in CI, local source in dev) ──────────────────
try:
    from godprofile_mcp.core import (
        github_trophies,
        icon_marquee,
        neural_bezier_engine,
        spotify_now_playing,
        terminal_emulator,
        wakatime_metrics,
    )
except ImportError:
    _local = os.path.join(os.path.dirname(__file__), "..", "god profile", "GodProfile", "src")
    sys.path.insert(0, os.path.abspath(_local))
    from godprofile_mcp.core import (
        github_trophies,
        icon_marquee,
        neural_bezier_engine,
        spotify_now_playing,
        terminal_emulator,
        wakatime_metrics,
    )

# ── Config ───────────────────────────────────────────────────────────────────
USERNAME = "Luc0-0"
THEME = "luxury-glass"
HEADER = os.path.join(os.path.dirname(__file__), "header")
os.makedirs(HEADER, exist_ok=True)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


# ── GitHub API helpers ────────────────────────────────────────────────────────
def _gh_request(url: str, *, method: str = "GET", body: bytes | None = None) -> dict:
    req = urllib.request.Request(url, method=method, data=body)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_github_stats(username: str) -> dict:
    """Fetch live stats from GitHub REST + GraphQL APIs."""
    print(f"Fetching live GitHub stats for @{username}...")

    # Basic user info
    user = _gh_request(f"https://api.github.com/users/{username}")
    followers = user.get("followers", 0)
    public_repos = user.get("public_repos", 0)

    # Total stars across all public repos
    repos = _gh_request(
        f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    )
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    # PRs authored
    pr_search = _gh_request(
        f"https://api.github.com/search/issues?q=author:{username}+type:pr&per_page=1"
    )
    total_prs = pr_search.get("total_count", 0)

    # Issues authored
    issue_search = _gh_request(
        f"https://api.github.com/search/issues?q=author:{username}+type:issue&per_page=1"
    )
    total_issues = issue_search.get("total_count", 0)

    # Commits (current year) via GraphQL
    total_commits = 0
    if GITHUB_TOKEN:
        gql_query = json.dumps({
            "query": (
                "{ user(login: \"%s\") { contributionsCollection {"
                " totalCommitContributions restrictedContributionsCount } } }"
            ) % username
        }).encode()
        try:
            gql_resp = _gh_request(
                "https://api.github.com/graphql", method="POST", body=gql_query
            )
            cc = gql_resp["data"]["user"]["contributionsCollection"]
            total_commits = (
                cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
            )
        except Exception:
            total_commits = 0

    stats = {
        "stars":     total_stars,
        "commits":   total_commits,
        "prs":       total_prs,
        "issues":    total_issues,
        "repos":     public_repos,
        "followers": followers,
    }
    print(f"  Stats: {stats}")
    return stats


# ── Asset generators ──────────────────────────────────────────────────────────
def save(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.basename(path)}")


def main() -> None:
    stats = fetch_github_stats(USERNAME)

    # 1. Terminal — animated whoami / skills intro
    print("Generating terminal SVG...")
    svg = terminal_emulator.create_typing_svg(
        commands=[
            "$ whoami",
            "nipun_sujesh",
            "$ cat skills.txt",
            "AI/ML  Full-Stack  Research  Open Source",
            "$ echo $MISSION",
            "Build systems at the edge of research and delivery.",
            "$ git log --oneline -3",
            "a1b2c3 ship: multimodal mental health assistant",
            "d4e5f6 feat: xlnet emotion classifier (94.2% acc)",
            "g7h8i9 build: real-time study path engine",
        ],
        theme=THEME,
    )
    save(os.path.join(HEADER, "terminal.svg"), svg)

    # 2. Icon marquee — scrolling tech band
    print("Generating icon marquee...")
    svg = icon_marquee.build_marquee(
        icons=[
            "Python", "TypeScript", "React", "FastAPI", "PyTorch",
            "HuggingFace", "Docker", "PostgreSQL", "Redis", "Next.js",
            "LangChain", "OpenCV", "Node.js", "TailwindCSS", "Linux",
        ],
        theme=THEME,
        speed=35,
    )
    save(os.path.join(HEADER, "icon_marquee.svg"), svg)

    # 3. Trophies — live GitHub stats
    print("Generating trophies (live stats)...")
    svg = github_trophies.generate_trophy_case(
        username=USERNAME,
        theme=THEME,
        stats=stats,
    )
    save(os.path.join(HEADER, "trophies.svg"), svg)

    # 4. Neural tech map
    print("Generating neural map...")
    svg = neural_bezier_engine.generate_map(
        tech_stack={
            "AI/ML":    ["PyTorch", "HuggingFace", "LangChain", "OpenCV"],
            "Backend":  ["FastAPI", "Node.js", "PostgreSQL", "Redis"],
            "Frontend": ["React", "Next.js", "TypeScript", "TailwindCSS"],
            "Infra":    ["Docker", "GH Actions", "Linux", "Vercel"],
        },
        theme=THEME,
    )
    save(os.path.join(HEADER, "tech_neural.svg"), svg)

    # 5. WakaTime — placeholder (update data when WakaTime key is configured)
    print("Generating WakaTime chart...")
    svg = wakatime_metrics.render_wakatime_activity_chart(
        theme=THEME,
        data={"Python": 52.4, "TypeScript": 21.3, "JavaScript": 12.8, "Shell": 7.1, "Other": 6.4},
    )
    save(os.path.join(HEADER, "wakatime.svg"), svg)

    # 6. Spotify — placeholder card (update when Spotify OAuth is configured)
    print("Generating Spotify card...")
    svg = spotify_now_playing.render_now_playing(
        track="Blinding Lights",
        artist="The Weeknd",
        theme=THEME,
        is_playing=True,
    )
    save(os.path.join(HEADER, "spotify.svg"), svg)

    print(f"\nDone — all assets saved to {HEADER}/")


if __name__ == "__main__":
    main()
