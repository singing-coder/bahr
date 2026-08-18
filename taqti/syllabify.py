"""Word-level syllabification (handbook chapters 1-2).

Weights: ``-`` short, ``=`` long, ``x`` flexible (long or short at the
poet's pleasure), ``*`` = the special ``aur`` pattern, (=) or (= -).
"""
from .rules import SHORT_V, LONG_V, DIGRAPHS, FLEX_WORDS, ALWAYS_SHORT, \
    ALWAYS_LONG, SPECIAL


def letters(word):
    """Split a word into metrical letters (1.1-1.2).

    Aspirate digraphs are single letters; the silent vāo of ḳhv- words is
    dropped (4.2); 'ain (') and hamzah (\u2019) are consonant letters;
    the digraph-breaker (\u00b7) separates letters that must not form a
    digraph (vaj\u00b7h) and is itself invisible.
    """
    w = word.replace("Kv", "K")               # 4.2 silent vāo after ḳhe
    out, i = [], 0
    while i < len(w):
        if w[i] in ("\u00b7", "\u2027"):
            i += 1; continue                   # breakers: skip, block digraphs
        if w[i:i+3] in DIGRAPHS:
            out.append(w[i:i+3]); i += 3; continue
        if w[i:i+2] in DIGRAPHS or w[i:i+2] in LONG_V:
            out.append(w[i:i+2]); i += 2; continue
        out.append(w[i]); i += 1
    return out


def is_vowel(letter):
    return letter in LONG_V or letter in SHORT_V


def syllabify(word, izafat=False):
    """Return ``[(syllable, weight), ...]`` for one word.

    Implements: two letters long / one letter short (1.2, 1.5); syllables
    start with a consonant where possible (1.3); word-final ġhunna and all
    medial ġhunna invisible (1.2); word-final open long-vowel syllables
    flexible (2.2) except under izafat, where flexibility is handled by
    the caller (3.2).
    """
    ls = letters(word)
    ls = [l for l in ls if l != "ñ"]           # ġhunna invisible (1.2)
    sylls, i = [], 0
    while i < len(ls):
        l = ls[i]
        if not is_vowel(l):
            if i + 1 < len(ls) and is_vowel(ls[i+1]):
                v = ls[i+1]
                if v in SHORT_V:
                    # close the syllable (CVC = long) when a single
                    # consonant follows and is not itself an onset
                    if i + 2 < len(ls) and not is_vowel(ls[i+2]) and \
                       (i + 3 >= len(ls) or not is_vowel(ls[i+3])):
                        sylls.append((l+v+ls[i+2], "=")); i += 3
                    else:
                        sylls.append((l+v, "-")); i += 2
                else:
                    sylls.append((l+v, "=")); i += 2
            else:
                sylls.append((l, "-")); i += 1  # bare consonant: short
        else:
            if l in SHORT_V:
                if i + 1 < len(ls) and not is_vowel(ls[i+1]) and \
                   (i + 2 >= len(ls) or not is_vowel(ls[i+2])):
                    sylls.append((l+ls[i+1], "=")); i += 2   # ab, in, us
                else:
                    sylls.append((l, "-")); i += 1
            else:
                sylls.append((l, "=")); i += 1
    # hamzah-carried vowels are flexible in hiatus (jā\u2019eñge, ro\u2019eñge)
    for k, (s, w) in enumerate(sylls):
        if s.startswith("\u2019") and w == "=":
            sylls[k] = (s, "x")
    if sylls and not izafat:                    # 2.2 word-final flexibility
        s, w = sylls[-1]
        if w == "=" and any(s.endswith(v) for v in LONG_V):
            sylls[-1] = (s, "x")
        # word-final short-vowel+h (pardah, reshah, kih-compounds): the
        # silent he makes the syllable flexible
        if w == "=" and len(s) >= 2 and s[-1] == "h" and s[-2] in "aiu":
            sylls[-1] = (s, "x")
    return sylls


def scan_word(word):
    """Word scansion with the 2.1 word lists and SPECIAL overrides."""
    if word in SPECIAL:
        return list(SPECIAL[word])
    if word in ALWAYS_SHORT:
        return [(word, "-")]
    if word in ALWAYS_LONG:
        return [(word, "=")]
    if word in FLEX_WORDS:
        return [(word, "x")]
    return syllabify(word)
