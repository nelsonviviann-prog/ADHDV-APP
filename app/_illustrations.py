"""
Hand-drawn inline SVG illustrations.

Why SVG and not images:
  - Self-contained. The app promises offline use in low-connectivity clinics;
    an <img src="https://..."> breaks that promise. These do not.
  - Tiny (a few KB) and crisp at any size / DPI.
  - No licensing exposure -- stock photos of real people carry usage terms.
  - Skin tones and styling are set deliberately, so the clinicians in a
    Nigerian tool look Nigerian.

Palette is the app's own: navy #1e3a8a, amber #b45309, stone neutrals.
Every function returns an SVG string to drop into st.markdown(unsafe_allow_html=True).
"""

from __future__ import annotations

# Brand
NAVY = "#1e3a8a"
NAVY_DEEP = "#1e293b"
AMBER = "#b45309"
COAT = "#fafaf9"
COAT_SHADE = "#e7e5e4"
LINE = "#1c1917"
STONE = "#78716c"

# Skin + hair
SKIN_DEEP = "#6b4226"
SKIN_WARM = "#8d5a34"
HAIR = "#171310"


def _clinician_female(x: float = 0) -> str:
    """Female clinician: lab coat, stethoscope, natural hair."""
    return f"""
    <g transform="translate({x},0)">
      <!-- hair back -->
      <circle cx="80" cy="62" r="46" fill="{HAIR}"/>
      <circle cx="46" cy="52" r="17" fill="{HAIR}"/>
      <circle cx="114" cy="52" r="17" fill="{HAIR}"/>
      <circle cx="54" cy="82" r="14" fill="{HAIR}"/>
      <circle cx="106" cy="82" r="14" fill="{HAIR}"/>

      <!-- neck -->
      <rect x="70" y="94" width="20" height="20" rx="8" fill="{SKIN_DEEP}"/>

      <!-- sleeves (drawn first, so the torso overlaps them at the shoulder) -->
      <path d="M44 122 C 30 128, 24 142, 23 158 L 20 214
               C 19 222, 33 224, 34 216 L 40 160 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>
      <path d="M116 122 C 130 128, 136 142, 137 158 L 140 214
               C 141 222, 127 224, 126 216 L 120 160 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>
      <circle cx="27" cy="219" r="8" fill="{SKIN_DEEP}"/>
      <circle cx="133" cy="219" r="8" fill="{SKIN_DEEP}"/>

      <!-- torso: real shoulders, straight sides -->
      <path d="M80 110
               L 50 121 C 42 124, 38 134, 37 146
               L 33 232 L 127 232 L 123 146
               C 122 134, 118 124, 110 121 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>

      <!-- navy top + V-neck under the open coat -->
      <path d="M80 112 L 66 118 L 80 156 L 94 118 Z" fill="{NAVY}"/>
      <!-- coat lapels folding back over the top -->
      <path d="M66 118 L 80 156 L 62 128 Z" fill="{COAT_SHADE}" opacity="0.7"/>
      <path d="M94 118 L 80 156 L 98 128 Z" fill="{COAT_SHADE}" opacity="0.7"/>
      <!-- centre seam -->
      <path d="M80 156 L 80 232" stroke="{COAT_SHADE}" stroke-width="1.5"/>

      <!-- face -->
      <circle cx="80" cy="66" r="33" fill="{SKIN_DEEP}"/>
      <!-- eyes -->
      <circle cx="69" cy="64" r="3.2" fill="{LINE}"/>
      <circle cx="91" cy="64" r="3.2" fill="{LINE}"/>
      <!-- brows -->
      <path d="M64 56 Q 69 53, 74 56" stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>
      <path d="M86 56 Q 91 53, 96 56" stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>
      <!-- smile -->
      <path d="M71 78 Q 80 86, 89 78" stroke="{LINE}" stroke-width="2.2" fill="none" stroke-linecap="round"/>

      <!-- stethoscope: round the neck, hanging down -->
      <path d="M66 116 C 54 142, 58 172, 74 186"
            stroke="{AMBER}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <path d="M94 116 C 106 142, 102 166, 94 178"
            stroke="{AMBER}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <circle cx="77" cy="190" r="8" fill="{AMBER}"/>
      <circle cx="77" cy="190" r="3.5" fill="{COAT}"/>

      <!-- pocket + name badge -->
      <rect x="96" y="188" width="22" height="18" rx="3" fill="{COAT_SHADE}"/>
      <rect x="44" y="170" width="15" height="20" rx="2" fill="{NAVY}"/>
      <rect x="47" y="175" width="9" height="2.5" rx="1.2" fill="{COAT}"/>
    </g>
    """


