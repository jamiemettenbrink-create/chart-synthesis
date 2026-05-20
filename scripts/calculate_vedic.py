#!/usr/bin/env python3
"""
Vedic Astrology (Jyotish) Calculator
Calculates: Sidereal positions, Lagna (rising), Nakshatras (27 lunar mansions),
planetary dignities (exaltation/debilitation/own sign), and Vimshottari dasha sequence.

Uses Lahiri ayanamsa (standard in India) for tropical → sidereal conversion.
Whole Sign houses (same as tropical calculator).

Usage:
    python3 calculate_vedic.py --year 1986 --month 4 --day 24 \
        --hour 6 --minute 10 --utc_offset -7 \
        --lat 33.4942 --lng -111.9261
"""

import math
import argparse

# ── Ayanamsa (Lahiri) ─────────────────────────────────────────────────────────
# Lahiri ayanamsa for J2000.0 = 23.85° and increases ~50.3"/year
AYANAMSA_J2000 = 23.85  # degrees at J2000.0 (Jan 1.5, 2000)
AYANAMSA_RATE  = 50.3 / 3600  # degrees per year

def lahiri_ayanamsa(T):
    """Return Lahiri ayanamsa in degrees for Julian centuries T from J2000."""
    return AYANAMSA_J2000 + AYANAMSA_RATE * T * 100  # T in centuries

# ── Signs ─────────────────────────────────────────────────────────────────────
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury',
              'Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']

# ── Nakshatras (27 Lunar Mansions) ───────────────────────────────────────────
NAKSHATRAS = [
    {'name':'Ashwini',      'ruler':'Ketu',    'start':0.0,   'deity':'Ashwini Kumaras', 'symbol':'Horse head'},
    {'name':'Bharani',      'ruler':'Venus',   'start':13.333,'deity':'Yama',            'symbol':'Yoni'},
    {'name':'Krittika',     'ruler':'Sun',     'start':26.667,'deity':'Agni',            'symbol':'Razor/flame'},
    {'name':'Rohini',       'ruler':'Moon',    'start':40.0,  'deity':'Brahma',          'symbol':'Chariot'},
    {'name':'Mrigashira',   'ruler':'Mars',    'start':53.333,'deity':'Soma',            'symbol':'Deer head'},
    {'name':'Ardra',        'ruler':'Rahu',    'start':66.667,'deity':'Rudra',           'symbol':'Teardrop'},
    {'name':'Punarvasu',    'ruler':'Jupiter', 'start':80.0,  'deity':'Aditi',           'symbol':'Quiver'},
    {'name':'Pushya',       'ruler':'Saturn',  'start':93.333,'deity':'Brihaspati',      'symbol':'Flower'},
    {'name':'Ashlesha',     'ruler':'Mercury', 'start':106.667,'deity':'Nagas',          'symbol':'Serpent'},
    {'name':'Magha',        'ruler':'Ketu',    'start':120.0, 'deity':'Pitris',          'symbol':'Throne'},
    {'name':'Purva Phalguni','ruler':'Venus',  'start':133.333,'deity':'Bhaga',          'symbol':'Hammock'},
    {'name':'Uttara Phalguni','ruler':'Sun',   'start':146.667,'deity':'Aryaman',        'symbol':'Bed'},
    {'name':'Hasta',        'ruler':'Moon',    'start':160.0, 'deity':'Savitar',         'symbol':'Hand'},
    {'name':'Chitra',       'ruler':'Mars',    'start':173.333,'deity':'Vishwakarma',    'symbol':'Pearl'},
    {'name':'Swati',        'ruler':'Rahu',    'start':186.667,'deity':'Vayu',           'symbol':'Coral'},
    {'name':'Vishakha',     'ruler':'Jupiter', 'start':200.0, 'deity':'Indra-Agni',      'symbol':'Arch'},
    {'name':'Anuradha',     'ruler':'Saturn',  'start':213.333,'deity':'Mitra',          'symbol':'Lotus'},
    {'name':'Jyeshtha',     'ruler':'Mercury', 'start':226.667,'deity':'Indra',          'symbol':'Earring'},
    {'name':'Mula',         'ruler':'Ketu',    'start':240.0, 'deity':'Nirrti',          'symbol':'Root'},
    {'name':'Purva Ashadha','ruler':'Venus',   'start':253.333,'deity':'Apas',           'symbol':'Fan'},
    {'name':'Uttara Ashadha','ruler':'Sun',    'start':266.667,'deity':'Vishvedevas',    'symbol':'Elephant tusk'},
    {'name':'Shravana',     'ruler':'Moon',    'start':280.0, 'deity':'Vishnu',          'symbol':'Ear/arrow'},
    {'name':'Dhanishtha',   'ruler':'Mars',    'start':293.333,'deity':'Vasus',          'symbol':'Drum'},
    {'name':'Shatabhisha',  'ruler':'Rahu',    'start':306.667,'deity':'Varuna',         'symbol':'Circle'},
    {'name':'Purva Bhadra', 'ruler':'Jupiter', 'start':320.0, 'deity':'Aja Ekapada',    'symbol':'Sword'},
    {'name':'Uttara Bhadra','ruler':'Saturn',  'start':333.333,'deity':'Ahir Budhnya',  'symbol':'Twins'},
    {'name':'Revati',       'ruler':'Mercury', 'start':346.667,'deity':'Pushan',         'symbol':'Fish'},
]

