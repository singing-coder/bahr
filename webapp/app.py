"""Streamlit web app: paste a ghazal, get meter identification and taqti.

Run:  streamlit run webapp/app.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from taqti import identify, taqti_lines, line_fits, METERS, GHALIB_METERS, \
    MIR_METERS, RARE_METERS, G_TO_HANDBOOK
from taqti.meters import M_TO_G, unified_table
from taqti.translit import from_roman, from_pritchett, from_urdu, \
    from_english, from_devanagari

st.set_page_config(page_title="Taqti — Urdu Meter & Scansion", page_icon="🪶",
                   layout="wide")

page = st.sidebar.radio("Page", ["Analyze", "Help: meters & patterns",
                                 "About"])

MODES = {
    "Roman Urdu (Rekhta style: aa/ā, KH, GH, ñ)": "roman",
    "Devanagari (देवनागरी, Rekhta-Hindi style)": "devanagari",
    "Urdu script (اردو)": "urdu",
    "Plain English roman (no length marks)": "english",
    "Pritchett site scheme (;x ;G aa ...)": "pritchett",
}


def normalizer_for(mode):
    if mode == "roman":
        return from_roman
    if mode == "pritchett":
        return lambda s: from_pritchett(from_roman(s))
    if mode == "devanagari":
        return from_devanagari
    if mode == "urdu":
        return from_urdu
    return lambda s: from_english(s)[0]


if page == "Analyze":
    st.title("Taqti — meter identification and scansion")
    st.caption("Rules and meter inventory: Pritchett & Khaliq, "
               "*Urdu Meter: A Practical Handbook*. Paste the whole poem: "
               "identification intersects fits across every line "
               "(handbook ch. 7, 'Scanning as Code-Breaking').")

    col1, col2 = st.columns([2, 1])
    with col2:
        mode_label = st.radio("Input script", list(MODES.keys()))
        mode = MODES[mode_label]
        lib_label = st.radio("Meter library",
                             ["Handbook 6.1 (all 37 + Hindi + rubā'ī)",
                              "Ghalib-site G-numbers (G1–G23)",
                              "Mir-site M-numbers (M1–M28)",
                              "Rare / extended (#41–#52)"])
        lib = (METERS if lib_label.startswith("Handbook")
               else GHALIB_METERS if "G-numbers" in lib_label
               else MIR_METERS if "M-numbers" in lib_label
               else RARE_METERS)
    with col1:
        default = ("ye na thī hamārī qismat ki visāl-e-yār hotā\n"
                   "agar aur jīte rahte yahī intizār hotā")
        text = st.text_area("Poem (one misra per line)", default, height=220)

    if st.button("Analyze", type="primary"):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        norm = normalizer_for(mode)
        if mode == "english":
            _, warn = from_english(text)
            if warn:
                st.warning(warn)
        if mode == "urdu":
            st.info("Urdu-script conversion is best-effort (short vowels "
                    "are unwritten; vāo/ye are guessed). If a line fails, "
                    "check the romanization shown below.")
        fits = identify(lines, library=lib, normalizer=norm)
        if not fits:
            st.error("No single meter fits every line.")
            st.markdown("**Per-line diagnosis** — meters fitting each line "
                        "individually (an empty set usually means a "
                        "transliteration issue in that line):")
            for ln in lines:
                f = sorted(line_fits(ln, library=lib, normalizer=norm))
                st.write(f"- `{norm(ln)}` → {f or '∅'}")
        else:
            name = sorted(fits)[0]
            extra = sorted(fits - {name})
            st.success(f"**Meter: {name}**"
                       + (f"  · also consistent: {', '.join(extra)}"
                          if extra else ""))
            if lib is GHALIB_METERS and name in G_TO_HANDBOOK:
                st.caption(f"Handbook 6.1 reference: {G_TO_HANDBOOK[name]}")
            if lib is MIR_METERS and name in M_TO_G:
                g = M_TO_G[name]
                hb = G_TO_HANDBOOK.get(g, g)
                st.caption(f"Ghalib-site equivalent: {g} · handbook: {hb}")
            pats = lib[name][0]
            st.markdown(f"Pattern{'s' if len(pats)>1 else ''}: "
                        + "  ·  ".join(f"`{p}`" for p in pats[:4])
                        + (" …" if len(pats) > 4 else ""))
            with st.expander("How to read this"):
                st.markdown(
                    "- `=` long syllable, `-` short (handbook notation)\n"
                    "- An unscanned short 'cheat syllable' is allowed at "
                    "line end (all meters except hazaj sālim #26/G2), and "
                    "before the caesura in caesura meters\n"
                    "- Flexible syllables (common monosyllables, word-final "
                    "vowels, izafat) may scan either way; the taqti below "
                    "shows the resolution that fits")
            _, scans = taqti_lines(lines, library=lib, meter=name,
                                   normalizer=norm)
            st.markdown("### Taqti")
            for ln, sc in zip(lines, scans):
                st.markdown(f"**{ln}**")
                if sc is None:
                    st.write("· does not scan under this meter")
                else:
                    st.code(" ".join(f"{s}({w})" for s, w in sc),
                            language=None)

elif page == "Help: meters & patterns":
    st.title("Meters and patterns")
    st.markdown(
        "One comprehensive table of every meter the engine knows: "
        "`=` long, `-` short (handbook notation), with the Ghalib-site "
        "(G) and Mir-site (M) numbers used by Pritchett's corpora where "
        "the meter occurs there. Affiliated pairs that may mix in one "
        "poem appear as one row; generated meters (Hindi meter, rubā'ī, "
        "dohā) show their foot notation.")
    st.dataframe(unified_table(), use_container_width=True)
    st.markdown(
        "**Conventions.** An unscanned short 'cheat syllable' is allowed "
        "at line end (all meters except hazaj sālim) and before the "
        "caesura in caesura meters. Flexible syllables (common "
        "monosyllables, word-final vowels, izafat) may scan either way. "
        "In the Hindi meter, even-numbered longs may each be replaced by "
        "two shorts; in the dohā (mātrik, 13+11 mātrās) any long may "
        "break into two shorts within the fixed cadences.")
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
        "Devanagari input is precise (vowel length explicit); "
        "chandrabindu and word-final anusvāra read as ġhunna, and "
        "standard schwa deletion applies (रहते → rahte). Write izafat "
        "as `-ए-`.\n\n"
        "### References\n"
        "1. Pritchett & Khaliq, [*Urdu Meter: A Practical Handbook*]"
        "(https://franpritchett.com/00ghalib/meterbk/00_index.html)\n"
        "2. Pritchett, [*A Desertful of Roses*](https://franpritchett.com/00ghalib/) "
        "(Ghalib; G-numbering)\n"
        "3. Pritchett, [*A Garden of Kashmir*](https://franpritchett.com/00garden/) "
        "(Mir; M-numbering)\n"
        "4. Aditya Pant ('Naaqid'), *A Metrical Analysis of My Poems* "
        "[Part 1](https://urgetofly.blogspot.com/2018/03/a-metrical-analysis-of-my-poems.html) "
        "and [Part 2](https://urgetofly.blogspot.com/2021/08/metrical-analysis-of-my-poems-part-2.html)\n"
        "5. Pybus, [*A Textbook of Urdu Prosody and Rhetoric*]"
        "(http://www.columbia.edu/itc/mealac/pritchett/00urduhindilinks/pybus/pybus.html)\n"
        "6. Irfan 'Abid', [*Bah'r: The Backbone of Shaayari*]"
        "(http://www.urdupoetry.com/articles/art5.html)\n"
        "7. Kamal Ahmad Siddiqui, [*Ahang aur Arooz*]"
        "(https://www.rekhta.org/ebook-detail/ahang-aur-arooz-kamal-ahmad-siddiqi-ebooks)\n"
        "8. Bhatnagar Shadab, [*Ilm-e-Arooz*]"
        "(https://www.youtube.com/playlist?list=PLCTGa9vfQ95Zp7pNC6woJkSonGrsuxp-a) "
        "(Rekhta Foundation)\n"
        "9. Shamsur Rahman Faruqi, [*Arooz Ahang aur Bayaan*]"
        "(https://www.rekhta.org/ebook-detail/arooz-aahang-aur-bayan-shamsur-rahman-faruqi-ebooks)\n"
        "10. [Rekhta](https://www.rekhta.org/)")

else:
    st.title("About")
    st.markdown(
        "Scansion rules and the meter inventory implement **Pritchett & "
        "Khaliq, *Urdu Meter: A Practical Handbook*** "
        "(franpritchett.com/00ghalib/meterbk/). The test corpus draws on "
        "Frances Pritchett's *A Desertful of Roses* (Ghalib) and *A Garden "
        "of Kashmir* (Mir), which provide ground-truth meter labels for "
        "every ghazal. The ghazal texts themselves are public domain; the "
        "transliterations and meter assignments are hers, used with "
        "attribution and gratitude.\n\n"
        "Identification is poem-level by design: a single misra often fits "
        "more than one meter; a whole ghazal almost never does.\n\n"
        "**Contact**: Uday Kamath — maintainer. Questions, scansion "
        "corrections, and corpus contributions welcome.")
