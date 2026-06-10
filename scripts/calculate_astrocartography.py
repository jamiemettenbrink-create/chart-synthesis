#!/usr/bin/env python3
"""
Astrocartography (Astro*Carto*Graphy) Calculator
=================================================

Computes the planetary relocation lines for a birth chart: the meridians and
horizon curves across the globe where each planet would be angular (on the MC,
IC, Ascendant, or Descendant) at the moment of birth.

This is the relocation layer that the natal calculator (calculate_chart.py) does
not provide. It reuses that module's ephemeris so the planetary longitudes are
identical to the natal chart.

Method
------
1. Each body's geocentric ecliptic longitude (lambda) is taken from the natal
   ephemeris. Ecliptic latitude is treated as 0 (the same flat-ecliptic
   assumption the natal calculator uses for house/angle work). This keeps the
   astrocartography consistent with the natal chart. The MC/IC meridian lines
   depend only on Right Ascension and are robust under this assumption; the
   ASC/DSC horizon curves carry a small error for the high-latitude bodies
   (Moon, Pluto), noted in the output.
2. Convert (lambda, beta=0) to equatorial coordinates with the obliquity eps:
        RA  alpha = atan2(cos(eps) sin(lambda), cos(lambda))
        dec delta = asin(sin(eps) sin(lambda))
3. MC line  : geographic longitude where Local Sidereal Time == alpha
              -> L_mc = alpha - GMST           (a meridian; all latitudes)
   IC line  : the opposite meridian            -> L_ic = L_mc + 180
4. ASC/DSC  : a body of declination delta sits on the horizon at latitude phi
   when its hour angle H satisfies  cos(H) = -tan(phi) tan(delta).
        rising  (ASC, eastern horizon): H = -H0, L = alpha - H0 - GMST
        setting (DSC, western horizon): H = +H0, L = alpha + H0 - GMST
   where H0 = acos(-tan(phi) tan(delta)). Traced over latitude to form a curve.
   (Where |tan(phi) tan(delta)| > 1 the body is circumpolar / never rises at
   that latitude, so the curve has no point there.)

Outputs
-------
- A text/JSON summary of every line.
- An equirectangular SVG world map (lat/long graticule + major-city anchors +
  the 40 planetary lines), written to outputs/.
- A proximity report: which major cities sit on (within a chosen orb of) which
  lines.

Usage
-----
    python3 scripts/calculate_astrocartography.py \
        --name "Jamie" \
        --year 1986 --month 4 --day 24 \
        --hour 6 --minute 10 --utc_offset -7 \
        --lat 33.4942 --lng -111.9261 \
        --svg outputs/jamie-astrocartography.svg \
        --orb 2.0
"""

import math
import json
import argparse
import os
import sys

# Reuse the natal ephemeris so longitudes match the birth chart exactly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculate_chart import (
    norm, r, julian_day, calculate_sidereal_time, calculate_full_chart,
    lon_to_sign,
)

# The ten traditional astrocartography bodies, in display order.
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
           'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

GLYPH = {
    'Sun': 'Sun', 'Moon': 'Moon', 'Mercury': 'Mer', 'Venus': 'Ven',
    'Mars': 'Mar', 'Jupiter': 'Jup', 'Saturn': 'Sat', 'Uranus': 'Ura',
    'Neptune': 'Nep', 'Pluto': 'Plu',
}

# A distinct, reasonably colour-blind-aware hue per planet.
COLOR = {
    'Sun':     '#E8A800',  # amber
    'Moon':    '#7C8BA1',  # slate
    'Mercury': '#11998E',  # teal
    'Venus':   '#E0529C',  # rose
    'Mars':    '#D7263D',  # red
    'Jupiter': '#8E44AD',  # purple
    'Saturn':  '#5D4037',  # brown
    'Uranus':  '#1565C0',  # blue
    'Neptune': '#0097A7',  # cyan
    'Pluto':   '#2E2E2E',  # near-black
}

