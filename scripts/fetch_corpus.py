"""Fetch ghazals with meter labels from Pritchett's sites into the corpus.

Ghalib:  https://franpritchett.com/00ghalib/NNN/index_NNN.html
         (meter as 'meter: Gn'; verse lines in italic blocks, typically
         two misras per block separated by <br>)
Mir:     same page grammar on her Mir site pages.

Usage:
    python scripts/fetch_corpus.py ghalib 111 10 35 49 62 71 78 115 208
    python scripts/fetch_corpus.py ghalib --debug 111    # dump HTML sample
    python scripts/fetch_corpus.py mir <ghazal-page-urls...>

Each ghazal is written to tests/corpus/<poet>_<n>.json in the Pritchett
scheme with its G-label, ready for the 100% test gate. A fetched ghazal
that fails the gate is a converter or engine gap: fix the rule, never
delete the case.
"""
import html as _html
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(__file__)
CORPUS = os.path.join(HERE, "..", "tests", "corpus")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "taqti-corpus"})
    return urllib.request.urlopen(req, timeout=30).read().decode(
        "utf-8", "replace")


def _clean(fragment):
    """One misra: strip tags, unescape entities, normalize whitespace."""
    t = re.sub(r"<[^>]+>", " ", fragment)
    t = _html.unescape(t)
    t = t.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", t).strip()


def _looks_like_verse(line):
    """Heuristic filter separating misras from navigation/notes italics."""
    if not line or len(line) < 8:
        return False
    bad = ("http", "meter", "translit", "SITEMAP", "index", "Raza",
           "Hamid", "Arshi", "ANTHOLOGY", "next ghazal", "About",
           "overview", "commentary")
    if any(b.lower() in line.lower() for b in bad):
        return False
    # her scheme is lowercase roman, EXCEPT that the marker digraphs
    # ;N ;G ;T ;D ;R (ghunna, ghain, retroflexes) use capitals; strip
    # those before rejecting on capitals
    stripped = re.sub(r"[;.:][A-Za-z]", "", line)
    if re.search(r"[A-Z]", stripped):
        return False
    return bool(re.search(r"[a-z]{3}", line))


def _italic_lines(chunk):
    """Verse-looking lines from the italic blocks of one HTML chunk."""
    out = []
    for block in re.findall(r"<(?:i|em)\b[^>]*>(.*?)</(?:i|em)>",
                            chunk, flags=re.S | re.I):
        for frag in re.split(r"<br\s*/?>", block, flags=re.I):
            t = _clean(frag)
            if _looks_like_verse(t):
                out.append(t)
    return out


def detect_meter(page):
    """Find the meter label: 'G6' (Ghalib site) or '#19' (handbook
    numbering, used on the Mir site). Returns None if not found and
    prints the page's meter-adjacent text to help."""
    m = re.search(r"meter:?\s*(G\d+)", page)
    if m:
        return m.group(1)
    m = re.search(r"meter:?\s*M?(\d{1,2})\b", page)
    if m:
        return "M" + str(int(m.group(1)))     # M01 / bare 01 -> M1
    m = re.search(r"meter[^#<\n]{0,60}#(\d+)", page, flags=re.I)
    if m:
        return "#" + m.group(1)
    m = re.search(r"[Mm]eter[^<\n]{0,120}", page)
    if m:
        print(f"  (meter text found but not classified: "
              f"{_clean(m.group(0))!r})")
    return None


def _entry_lines(chunk):
    """Verse lines from one vs-entry: inline formatting (<strong> etc.)
    can split the <em> block mid-misra, so strip ALL inline tags first
    and only then split on <br>."""
    m = re.search(r'class="vs-text"[^>]*>(.*?)</p>', chunk, flags=re.S) \
        or re.search(r'class="vs-text"[^>]*>(.*)', chunk, flags=re.S)
    body = m.group(1) if m else chunk
    body = re.sub(r"</?(?:strong|b|em|i|a|span|p|div|h\d)\b[^>]*>", "", body)
    out = []
    for frag in re.split(r"<br\s*/?>", body, flags=re.I):
        t = _clean(frag)
        if _looks_like_verse(t):
            out.append(t)
    return out


def parse_page(page):
    """Return (meter_label, misra_lines) from a ghazal index page.

    Structure-first, two page grammars:
    1. Mir site: each sher in a <div class="vs-entry"> (anchor links
       only on commented verses, so anchors cannot be the splitter).
    2. Ghalib site: split at verse anchors (links to NN_MM.html).
    Take at most TWO verse lines per chunk; captions can then never
    inflate the count.
    """
    meter = detect_meter(page)
    lines = []
    entries = re.split(r'<div\s+class="vs-entry"', page)
    if len(entries) > 2:                      # Mir page grammar
        for chunk in entries[1:]:
            lines += _entry_lines(chunk)[:2]
        return meter, lines
    chunks = re.split(r'(?=<a[^>]+href="[^"]*?\d+_\d+x?\.html")', page)
    if len(chunks) > 2:                       # Ghalib page grammar
        for chunk in chunks[1:]:
            lines += _italic_lines(chunk)[:2]
    else:                                     # fallback: flat scan
        lines = _italic_lines(page)
    return meter, lines


def write_ghazal(url, poet, n, meter, lines):
    out = {"source": url, "poet": poet, "ghazal": n, "meter": meter,
           "scheme": "pritchett", "lines": lines}
    os.makedirs(CORPUS, exist_ok=True)
    tag = f"{int(n):03d}" if str(n).isdigit() else str(n)
    path = os.path.join(CORPUS, f"{poet}_{tag}.json")
    json.dump(out, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"wrote {path}: {meter}, {len(lines)} misras "
          f"({'even' if len(lines) % 2 == 0 else 'ODD — check!'})")


def main():
    args = sys.argv[1:]
    debug = "--debug" in args
    if debug:
        args.remove("--debug")
    if not args:
        print(__doc__)
        return
    poet, items = args[0], args[1:]

    for item in items:
        if poet == "ghalib":
            n3 = f"{int(item):03d}"
            url = f"https://franpritchett.com/00ghalib/{n3}/index_{n3}.html"
            gid = item
        else:
            url, gid = item, re.sub(r"\D", "", item.rsplit("/", 1)[-1]) or "x"
        try:
            page = fetch(url)
        except Exception as e:
            print(f"SKIP {item}: fetch failed ({e})")
            continue
        if debug:
            # show the neighborhood of the first verse so the parser can
            # be adjusted to the real markup
            m = re.search(r"yih|kih|;G|aa[nr]", page)
            i = m.start() if m else 0
            print(f"--- {url} : HTML around first verse ---")
            print(page[max(0, i-300):i+1200])
            print("--- end sample ---")
            continue
        meter, lines = parse_page(page)
        if not meter or not lines:
            print(f"SKIP {item}: could not parse (meter={meter}, "
                  f"{len(lines)} lines). Re-run with --debug {item} and "
                  f"share the sample.")
            continue
        write_ghazal(url, poet, gid, meter, lines)


if __name__ == "__main__":
    main()
