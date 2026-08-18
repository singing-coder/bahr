"""Meter identification and taqti output.

The reliable procedure (handbook chapter 7, "Scanning as Code-Breaking")
is to intersect the meters fitting *every* line of a poem: a single misra
often fits more than one meter, a whole ghazal almost never does.
:func:`identify` implements exactly that and is the primary entry point.
"""
from .parse import misra_parses
from .meters import METERS, GHALIB_METERS


def expand(weights):
    """All concrete ``-``/``=`` strings a weight sequence can realize."""
    opts = [""]
    for w in weights:
        if w == "-":
            opts = [o + "-" for o in opts]
        elif w == "=":
            opts = [o + "=" for o in opts]
        elif w == "x":
            opts = [o + c for o in opts for c in ("-", "=")]
        elif w == "*":
            opts = [o + c for o in opts for c in ("=", "=-")]
    return opts


def target_patterns(pats, caesura, cheat):
    """Base patterns plus the unscanned 'cheat' short at line end and,
    for caesura meters, before the caesura (6.1 headnote)."""
    out = set()
    for p in pats:
        variants = [p]
        if caesura:
            variants.append(p[:caesura] + "-" + p[caesura:])
        for v in variants:
            out.add(v)
            if cheat:
                out.add(v + "-")
    return out


def line_fits(misra_weights_or_text, library=None, name=None, normalizer=None):
    """Meters fitting one line.

    ``library`` defaults to :data:`taqti.meters.METERS`; pass
    :data:`taqti.meters.GHALIB_METERS` to work in G-numbers.
    With ``name`` given, returns the successful (syllables, resolved
    weights) parses for that meter instead of a set of names.
    """
    lib = library or METERS
    m = normalizer(misra_weights_or_text) if normalizer \
        else misra_weights_or_text
    results, taqtis = set(), []
    for sy in misra_parses(m):
        ws = "".join(w for _, w in sy)
        conc = set(expand(ws))
        for nm, (pats, cae, cheat) in lib.items():
            if name and nm != name:
                continue
            hit = conc & target_patterns(pats, cae, cheat)
            if hit:
                results.add(nm)
                if name:
                    taqtis.append((sy, sorted(hit)[0]))
    return taqtis if name else results


def identify(lines, library=None, normalizer=None):
    """Intersect meter fits across all lines. THE primary entry point."""
    fits = None
    for ln in lines:
        f = line_fits(ln, library=library, normalizer=normalizer)
        fits = f if fits is None else fits & f
        if not fits:
            return set()
    return fits


def taqti_lines(lines, library=None, meter=None, normalizer=None):
    """Return (meter_names, per-line scansions) for a poem.

    Each scansion is a list of (syllable, resolved_weight) pairs, or None
    for a line that does not scan under the identified meter.
    """
    fits = {meter} if meter else identify(lines, library, normalizer)
    if not fits:
        return set(), [None] * len(lines)
    name = sorted(fits)[0]
    out = []
    for ln in lines:
        rs = line_fits(ln, library=library, name=name, normalizer=normalizer)
        if not rs:
            out.append(None)
            continue
        sy, hit = rs[0]
        aligned, i = [], 0
        for s, w in sy:
            n = 2 if w == "*" and hit[i:i+2] == "=-" else 1
            aligned.append((s, hit[i:i+n]))
            i += n
        out.append(aligned)
    return fits, out


def format_taqti(lines, library=None, meter=None, normalizer=None):
    """Human-readable taqti of a poem."""
    fits, scans = taqti_lines(lines, library, meter, normalizer)
    buf = []
    if not fits:
        buf.append("No single meter fits every line.")
        for ln in lines:
            f = sorted(line_fits(ln, library=library, normalizer=normalizer))
            buf.append(f"  {f or 'NONE'} <- {ln}")
        return "\n".join(buf)
    if len(fits) > 1:
        buf.append("Consistent with more than one meter "
                   "(add more lines to settle): " + ", ".join(sorted(fits)))
    buf.append(f"METER: {sorted(fits)[0]}\n")
    for ln, sc in zip(lines, scans):
        buf.append(ln)
        buf.append("   " + " ".join(f"{s}({w})" for s, w in sc) + "\n")
    return "\n".join(buf)
