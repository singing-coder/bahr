"""Input transliteration.

Four input modes, all converging on the package-internal romanization
(see :mod:`taqti.rules`):

* ``roman``     -- Rekhta-style Roman Urdu with length marks (aa/ā, KH/GH,
                   ñ). Precise; the recommended mode.
* ``pritchett`` -- the transliteration scheme of *A Desertful of Roses*
                   and *A Garden of Kashmir* (;x ;G aa ii ;N (( )) ...).
                   Precise; used by the test corpus.
* ``devanagari``-- Devanagari, Rekhta-Hindi style. Precise: vowel length
                   is explicit; chandrabindu/final anusvāra map to ġhunna.
* ``urdu``      -- Urdu script (best effort: unvocalized script does not
                   mark short vowels, which the letter-based metrical
                   system tolerates, but vāo/ye ambiguity means results
                   should be reviewed).
* ``english``   -- plain roman without length marks (best effort with a
                   common-words dictionary; a warning is attached).
"""
import re

# ------------------------------------------------------------ roman (Rekhta)
def from_roman(text):
    t = text
    t = t.replace("KH", "K").replace("GH", "G")
    t = t.replace("Kh", "K").replace("Gh", "G")
    t = t.replace("w", "v").replace("W", "v")
    t = t.replace(".n", "ñ").replace(".N", "ñ")
    t = t.replace("aa", "ā").replace("ii", "ī").replace("uu", "ū")
    t = t.replace("'", "'")
    return t


# ------------------------------------------------------ pritchett site scheme
_PRITCHETT_MAP = [
    # multi-char first
    (";Th", "Th"), (";Dh", "Dh"), (";Rh", "Rh"),   # aspirates: map first
    (";x", "K"), (";G", "G"), (";T", "T\u2027"), (";D", "D\u2027"),
    (";R", "R\u2027"), (";N", "ñ"),
    # marker-derived single letters get the digraph-breaker so they can
    # never fuse with a neighboring h into an aspirate: .sub;h = sub-h
    # (bh here is be+he, not the aspirate), ma;zhab = maz-hab, etc.
    (";s", "s\u2027"), (";h", "\u2027h"), (";z", "z\u2027"),
    (".s", "s\u2027"), (".z", "z\u2027"), (".t", "t\u2027"),
    (".h", "\u2027h"), (".g", "g\u2027"),
    (":t", "t\u2027"), (":z", "z\u2027"),
    ("((", "'"),                     # 'ain: a consonant letter
    ("))", "\u2019"),               # hamzah: a consonant whose syllable
                                     # is flexible (hiatus: jaa))e;Nge)
    ("aa", "ā"), ("ii", "ī"), ("uu", "ū"),
]

#: her spellings whose silent choTī he / final h maps to our word forms
_PRITCHETT_WORDS = {
    "yih": "ye", "vuh": "vo", "kih": "ki", "nah": "na", "pah": "pa",
    "yihī": "yahī", "vuhī": "vahī",
}


def from_pritchett(text):
    """Convert a line in the Desertful-of-Roses scheme."""
    # her bare apostrophe is a digraph-breaker (vaj'h = j+h separately,
    # kaavish'haa = vish+haa), not a letter: map to the internal breaker
    t = text.replace("'", "\u00b7")
    for a, b in _PRITCHETT_MAP:
        t = t.replace(a, b)
    # al-construction (3.4): buu al-havas -> buul-havas (vowel elides)
    t = re.sub(r"([āīūaeiou]) al-", r"\1l-", t)
    # izafat: she writes "vi.saal-e yaar" -> join to "visāl-e-yār"
    t = re.sub(r"-e\s+", "-e-", t)
    # word-final silent he in -ah words (baadah, chaarah, yagaanah, janaazah)
    words = []
    for w in t.split():
        base = w
        for src, dst in _PRITCHETT_WORDS.items():
            if base == src:
                base = dst
        words.append(base)
    t = " ".join(words)
    # any marker punctuation not consumed above is noise (asadull;aah)
    t = re.sub(r"[;:.,]", "", t)
    return t


