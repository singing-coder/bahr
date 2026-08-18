"""Same poem, different scripts, same meter. Devanagari test lines use
natural spelling (no explicit halant), exercising schwa deletion."""
from taqti import identify, GHALIB_METERS
from taqti.translit import from_roman, from_devanagari, from_pritchett

ROMAN = ["ye na thī hamārī qismat ki visāl-e-yār hotā",
         "agar aur jīte rahte yahī intizār hotā"]
DEVANAGARI = ["ये न थी हमारी क़िस्मत कि विसाल-ए-यार होता",
              "अगर और जीते रहते यही इंतिज़ार होता"]
PRITCHETT = ["yih nah thii hamaarii qismat kih vi.saal-e yaar hotaa",
             "agar aur jiite rahte yihii inti:zaar hotaa"]

def _fits(lines, norm):
    return identify(lines, library=GHALIB_METERS, normalizer=norm)

def test_three_scripts_agree():
    a = _fits(ROMAN, from_roman)
    b = _fits(DEVANAGARI, from_devanagari)
    c = _fits(PRITCHETT, lambda s: from_pritchett(from_roman(s)))
    assert "G6" in a and a == b == c

def test_devanagari_schwa_deletion():
    assert from_devanagari("समझते रहते टपकता") == "samajhte rahte Tapaktā"

def test_devanagari_ghunna_vs_full_nun():
    # chandrabindu = ghunna (invisible), medial anusvara = full nun
    assert from_devanagari("कहाँ") == "kahāñ"
    assert from_devanagari("इंतिज़ार") == "intizār"
    assert from_devanagari("बयान") == "bayān"