NAKSHATRA_SPAN = 360 / 27  # 13.333...°

def get_nakshatra(sidereal_lon):
    """Return nakshatra, pada (quarter), and degrees within nakshatra."""
    lon = sidereal_lon % 360
    idx = int(lon / NAKSHATRA_SPAN)
    idx = min(idx, 26)
    within = lon - NAKSHATRAS[idx]['start']
    pada = int(within / (NAKSHATRA_SPAN / 4)) + 1
    pada = min(pada, 4)
    return NAKSHATRAS[idx], pada, within

# ── Vimshottari Dasha ─────────────────────────────────────────────────────────
# Order and years for each planet
DASHA_ORDER  = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS  = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_TOTAL  = 120  # years

# Nakshatra rulers in dasha order
NAKSHATRA_RULERS = [n['ruler'] for n in NAKSHATRAS]

def vimshottari_dasha(moon_sidereal_lon, birth_year, birth_month, birth_day):
    """
    Calculate Vimshottari dasha sequence from birth.
    Returns list of dashas with planet, start_age, end_age, years.
    """
    moon_lon = moon_sidereal_lon % 360
    nakshatra_idx = int(moon_lon / NAKSHATRA_SPAN)
    nakshatra_idx = min(nakshatra_idx, 26)
    
    # Position within nakshatra (0.0 to 1.0)
    within_nakshatra = (moon_lon - NAKSHATRAS[nakshatra_idx]['start']) / NAKSHATRA_SPAN
    
    # Ruling planet of birth nakshatra
    birth_ruler = NAKSHATRAS[nakshatra_idx]['ruler']
    
    # Find starting position in dasha cycle
    start_dasha_idx = DASHA_ORDER.index(birth_ruler)
    
    # Remaining years in first dasha
    first_dasha_years = DASHA_YEARS[birth_ruler]
    elapsed_fraction = within_nakshatra  # fraction of nakshatra elapsed = fraction of dasha elapsed
    remaining_first = first_dasha_years * (1 - elapsed_fraction)
    
    dashas = []
    age = -remaining_first  # birth age offset (negative = started before birth)
    
    # Build full dasha sequence (cover ~150 years = at least one full cycle + partial)
    total_covered = 0
    cycle_pos = start_dasha_idx
    first = True
    
    while total_covered < 150:
        planet = DASHA_ORDER[cycle_pos % 9]
        years = DASHA_YEARS[planet] if not first else remaining_first
        
        dashas.append({
            'planet': planet,
            'start_age': round(age, 2),
            'end_age': round(age + years, 2),
            'years': round(years, 2),
            'start_year': birth_year + age,
            'end_year': birth_year + age + years,
        })
        
        age += years
        total_covered += years
        cycle_pos += 1
        first = False
    
    return dashas, birth_ruler, remaining_first