# Geographic anchors. Without coastline data the map is read off a lat/long grid
# and a globally distributed set of major cities. (name, lat, lng)
CITIES = [
    ("Phoenix (birthplace)", 33.49, -111.93),
    ("Boulder", 40.015, -105.27),
    ("Los Angeles", 34.05, -118.24), ("Vancouver", 49.28, -123.12),
    ("Denver", 39.74, -104.99), ("Chicago", 41.88, -87.63),
    ("Toronto", 43.65, -79.38), ("New York", 40.71, -74.01),
    ("Miami", 25.76, -80.19), ("Mexico City", 19.43, -99.13),
    ("Bogota", 4.71, -74.07), ("Lima", -12.05, -77.04),
    ("Santiago", -33.45, -70.67), ("Buenos Aires", -34.60, -58.38),
    ("Rio de Janeiro", -22.91, -43.17), ("Reykjavik", 64.15, -21.94),
    ("London", 51.51, -0.13), ("Paris", 48.86, 2.35),
    ("Madrid", 40.42, -3.70), ("Rome", 41.90, 12.50),
    ("Berlin", 52.52, 13.40), ("Athens", 37.98, 23.73),
    ("Istanbul", 41.01, 28.98), ("Moscow", 55.76, 37.62),
    ("Casablanca", 33.57, -7.59), ("Cairo", 30.04, 31.24),
    ("Lagos", 6.52, 3.38), ("Nairobi", -1.29, 36.82),
    ("Cape Town", -33.92, 18.42), ("Dubai", 25.20, 55.27),
    ("Mumbai", 19.08, 72.88), ("New Delhi", 28.61, 77.21),
    ("Bangkok", 13.76, 100.50), ("Singapore", 1.35, 103.82),
    ("Hong Kong", 22.32, 114.17), ("Beijing", 39.90, 116.41),
    ("Tokyo", 35.68, 139.65), ("Seoul", 37.57, 126.98),
    ("Sydney", -33.87, 151.21), ("Auckland", -36.85, 174.76),
    ("Honolulu", 21.31, -157.86),
]


def wrap180(x):
    """Normalize a longitude to the range (-180, 180]."""
    x = (x + 180) % 360 - 180
    return x + 360 if x <= -180 else x


def obliquity(JD):
    """Mean obliquity of the ecliptic (deg), same model as the natal calc."""
    T = (JD - 2451545.0) / 36525.0
    return 23.439291111 - 0.013004167 * T - 0.000000164 * T * T + 0.000000504 * T ** 3


def birth_jd_gmst(year, month, day, hour, minute, utc_offset):
    """Replicate the natal calculator's UT/JD/GMST derivation exactly."""
    hour_ut = hour + minute / 60.0 - utc_offset
    extra_days = 0
    if hour_ut >= 24:
        hour_ut -= 24
        extra_days = 1
    elif hour_ut < 0:
        hour_ut += 24
        extra_days = -1
    JD = julian_day(year, month, day + extra_days, hour_ut)
    GMST = calculate_sidereal_time(JD)
    return JD, GMST


def ecliptic_to_equatorial(lon, eps):
    """(ecliptic longitude, beta=0) -> (RA, dec) in degrees."""
    lon_r, eps_r = r(lon), r(eps)
    ra = norm(math.degrees(math.atan2(math.cos(eps_r) * math.sin(lon_r),
                                      math.cos(lon_r))))
    dec = math.degrees(math.asin(math.sin(eps_r) * math.sin(lon_r)))
    return ra, dec


def asc_dsc_longitude(ra, dec, phi, gmst):
    """
    Geographic longitudes where the body rises (ASC) / sets (DSC) at latitude phi.
    Returns (lon_asc, lon_dsc) in (-180,180], or (None, None) if the body does
    not cross the horizon at this latitude (circumpolar or never-rising).
    """
    arg = -math.tan(r(phi)) * math.tan(r(dec))
    if arg < -1 or arg > 1:
        return None, None
    H0 = math.degrees(math.acos(arg))          # semi-diurnal arc, 0..180
    lon_asc = wrap180(ra - H0 - gmst)           # eastern horizon (rising)
    lon_dsc = wrap180(ra + H0 - gmst)           # western horizon (setting)
    return lon_asc, lon_dsc


