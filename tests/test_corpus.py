"""Corpus gate: every ghazal must identify as its labelled meter and every
misra must scan under it. The CI gate is 100%. Labels may be Ghalib-site
G-numbers or handbook 6.1 numbers (Mir corpus)."""
import json, glob, os, pytest
from taqti import identify, taqti_lines
from taqti.meters import resolve_meter_label
from taqti.translit import normalize

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__),
                                       "corpus", "*.json")))

@pytest.mark.parametrize("path", CORPUS, ids=[os.path.basename(p) for p in CORPUS])
def test_ghazal(path):
    g = json.load(open(path, encoding="utf-8"))
    assert len(g["lines"]) % 2 == 0, \
        f"odd misra count ({len(g['lines'])}): a line was dropped in fetching"
    norm = lambda s: normalize(s, g["scheme"])
    library, key = resolve_meter_label(g["meter"])
    fits = identify(g["lines"], library=library, normalizer=norm)
    assert key in fits, f"expected {key}, engine found {sorted(fits)}"
    _, scans = taqti_lines(g["lines"], library=library, meter=key,
                           normalizer=norm)
    failed = [g["lines"][i] for i, s in enumerate(scans) if s is None]
    assert not failed, f"lines not scanning under {key}: {failed}"
