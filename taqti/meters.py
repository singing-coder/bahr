import re
"""The meter library.

Two authoritative sources, both from Pritchett:

* :data:`METERS` -- the complete list of handbook section 6.1 (37 meters),
  plus Mir's "Hindi" meter (6.2, Russell generator) and the rubā'ī family
  (6.3, all 12 genuine forms), with the handbook's combination rules.
* :data:`GHALIB_METERS` -- the G1-G23 numbering used across
  *A Desertful of Roses* (franpritchett.com/00ghalib/about/txt_meters.html),
  which is the ground-truth labelling for the test corpus.

Patterns use the handbook notation: ``-`` short, ``=`` long.
Each entry is ``(patterns, caesura_index_or_None, cheat_allowed)``.
"""
from itertools import product as _prod


def _star(pats):
    """First syllable properly long, may be replaced with a short."""
    out = []
    for p in pats:
        out += [p, "-" + p[1:]]
    return out


def _antepenult_split(pats):
    """Next-to-last long replaceable by two shorts (G5/G8/G9/G11 note)."""
    out = []
    for p in pats:
        out.append(p)
        i = p.rfind("=", 0, len(p) - 1)
        if i > 0:
            out.append(p[:i] + "--" + p[i+1:])
    return out


# ---------------------------------------------------------------- 6.1 list
METERS = {}
METERS["#1/#9 hazaj musaddas aKHram ashtar mahzūf / aKHrab maqbūz mahzūf"] = (
    ["====-=-==", "==--=-=-=="], None, True)
METERS["#2 mutaqārib musamman asram"] = (["==-====-=="], 5, True)
METERS["#3 rajaz musamman sālim"] = (["==-=" * 4], None, True)
METERS["#4 muzāri' musamman aKHrab"] = (["==-=-==" * 2], 7, True)
METERS["#5 muzāri' musamman aKHrab makfūf mahzūf"] = (
    ["==-=-=--==-=-="], None, True)
METERS["#6 mutadārik musamman muzā'af maqtū' maKHbūn"] = (
    ["==--=======--====="], None, True)
METERS["#7 hazaj musamman aKHrab"] = (["==--===" * 2], 7, True)
METERS["#8 hazaj musamman aKHrab makfūf mahzūf"] = (
    ["==--==--==--=="], None, True)
METERS["#10 ramal musamman mahzūf"] = (["=-==" * 3 + "=-="], None, True)
METERS["#11 ramal musaddas mahzūf"] = (["=-==" * 2 + "=-="], None, True)
METERS["#12 mutadārik muzā'af sālim (also 4-foot)"] = (
    ["=-=" * 8, "=-=" * 4], None, True)
METERS["#13 mutadārik musamman maqtū' mahzūf"] = (["=-=" * 3 + "="], None, True)
METERS["#14/#15 KHafīf musaddas maKHbūn mahzūf (maqtū')"] = (
    _star(["=-==-=-===", "=-==-=-=--="]), None, True)
METERS["#16/#17 ramal musaddas maKHbūn mahzūf (maqtū')"] = (
    _star(["=-==--====", "=-==--==--="]), None, True)
METERS["#18/#19 ramal musamman maKHbūn mahzūf (maqtū')"] = (
    _star(["=-==--==--====", "=-==--==--==--="]), None, True)
METERS["#20 hazaj musamman ashtar"] = (["=-=-===" * 2], 7, True)
METERS["#21 hazaj musamman ashtar maqbūz"] = (["=-=-=-=" * 2], 7, True)
METERS["#22 munsarih musamman matvī maksūf"] = (["=--==-=" * 2], 7, True)
METERS["#23 munsarih musamman matvī manhūr"] = (["=--==-=-=--=="], None, True)
METERS["#24 sarī' musaddas matvī maksūf"] = (["=--==--==-="], None, True)
METERS["#25 rajaz musamman matvī maKHbūn"] = (["=--=-=-=" * 2], 8, True)
METERS["#26 hazaj musamman sālim"] = (["-===" * 4], None, False)
METERS["#27 hazaj musaddas mahzūf"] = (["-===-===-=="], None, True)
METERS["#28 mutaqārib musamman sālim"] = (["-==" * 4], None, True)
METERS["#29 mutaqārib musamman mahzūf"] = (["-==-==-==-="], None, True)
METERS["#30 mutaqārib musamman muzā'af maqbūz aslam"] = (
    ["-=-==" * 4], None, True)
