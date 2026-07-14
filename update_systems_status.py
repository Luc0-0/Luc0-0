import urllib.request
import re
import time
from datetime import datetime, timezone

SVG_PATH = "header/live_systems.svg"

SERVICES = [
    ("SERENITY", "Serenity", "https://serenity.nipun.space"),
    ("PRAGATI", "Pragati", "https://pragati-366193575719.us-central1.run.app"),
    ("UNIVERSE", "Uni-Verse", "https://uni-verse.co.in"),
]

UP_COLOR = "#3fb950"
DOWN_COLOR = "#f85149"


def check(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            ms = int((time.monotonic() - start) * 1000)
            return resp.status < 500, resp.status, ms
    except urllib.error.HTTPError as e:
        ms = int((time.monotonic() - start) * 1000)
        return e.code < 500, e.code, ms
    except Exception:
        ms = int((time.monotonic() - start) * 1000)
        return False, None, ms


def replace_block(content, tag, new_inner):
    pattern = rf'(<!-- {tag} -->).*?(<!-- /{tag} -->)'
    return re.sub(pattern, lambda m: f"{m.group(1)}{new_inner}{m.group(2)}", content, flags=re.DOTALL)


def main():
    with open(SVG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    for tag, name, url in SERVICES:
        is_up, status_code, ms = check(url)
        color = UP_COLOR if is_up else DOWN_COLOR
        label = f"UP · {ms}ms" if is_up else f"DOWN · {status_code or 'timeout'}"

        content = replace_block(
            content, f"DOT_{tag}",
            f'<circle cx="5" cy="-4" r="4" fill="{color}" filter="url(#glow)"/>'
        )
        content = replace_block(content, f"STATUS_{tag}", label)
        print(f"{name}: {label}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = replace_block(content, "LAST_CHECKED", today)

    with open(SVG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    main()