def compute_lines(chart, JD, GMST, lat_step=1.0, lat_limit=72.0):
    """
    Build the line geometry for every planet.

    Returns a dict: planet -> {
        'ra','dec','sign',
        'MC': lon, 'IC': lon,                 # meridian longitudes
        'ASC': [(lat,lon),...], 'DSC': [...]  # horizon curves
    }
    """
    eps = obliquity(JD)
    out = {}
    lats = []
    n = int((2 * lat_limit) / lat_step)
    for i in range(n + 1):
        lats.append(lat_limit - i * lat_step)

    for p in PLANETS:
        lon = chart['planets'][p]['lon']
        ra, dec = ecliptic_to_equatorial(lon, eps)
        sign, deg, _ = lon_to_sign(lon)
        rec = {
            'ra': ra, 'dec': dec,
            'sign': sign, 'sign_deg': round(deg, 2),
            'ecliptic_lon': round(lon, 2),
            'MC': wrap180(ra - GMST),
            'IC': wrap180(ra - GMST + 180),
            'ASC': [], 'DSC': [],
        }
        for phi in lats:
            la, ld = asc_dsc_longitude(ra, dec, phi, GMST)
            if la is not None:
                rec['ASC'].append((phi, la))
            if ld is not None:
                rec['DSC'].append((phi, ld))
        out[p] = rec
    return out


# ----------------------------------------------------------------------------
# Proximity report
# ----------------------------------------------------------------------------

def line_lon_at_lat(curve, lat):
    """Interpolate a horizon curve's longitude at a given latitude."""
    best = None
    for i in range(len(curve) - 1):
        (la1, lo1), (la2, lo2) = curve[i], curve[i + 1]
        if (la1 - lat) * (la2 - lat) <= 0 and la1 != la2:
            # guard against the +-180 seam: skip if the segment wraps
            if abs(lo1 - lo2) > 180:
                continue
            f = (lat - la1) / (la2 - la1)
            return lo1 + f * (lo2 - lo1)
    # fall back to the nearest sampled latitude
    for la, lo in curve:
        if best is None or abs(la - lat) < abs(best[0] - lat):
            best = (la, lo)
    return best[1] if best and abs(best[0] - lat) <= 2.5 else None


def proximity_report(lines, orb=2.0):
    """For each city, list the planetary lines within `orb` degrees of longitude."""
    rows = []
    for name, lat, lng in CITIES:
        hits = []
        for p in PLANETS:
            rec = lines[p]
            for angle in ('MC', 'IC'):
                d = abs(wrap180(rec[angle] - lng))
                if d <= orb:
                    hits.append((d, p, angle))
            for angle in ('ASC', 'DSC'):
                ll = line_lon_at_lat(rec[angle], lat)
                if ll is not None:
                    d = abs(wrap180(ll - lng))
                    if d <= orb:
                        hits.append((d, p, angle))
        hits.sort()
        if hits:
            rows.append((name, lat, lng, hits))
    return rows


# ----------------------------------------------------------------------------
# SVG rendering (equirectangular projection)
# ----------------------------------------------------------------------------

REGIONS = {
    'world':         (-180, 180, -85, 85),
    'north-america': (-140, -52, 7, 72),
    'europe':        (-25, 45, 30, 72),
    'asia':          (40, 150, -10, 60),
}