METERS["#31 mutaqārib musaddas muzā'af maqbūz aslam"] = (
    ["-=-==" * 3], None, True)
METERS["#32 hazaj musamman maqbūz"] = (["-=-=" * 4], None, True)
METERS["#33/#34 mujtas musamman maKHbūn mahzūf (maqtū')"] = (
    ["-=-=--==-=-===", "-=-=--==-=-=--="], None, True)
METERS["#35 mujtas musamman maKHbūn"] = (["-=-=--==-=-=--=="], None, True)
METERS["#36 ramal musamman mashkūl"] = (["--=-=-==" * 2], 8, True)
METERS["#37 kāmil musamman sālim"] = (["--=-=" * 4], None, True)

# ---------------------------------------------- 6.2 Mir's "Hindi" meter
# = = / = = / = = / = = // = = / = = / = = / =
# Any even-numbered long may be replaced by two shorts (rarely so for
# syllable 8); quasi-caesura after the first half permits an extra
# unscanned short there (pre-expanded below, since substitution makes
# the half-line length variable). Rare syncopated - = - not generated.
_hindi = []
for subs in _prod(*[["=", "--"]] * 4):
    a, b, c, d = subs
    h1 = "=" + a + "=" + b + "=" + c + "=" + d
    for subs2 in _prod(*[["=", "--"]] * 3):
        e, f, g = subs2
        h2 = "=" + e + "=" + f + "=" + g + "="
        _hindi.append(h1 + h2)
        _hindi.append(h1 + "-" + h2)          # pre-caesura cheat short
_hindi = sorted(set(_hindi))
METERS["Mir's 'Hindi' meter (6.2)"] = (_hindi, None, True)

# ---------------------------------------------- 6.3 rubā'ī meters
_rubai = set()
for f1 in ["===", "==--"]:
    for f2 in ["===", "==--", "=-=-"]:
        for f3 in ["===", "==--"]:
            _rubai.add(f1 + f2 + f3 + "=")
METERS["rubā'ī meters (6.3, all 12 forms)"] = (sorted(_rubai), None, True)


# -------------------------------------------------------------------------
# Rare and extended meters (#41-#52): meters seldom used in Urdu poetry,
# from the enumeration contributed by Uday Kamath (usage counts and
# example couplets by Kamal Ahmad Siddiqui, Dr. Arif Hasan Khan, Nida
# Fazli, and Naaqid). #51 aliases the ruba'i family (6.3); #52 (doha) is
# matra-based and generated combinatorially.
RARE_METERS = {}
RARE_METERS["#41 'arīz musamman sālim (mafā'īlun fa'ūlun x2)"] = (
    ["-===-==" * 2], 7, True)
RARE_METERS["#42 'amīq musamman sālim (fā'ilun fā'ilātun x2)"] = (
    ["=-==-==" * 2], 7, True)
RARE_METERS["#43 vāfir musamman sālim (mufā'ilatan x4)"] = (
    ["-=--=" * 4], None, True)
RARE_METERS["#44 jadīd musaddas maKHbūn (fa'ilātun fa'ilātun mafā'ilun)"] = (
    ["--==--==-=-="], None, True)
RARE_METERS["#45 tavīl musamman maqbūz (fa'ūlun mafā'ilun x2)"] = (
    ["-==-=-=" * 2], 7, True)
RARE_METERS["#46 qarīb musaddas aKHrab makfūf mahzūf (maf'ūlu mafā'īlu fā'ilun)"] = (
    ["==--==-=-="], None, True)
RARE_METERS["#47 muqtazab musamman matvī (fā'ilātu mufta'ilun x2)"] = (
    ["=-=-=--=" * 2], 8, True)
RARE_METERS["#48 mushākil musaddas makfūf mahzūf (fā'ilātu mafā'īlu fa'ūlun)"] = (
    ["=-=--==--=="], None, True)
RARE_METERS["#49 madīd musamman sālim (fā'ilātun fā'ilun x2)"] = (
    ["=-===-=" * 2], 7, True)
RARE_METERS["#50 basīt musamman sālim (mustaf'ilun fā'ilun x2)"] = (
    ["==-==-=" * 2], 7, True)
RARE_METERS["#51 rubā'ī (see 6.3; Mir wrote one ghazal in it)"] = (
    sorted(_rubai), None, True)

