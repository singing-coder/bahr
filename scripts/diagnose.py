"""Compact failure report for the corpus: per ghazal, only the misras
that do not fit the labelled meter, with their normalized forms and raw
syllable weights. Paste this output when reporting engine gaps."""
import json, glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from taqti import line_fits
from taqti.meters import resolve_meter_label
from taqti.translit import normalize
from taqti.parse import misra_parses

for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__),
                                          "..", "tests", "corpus", "*.json"))):
    g = json.load(open(path, encoding="utf-8"))
    norm = lambda s: normalize(s, g["scheme"])
    library, key = resolve_meter_label(g["meter"])
    bad = []
    for ln in g["lines"]:
        if key not in line_fits(ln, library=library, normalizer=norm):
            bad.append(ln)
    tag = os.path.basename(path)
    if not bad:
        print(f"OK   {tag} [{g['meter']}] all {len(g['lines'])} misras")
        continue
    print(f"FAIL {tag} [{g['meter']}] {len(bad)}/{len(g['lines'])} misras:")
    for ln in bad:
        n = norm(ln)
        ws = "".join(w for _, w in misra_parses(n)[0])
        print(f"  RAW  {ln}")
        print(f"  NORM {n}")
        print(f"  WTS  {ws}   (pattern: {library[key][0][0]})")
