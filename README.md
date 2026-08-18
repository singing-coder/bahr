# taqti

Urdu-Hindi meter identification and scansion ('arūz), implementing the
rules and complete meter inventory of **Pritchett & Khaliq, *Urdu Meter:
A Practical Handbook*** ([franpritchett.com/00ghalib/meterbk](https://franpritchett.com/00ghalib/meterbk/00_index.html)).

Notation follows the handbook: `-` short syllable, `=` long syllable.

## What it does

```python
from taqti import identify, format_taqti

ghazal = [
    "ye na thī hamārī qismat ki visāl-e-yār hotā",
    "agar aur jīte rahte yahī intizār hotā",
]
print(format_taqti(ghazal))
# METER: #36 ramal musamman mashkūl
# ye(-) na(-) thī(=) ha(-) mā(=) rī(-) qis(=) mat(=) ...
```

Identification is **poem-level by design** (handbook ch. 7, "Scanning as
Code-Breaking"): a single misra often fits several meters; a whole ghazal
almost never does. `identify()` intersects fits across every line.

## Implemented rules

- Two letters long, one letter short; syllables start with consonants
  where possible (Pritchett 1.2–1.5)
- Flexible monosyllables; word-final vowel flexibility; always-short
  `nah`/`kih` (2.1–2.2); flexible divisions (2.3); spelling-encodes-
  scansion (`bayān` vs `bayāñ`, 2.4)
- Word-grafting (3.1), izafat (3.2), the o-construction (3.3), and the
  al-construction (3.4)
- Silent vāo of ḳhv- words and other irregulars (4.2)
- The unscanned "cheat" short at line end (all meters except hazaj
  sālim), and before the caesura in caesura meters

## The meters

One comprehensive library: Pritchett's complete handbook inventory
(6.1–6.3), the Ghalib-site (G) and Mir-site (M) numberings of her two
corpora, and the extended rare meters (#41–#52). The same table is on
the web app's Help page, generated from `taqti.meters.unified_table()`.

| Meter | Scansion (– short, = long) | Ghalib site | Mir site |
|---|---|---|---|
| #1/#9 hazaj musaddas aKHram ashtar mahzūf / aKHrab maqbūz mahzūf | `====-=-==` | G19 | M8 |
| #2 mutaqārib musamman asram | `==-====-==` | G22 | M2 |
| #3 rajaz musamman sālim | `==-===-===-===-=` |  | M3 |
| #4 muzāri' musamman aKHrab | `==-=-====-=-==` | G10 | M4 |
| #5 muzāri' musamman aKHrab makfūf mahzūf | `==-=-=--==-=-=` | G3 | M5 |
| #6 mutadārik musamman muzā'af maqtū' maKHbūn | `==--=======--=====` |  |  |
| #7 hazaj musamman aKHrab | `==--=====--===` | G18 | M6 |
| #8 hazaj musamman aKHrab makfūf mahzūf | `==--==--==--==` | G13 | M7 |
| #10 ramal musamman mahzūf | `=-===-===-===-=` | G1 | M10 |
| #11 ramal musaddas mahzūf | `=-===-===-=` | G14 | M11 |
| #12 mutadārik muzā'af sālim (also 4-foot) | `=-==-==-==-==-==-==-==-=` |  |  |
| #13 mutadārik musamman maqtū' mahzūf | `=-==-==-==` |  |  |
| #14/#15 KHafīf musaddas maKHbūn mahzūf (maqtū') | `=-==-=-===` | G8 | M12 |
| #16/#17 ramal musaddas maKHbūn mahzūf (maqtū') | `=-==--====` | G11 |  |
| #18/#19 ramal musamman maKHbūn mahzūf (maqtū') | `=-==--==--====` | G5 | M13 |
| #20 hazaj musamman ashtar | `=-=-====-=-===` | G4 |  |
| #21 hazaj musamman ashtar maqbūz | `=-=-=-==-=-=-=` |  |  |
| #22 munsarih musamman matvī maksūf | `=--==-==--==-=` | G21 | M16 |
| #23 munsarih musamman matvī manhūr | `=--==-=-=--==` | G17 |  |
| #24 sarī' musaddas matvī maksūf | `=--==--==-=` |  | M18 |
| #25 rajaz musamman matvī maKHbūn | `=--=-=-==--=-=-=` | G15 | M19 |
| #26 hazaj musamman sālim | `-===-===-===-===` | G2 | M20 |
| #27 hazaj musaddas mahzūf | `-===-===-==` | G7 | M21 |
| #28 mutaqārib musamman sālim | `-==-==-==-==` | G12 | M22 |
| #29 mutaqārib musamman mahzūf | `-==-==-==-=` | G23 | M23 |
| #30 mutaqārib musamman muzā'af maqbūz aslam | `-=-==-=-==-=-==-=-==` |  | M24 |
| #31 mutaqārib musaddas muzā'af maqbūz aslam | `-=-==-=-==-=-==` |  |  |
| #32 hazaj musamman maqbūz | `-=-=-=-=-=-=-=-=` |  |  |
| #33/#34 mujtas musamman maKHbūn mahzūf (maqtū') | `-=-=--==-=-===` | G9 | M25 |
| #35 mujtas musamman maKHbūn | `-=-=--==-=-=--==` | G16 |  |
| #36 ramal musamman mashkūl | `--=-=-==--=-=-==` | G6 | M27 |
| #37 kāmil musamman sālim | `--=-=--=-=--=-=--=-=` |  | M28 |
| Mir's 'Hindi' meter (6.2) | `= = / = = / = = / = = // = = / = = / = = / =` | G20 | M1 |
| rubā'ī meters (6.3, all 12 forms) | `= = (=) / = = (=) / = = (=) / =` |  |  |
| #41 'arīz musamman sālim (mafā'īlun fa'ūlun x2) | `-===-==-===-==` |  |  |
| #42 'amīq musamman sālim (fā'ilun fā'ilātun x2) | `=-==-===-==-==` |  |  |
| #43 vāfir musamman sālim (mufā'ilatan x4) | `-=--=-=--=-=--=-=--=` |  |  |
| #44 jadīd musaddas maKHbūn (fa'ilātun fa'ilātun mafā'ilun) | `--==--==-=-=` |  |  |
| #45 tavīl musamman maqbūz (fa'ūlun mafā'ilun x2) | `-==-=-=-==-=-=` |  |  |
| #46 qarīb musaddas aKHrab makfūf mahzūf (maf'ūlu mafā'īlu fā'ilun) | `==--==-=-=` |  |  |
| #47 muqtazab musamman matvī (fā'ilātu mufta'ilun x2) | `=-=-=--==-=-=--=` |  |  |
| #48 mushākil musaddas makfūf mahzūf (fā'ilātu mafā'īlu fa'ūlun) | `=-=--==--==` |  |  |
| #49 madīd musamman sālim (fā'ilātun fā'ilun x2) | `=-===-==-===-=` |  |  |
| #50 basīt musamman sālim (mustaf'ilun fā'ilun x2) | `==-==-===-==-=` |  |  |
| #51 rubā'ī (see 6.3; Mir wrote one ghazal in it) | `= = - / - = - = / - = = - / - =` |  | M-rare |
| #52 dohā (mātrik, 13+11 mātrās) | `= = / = = / = - = // = = / = = / = -` |  |  |

## Input modes

| mode | precision |
|---|---|
| Roman Urdu, Rekhta style (`aa/ā`, `KH`, `GH`, `ñ`) | precise (recommended) |
| Devanagari, Rekhta-Hindi style (chandrabindu = ġhunna, `-ए-` izafat) | precise |
| Pritchett site scheme (`;x ;G aa ;N (( ))`) | precise (used by the corpus) |
| Urdu script | best effort (short vowels unwritten; review on failure) |
| Plain English roman | best effort with warnings |

## Tests: the 100% corpus gate

`tests/corpus/` holds **21 ghazals** (10 Ghalib + 11 Mir, ~370 misras,
19 distinct meters) from Pritchett's *A Desertful of Roses* (Ghalib) and
*A Garden of Kashmir* (Mir), in her transliteration, each carrying her
ground-truth meter label (Ghalib-site G-numbers G1–G23; Mir-site
M-numbers M1–M28; both resolve through `taqti.meters.resolve_meter_label`).
The gate: every ghazal must identify as its labelled meter AND every
misra must scan under it, with an even misra count — and the same ghazal
is tested **across scripts** (the Devanagari corpus files are round-trip
generated from the roman and must yield the same meter;
`tests/test_cross_script.py` additionally locks Roman, Devanagari, and
the Pritchett scheme to identical identification). Coverage includes
Mir's "Hindi" meter (three ghazals, 38 misras) validated against the
Russell-generator patterns.
CI fails on anything less than 100%.

```
./setup.sh                      # creates .venv, pins deps, runs the gate
source .venv/bin/activate
pytest tests/ -v                # the gate under pytest (CI runs this)
python scripts/run_tests.py     # dependency-free runner (no venv needed)
```

On Windows: `.\setup.ps1`. The engine itself is stdlib-only; the venv
pins `pytest` and `streamlit` (see `requirements.txt`) so the dev and
webapp environment is identical everywhere. Python 3.9+ (CI runs 3.11).

Grow the corpus further (Ghalib by number; Mir by URL — only ghazals
with commentary have index pages, and her xghazindex range pages list
each ghazal's meter):

```
python scripts/fetch_corpus.py ghalib 20 111 10
python scripts/fetch_corpus.py mir https://franpritchett.com/00garden/00c/0054/index_0054.html
```

A fetched ghazal that fails is a converter or engine gap: fix the rule,
never delete the case.

## Web app

```
source .venv/bin/activate       # after ./setup.sh
streamlit run webapp/app.py
```

Paste a ghazal in any input mode; get the identified meter with its
pattern, a reading guide, per-line taqti, and per-line diagnosis on
failure. The Help page carries both meter tables (G-numbers and the full
6.1 list) and the input conventions.

## Roadmap

- Ghazal-structure layer: radif/qafiya extraction, matla validation
- Urdu-script mode: dictionary-backed vāo/ye disambiguation
- Mir's syncopated Hindi-meter variants; #6's rare flexible form

## Credits and references

Rules, meter inventory, and corpus labels: Frances Pritchett (with Khaliq
Ahmad Khaliq), *Urdu Meter: A Practical Handbook*, and her Ghalib and Mir
sites. The ghazal texts are public domain; the transliterations and meter
assignments are hers, used with attribution and gratitude. The extended
rare-meter enumeration (#41–#52) and its examples follow Aditya Pant's
("Naaqid") metrical-analysis survey. Code: MIT.

1. Pritchett, F. W. & Khaliq, K. A., [*Urdu Meter: A Practical Handbook*](https://franpritchett.com/00ghalib/meterbk/00_index.html)
2. Pritchett, F. W., [*A Desertful of Roses*](https://franpritchett.com/00ghalib/) (Ghalib) — source of the G-numbering and the Ghalib corpus
3. Pritchett, F. W., [*A Garden of Kashmir*](https://franpritchett.com/00garden/) (Mir) — source of the M-numbering and the Mir corpus
4. Pant, A. ("Naaqid"), [A Metrical Analysis of My Poems, Part 1](https://urgetofly.blogspot.com/2018/03/a-metrical-analysis-of-my-poems.html) and [Part 2](https://urgetofly.blogspot.com/2021/08/metrical-analysis-of-my-poems-part-2.html)
5. Pybus, G. D., [*A Textbook of Urdu Prosody and Rhetoric*](http://www.columbia.edu/itc/mealac/pritchett/00urduhindilinks/pybus/pybus.html)
6. Irfan 'Abid', [*Bah'r: The Backbone of Shaayari*](http://www.urdupoetry.com/articles/art5.html)
7. Siddiqui, K. A., [*Ahang aur Arooz*](https://www.rekhta.org/ebook-detail/ahang-aur-arooz-kamal-ahmad-siddiqi-ebooks)
8. Bhatnagar Shadab, [*Ilm-e-Arooz*](https://www.youtube.com/playlist?list=PLCTGa9vfQ95Zp7pNC6woJkSonGrsuxp-a) (Rekhta Foundation tutorials)
9. Faruqi, S. R., [*Arooz Ahang aur Bayaan*](https://www.rekhta.org/ebook-detail/arooz-aahang-aur-bayan-shamsur-rahman-faruqi-ebooks)
10. [Rekhta](https://www.rekhta.org/)

## Contact

Uday Kamath — maintainer. Questions, corrections to scansions, corpus
contributions, and issue reports are welcome.
