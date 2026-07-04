# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Merge claude-code-transcripts multi-page output into a single HTML file.

Layout of each file: <body> <div class="container"> header, pagination,
messages..., pagination </div> </body>. We keep index.html's TOC, append the
message streams of all pages, drop pagination bars, and localize anchors."""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])

def read(name):
    return (src / name).read_text()

def strip_pagination(html):
    # pagination divs contain only links/text, no nested divs
    return re.sub(r'<div class="pagination">.*?</div>', "", html, flags=re.S)

def body_content(html):
    """Container content without the trailing script and closing tags."""
    m = re.search(r"<body>\s*<div class=\"container\">(.*)</body>", html, re.S)
    inner = m.group(1)
    inner = re.sub(r"<script>.*?</script>", "", inner, flags=re.S)
    inner = inner.rstrip()
    if inner.endswith("</div>"):
        inner = inner[: -len("</div>")]
    return inner

def page_script(html):
    m = re.search(r"<script>.*?</script>", html, re.S)
    return m.group(0) if m else ""

pages = sorted(p.name for p in src.glob("page-*.html"))
index = read("index.html")

# index: everything in the container is the header + TOC of user prompts
toc = strip_pagination(body_content(index))
toc = re.sub(r'href="page-\d+\.html(#[^"]*)"', r'href="\1"', toc)
toc = re.sub(r'href="page-\d+\.html"', 'href="#"', toc)

# head (css) from index, but keep a proper title
head = index[: index.index("<body>")]

parts = [head, "<body>\n<div class=\"container\">\n", toc]
for name in pages:
    html = read(name)
    content = strip_pagination(body_content(html))
    # drop the per-page h1 back-link header
    content = re.sub(r"<h1>.*?</h1>", "", content, count=1, flags=re.S)
    content = re.sub(r'href="page-\d+\.html(#[^"]*)"', r'href="\1"', content)
    content = re.sub(r'href="index\.html"', 'href="#"', content)
    parts.append(content)
parts.append("</div>\n" + page_script(read(pages[0])) + "\n</body>\n</html>\n")

merged = "".join(parts)
out.write_text(merged)
print(f"{out}: {len(merged)} bytes from {len(pages)} pages")
# sanity: no dangling page refs
left = re.findall(r'page-\d+\.html', merged)
print("dangling page refs:", len(left))