# #52 doha: matra meter, 13 + 11 matras. Base: == == =-= // == == =-
# A long may break into two shorts; the half-line cadences (-= and
# final -) are kept fixed, free positions enumerate all compositions.
def _matra_strings(total):
    if total == 0:
        return [""]
    out = []
    if total >= 1:
        out += [s + "-" for s in _matra_strings(total - 1)]
    if total >= 2:
        out += [s + "=" for s in _matra_strings(total - 2)]
    return out

_doha = []
for h1p in _matra_strings(10):                 # 13 = 10 free + "-=" cadence
    for h2p in _matra_strings(10):             # 11 = 10 free + final "-"
        _doha.append(h1p + "-=" + h2p + "-")
RARE_METERS["#52 dohā (mātrik, 13+11 mātrās)"] = (
    sorted(set(_doha)), None, False)


# -------------------------------------------------------------------------
# The G-numbering of *A Desertful of Roses*: ground truth for the corpus.
# Source: franpritchett.com/00ghalib/about/txt_meters.html
# Notes column encoded: _star = first long may be short;
# _antepenult_split = next-to-last long may be two shorts.
GHALIB_METERS = {
    "G1":  (["=-==" * 3 + "=-="], None, True),
    "G2":  (["-===" * 4], None, False),
    "G3":  (["==-=-=--==-=-="], None, True),
    "G4":  (["=-=-===" * 2], 7, True),
    "G5":  (_antepenult_split(_star(["=-==--==--===="])), None, True),
    "G6":  (["--=-=-==" * 2], 8, True),
    "G7":  (["-===-===-=="], None, True),
    "G8":  (_antepenult_split(_star(["=-==-=-==="])), None, True),
    "G9":  (_antepenult_split(["-=-=--==-=-==="]), None, True),
    "G10": (["==-=-==" * 2], 7, True),
    "G11": (_antepenult_split(_star(["=-==--===="])), None, True),
    "G12": (["-==" * 4], None, True),
    "G13": (["==--==--==--=="], None, True),
    "G14": (["=-==" * 2 + "=-="], None, True),
    "G15": (["=--=-=-=" * 2], 8, True),
    "G16": (["-=-=--==-=-=--=="], None, True),
    "G17": (["=--==-=-=--=="], None, True),
    "G18": (["==--===" * 2], 7, True),
    "G19": (["==--=-=-==", "====-=-=="], None, True),
    "G20": (_hindi, None, True),
    "G21": (["=--==-=" * 2], 7, True),
    "G22": (["==-====-=="], 5, True),
    "G23": (["-==-==-==-="], None, True),
}

# -------------------------------------------------------------------------
# The M-numbering of *A Garden of Kashmir* (Mir site): ground truth for
# the Mir corpus. Source: 00garden/apparatus/txt_meters.html. M9, M14,
# M15, M17, M26 are unused on her site (her note) and omitted here.
MIR_METERS = {
    "M1":  (_hindi, None, True),                       # the Hindi meter
    "M2":  (["==-====-=="], 5, True),                  # = G22
    "M3":  (["==-=" * 4], None, True),                 # = G-none (#3)
    "M4":  (["==-=-==" * 2], 7, True),                 # = G10
    "M5":  (["==-=-=--==-=-="], None, True),           # = G3
    "M6":  (["==--===" * 2], 7, True),                 # = G18
    "M7":  (["==--==--==--=="], None, True),           # = G13
    "M8":  (["==--=-=-==", "====-=-=="], None, True),  # = G19 (dual form)
    "M10": (["=-==" * 3 + "=-="], None, True),         # = G1
    "M11": (["=-==" * 2 + "=-="], None, True),         # = G14
    "M12": (_antepenult_split(_star(["=-==-=-==="])), None, True),   # = G8
    "M13": (_antepenult_split(_star(["=-==--==--===="])), None, True),  # = G5
    "M16": (["=--==-=" * 2], 7, True),                 # = G21
    "M18": (["=--==--==-="], None, True),              # (#24)
    "M19": (["=--=-=-=" * 2], 8, True),                # = G15
    "M20": (["-===" * 4], None, False),                # = G2 (no cheat)
    "M21": (["-===-===-=="], None, True),              # = G7
    "M22": (["-==" * 4], None, True),                  # = G12
    "M23": (["-==-==-==-="], None, True),              # = G23
    "M24": (["-=-==" * 4], None, True),                # (#30)
    "M25": (_antepenult_split(["-=-=--==-=-==="]), None, True),      # = G9
    "M27": (["--=-=-==" * 2], 8, True),                # = G6
    "M28": (["--=-=" * 4], None, True),                # (#37 kāmil)
}

