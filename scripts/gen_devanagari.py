"""Generate Devanagari from internal romanization (round-trip helper).

Internal roman is unambiguous, so roman -> Devanagari -> roman must
round-trip exactly; the generated corpus then exercises from_devanagari
through the full meter gate.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CONS = {"chh":"छ","bh":"भ","ph":"फ","th":"थ","dh":"ध","jh":"झ","kh":"ख",
        "gh":"घ","Th":"ठ","Dh":"ढ","Rh":"ढ़","sh":"श","ch":"च",
        "k":"क","K":"ख़","g":"ग","G":"ग़","j":"ज","z":"ज़","T":"ट","D":"ड",
        "R":"ड़","t":"त","d":"द","n":"न","p":"प","f":"फ़","b":"ब","m":"म",
        "y":"य","r":"र","l":"ल","v":"व","s":"स","h":"ह","q":"क़"}
VOWELS = ["ai","au","ā","ī","ū","a","i","u","e","o"]
V_IND = {"a":"अ","ā":"आ","i":"इ","ī":"ई","u":"उ","ū":"ऊ","e":"ए",
         "ai":"ऐ","o":"ओ","au":"औ"}
V_MAT = {"a":"","ā":"ा","i":"ि","ī":"ी","u":"ु","ū":"ू","e":"े",
         "ai":"ै","o":"ो","au":"ौ"}

def tokenize(seg):
    toks, i = [], 0
    keys = sorted(list(CONS) + VOWELS + ["ñ", "'"], key=len, reverse=True)
    while i < len(seg):
        for k in keys:
            if seg.startswith(k, i):
                toks.append(k); i += len(k); break
        else:
            raise ValueError(f"untokenizable at {seg[i:]!r} in {seg!r}")
    return toks

def seg_to_dev(seg):
    toks = tokenize(seg)
    # Rekhta convention: Urdu final-he words (bāda, janāza) carry final ā
    if len(toks) >= 4 and toks[-1] == "a" and toks[-2] in CONS:
        toks[-1] = "ā"
    out = []
    for j, t in enumerate(toks):
        prev = toks[j-1] if j else None
        nxt = toks[j+1] if j+1 < len(toks) else None
        if t == "ñ":
            out.append("ँ")
        elif t == "'":
            out.append("'")
        elif t in CONS:
            if nxt in V_MAT:
                pass                             # matra added on vowel turn
            elif nxt in CONS:
                out.append(CONS[t] + "्"); continue
            out.append(CONS[t])
        else:                                    # vowel
            if prev in CONS:
                out.append(V_MAT[t])
            else:
                out.append(V_IND[t])
    return "".join(out)

def to_devanagari(line):
    words = []
    for w in line.split():
        words.append("-".join("e" == sg and "ए" or seg_to_dev(sg)
                              for sg in w.split("-")).replace("-ए-", "-ए-"))
    return " ".join(words).replace("-e-", "-ए-")