def current_dasha(dashas, current_age):
    """Find the current mahadasha and approximate antardasha."""
    for d in dashas:
        if d['start_age'] <= current_age < d['end_age']:
            return d
    return dashas[-1]

# ── Planetary Dignities ───────────────────────────────────────────────────────
# Format: sign index (0=Aries ... 11=Pisces)
EXALTATION = {
    'Sun': 0,      # Aries (exact: 10°)
    'Moon': 1,     # Taurus (exact: 3°)
    'Mercury': 5,  # Virgo (exact: 15°)
    'Venus': 11,   # Pisces (exact: 27°)
    'Mars': 9,     # Capricorn (exact: 28°)
    'Jupiter': 3,  # Cancer (exact: 5°)
    'Saturn': 6,   # Libra (exact: 20°)
    'Rahu': 1,     # Taurus (varies by tradition)
    'Ketu': 7,     # Scorpio (varies)
}
DEBILITATION = {k: (v+6)%12 for k,v in EXALTATION.items()}  # opposite sign

OWN_SIGNS = {
    'Sun':     [4],        # Leo
    'Moon':    [3],        # Cancer
    'Mercury': [2, 5],     # Gemini, Virgo
    'Venus':   [1, 6],     # Taurus, Libra
    'Mars':    [0, 7],     # Aries, Scorpio
    'Jupiter': [8, 11],    # Sagittarius, Pisces
    'Saturn':  [9, 10],    # Capricorn, Aquarius
}

def get_dignity(planet, sidereal_lon):
    sign_idx = int(sidereal_lon % 360 / 30)
    if planet in EXALTATION and sign_idx == EXALTATION[planet]:
        return 'Exalted'
    if planet in DEBILITATION and sign_idx == DEBILITATION[planet]:
        return 'Debilitated'
    if planet in OWN_SIGNS and sign_idx in OWN_SIGNS[planet]:
        return 'Own Sign'
    return 'Neutral'

# ── Main Calculator ───────────────────────────────────────────────────────────
def norm(x):
    return x % 360

def r(x):
    return math.radians(x)

def julian_day(year, month, day, hour_ut):
    if month <= 2:
        year -= 1; month += 12
    A = int(year/100); B = 2 - A + int(A/4)
    return int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + hour_ut/24.0 + B - 1524.5