#: cross-reference: Mir-site M-code -> Ghalib-site G-code (hers), and
#: to the handbook where no G-code exists
M_TO_G = {
    "M1": "G20", "M2": "G22", "M3": "(#3)", "M4": "G10", "M5": "G3",
    "M6": "G18", "M7": "G13", "M8": "G19", "M10": "G1", "M11": "G14",
    "M12": "G8", "M13": "G5", "M16": "G21", "M18": "(#24)", "M19": "G15",
    "M20": "G2", "M21": "G7", "M22": "G12", "M23": "G23", "M24": "(#30)",
    "M25": "G9", "M27": "G6", "M28": "(#37)",
}

#: cross-reference: G-code -> handbook 6.1 number (for explanations)
G_TO_HANDBOOK = {
    "G1": "#10", "G2": "#26", "G3": "#5", "G4": "#20", "G5": "#18/#19",
    "G6": "#36", "G7": "#27", "G8": "#14/#15", "G9": "#33/#34", "G10": "#4",
    "G11": "#16/#17", "G12": "#28", "G13": "#8", "G14": "#11", "G15": "#25",
    "G16": "#35", "G17": "#23", "G18": "#7", "G19": "#1/#9", "G20": "6.2",
    "G21": "#22", "G22": "#2", "G23": "#29",
}


def resolve_meter_label(label):
    """Resolve a corpus meter label to (library, key).

    Accepts the Ghalib-site G-numbers ("G6") and handbook 6.1 numbers
    ("#19", "#36"); handbook numbers match the affiliated-pair entries
    ("#19" resolves to the "#18/#19 ..." key). Raises KeyError otherwise.
    """
    if label in GHALIB_METERS:
        return GHALIB_METERS, label
    if re.fullmatch(r"M0*\d+", label):
        label = "M" + str(int(label[1:]))      # M01 -> M1
    if label in MIR_METERS:
        return MIR_METERS, label
    if label.startswith("#"):
        for lib in (METERS, RARE_METERS):
            for key in lib:
                head = key.split()[0]      # e.g. "#18/#19"
                if label in head.split("/"):
                    return lib, key
    if label == "hindi":
        return METERS, "Mir's 'Hindi' meter (6.2)"
    raise KeyError(f"unknown meter label: {label}")


def unified_table():
    """One comprehensive meter table: every meter the engine knows, with
    its technical name, scansion, and the Ghalib-site (G) and Mir-site
    (M) numbers where Pritchett's corpora use it. Single source of truth
    for the README table and the webapp Help page."""
    hb_to_g = {v: k for k, v in G_TO_HANDBOOK.items()}
    g_to_m = {}
    for m, g in M_TO_G.items():
        g_to_m[g.strip("()")] = m
    rows = []
    for name, (pats, cae, cheat) in METERS.items():
        head = name.split()[0]                       # "#18/#19", "Mir's", "rubā'ī"
        if head.startswith("#"):
            hb = head
        elif name.startswith("Mir's"):
            hb = "6.2"
        else:
            hb = "6.3"
        g = hb_to_g.get(hb, "")
        m = g_to_m.get(g, "") or g_to_m.get(hb, "")
        if hb == "6.2":
            g, m = "G20", "M1"
        pattern = pats[0]
        if name.startswith("Mir's"):
            pattern = "= = / = = / = = / = = // = = / = = / = = / ="
        if hb == "6.3":
            pattern = "= = (=) / = = (=) / = = (=) / ="
        rows.append({"meter": name, "scansion": pattern,
                     "ghalib": g, "mir": m,
                     "notes": (f"{len(pats)} forms" if len(pats) > 1 else "")
                              + (", caesura" if cae else "")
                              + ("" if cheat else ", no cheat syllable")})
    for name, (pats, cae, cheat) in RARE_METERS.items():
        pattern = pats[0]
        if "#51" in name:
            pattern = "= = - / - = - = / - = = - / - ="
        if "#52" in name:
            pattern = "= = / = = / = - = // = = / = = / = -"
        rows.append({"meter": name, "scansion": pattern,
                     "ghalib": "", "mir": "M-rare" if "#51" in name else "",
                     "notes": (f"{len(pats)} forms" if len(pats) > 1 else "")
                              + (", caesura" if cae else "")
                              + (", rare" if True else "")})
    return rows
