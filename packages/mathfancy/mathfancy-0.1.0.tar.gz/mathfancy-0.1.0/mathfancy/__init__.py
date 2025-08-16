"""
mathfancy
A tiny single-function package: to_math(text, style) -> str
"""

_STYLE = {
    "bold":            (0x1D400, 0x1D41A, 0x1D7CE),
    "italic":          (0x1D434, 0x1D44E, None),
    "bolditalic":      (0x1D468, 0x1D482, 0x1D7CE),
    "script":          (0x1D49C, 0x1D4B6, None),
    "boldscript":      (0x1D4D0, 0x1D4EA, None),
    "fraktur":         (0x1D504, 0x1D51E, None),
    "doublestruck":    (0x1D538, 0x1D552, 0x1D7D8),
    "boldfraktur":     (0x1D56C, 0x1D586, None),
    "sans":            (0x1D5A0, 0x1D5BA, 0x1D7E2),
    "sansserifbold":   (0x1D5D4, 0x1D5EE, 0x1D7EC),
    "sansserifitalic": (0x1D608, 0x1D622, None),
    "sansserifbolditalic": (0x1D63C, 0x1D656, None),
    "monospace":       (0x1D670, 0x1D68A, 0x1D7F6),
}

def _make_map(a, z, zero):
    m = {}
    if a:
        for i in range(26):
            m[chr(65 + i)] = chr(a + i)
            m[chr(97 + i)] = chr(z + i)
    if zero is not None:
        for i in range(10):
            m[str(i)] = chr(zero + i)
    return m

_MAP = {k: _make_map(A, a, zero) for k, (A, a, zero) in _STYLE.items()}

def to_math(text: str, style: str = "doublestruck") -> str:
    """
    Convert plain text to the desired Unicode mathematical style.

    Parameters
    ----------
    text : str
        Input string.
    style : str
        Target style (see _STYLE.keys()).

    Returns
    -------
    str
        Styled string.
    """
    style = style.lower()
    if style not in _MAP:
        raise ValueError(f"Unknown style '{style}'. Choose from {list(_MAP)}")
    trans = _MAP[style]
    return "".join(trans.get(ch, ch) for ch in text)

__all__ = ["to_math"]