def _clinician_male(x: float = 0) -> str:
    """Male clinician: lab coat, stethoscope, short hair."""
    return f"""
    <g transform="translate({x},0)">
      <!-- neck -->
      <rect x="70" y="94" width="20" height="20" rx="8" fill="{SKIN_WARM}"/>

      <!-- sleeves -->
      <path d="M44 122 C 30 128, 24 142, 23 158 L 20 214
               C 19 222, 33 224, 34 216 L 40 160 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>
      <path d="M116 122 C 130 128, 136 142, 137 158 L 140 214
               C 141 222, 127 224, 126 216 L 120 160 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>
      <circle cx="27" cy="219" r="8" fill="{SKIN_WARM}"/>
      <circle cx="133" cy="219" r="8" fill="{SKIN_WARM}"/>

      <!-- torso -->
      <path d="M80 110
               L 50 121 C 42 124, 38 134, 37 146
               L 33 232 L 127 232 L 123 146
               C 122 134, 118 124, 110 121 Z"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2"/>

      <!-- shirt + tie under the open coat -->
      <path d="M80 112 L 66 118 L 80 156 L 94 118 Z" fill="{NAVY_DEEP}"/>
      <path d="M80 116 L 75 124 L 80 152 L 85 124 Z" fill="{AMBER}"/>
      <path d="M66 118 L 80 156 L 62 128 Z" fill="{COAT_SHADE}" opacity="0.7"/>
      <path d="M94 118 L 80 156 L 98 128 Z" fill="{COAT_SHADE}" opacity="0.7"/>
      <path d="M80 156 L 80 232" stroke="{COAT_SHADE}" stroke-width="1.5"/>

      <!-- face -->
      <circle cx="80" cy="66" r="33" fill="{SKIN_WARM}"/>
      <!-- short hair -->
      <path d="M47 60 A 33 33 0 0 1 113 60 L 113 54
               A 33 30 0 0 0 47 54 Z" fill="{HAIR}"/>
      <path d="M47 58 A 33 33 0 0 1 113 58 L 113 66
               C 108 46, 52 46, 47 66 Z" fill="{HAIR}"/>
      <!-- eyes -->
      <circle cx="69" cy="66" r="3.2" fill="{LINE}"/>
      <circle cx="91" cy="66" r="3.2" fill="{LINE}"/>
      <path d="M64 58 Q 69 55, 74 58" stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>
      <path d="M86 58 Q 91 55, 96 58" stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>
      <!-- smile -->
      <path d="M71 80 Q 80 87, 89 80" stroke="{LINE}" stroke-width="2.2" fill="none" stroke-linecap="round"/>

      <!-- stethoscope -->
      <path d="M66 116 C 54 142, 58 172, 74 186"
            stroke="{NAVY}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <path d="M94 116 C 106 142, 102 166, 94 178"
            stroke="{NAVY}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <circle cx="77" cy="190" r="8" fill="{NAVY}"/>
      <circle cx="77" cy="190" r="3.5" fill="{COAT}"/>

      <rect x="96" y="188" width="22" height="18" rx="3" fill="{COAT_SHADE}"/>
      <rect x="44" y="170" width="15" height="20" rx="2" fill="{AMBER}"/>
      <rect x="47" y="175" width="9" height="2.5" rx="1.2" fill="{COAT}"/>
    </g>
    """


def consultation_clinicians(height: int = 240) -> str:
    """Two clinicians side by side -- the Consult page hero.

    `preserveAspectRatio` + a viewBox means this scales to any column width
    without distorting, and `max-width:100%` keeps it inside its container on a
    phone.
    """
    return f"""
    <div style="display:flex; justify-content:center; margin:6px 0 18px 0;">
      <svg viewBox="0 0 320 240" height="{height}" width="100%"
           style="max-width:340px; height:auto; overflow:visible;"
           xmlns="http://www.w3.org/2000/svg" role="img"
           aria-label="A female and a male clinician in lab coats with stethoscopes">
        <!-- soft ground -->
        <ellipse cx="160" cy="232" rx="140" ry="12" fill="{NAVY}" opacity="0.06"/>
        {_clinician_female(x=8)}
        {_clinician_male(x=162)}
      </svg>
    </div>
    """


def _empty_state(svg_body: str, message: str, sub: str = "") -> str:
    """Shared frame for the 'nothing here yet' moments."""
    sub_html = (
        f"<div style='color:{STONE}; font-size:13px; margin-top:4px;'>{sub}</div>"
        if sub else ""
    )
    return f"""
    <div style="text-align:center; padding:30px 20px 34px 20px;
                border:1px dashed {COAT_SHADE}; border-radius:6px; margin:6px 0 12px 0;">
      <svg viewBox="0 0 120 100" width="120" height="100" role="img"
           xmlns="http://www.w3.org/2000/svg" aria-label="{message}">
        {svg_body}
      </svg>
      <div style="color:#44403c; font-size:15px; font-weight:600; margin-top:10px;">
        {message}
      </div>
      {sub_html}
    </div>
    """