# ------------------------------------------------------------------ urdu
_URDU_CONS = {
    "ب": "b", "پ": "p", "ت": "t", "ٹ": "T", "ث": "s", "ج": "j", "چ": "ch",
    "ح": "h", "خ": "K", "د": "d", "ڈ": "D", "ذ": "z", "ر": "r", "ڑ": "R",
    "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s", "ض": "z", "ط": "t",
    "ظ": "z", "ع": "'", "غ": "G", "ف": "f", "ق": "q", "ک": "k", "گ": "g",
    "ل": "l", "م": "m", "ن": "n", "ں": "ñ", "ہ": "h", "ھ": "h", "ء": "'",
    "ئ": "'", "ی": "y", "ے": "e", "و": "v", "ا": "ā", "آ": "ā",
}


def from_urdu(text):
    """Best-effort Urdu script conversion.

    Unvocalized script omits short vowels; since the metrical system is
    letter-based (1.1), consonant clusters still scan correctly in most
    positions, but vāo/ye as vowel-vs-consonant is guessed by context.
    Review the output romanization before trusting a failed scan.
    """
    out_words = []
    for w in text.split():
        letters_ = [c for c in w if c in _URDU_CONS or c in "ًٰ"]
        buf = ""
        for idx, c in enumerate(letters_):
            r = _URDU_CONS.get(c, "")
            if c == "و":
                prev = letters_[idx-1] if idx else None
                r = "ū" if prev and prev not in "اآوی" else "o" \
                    if idx == 0 else "ū"
                # word-initial vao is consonant v
                if idx == 0:
                    r = "v"
            if c == "ی":
                r = "ī" if idx == len(letters_) - 1 or idx > 0 else "y"
                if idx == 0:
                    r = "y"
            if c == "ا" and idx == 0:
                r = "a"                          # initial alif: short carrier
            buf += r
        out_words.append(buf)
    return " ".join(out_words)


# ------------------------------------------------------------- devanagari
_DEV_CONS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "च": "ch", "छ": "chh",
    "ज": "j", "झ": "jh", "ट": "T", "ठ": "Th", "ड": "D", "ढ": "Dh",
    "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y",
    "र": "r", "ल": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s",
    "ह": "h",
    # nukta forms
    "क़": "q", "ख़": "K", "ग़": "G", "ज़": "z", "ड़": "R", "ढ़": "Rh",
    "फ़": "f", "ऱ": "r", "य़": "y",
}
_DEV_VOWEL_IND = {"अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u",
                  "ऊ": "ū", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
                  "ऋ": "ri"}
_DEV_MATRA = {"ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
              "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ृ": "ri"}
_DEV_HALANT = "्"
_DEV_NUKTA = "़"


def _dev_segment(seg):
    """Convert one hyphen-free Devanagari segment; Latin passes through."""
    import unicodedata
    if re.fullmatch(r"[a-zāīūñ'KGTDR]+", seg):
        return seg                               # already roman (izafat e)
    folded = []
    for c in seg:
        if c == _DEV_NUKTA and folded:
            folded[-1] = unicodedata.normalize("NFC", folded[-1] + c)
        else:
            folded.append(c)
    # first pass: (consonant, vowel|None) units and standalone marks
    units = []
    i = 0
    while i < len(folded):
        c = folded[i]
        if c in _DEV_CONS:
            nxt = folded[i+1] if i + 1 < len(folded) else None
            if nxt in _DEV_MATRA:
                units.append((_DEV_CONS[c], _DEV_MATRA[nxt])); i += 2
            elif nxt == _DEV_HALANT:
                units.append((_DEV_CONS[c], None)); i += 2
            else:
                units.append((_DEV_CONS[c], "a")); i += 1   # inherent
        elif c in _DEV_VOWEL_IND:
            units.append(("", _DEV_VOWEL_IND[c])); i += 1
        elif c == "\u0901":                                  # chandrabindu
            units.append(("ñ", None)); i += 1
        elif c == "\u0902":                                  # anusvara
            rest = folded[i+1:]
            units.append(("ñ" if not rest else "n", None)); i += 1
        elif c == "'":
            units.append(("'", None)); i += 1
        else:
            i += 1
    # second pass: schwa deletion on inherent 'a', applied RIGHT-TO-LEFT
    # on the mutating word (the standard Hindi rule):
    #  - word-final inherent a deletes
    #  - medial inherent a deletes when, at that point, both the previous
    #    and the next unit still carry a vowel (V C _a_ C V)
    #  - never delete the word's only vowel
    vowels = [v for _, v in units if v]
    if len(vowels) > 1:
        for k in range(len(units) - 1, -1, -1):
            cons, v = units[k]
            if v != "a":
                continue
            if k == len(units) - 1:
                units[k] = (cons, None)          # word-final schwa
                continue
            prev_vowel = any(u[1] for u in units[:k])
            nxt = units[k+1] if k + 1 < len(units) else None
            if prev_vowel and nxt and nxt[0] and nxt[1]:
                units[k] = (cons, None)          # rahte, chalte
    out = [c + (v or "") for c, v in units]
    return "".join(out)


