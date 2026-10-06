#!/usr/bin/env python3
"""Render the activation report's README.md into this page's template.

    python3 activation/render.py [path/to/README.md] [source-commit]

The report itself is computed by scripts/activation-report in the app repo (it reads PostHog
with a key that never leaves the Mac). This only turns its Markdown into activation/index.html,
keeping the <head> and styles of the page that is already here.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MD = Path.home() / "Library/Application Support/Latent/activation-report/README.md"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text):
    out = html.escape(text, quote=False)
    out = re.sub(r"&lt;sub&gt;(.*?)&lt;/sub&gt;", r"<sub>\1</sub>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`(.+?)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', out)
    return out


def cell(text):
    plain = re.sub(r"<[^>]+>|\*\*|`", "", text)
    cls = ""
    if len(plain) <= 14 or plain[:1] in "🔴🟡🟢":
        cls = ' class="nw"'
    elif len(plain) > 60:
        cls = ' class="long"'
    return f"<td{cls}>{inline(text)}</td>"


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render(md):
    lines = md.splitlines()
    body, toc, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            body.append(f'<h1 id="{slug(line[2:])}">{inline(line[2:])}</h1>')
        elif line.startswith("## "):
            title = line[3:]
            toc.append(f'<a href="#{slug(title)}">{inline(title)}</a>')
            body.append(f'<h2 id="{slug(title)}">{inline(title)}</h2>')
        elif line.startswith("|"):
            head = split_row(line)
            i += 2   # skip the |---| row
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append("<tr>" + "".join(cell(c) for c in split_row(lines[i])) + "</tr>")
                i += 1
            body.append('<div class="table-wrap"><table>\n<thead><tr>'
                        + "".join(f"<th>{inline(h)}</th>" for h in head)
                        + "</tr></thead><tbody>\n" + "\n".join(rows) + "\n</tbody></table></div>")
            continue
        elif line.strip():
            body.append(f"<p>{inline(line)}</p>")
        i += 1
    # The table of contents sits under the opening paragraph.
    body.insert(2, '<nav class="toc">' + "".join(toc) + "</nav>")
    return "\n".join(body)


def main():
    md_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    commit = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    page = HERE / "index.html"
    old = page.read_text()
    head = old[: old.index('<h1 id=')]
    head = re.sub(r'<meta name="source-commit" content="[^"]*">',
                  f'<meta name="source-commit" content="{commit}">', head)
    footer = (f'<footer>Regenerated from <code>scripts/activation-report</code>. Aggregate numbers '
              f'only. Source commit <code>{commit[:7]}</code>.</footer>\n</div>\n</body>\n</html>\n')
    page.write_text(head + render(md_path.read_text()) + "\n" + footer)
    print(f"wrote {page}")


if __name__ == "__main__":
    main()
