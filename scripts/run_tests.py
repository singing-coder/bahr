"""Dependency-free test runner (mirrors the pytest suite for environments
without pytest). CI uses pytest; the gate is identical: 100%."""
import json, glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from taqti import identify, taqti_lines, line_fits
from taqti.meters import resolve_meter_label
from taqti.translit import normalize

failures = 0

# ---- unit tests (mirror tests/test_rules.py, tests/test_cross_script.py)
import importlib, inspect
for mod_name in ("tests.test_rules", "tests.test_cross_script"):
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        mod = importlib.import_module(mod_name)
    for fname, fn in inspect.getmembers(mod, inspect.isfunction):
        if fname.startswith("test_"):
            try:
                fn()
                print(f"PASS {mod_name}.{fname}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {mod_name}.{fname}: {e}")

# ---- corpus gate
for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__),
                                          "..", "tests", "corpus", "*.json"))):
    g = json.load(open(path, encoding="utf-8"))
    name = os.path.basename(path)
    norm = lambda s: normalize(s, g["scheme"])
    try:
        library, key = resolve_meter_label(g["meter"])
        fits = identify(g["lines"], library=library, normalizer=norm)
        assert key in fits, f"expected {key}, got {sorted(fits)}"
        _, scans = taqti_lines(g["lines"], library=library,
                               meter=key, normalizer=norm)
        bad = [(i, g["lines"][i]) for i, s in enumerate(scans) if s is None]
        assert not bad, f"unscanned: {bad}"
        extra = sorted(fits - {g["meter"]})
        print(f"PASS {name}: {g['meter']}"
              + (f"  (also fits {extra})" if extra else ""))
    except AssertionError as e:
        failures += 1
        print(f"FAIL {name}: {e}")
        library, key = resolve_meter_label(g["meter"])
        for ln in g["lines"]:
            f = line_fits(ln, library=library, normalizer=norm)
            if key not in f:
                print(f"   line does not fit {key}: {ln}")
                print(f"     -> normalized: {norm(ln)}")
print("\n" + ("ALL PASS" if failures == 0 else f"{failures} FAILURES"))
sys.exit(1 if failures else 0)