def from_devanagari(text):
    """Devanagari (Rekhta-Hindi style) to internal romanization.

    Vowel length is explicit in the script, so this mode is precise.
    Conventions: chandrabindu and *word-final* anusvāra are nūn-e ġhunna
    (-> ñ, metrically invisible); *medial* anusvāra is the homorganic
    full nasal (-> n). Standard Hindi schwa deletion applies: word-final
    inherent 'a' drops, and medial inherent 'a' drops in the VC_CV
    environment (रहते -> rahte). The izafat joiner -ए- becomes -e-.
    """
    import unicodedata
    t = unicodedata.normalize("NFC", text).replace("-ए-", "-e-") \
        .replace("-ओ-", "-o-")
    out_words = []
    for w in t.split():
        segs = w.split("-")
        out_words.append("-".join(_dev_segment(sg) for sg in segs if sg != "")
                         if any(sg for sg in segs) else w)
    return " ".join(out_words)


# ---------------------------------------------------------------- english
_EN_COMMON = {
    "hai": "hai", "hain": "haiñ", "main": "maiñ", "mein": "meñ",
    "nahin": "nahīñ", "nahi": "nahīñ", "ki": "ki", "ke": "ke", "ka": "kā",
    "ko": "ko", "kya": "kyā", "kyun": "kyoñ", "aur": "aur", "par": "par",
    "dil": "dil", "yaar": "yār", "yar": "yār", "pyaar": "pyār",
    "zindagi": "zindagī", "duniya": "duniyā", "khuda": "Kudā",
    "ishq": "ishq", "gham": "Gam", "hum": "ham", "tum": "tum",
    "raat": "rāt", "din": "din", "aankh": "āñkh", "ansu": "āñsū",
}


def from_english(text):
    """Plain roman without length marks: dictionary + heuristics.

    Returns (converted_text, warning). Unknown words keep their vowels as
    written, which under-marks length; the warning says so.
    """
    words = []
    unknown = []
    for w in text.lower().split():
        if w in _EN_COMMON:
            words.append(_EN_COMMON[w])
        else:
            t = from_roman(w)
            if t == w and re.search(r"[aiu]", w):
                unknown.append(w)
            words.append(t)
    warn = None
    if unknown:
        warn = ("No vowel-length marks found for: " + ", ".join(unknown[:8])
                + (" ..." if len(unknown) > 8 else "")
                + ". Scansion may fail; prefer Roman Urdu with aa/ii/uu "
                  "or ā/ī/ū.")
    return " ".join(words), warn


def normalize(text, mode="roman"):
    """Dispatch. Returns converted text (and for 'english', may raise the
    warning through the returned tuple of :func:`from_english`)."""
    if mode == "roman":
        return from_roman(text)
    if mode == "pritchett":
        return from_pritchett(from_roman(text))
    if mode == "devanagari":
        return from_devanagari(text)
    if mode == "urdu":
        return from_urdu(text)
    if mode == "english":
        return from_english(text)[0]
    raise ValueError(f"unknown mode: {mode}")
