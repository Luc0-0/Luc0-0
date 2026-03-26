"""
generate_assets.py — Auto-generate all GodProfile SVG assets for Luc0-0.
Fetches live stats from GitHub, WakaTime, and Spotify APIs when keys are set.
Run locally or via GitHub Actions (daily cron).

Env vars:
  GITHUB_TOKEN        — required for commit count (GraphQL); optional for REST
  WAKATIME_API_KEY    — WakaTime v1 API key for real language stats
  SPOTIFY_ACCESS_TOKEN — Spotify OAuth access token for now-playing card
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

# ── Config ────────────────────────────────────────────────────────────────────
USERNAME         = "Luc0-0"
THEME            = "luxury-glass"
HEADER           = os.path.join(os.path.dirname(__file__), "header")
GITHUB_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
WAKATIME_KEY     = os.environ.get("WAKATIME_API_KEY", "")
SPOTIFY_TOKEN    = os.environ.get("SPOTIFY_ACCESS_TOKEN", "")

os.makedirs(HEADER, exist_ok=True)


# ── GitHub API helpers ────────────────────────────────────────────────────────
def _gh(url: str, *, accept: str = "application/vnd.github+json",
        method: str = "GET", body: bytes | None = None) -> dict:
    req = urllib.request.Request(url, method=method, data=body)
    req.add_header("Accept", accept)
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_github_stats() -> dict:
    print(f"Fetching live GitHub stats for @{USERNAME}...")

    user = _gh(f"https://api.github.com/users/{USERNAME}")
    followers    = user.get("followers", 0)
    public_repos = user.get("public_repos", 0)

    repos      = _gh(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    pr_resp    = _gh(f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr&per_page=1")
    total_prs  = pr_resp.get("total_count", 0)

    iss_resp    = _gh(f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue&per_page=1")
    total_issues = iss_resp.get("total_count", 0)

    # Commits: GraphQL (needs token) → REST search fallback → 0
    total_commits = 0
    if GITHUB_TOKEN:
        gql = json.dumps({"query": (
            '{ user(login: "%s") { contributionsCollection {'
            ' totalCommitContributions restrictedContributionsCount } } }'
        ) % USERNAME}).encode()
        try:
            resp = _gh("https://api.github.com/graphql", method="POST", body=gql)
            cc = resp["data"]["user"]["contributionsCollection"]
            total_commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        except Exception:
            pass
    else:
        # Fallback: search commits API (public, no token needed)
        try:
            r = _gh(
                f"https://api.github.com/search/commits?q=author:{USERNAME}&per_page=1",
                accept="application/vnd.github.cloak-preview+json",
            )
            total_commits = r.get("total_count", 0)
        except Exception:
            pass

    stats = {
        "stars":     total_stars,
        "commits":   total_commits,
        "prs":       total_prs,
        "issues":    total_issues,
        "repos":     public_repos,
        "followers": followers,
    }
    print(f"  {stats}")
    return stats


# ── Asset generators ──────────────────────────────────────────────────────────
def save(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.basename(path)}")


def main() -> None:
    stats = fetch_github_stats()

    # 1. Terminal
    print("Generating terminal...")
    save(os.path.join(HEADER, "terminal.svg"), terminal_emulator.create_typing_svg(
        commands=[
            "$ whoami",         "nipun_sujesh",
            "$ cat skills.txt", "AI/ML  Full-Stack  Research  Open Source",
            "$ echo $MISSION",  "Build systems at the edge of research and delivery.",
            "$ git log --oneline -3",
            "a1b2c3 ship: multimodal mental health assistant",
            "d4e5f6 feat: xlnet emotion classifier (94.2% acc)",
            "g7h8i9 build: real-time study path engine",
        ],
        theme=THEME,
    ))

    # 2. Icon marquee
    print("Generating icon marquee...")
    save(os.path.join(HEADER, "icon_marquee.svg"), icon_marquee.build_marquee(
        icons=[
            "Python", "TypeScript", "React", "FastAPI", "PyTorch",
            "HuggingFace", "Docker", "PostgreSQL", "Redis", "Next.js",
            "LangChain", "OpenCV", "Node.js", "TailwindCSS", "Linux",
        ],
        theme=THEME, speed=35,
    ))

    # 3. Trophies — live GitHub stats
    print("Generating trophies (live)...")
    save(os.path.join(HEADER, "trophies.svg"), github_trophies.generate_trophy_case(
        username=USERNAME, theme=THEME, stats=stats,
    ))

    # 4. Neural tech map
    print("Generating neural map...")
    save(os.path.join(HEADER, "tech_neural.svg"), neural_bezier_engine.generate_map(
        tech_stack={
            "AI/ML":    ["PyTorch", "HuggingFace", "LangChain", "OpenCV"],
            "Backend":  ["FastAPI", "Node.js", "PostgreSQL", "Redis"],
            "Frontend": ["React", "Next.js", "TypeScript", "TailwindCSS"],
            "Infra":    ["Docker", "GH Actions", "Linux", "Vercel"],
        },
        theme=THEME,
    ))

    # 5. WakaTime — live if key set, else placeholder
    print("Generating WakaTime chart" + (" (live)" if WAKATIME_KEY else " (placeholder — set WAKATIME_API_KEY)") + "...")
    if WAKATIME_KEY:
        svg = wakatime_metrics.fetch_wakatime_stats(WAKATIME_KEY, THEME)
    else:
        svg = wakatime_metrics.render_wakatime_activity_chart(
            theme=THEME,
            data={"Python": 52.4, "TypeScript": 21.3, "JavaScript": 12.8, "Shell": 7.1, "Other": 6.4},
        )
    save(os.path.join(HEADER, "wakatime.svg"), svg)

    # 6. Spotify — live if token set, else placeholder
    print("Generating Spotify card" + (" (live)" if SPOTIFY_TOKEN else " (placeholder — set SPOTIFY_ACCESS_TOKEN)") + "...")
    if SPOTIFY_TOKEN:
        svg = spotify_now_playing.fetch_now_playing(SPOTIFY_TOKEN, THEME)
    else:
        svg = spotify_now_playing.render_now_playing(
            track="Blinding Lights", artist="The Weeknd", theme=THEME, is_playing=True,
        )
    save(os.path.join(HEADER, "spotify.svg"), svg)

    print(f"\nDone — assets saved to {HEADER}/")


if __name__ == "__main__":
    main()
