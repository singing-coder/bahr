from taqti.syllabify import scan_word, syllabify
from taqti import identify, METERS
from taqti.translit import from_pritchett

def test_flexible_monosyllable():
    assert scan_word("bhī") == [("bhī", "x")]

def test_always_short():
    assert scan_word("na") == [("na", "-")]

def test_ghunna_invisible():
    # ghunna drops; the resulting word-final open long syllable is
    # FLEXIBLE (2.2), so the weight is 'x' (which realizes as '=' or '-')
    assert [w for _, w in syllabify("kahāñ")] == ["-", "x"]
    assert [s for s, _ in syllabify("kahāñ")] == ["ka", "hā"]

def test_pritchett_scheme():
    # spelling is preserved in transliteration; the silent vāo of
    # ḳhv- words (4.2) is dropped at scansion time, in letters()
    assert from_pritchett("yih nah thii ;xvushii") == "ye na thī Kvushī"

def test_silent_vao_dropped_at_scansion():
    from taqti.syllabify import letters
    assert letters("Kvushī") == letters("Kushī") == ["K", "u", "sh", "ī"]

def test_khafif_matla():
    fits = identify(["dil-e-nādāñ tujhe huā kyā hai",
                     "āKHir is dard kī davā kyā hai"],
                    normalizer=lambda s: s.replace("KH", "K"))
    assert any("KHafīf" in f for f in fits)