def calc_sun_tropical(T):
    M = r(norm(357.52911 + 35999.05029*T - 0.0001537*T*T))
    C = ((1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(M) +
         (0.019993 - 0.000101*T)*math.sin(2*M) +
         0.000289*math.sin(3*M))
    return norm(280.46646 + 36000.76983*T + 0.0003032*T*T + C)

def calc_moon_tropical(T):
    D  = r(norm(297.85036 + 445267.111480*T - 0.0019142*T*T + T**3/189474))
    Ms = r(norm(357.52772 + 35999.050340*T - 0.0001603*T*T - T**3/300000))
    Mm = r(norm(134.96298 + 477198.867398*T + 0.0086972*T*T + T**3/56250))
    F  = r(norm(93.27191 + 483202.017538*T - 0.0036825*T*T + T**3/327270))
    return norm(218.3165 + 481267.8813*T +
        6.289*math.sin(Mm) + 1.274*math.sin(2*D-Mm) +
        0.658*math.sin(2*D) + 0.214*math.sin(2*Mm) -
        0.186*math.sin(Ms) - 0.114*math.sin(2*F) +
        0.059*math.sin(2*D-2*Mm) + 0.057*math.sin(2*D-Ms-Mm) +
        0.053*math.sin(2*D+Mm) + 0.046*math.sin(2*D-Ms) +
        0.041*math.sin(Mm-Ms) - 0.035*math.sin(D) -
        0.031*math.sin(Ms+Mm) - 0.015*math.sin(2*F-2*D) +
        0.011*math.sin(Mm-4*D))

def solve_kepler(M, e):
    E = float(M)
    for _ in range(100):
        dE = (M + e*math.sin(E) - E) / (1 - e*math.cos(E))
        E += dE
        if abs(dE) < 1e-10: break
    return E

def earth_pos(T):
    M = r(norm(357.52911 + 35999.05029*T - 0.0001537*T*T))
    e = 0.016708634 - 0.000042037*T
    C = ((1.914602-0.004817*T-0.000014*T*T)*math.sin(M) +
         (0.019993-0.000101*T)*math.sin(2*M) + 0.000289*math.sin(3*M))
    Ls = norm(280.46646 + 36000.76983*T + 0.0003032*T*T + C)
    le = norm(Ls+180)
    E = solve_kepler(M, e)
    re = 1.000001018*(1-e*math.cos(E))
    return le, re

def planet_lon(T, L0c,L0k,wc,wk,ec,ek,a):
    L = norm(L0k + L0c*T); w = norm(wk + wc*T)
    M = r(L-w); e = ek + ec*T
    E = solve_kepler(M, e)
    v = 2*math.atan2(math.sqrt(1+e)*math.sin(E/2), math.sqrt(1-e)*math.cos(E/2))
    lh = norm(math.degrees(v)+w)
    rp = a*(1-e*math.cos(E))
    le, re = earth_pos(T)
    dx = rp*math.cos(r(lh)) - re*math.cos(r(le))
    dy = rp*math.sin(r(lh)) - re*math.sin(r(le))
    return norm(math.degrees(math.atan2(dy,dx)))

def calc_north_node_tropical(T):
    D  = r(norm(297.85036 + 445267.111480*T))
    Ms = r(norm(357.52772 + 35999.050340*T))
    Mm = r(norm(134.96298 + 477198.867398*T))
    F  = r(norm(93.27191 + 483202.017538*T))
    mn = norm(125.0445550 - 1934.1361849*T + 0.0020762*T*T + T**3/467410)
    return norm(mn - 1.4979*math.sin(2*(D-F)) - 0.1500*math.sin(Ms)
                - 0.1226*math.sin(2*D) + 0.1176*math.sin(2*F) - 0.0801*math.sin(2*Mm))

def calc_gmst(JD):
    T = (JD-2451545.0)/36525.0
    return norm(280.46061837 + 360.98564736629*(JD-2451545.0) +
                0.000387933*T*T - T*T*T/38710000)

def calc_lagna(GMST, lng, lat, eps=23.4393):
    LST = norm(GMST+lng)
    RAMC = r(LST)
    er = r(eps); lr = r(lat)
    MC = norm(math.degrees(math.atan2(math.sin(RAMC), math.cos(RAMC)*math.cos(er))))
    num = -math.cos(RAMC)
    den = math.sin(er)*math.tan(lr) + math.cos(er)*math.sin(RAMC)
    ar = norm(math.degrees(math.atan2(num,den)))
    c1,c2 = ar, norm(ar+180)
    exp = norm(MC+90)
    ASC = c2 if abs(norm(c2-exp+180)-180) < abs(norm(c1-exp+180)-180) else c1
    return ASC, MC

def lon_to_sign(lon):
    lon = lon % 360
    idx = int(lon/30)
    return SIGNS[idx], round(lon%30, 2), idx

def calculate_vedic(year, month, day, hour, minute, utc_offset, lat, lng):
    hour_ut = hour + minute/60.0 - utc_offset
    extra = 0
    if hour_ut >= 24: hour_ut -= 24; extra = 1
    elif hour_ut < 0: hour_ut += 24; extra = -1
    
    JD = julian_day(year, month, day+extra, hour_ut)
    T  = (JD - 2451545.0) / 36525.0
    eps = 23.439291111 - 0.013004167*T
    
    # Lahiri ayanamsa
    ayanamsa = lahiri_ayanamsa(T)
    
    def to_sidereal(tropical_lon):
        return norm(tropical_lon - ayanamsa)
    
    # Tropical positions (reuse from western calc)
    trop = {
        'Sun':      calc_sun_tropical(T),
        'Moon':     calc_moon_tropical(T),
        'Mercury':  planet_lon(T,149472.6746358,252.250906,1.5564776,77.456119,-0.000059,0.20563069,0.38709927),
        'Venus':    planet_lon(T,58517.8156760,181.979801,1.4022288,131.563703,-0.000047890,0.00677323,0.72332982),
        'Mars':     planet_lon(T,19140.2993313,355.433275,1.8410449,336.060234,-0.000092064,0.09341233,1.52366231),
        'Jupiter':  planet_lon(T,3034.9056606,34.351519,1.6126,14.331289,0.000163244,0.04849485,5.20260319),
        'Saturn':   planet_lon(T,1222.1138488,50.077444,1.9637,93.057136,-0.000346641,0.05550825,9.55491150),
        'Rahu':     calc_north_node_tropical(T),  # North Node = Rahu
    }
    trop['Ketu'] = norm(trop['Rahu'] + 180)
    
    # Lagna (tropical then convert)
    GMST = calc_gmst(JD)
    trop_asc, trop_mc = calc_lagna(GMST, lng, lat, eps)
    
    # Convert all to sidereal
    sid = {p: to_sidereal(lon) for p, lon in trop.items()}
    sid_asc = to_sidereal(trop_asc)
    sid_mc  = to_sidereal(trop_mc)
    
    # Lagna sign
    lagna_sign, lagna_deg, lagna_sign_idx = lon_to_sign(sid_asc)
    
    # Whole Sign houses from Lagna
    def whole_sign_house(sid_lon):
        pidx = int(sid_lon % 360 / 30)
        return (pidx - lagna_sign_idx + 12) % 12 + 1
    
    # Assemble planets
    planets = {}
    for pname, sid_lon in sid.items():
        sign, deg, sign_idx = lon_to_sign(sid_lon)
        nak, pada, within = get_nakshatra(sid_lon)
        dignity = get_dignity(pname, sid_lon)
        house = whole_sign_house(sid_lon)
        lord = SIGN_LORDS[sign_idx]
        planets[pname] = {
            'sidereal_lon': round(sid_lon, 2),
            'sign': sign,
            'degree': round(deg, 2),
            'sign_idx': sign_idx,
            'sign_lord': lord,
            'house': house,
            'nakshatra': nak['name'],
            'nakshatra_ruler': nak['ruler'],
            'nakshatra_deity': nak['deity'],
            'nakshatra_symbol': nak['symbol'],
            'pada': pada,
            'dignity': dignity,
        }
    
    # Moon nakshatra detail (most important)
    moon_nak, moon_pada, moon_within = get_nakshatra(sid['Moon'])
    
    # Vimshottari dasha from Moon nakshatra
    from datetime import date
    dashas, birth_ruler, remaining_first = vimshottari_dasha(sid['Moon'], year, month, day)
    
    # Current age (approximate)
    today = date.today()
    current_age = (today.year - year) + (today.month - month)/12.0
    curr_dasha = current_dasha(dashas, current_age)
    
    return {
        'ayanamsa': round(ayanamsa, 4),
        'lagna': {'sign': lagna_sign, 'degree': round(lagna_deg, 2), 'sign_idx': lagna_sign_idx, 'lord': SIGN_LORDS[lagna_sign_idx]},
        'mc': {'sign': lon_to_sign(sid_mc)[0], 'degree': round(lon_to_sign(sid_mc)[1], 2)},
        'planets': planets,
        'moon_nakshatra': {
            'name': moon_nak['name'],
            'ruler': moon_nak['ruler'],
            'deity': moon_nak['deity'],
            'symbol': moon_nak['symbol'],
            'pada': moon_pada,
            'within_degrees': round(moon_within, 2),
        },
        'dashas': dashas,
        'birth_dasha_ruler': birth_ruler,
        'current_dasha': curr_dasha,
        'current_age': round(current_age, 1),
    }

def format_vedic(v):
    lines = []
    lines.append('\n' + '='*60)
    lines.append('  VEDIC (JYOTISH) CHART')
    lines.append(f"  Lahiri Ayanamsa: {v['ayanamsa']}°")
    lines.append('='*60)
    
    lines.append(f"\nLAGNA (Rising): {v['lagna']['degree']}° {v['lagna']['sign']} — Lord: {v['lagna']['lord']}")
    lines.append(f"MC (sidereal):  {v['mc']['degree']}° {v['mc']['sign']}")
    
    lines.append(f"\n{'PLANET':<12} {'SIGN':<14} {'DEG':>6}  {'HOUSE':>5}  {'NAKSHATRA':<20} {'PADA':>4}  {'DIGNITY':<12}  {'RULER'}")
    lines.append('-'*95)
    
    planet_order = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Rahu','Ketu']
    for pname in planet_order:
        if pname not in v['planets']: continue
        p = v['planets'][pname]
        lines.append(
            f"{pname:<12} {p['sign']:<14} {p['degree']:>6.2f}  {p['house']:>5}  "
            f"{p['nakshatra']:<20} {p['pada']:>4}  {p['dignity']:<12}  {p['nakshatra_ruler']}"
        )
    
    lines.append('\n' + '-'*60)
    mn = v['moon_nakshatra']
    lines.append(f"MOON NAKSHATRA DETAIL: {mn['name']} (Pada {mn['pada']})")
    lines.append(f"  Ruler:  {mn['ruler']}")
    lines.append(f"  Deity:  {mn['deity']}")
    lines.append(f"  Symbol: {mn['symbol']}")
    lines.append(f"  Degrees within nakshatra: {mn['within_degrees']:.2f}° of 13.33°")
    
    lines.append(f"\nVIMSHOTTARI DASHA SEQUENCE (birth ruler: {v['birth_dasha_ruler']}):")
    lines.append(f"{'DASHA':<12} {'START AGE':>10}  {'END AGE':>8}  {'START YEAR':>10}  {'END YEAR':>8}  YEARS")
    lines.append('-'*65)
    cd = v['current_dasha']
    for d in v['dashas']:
        marker = ' ◄ NOW' if d['planet'] == cd['planet'] and abs(d['start_age'] - cd['start_age']) < 0.1 else ''
        if d['end_age'] < -1: continue  # skip fully pre-birth
        if d['start_year'] > 2100: break
        lines.append(
            f"{d['planet']:<12} {d['start_age']:>10.1f}  {d['end_age']:>8.1f}  "
            f"{d['start_year']:>10.1f}  {d['end_year']:>8.1f}  {d['years']:.1f}{marker}"
        )
    
    lines.append(f"\nCURRENT DASHA (age {v['current_age']}): {cd['planet']} mahadasha")
    lines.append(f"  Runs until age {cd['end_age']:.1f} (~{cd['end_year']:.1f})")
    lines.append('='*60 + '\n')
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',  type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day',   type=int, required=True)
    parser.add_argument('--hour',  type=int, required=True)
    parser.add_argument('--minute',type=int, default=0)
    parser.add_argument('--utc_offset', type=float, required=True)
    parser.add_argument('--lat',   type=float, required=True)
    parser.add_argument('--lng',   type=float, required=True)
    args = parser.parse_args()
    
    v = calculate_vedic(args.year, args.month, args.day, args.hour, args.minute,
                        args.utc_offset, args.lat, args.lng)
    print(format_vedic(v))

if __name__ == '__main__':
    main()