def build_svg(lines, title, subtitle, orb=2.0, bounds=None, home=None):
    lon_min, lon_max, lat_min, lat_max = bounds or REGIONS['world']
    W, H = 1500, 820
    MX, MTOP, MBOT = 60, 70, 150          # margins (legend lives in MBOT)
    plot_w = W - 2 * MX
    plot_h = H - MTOP - MBOT
    lon_span = lon_max - lon_min
    # Finer graticule when zoomed in.
    lon_grid = 30 if lon_span > 140 else (20 if lon_span > 80 else 10)
    lat_grid = 20 if (lat_max - lat_min) > 100 else 10

    def in_lon(lon):
        return lon_min <= lon <= lon_max

    def X(lon):
        return MX + (lon - lon_min) / (lon_max - lon_min) * plot_w

    def Y(lat):
        return MTOP + (lat_max - lat) / (lat_max - lat_min) * plot_h

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1117"/>')
    s.append(f'<rect x="{MX}" y="{MTOP}" width="{plot_w}" height="{plot_h}" '
             f'fill="#171a22" stroke="#3a3f4b"/>')

    # Title
    s.append(f'<text x="{MX}" y="34" fill="#f5f5f5" font-size="24" '
             f'font-weight="bold">{title}</text>')
    s.append(f'<text x="{MX}" y="56" fill="#9aa0ac" font-size="14">{subtitle}</text>')

    # Graticule
    g0 = int(math.ceil(lon_min / lon_grid) * lon_grid)
    for lon in range(g0, int(lon_max) + 1, lon_grid):
        x = X(lon)
        s.append(f'<line x1="{x:.1f}" y1="{MTOP}" x2="{x:.1f}" y2="{MTOP+plot_h}" '
                 f'stroke="#2a2e38" stroke-width="1"/>')
        s.append(f'<text x="{x:.1f}" y="{MTOP+plot_h+16}" fill="#6b7280" '
                 f'font-size="11" text-anchor="middle">{lon}°</text>')
    lg0 = int(math.ceil(lat_min / lat_grid) * lat_grid)
    for lat in range(lg0, int(lat_max) + 1, lat_grid):
        y = Y(lat)
        s.append(f'<line x1="{MX}" y1="{y:.1f}" x2="{MX+plot_w}" y2="{y:.1f}" '
                 f'stroke="#2a2e38" stroke-width="1"/>')
        s.append(f'<text x="{MX-8}" y="{y+4:.1f}" fill="#6b7280" font-size="11" '
                 f'text-anchor="end">{lat}°</text>')
    # Equator emphasis
    if lat_min <= 0 <= lat_max:
        s.append(f'<line x1="{MX}" y1="{Y(0):.1f}" x2="{MX+plot_w}" y2="{Y(0):.1f}" '
                 f'stroke="#3c4250" stroke-width="1.5"/>')

    # Cities
    for name, lat, lng in CITIES:
        if not (lat_min <= lat <= lat_max and in_lon(lng)):
            continue
        cx, cy = X(lng), Y(lat)
        birth = name.endswith('(birthplace)')
        fill = '#ffd166' if birth else '#cfd3da'
        rad = 4.2 if birth else 2.4
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad}" fill="{fill}" '
                 f'stroke="#0f1117" stroke-width="0.6"/>')
        label = name.replace(' (birthplace)', '*')
        s.append(f'<text x="{cx+5:.1f}" y="{cy+3:.1f}" fill="#8b909b" '
                 f'font-size="9">{label}</text>')

    # Home marker (where the person currently lives)
    if home and (lat_min <= home['lat'] <= lat_max) and in_lon(home['lng']):
        hx, hy = X(home['lng']), Y(home['lat'])
        s.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="7" fill="none" '
                 f'stroke="#39FF88" stroke-width="2"/>')
        s.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="2.5" fill="#39FF88"/>')
        s.append(f'<text x="{hx+10:.1f}" y="{hy-8:.1f}" fill="#39FF88" '
                 f'font-size="12" font-weight="bold">{home["name"]}</text>')

    # Line styles per angle
    dash = {'MC': 'none', 'IC': '2,4', 'ASC': '7,4', 'DSC': '7,4,1,4'}

    def draw_meridian(lon, color, da, label):
        if not in_lon(lon):
            return
        x = X(lon)
        s.append(f'<line x1="{x:.1f}" y1="{MTOP}" x2="{x:.1f}" y2="{MTOP+plot_h}" '
                 f'stroke="{color}" stroke-width="2" stroke-dasharray="{da}" '
                 f'opacity="0.92"/>')
        s.append(f'<text x="{x:.1f}" y="{MTOP-4}" fill="{color}" font-size="10" '
                 f'text-anchor="middle">{label}</text>')

    def draw_curve(curve, color, da, label):
        # Break into segments on the +-180 seam OR when a point leaves the
        # visible bounds, so zoomed panels don't draw lines across the margins.
        seg, segs = [], []
        prev = None
        for lat, lon in curve:
            visible = in_lon(lon) and (lat_min <= lat <= lat_max)
            if prev is not None and abs(lon - prev) > 180:
                segs.append(seg); seg = []
            if not visible:
                if seg:
                    segs.append(seg); seg = []
                prev = lon
                continue
            seg.append((lat, lon)); prev = lon
        segs.append(seg)
        drawn = False
        for sg in segs:
            if len(sg) < 2:
                continue
            drawn = True
            pts = ' '.join(f'{X(lo):.1f},{Y(la):.1f}' for la, lo in sg)
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="2" stroke-dasharray="{da}" opacity="0.92"/>')
        # label near the top of the longest visible segment
        vis = [sg for sg in segs if len(sg) >= 2]
        if drawn and vis:
            longest = max(vis, key=len)
            la, lo = longest[0]
            s.append(f'<text x="{X(lo)+4:.1f}" y="{Y(la)+10:.1f}" fill="{color}" '
                     f'font-size="9">{label}</text>')

    for p in PLANETS:
        rec = lines[p]
        c = COLOR[p]
        g = GLYPH[p]
        draw_meridian(rec['MC'], c, dash['MC'], f'{g} MC')
        draw_meridian(rec['IC'], c, dash['IC'], f'{g} IC')
        draw_curve(rec['ASC'], c, dash['ASC'], f'{g} AS')
        draw_curve(rec['DSC'], c, dash['DSC'], f'{g} DS')

    # Legend
    ly = MTOP + plot_h + 40
    s.append(f'<text x="{MX}" y="{ly}" fill="#cfd3da" font-size="12" '
             f'font-weight="bold">Planets</text>')
    for i, p in enumerate(PLANETS):
        col = i % 5
        row = i // 5
        lx = MX + 70 + col * 150
        lyy = ly + row * 22 - 10
        s.append(f'<line x1="{lx}" y1="{lyy}" x2="{lx+22}" y2="{lyy}" '
                 f'stroke="{COLOR[p]}" stroke-width="3"/>')
        s.append(f'<text x="{lx+28}" y="{lyy+4}" fill="#cfd3da" '
                 f'font-size="11">{p}</text>')
    # Angle key
    kx = MX + 70 + 4 * 150 + 120
    keys = [('MC  (solid) culminating', 'none'),
            ('IC  (dotted) anti-culminating', '2,4'),
            ('ASC (dashed) rising', '7,4'),
            ('DSC (dash-dot) setting', '7,4,1,4')]
    for i, (txt, da) in enumerate(keys):
        kyy = ly + i * 18 - 10
        s.append(f'<line x1="{kx}" y1="{kyy}" x2="{kx+26}" y2="{kyy}" '
                 f'stroke="#cfd3da" stroke-width="2" stroke-dasharray="{da}"/>')
        s.append(f'<text x="{kx+32}" y="{kyy+4}" fill="#9aa0ac" '
                 f'font-size="10">{txt}</text>')

    s.append(f'<text x="{MX}" y="{H-12}" fill="#5b606b" font-size="10">'
             f'Equirectangular projection. Lines = where a planet is angular at '
             f'birth. Orb of influence ~{orb:.0f}° longitude (~{int(orb*69)} mi at the equator). '
             f'* = birthplace.</text>')
    s.append('</svg>')
    return '\n'.join(s)