def empty_screenings(message: str, sub: str = "") -> str:
    """A clipboard with blank lines -- no screenings recorded yet."""
    body = f"""
      <rect x="30" y="16" width="60" height="74" rx="5"
            fill="{COAT}" stroke="{COAT_SHADE}" stroke-width="2.5"/>
      <rect x="46" y="9" width="28" height="14" rx="4" fill="{NAVY}"/>
      <circle cx="60" cy="16" r="3.4" fill="{COAT}"/>
      <rect x="40" y="38" width="40" height="4" rx="2" fill="{COAT_SHADE}"/>
      <rect x="40" y="50" width="30" height="4" rx="2" fill="{COAT_SHADE}"/>
      <rect x="40" y="62" width="36" height="4" rx="2" fill="{COAT_SHADE}"/>
      <rect x="40" y="74" width="22" height="4" rx="2" fill="{COAT_SHADE}"/>
    """
    return _empty_state(body, message, sub)


def empty_feedback(message: str, sub: str = "") -> str:
    """Two speech bubbles -- no feedback submitted yet."""
    body = f"""
      <rect x="14" y="22" width="66" height="40" rx="12"
            fill="{COAT}" stroke="{NAVY}" stroke-width="2.5"/>
      <path d="M32 62 L 29 76 L 47 62 Z" fill="{COAT}" stroke="{NAVY}" stroke-width="2.5"/>
      <circle cx="34" cy="42" r="3.4" fill="{NAVY}" opacity="0.4"/>
      <circle cx="47" cy="42" r="3.4" fill="{NAVY}" opacity="0.4"/>
      <circle cx="60" cy="42" r="3.4" fill="{NAVY}" opacity="0.4"/>
      <rect x="62" y="46" width="44" height="30" rx="10"
            fill="{COAT}" stroke="{AMBER}" stroke-width="2.5"/>
      <path d="M92 76 L 96 88 L 80 76 Z" fill="{COAT}" stroke="{AMBER}" stroke-width="2.5"/>
    """
    return _empty_state(body, message, sub)


def empty_rating(message: str, sub: str = "") -> str:
    """One filled figure, one dashed outline -- the second rater is missing."""
    body = f"""
      <circle cx="40" cy="34" r="14" fill="{NAVY}"/>
      <path d="M40 52 C 26 52, 18 62, 17 78 L 63 78 C 62 62, 54 52, 40 52 Z"
            fill="{NAVY}"/>
      <circle cx="84" cy="34" r="14" fill="none" stroke="{COAT_SHADE}"
              stroke-width="2.5" stroke-dasharray="5 4"/>
      <path d="M84 52 C 70 52, 62 62, 61 78 L 107 78 C 106 62, 98 52, 84 52 Z"
            fill="none" stroke="{COAT_SHADE}" stroke-width="2.5" stroke-dasharray="5 4"/>
    """
    return _empty_state(body, message, sub)


def chat_bubbles() -> str:
    """Small decorative 'conversation' motif for the Consult page."""
    return f"""
    <div style="display:flex; justify-content:center; margin:0 0 6px 0;">
      <svg viewBox="0 0 200 70" width="180" height="63"
           xmlns="http://www.w3.org/2000/svg" role="img"
           aria-label="Two chat bubbles">
        <rect x="6" y="8" width="104" height="34" rx="14" fill="{NAVY}"/>
        <path d="M28 42 L 26 54 L 42 42 Z" fill="{NAVY}"/>
        <circle cx="38" cy="25" r="3.4" fill="{COAT}" opacity="0.9"/>
        <circle cx="56" cy="25" r="3.4" fill="{COAT}" opacity="0.9"/>
        <circle cx="74" cy="25" r="3.4" fill="{COAT}" opacity="0.9"/>

        <rect x="92" y="28" width="102" height="32" rx="13" fill="{AMBER}"/>
        <path d="M172 60 L 176 70 L 158 60 Z" fill="{AMBER}"/>
        <circle cx="124" cy="44" r="3.2" fill="{COAT}" opacity="0.95"/>
        <circle cx="142" cy="44" r="3.2" fill="{COAT}" opacity="0.95"/>
        <circle cx="160" cy="44" r="3.2" fill="{COAT}" opacity="0.95"/>
      </svg>
    </div>
    """
