"""Streamlit web app: paste a ghazal, get the meter and taqti.

Run:  streamlit run webapp/app.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from taqti import identify, line_fits, METERS, RARE_METERS
from taqti.meters import unified_table
from taqti.translit import from_roman, from_pritchett, from_urdu, \
    from_english, from_devanagari

st.set_page_config(page_title="Bahr — Urdu-Hindi Meter & Scansion",
                   page_icon="🌊", layout="wide")

# ------------------------------------------------------------------ style
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 17px; }
h1 { font-family: Georgia, 'Times New Roman', serif; font-weight: 700;
     letter-spacing: -0.5px; }
h1 .accent { color: #0e7c7b; }
.stTextArea textarea { font-size: 1.15rem !important; line-height: 1.9;
     font-family: Georgia, serif; }
.stRadio label, .stMarkdown p, .stCaption { font-size: 1.02rem; }
div[data-testid="stDataFrame"] { font-size: 1rem; }

.meter-card { background: linear-gradient(135deg, #0e7c7b 0%, #17505f 100%);
     color: #fff; padding: 1.1rem 1.4rem; border-radius: 14px;
     margin: 0.6rem 0 1.1rem 0; }
.meter-card .name { font-size: 1.35rem; font-weight: 700;
     font-family: Georgia, serif; }
.meter-card .pattern { font-family: ui-monospace, Menlo, monospace;
     font-size: 1.15rem; letter-spacing: 3px; margin-top: 0.35rem;
     opacity: 0.95; }
.meter-card .refs { margin-top: 0.4rem; font-size: 0.95rem; opacity: 0.9; }
.badge { display: inline-block; background: rgba(255,255,255,0.18);
     border-radius: 999px; padding: 0.1rem 0.7rem; margin-right: 0.4rem; }

.misra { font-family: Georgia, serif; font-size: 1.18rem; margin: 0.9rem 0
     0.25rem 0; color: #1b1b1b; }
.taqti { margin-bottom: 0.35rem; }
.syl { display: inline-block; font-family: ui-monospace, Menlo, monospace;
     font-size: 1.02rem; border-radius: 8px; padding: 0.14rem 0.5rem;
     margin: 0.12rem 0.18rem 0.12rem 0; }
.syl.long  { background: #0e7c7b; color: #fff; }
.syl.short { background: #fff; color: #0e7c7b;
     border: 1.5px solid #0e7c7b; }
.syl sub { opacity: 0.75; margin-left: 0.25rem; }
.footer-note { color: #666; font-size: 0.95rem; margin-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)

ALL_METERS = {**METERS, **RARE_METERS}
_UT = {row["meter"]: row for row in unified_table()}

MODES = {
    "Roman Urdu  ·  aa/ā, KH, GH, ñ  (Rekhta style)": ("roman", from_roman),
    "Devanagari  ·  देवनागरी": ("devanagari", from_devanagari),
    "Urdu script  ·  اردو  (best effort)": ("urdu", from_urdu),
    "Plain English roman  ·  no length marks (best effort)":
        ("english", lambda s: from_english(s)[0]),
    "Pritchett site scheme  ·  ;x ;G aa ;N": (
        "pritchett", lambda s: from_pritchett(from_roman(s))),
}

REFERENCES_MD = """
1. Pritchett, F. W. & Khaliq, K. A., [*Urdu Meter: A Practical Handbook*](https://franpritchett.com/00ghalib/meterbk/00_index.html) — the rules and meter inventory this engine implements
2. Pritchett, F. W., [*A Desertful of Roses*](https://franpritchett.com/00ghalib/) (Ghalib) — source of the G-numbering and the Ghalib test corpus
3. Pritchett, F. W., [*A Garden of Kashmir*](https://franpritchett.com/00garden/) (Mir) — source of the M-numbering and the Mir test corpus
4. Pant, A. ("Naaqid"), *A Metrical Analysis of My Poems* — [Part 1](https://urgetofly.blogspot.com/2018/03/a-metrical-analysis-of-my-poems.html) · [Part 2](https://urgetofly.blogspot.com/2021/08/metrical-analysis-of-my-poems-part-2.html) — source of the rare-meter enumeration (#41–#52)
5. Pybus, G. D., [*A Textbook of Urdu Prosody and Rhetoric*](http://www.columbia.edu/itc/mealac/pritchett/00urduhindilinks/pybus/pybus.html)
6. Irfan 'Abid', [*Bah'r: The Backbone of Shaayari*](http://www.urdupoetry.com/articles/art5.html)
7. Siddiqui, K. A., [*Ahang aur Arooz*](https://www.rekhta.org/ebook-detail/ahang-aur-arooz-kamal-ahmad-siddiqi-ebooks)
8. Bhatnagar Shadab, [*Ilm-e-Arooz*](https://www.youtube.com/playlist?list=PLCTGa9vfQ95Zp7pNC6woJkSonGrsuxp-a) (Rekhta Foundation tutorials)
9. Faruqi, S. R., [*Arooz Ahang aur Bayaan*](https://www.rekhta.org/ebook-detail/arooz-aahang-aur-bayan-shamsur-rahman-faruqi-ebooks)
10. [Rekhta](https://www.rekhta.org/)
"""


def meter_card(name):
    row = _UT.get(name, {})
    refs = ""
    if row.get("ghalib"):
        refs += f"<span class='badge'>Ghalib site: {row['ghalib']}</span>"
    if row.get("mir"):
        refs += f"<span class='badge'>Mir site: {row['mir']}</span>"
    if row.get("notes"):
        refs += f"<span class='badge'>{row['notes']}</span>"
    pattern = row.get("scansion", ALL_METERS[name][0][0])
    st.markdown(
        f"<div class='meter-card'><div class='name'>{name}</div>"
        f"<div class='pattern'>{pattern}</div>"
        f"<div class='refs'>{refs}</div></div>", unsafe_allow_html=True)


def taqti_html(scan):
    chips = []
    for s, w in scan:
        cls = "long" if w == "=" else "short"
        chips.append(f"<span class='syl {cls}'>{s}<sub>{w}</sub></span>")
    return "<div class='taqti'>" + "".join(chips) + "</div>"


page = st.sidebar.radio("Page", ["Analyze", "Meters", "About & references"])

# ---------------------------------------------------------------- analyze
if page == "Analyze":
    st.markdown("<h1><span class='accent'>Bahr</span> — Urdu-Hindi meter "
                "&amp; scansion</h1>", unsafe_allow_html=True)
    st.caption("Paste the whole poem, one misra per line. The meter is "
               "identified automatically across the complete library "
               "(handbook, Ghalib-site, Mir-site, and rare meters), by "
               "intersecting the meters that fit every line — the "
               "code-breaking procedure of Pritchett's Chapter 7.")

    col1, col2 = st.columns([2.4, 1])
    with col2:
        mode_label = st.radio("Script of your text", list(MODES.keys()))
        mode, norm = MODES[mode_label]
    with col1:
        default = ("ye na thī hamārī qismat ki visāl-e-yār hotā\n"
                   "agar aur jīte rahte yahī intizār hotā")
        text = st.text_area("Poem", default, height=210,
                            label_visibility="collapsed")

    if st.button("Analyze", type="primary", use_container_width=True):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if mode == "english":
            _, warn = from_english(text)
            if warn:
                st.warning(warn)
        if mode == "urdu":
            st.info("Urdu-script conversion is best-effort (short vowels "
                    "are unwritten; vāo/ye are guessed). If a line fails, "
                    "check the romanization in the diagnosis.")

        fits = identify(lines, library=ALL_METERS, normalizer=norm)
        if not fits:
            st.error("No single meter fits every line.")
            st.markdown("**Per-line diagnosis** — meters fitting each line "
                        "individually. An empty set usually means a "
                        "transliteration issue in that line (check ñ vs n, "
                        "vowel length, izafat hyphens):")
            for ln in lines:
                f = sorted(line_fits(ln, library=ALL_METERS, normalizer=norm))
                st.write(f"- `{norm(ln)}` → {f or '∅'}")
        else:
            name = sorted(fits)[0]
            extra = sorted(fits - {name})
            meter_card(name)
            if extra:
                st.caption("Also consistent (add more lines to settle): "
                           + ", ".join(extra))
            st.markdown("#### Taqti")
            for ln in lines:
                rs = line_fits(ln, library=ALL_METERS, name=name,
                               normalizer=norm)
                st.markdown(f"<div class='misra'>{ln}</div>",
                            unsafe_allow_html=True)
                if not rs:
                    st.write("· does not scan under this meter")
                    continue
                sy, hit = rs[0]
                aligned, i = [], 0
                for s, w in sy:
                    n = 2 if w == "*" and hit[i:i+2] == "=-" else 1
                    aligned.append((s, hit[i:i+n] if n == 1 else "="))
                    i += n
                st.markdown(taqti_html(aligned), unsafe_allow_html=True)
            st.markdown("<div class='footer-note'>Filled chips are long "
                        "syllables (=), outlined chips short (–). Flexible "
                        "syllables are shown in the resolution that fits "
                        "the meter.</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------- meters
elif page == "Meters":
    st.markdown("<h1>The <span class='accent'>meters</span></h1>",
                unsafe_allow_html=True)
    st.markdown(
        "One comprehensive table of every meter the engine knows: "
        "technical name, scansion (`=` long, `–` short), and the "
        "Ghalib-site (G) and Mir-site (M) numbers used by Pritchett's "
        "corpora where the meter occurs there. Affiliated pairs that may "
        "mix in one poem appear as one row; generated meters (Hindi "
        "meter, rubā'ī, dohā) show their foot notation.")
    st.dataframe(unified_table(), use_container_width=True, height=680)
    st.markdown(
        "**Conventions.** An unscanned short 'cheat syllable' is allowed "
        "at line end (all meters except hazaj sālim) and before the "
        "caesura in caesura meters. Flexible syllables — common "
        "monosyllables, word-final vowels, izafat — may scan either way. "
        "In the Hindi meter, even-numbered longs may each be replaced by "
        "two shorts; the dohā is mātrik (13+11 mātrās) with longs "
        "breaking into two shorts within fixed cadences.")
    st.markdown(
        "### Input conventions (Roman Urdu)\n"
        "| Sound | Write | Example |\n|---|---|---|\n"
        "| long vowels | `aa ii uu` or `ā ī ū`, plus `e o ai au` | `jaan` |\n"
        "| short vowels | `a i u` | `dil` |\n"
        "| ḳhe / ġhain | `KH`/`Kh` / `GH`/`Gh` | `KHushī`, `GHam` |\n"
        "| aspirates | lowercase `kh gh th bh ...` | `thā`, `bhī` |\n"
        "| retroflex | `T D R` | `jhūT`, `toR` |\n"
        "| nūn-e ġhunna | `ñ` (or `.n`/`.N`) | `kahāñ` |\n"
        "| full nūn | `n` | `bayān` |\n"
        "| vāo | `v` or `w` | `visāl`, `waqt` |\n"
        "| izafat | `-e-` | `visāl-e-yār` |\n\n"
        "Devanagari input is precise (vowel length is explicit); "
        "chandrabindu and word-final anusvāra read as ġhunna, standard "
        "schwa deletion applies (रहते → rahte), and izafat is `-ए-`. "
        "The ñ/n distinction matters everywhere: ġhunna is metrically "
        "invisible, full nūn is a consonant (`bayān` vs `bayāñ` scan "
        "differently — the spelling encodes the scansion).")

# ------------------------------------------------------------------ about
else:
    st.markdown("<h1>About</h1>", unsafe_allow_html=True)
    st.markdown(
        "**Bahr** identifies the meter of Urdu-Hindi poetry and prints "
        "its taqti (scansion), implementing the rules and complete meter "
        "inventory of **Pritchett & Khaliq, *Urdu Meter: A Practical "
        "Handbook***.\n\n"
        "Identification is **poem-level by design**: a single misra often "
        "fits more than one meter; a whole ghazal almost never does. The "
        "engine intersects the meters fitting every line — the "
        "'Scanning as Code-Breaking' procedure of the handbook's "
        "Chapter 7 — searching the full library automatically: all 37 "
        "handbook meters with their combination rules, Mir's Hindi meter "
        "(Russell generator), the 12 rubā'ī forms, and the rare meters "
        "#41–#52 including the mātrik dohā.\n\n"
        "The engine is validated by a **100% test gate over 21 ghazals** "
        "of Ghalib and Mir (~370 misras, 19 meters) drawn from Frances "
        "Pritchett's *A Desertful of Roses* and *A Garden of Kashmir*, "
        "which supply the ground-truth meter labels — and the same poems "
        "are tested across scripts (Roman, Devanagari, her site scheme) "
        "with identical results required.\n\n"
        "The ghazal texts are public domain; the transliterations and "
        "meter assignments are Pritchett's, used with attribution and "
        "gratitude. The rare-meter enumeration follows Aditya Pant "
        "('Naaqid'). Code: MIT.\n\n"
        "**Contact**: Uday Kamath — maintainer. Questions, scansion "
        "corrections, and corpus contributions welcome.")
    st.markdown("### References")
    st.markdown(REFERENCES_MD)
