"""Constants encoding the rules of Pritchett & Khaliq, *Urdu Meter: A
Practical Handbook* (https://franpritchett.com/00ghalib/meterbk/).

Section numbers in comments refer to the handbook throughout the package.

Internal transliteration
------------------------
Long vowels carry macrons (ā ī ū) or are inherently long (e o ai au).
Short vowels are bare a i u.  ``K``/``G`` are ḳhe/ġhain, ``T``/``D``/``R``
retroflex, ``'`` stands for 'ain or hamza (a consonant letter, 1.1), and
``ñ`` marks nūn-e ġhunna (metrically invisible, 1.2).  Aspirates are the
lowercase C+h digraphs; do-chashmī he is metrically invisible (1.2).
"""

# NOTE: a tuple, not a string -- membership must be exact, because the
# two-letter long vowels "ai"/"iu" are substrings of "aiu"
SHORT_V = ("a", "i", "u")
LONG_V = ["ā", "ī", "ū", "ai", "au", "e", "o"]

#: aspirate and cluster digraphs that count as a single letter (1.2)
DIGRAPHS = ["chh", "bh", "ph", "th", "dh", "jh", "kh", "gh",
            "Th", "Dh", "Rh", "sh", "zh", "ch",
            "ky", "gy", "py"]  # onset clusters: kyā, gyān, pyār (2.1)
# NOTE: mh/nh/lh are NOT digraphs: romanization cannot distinguish
# do-chashmī he (aspirate: tumheñ = tu-mheñ) from baṛī he (consonant:
# pinhāñ = pin-hāñ). Aspirate-he words are listed in SPECIAL instead.

#: 2.1 -- flexible monosyllables: may scan long OR short
FLEX_WORDS = {
    "bhī", "to", "tū", "thā", "the", "thī", "jo", "do", "sā", "se", "sī",
    "so", "kā", "ke", "kī", "ko", "meñ", "maiñ", "ne", "vo", "ye", "ho",
    "hūñ", "hoñ", "hī", "hai", "haiñ", "yūñ", "pa",
}

#: 2.1 -- always short (written nah, kih, pah in Urdu script)
ALWAYS_SHORT = {"na", "ki", "ba"}

#: 2.1 -- always long
ALWAYS_LONG = {"tā", "go", "yā"}

#: fixed scansions for words the general rules do not cover:
#: 2.2 exceptions, 2.3 flexible divisions, and lexicalized items.
#: Weight symbols: '-' short, '=' long, 'x' flexible, '*' = (=) or (=-).
#: 2.3 flexible divisions with more than one legal parse: each word maps
#: to a LIST of alternative [(syllable, weight), ...] sequences.
SPECIAL_ALT = {
    # Mir-era postposition ke ta'īñ: full form ta-'īñ, or contracted to
    # one long syllable (pronounced ~teñ)
    "ta\u2019īñ": [[("ta", "-"), ("\u2019īñ", "x")],
                    [("ta\u2019īñ", "=")]],
    "taīñ":   [[("ta", "-"), ("īñ", "x")],
               [("taīñ", "=")]],
    "qatrah": [[("qat", "="), ("rah", "x")],
               [("qa", "-"), ("tr", "="), ("ah", "x")]],
    "qatra":  [[("qat", "="), ("ra", "x")],
               [("qa", "-"), ("tr", "="), ("a", "x")]],
}

SPECIAL = {
    "koī":   [("ko", "x"), ("ī", "x")],       # 2.2
    "ko\u2019ī": [("ko", "x"), ("\u2019ī", "x")],   # hamzah spelling
    "hu\u2019e": [("hu", "-"), ("\u2019e", "x")],
    "du\u2019ī": [("du", "-"), ("\u2019ī", "x")],
    "dū\u2019ī": [("du", "-"), ("\u2019ī", "x")],   # 2.3 flexible division
    "dūī":  [("du", "-"), ("ī", "x")],
    "kyā":   [("kyā", "=")],
    "kyoñ":  [("kyoñ", "=")],
    "kyūñ":  [("kyūñ", "=")],
    "jyūñ":  [("jyūñ", "=")],
    "hue":   [("hu", "-"), ("e", "x")],
    # do-chashmī he pronouns (aspirated, the h is metrically invisible)
    "tumheñ": [("tu", "-"), ("mheñ", "x")],
    "tumhīñ": [("tu", "-"), ("mhīñ", "x")],
    "tumhārā": [("tu", "-"), ("mhā", "="), ("rā", "x")],
    "tumhāre": [("tu", "-"), ("mhā", "="), ("re", "x")],
    "tumhārī": [("tu", "-"), ("mhā", "="), ("rī", "x")],
    "unheñ":  [("u", "-"), ("nheñ", "x")],
    "inheñ":  [("i", "-"), ("nheñ", "x")],
    "unhīñ":  [("u", "-"), ("nhīñ", "x")],
    "inhīñ":  [("i", "-"), ("nhīñ", "x")],
    "unhoñ":  [("u", "-"), ("nhoñ", "x")],
    "inhoñ":  [("i", "-"), ("nhoñ", "x")],
    "aur":   [("aur", "*")],                   # 2.1
    "dariyā": [("dar", "="), ("yā", "x")],     # 2.3
    "daryā": [("dar", "="), ("yā", "x")],
}