# ----------------------------------------------------------------------------
# Text summary
# ----------------------------------------------------------------------------

def format_summary(lines, chart, orb):
    L = []
    L.append("=" * 70)
    L.append("ASTROCARTOGRAPHY LINE SUMMARY")
    L.append(f"  {chart['name']} | {chart['birth_date']} {chart['birth_time']} | "
             f"{chart['location']}")
    L.append("=" * 70)
    L.append(f"\n{'PLANET':<9}{'NATAL':<16}{'MC lon':>9}{'IC lon':>9}"
             f"{'ASC@0':>9}{'DSC@0':>9}{'decl':>8}")
    L.append("-" * 70)
    for p in PLANETS:
        rec = lines[p]
        natal = f"{rec['sign_deg']:.1f} {rec['sign'][:3]}"
        a0 = line_lon_at_lat(rec['ASC'], 0.0)
        d0 = line_lon_at_lat(rec['DSC'], 0.0)
        a0s = f"{a0:7.1f}" if a0 is not None else "   --  "
        d0s = f"{d0:7.1f}" if d0 is not None else "   --  "
        L.append(f"{p:<9}{natal:<16}{rec['MC']:8.1f} {rec['IC']:8.1f} "
                 f"{a0s} {d0s} {rec['dec']:7.1f}")
    L.append("\n(MC/IC are fixed meridians. ASC/DSC shown at the equator; they "
             "curve with latitude.)")

    L.append("\n" + "=" * 70)
    L.append(f"CITIES ON A LINE  (within {orb:.1f}° longitude)")
    L.append("=" * 70)
    rows = proximity_report(lines, orb)
    if not rows:
        L.append("  (none within orb)")
    for name, lat, lng, hits in rows:
        tags = ", ".join(f"{p} {ang} ({d:.1f}°)" for d, p, ang in hits)
        L.append(f"  {name:<22} {tags}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Astrocartography line calculator")
    ap.add_argument('--name', default='Chart')
    ap.add_argument('--year', type=int, required=True)
    ap.add_argument('--month', type=int, required=True)
    ap.add_argument('--day', type=int, required=True)
    ap.add_argument('--hour', type=int, required=True)
    ap.add_argument('--minute', type=int, default=0)
    ap.add_argument('--utc_offset', type=float, required=True)
    ap.add_argument('--lat', type=float, required=True)
    ap.add_argument('--lng', type=float, required=True)
    ap.add_argument('--orb', type=float, default=2.0,
                    help='Orb of influence in degrees of longitude (default 2.0)')
    ap.add_argument('--region', default='world', choices=sorted(REGIONS),
                    help='Map extent (default world)')
    ap.add_argument('--home', default=None,
                    help='Current home to mark, as "Name,lat,lng" '
                         '(e.g. "Boulder,40.015,-105.27")')
    ap.add_argument('--svg', default=None, help='Path to write the SVG map')
    ap.add_argument('--json', default=None, help='Path to write the raw line JSON')
    args = ap.parse_args()

    chart = calculate_full_chart(args.year, args.month, args.day, args.hour,
                                 args.minute, args.utc_offset, args.lat,
                                 args.lng, args.name)
    JD, GMST = birth_jd_gmst(args.year, args.month, args.day, args.hour,
                             args.minute, args.utc_offset)
    lines = compute_lines(chart, JD, GMST)

    print(format_summary(lines, chart, args.orb))

    home = None
    if args.home:
        parts = args.home.split(',')
        home = {'name': parts[0].strip(),
                'lat': float(parts[1]), 'lng': float(parts[2])}

    if args.svg:
        title = f"{args.name} — Astrocartography"
        sign = chart['planets']['Sun']
        sub = (f"{chart['birth_date']} {chart['birth_time']} · "
               f"lat {args.lat}, lng {args.lng} · "
               f"Sun {sign['degree']}° {sign['sign']}, "
               f"Moon {chart['planets']['Moon']['degree']}° "
               f"{chart['planets']['Moon']['sign']}")
        svg = build_svg(lines, title, sub, args.orb,
                        bounds=REGIONS[args.region], home=home)
        os.makedirs(os.path.dirname(args.svg) or '.', exist_ok=True)
        with open(args.svg, 'w') as f:
            f.write(svg)
        print(f"\nSVG map written to {args.svg}")

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(lines, f, indent=2)
        print(f"Line data written to {args.json}")


if __name__ == '__main__':
    main()
