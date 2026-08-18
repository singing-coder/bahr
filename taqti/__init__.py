"""taqti: Urdu-Hindi meter identification and scansion.

Rules and meter inventory: Pritchett & Khaliq, *Urdu Meter: A Practical
Handbook* (https://franpritchett.com/00ghalib/meterbk/). Test corpus:
*A Desertful of Roses* (Ghalib) and *A Garden of Kashmir* (Mir), both by
Frances Pritchett, which supply ground-truth meter labels (G1-G23).
"""
from .identify import identify, taqti_lines, format_taqti, line_fits
from .meters import METERS, GHALIB_METERS, MIR_METERS, RARE_METERS, G_TO_HANDBOOK
from .translit import normalize

__version__ = "0.1.0"
__all__ = ["identify", "taqti_lines", "format_taqti", "line_fits",
           "METERS", "GHALIB_METERS", "MIR_METERS", "RARE_METERS", "G_TO_HANDBOOK", "normalize"]
