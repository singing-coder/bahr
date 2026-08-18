import re
"""Line-level parsing (handbook chapter 3).

A misra admits several legal syllable sequences, because word-grafting
(3.1), izafat attachment (3.2), and certain syllable divisions are the
poet's choice.  :func:`misra_parses` enumerates them all; the matcher in
:mod:`taqti.identify` then searches for one that fits a meter.
"""
from .rules import LONG_V
from .rules import SPECIAL_ALT
from .syllabify import letters, is_vowel, syllabify, scan_word


def _tokens(misra):
    """Split a misra into tokens, folding izafat (3.2) and the
    o-construction (3.3). Multiple constructions may chain in one
    chunk (jādah-e rāh-e fanā; shab-o-roz-o-māh-o-sāl)."""
    toks = []
    for chunk in misra.split():
        parts = re.split(r"-(e|o)-|-(e|o)$", chunk)
        # re.split with two groups yields [word, e/None, None, word, ...]
        seq = [p for p in parts if p is not None]
        if len(seq) == 1:
            for piece in re.split(r"[-\u00b7]", chunk):
                if piece:
                    toks.append(("W", piece))
            continue
        i = 0
        while i < len(seq):
            word = seq[i]
            join = seq[i + 1] if i + 1 < len(seq) else None
            pieces = [p for p in re.split(r"[-\u00b7]", word) if p]
            for piece in pieces:
                if join == "e" and piece == pieces[-1]:
                    toks.append(("IZ", piece))
                elif join == "o" and piece == pieces[-1]:
                    toks.append(("O", piece))
                else:
                    toks.append(("W", piece))
            i += 2
    return toks


def _graft_variants(sy):
    """3.1 word-grafting: a word-final consonant may join a following
    vowel-initial word; equivalently a closed syllable may re-open."""
    outs = [sy]
    for i in range(len(sy) - 1):
        a, wa = sy[i]
        b, wb = sy[i + 1]
        la, lb = letters(a), letters(b)
        if wa == "-" and len(la) == 1 and not is_vowel(la[0]) \
           and lb and is_vowel(lb[0]):
            fused = sy[:i] + [(a + b, "=" if wb in "=x" else "-")] + sy[i+2:]
            outs += _graft_variants(fused)
        if wa == "-" and len(la) == 1 and not is_vowel(la[0]) and b == "aur":
            fused = sy[:i] + [(a + "a", "-"), ("ur", "=")] + sy[i+2:]
            outs += _graft_variants(fused)
        if a == "aur" and wa == "*" and lb and is_vowel(lb[0]):
            # aur grafts onto a following vowel (aur ārā'ish -> au-rā-...);
            # the stranded au is flexible in this position
            fused = sy[:i] + [("au", "x"),
                              ("r" + b, "=" if wb in "=x" else "-")] + sy[i+2:]
            outs += _graft_variants(fused)
        if wa == "=" and len(la) == 3 and la[1] in "aiu" and b == "aur":
            opened = sy[:i] + [(la[0]+la[1], "-"), (la[2]+"au", "="),
                               ("r", "-")] + sy[i+2:]
            outs += _graft_variants(opened)
        if wa == "=" and len(la) == 2 and la[0] in ("a", "i", "u") \
           and lb and is_vowel(lb[0]):
            # VC syllable re-opens: us āvāz -> u-sā-vāz
            opened = sy[:i] + [(la[0], "-"),
                               (la[1]+b, "=" if wb in "=x" else "-")] + sy[i+2:]
            outs += _graft_variants(opened)
        if wa == "=" and len(la) == 3 and la[1] in "aiu" \
           and lb and is_vowel(lb[0]):
            opened = sy[:i] + [(la[0]+la[1], "-"),
                               (la[2]+b, "=" if wb in "=x" else "-")] + sy[i+2:]
            outs += _graft_variants(opened)
    return outs


def _coda_variants(sy):
    """A long-vowel syllable may keep a following lone consonant as coda
    (dos-t, yār-), scanning as one long."""
    outs = [sy]
    for i in range(len(sy) - 1):
        a, wa = sy[i]
        b, wb = sy[i + 1]
        la, lb = letters(a), letters(b)
        if wa == "=" and la and la[-1] in LONG_V and \
           wb == "-" and len(lb) == 1 and not is_vowel(lb[0]):
            fused = sy[:i] + [(a + b, "=")] + sy[i+2:]
            outs += _coda_variants(fused)
    return outs


def misra_parses(misra):
    """All legal ``[(syllable, weight), ...]`` sequences for a misra."""
    seqs = [[]]
    for kind, w in _tokens(misra):
        if kind == "IZ":                        # 3.2 izafat
            if w and (w[-1] in "aāīūeo" or w.endswith("ñ")):
                # vowel-final base (jāda-e, garmī-e): the izafat is a
                # separate flexible syllable, and the base keeps its own
                # word-final flexibility (garmī-e = gar-mi-e or gar-mī-e)
                body = syllabify(w) + [("e", "x")]
            else:
                body = syllabify(w + "e", izafat=True)
                body[-1] = (body[-1][0], "x")   # izafat syllable flexible
            seqs = [s + body for s in seqs]
        elif kind == "O":                       # 3.3 o-construction
            if w and (w[-1] in "aāīūeo" or w.endswith("ñ")):
                body = syllabify(w, izafat=True) + [("o", "x")]
            else:                               # nushv-o -> nush-vo
                body = syllabify(w + "o", izafat=True)
                body[-1] = (body[-1][0], "x")
            seqs = [s + body for s in seqs]
        elif w in SPECIAL_ALT:                  # 2.3 flexible division
            seqs = [s + list(alt) for s in seqs for alt in SPECIAL_ALT[w]]
        else:
            seqs = [s + scan_word(w) for s in seqs]
    allouts = []
    for sq in seqs:
        for g in _graft_variants(sq):
            allouts += _coda_variants(g)
    seen, uniq = set(), []
    for o in allouts:
        k = tuple(o)
        if k not in seen:
            seen.add(k)
            uniq.append(o)
    return uniq
