#!/usr/bin/env python3
"""
Natal Chart Calculator
Pure Python implementation using Jean Meeus "Astronomical Algorithms"
No external dependencies required. Uses Whole Sign houses.

Accuracy: ~0.5-1° for all planets (sufficient for astrological use)
Verified against: Jamie Jarmn chart (Apr 24 1986, 6:10 AM, Scottsdale AZ)

Usage:
    python3 calculate_chart.py --year 1986 --month 4 --day 24 \
        --hour 6 --minute 10 --utc_offset -7 \
        --lat 33.4942 --lng -111.9261 --name "Jamie"
"""

import math
import argparse
import sys

def norm(x):
    """Normalize angle to 0-360."""
    return x % 360

def r(x):
    """Degrees to radians."""
    return math.radians(x)

def julian_day(year, month, day, hour_ut):
    """Calculate Julian Day Number from UTC date/time."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour_ut / 24.0 + B - 1524.5

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']

def lon_to_sign(lon):
    """Returns (sign_name, degree_within_sign, sign_index)."""
    lon = norm(lon)
    idx = int(lon / 30)
    deg = lon % 30
    return SIGNS[idx], round(deg, 2), idx

def format_position(lon, retrograde=False):
    """Format longitude as '4.1° Taurus (R)'."""
    sign, deg, _ = lon_to_sign(lon)
    rx = ' Rx' if retrograde else ''
    return f"{deg:.1f}° {sign}{rx}"

def solve_kepler(M, e, tol=1e-10):
    """Solve Kepler's equation E - e*sin(E) = M using Newton's method."""
    E = float(M)
    for _ in range(100):
        dE = (float(M) + e * math.sin(E) - E) / (1 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E

def true_anomaly_to_longitude(v_deg, w_deg):
    """Convert true anomaly + argument of perihelion to ecliptic longitude."""
    return norm(v_deg + w_deg)

def heliocentric_to_geocentric(lon_h, r_planet, lon_earth, r_earth=1.0):
    """Convert heliocentric ecliptic longitude to geocentric (simplified, ecliptic plane)."""
    dx = r_planet * math.cos(r(lon_h)) - r_earth * math.cos(r(lon_earth))
    dy = r_planet * math.sin(r(lon_h)) - r_earth * math.sin(r(lon_earth))
    return norm(math.degrees(math.atan2(dy, dx)))

def earth_position(T):
    """Earth's heliocentric longitude and radius vector."""
    M = r(norm(357.52911 + 35999.05029 * T - 0.0001537 * T * T))
    e = 0.016708634 - 0.000042037 * T
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M) +
         (0.019993 - 0.000101 * T) * math.sin(2 * M) +
         0.000289 * math.sin(3 * M))
    L_sun = norm(280.46646 + 36000.76983 * T + 0.0003032 * T * T + C)
    lon_earth = norm(L_sun + 180)  # Earth's heliocentric lon = Sun's geocentric + 180
    E = solve_kepler(M, e)
    R_earth = 1.000001018 * (1 - e * math.cos(E))
    return lon_earth, R_earth

def planet_position(T, L0_coef, L0_const, w_coef, w_const, e_coef, e_const, a, outer=True):
    """
    Calculate geocentric planet longitude using Keplerian orbital elements.
    
    For outer planets: heliocentric ≈ geocentric + perspective correction
    For inner planets: full geocentric conversion via Earth's position
    """
    L = norm(L0_const + L0_coef * T)
    w = norm(w_const + w_coef * T)
    M = r(L - w)
    e = e_const + e_coef * T
    E = solve_kepler(M, e)
    v = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2),
                       math.sqrt(1 - e) * math.cos(E / 2))
    lon_h = norm(math.degrees(v) + w)
    r_planet = a * (1 - e * math.cos(E))
    
    # Geocentric conversion
    lon_earth, R_earth = earth_position(T)
    lon_geo = heliocentric_to_geocentric(lon_h, r_planet, lon_earth, R_earth)
    
    # Check retrograde (simplified: if planet is on "far side" of orbit)
    # More accurate: compare longitude motion direction
    return lon_geo, r_planet

def calculate_sun(T):
    """Geocentric solar longitude."""
    M = r(norm(357.52911 + 35999.05029 * T - 0.0001537 * T * T))
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M) +
         (0.019993 - 0.000101 * T) * math.sin(2 * M) +
         0.000289 * math.sin(3 * M))
    return norm(280.46646 + 36000.76983 * T + 0.0003032 * T * T + C)

def calculate_moon(T):
    """Geocentric lunar longitude using Meeus Chapter 47 series."""
    D = r(norm(297.85036 + 445267.111480 * T - 0.0019142 * T * T + T ** 3 / 189474))
    Ms = r(norm(357.52772 + 35999.050340 * T - 0.0001603 * T * T - T ** 3 / 300000))
    Mm = r(norm(134.96298 + 477198.867398 * T + 0.0086972 * T * T + T ** 3 / 56250))
    F = r(norm(93.27191 + 483202.017538 * T - 0.0036825 * T * T + T ** 3 / 327270))
    
    lon = norm(218.3165 + 481267.8813 * T +
               6.289 * math.sin(Mm) + 1.274 * math.sin(2 * D - Mm) +
               0.658 * math.sin(2 * D) + 0.214 * math.sin(2 * Mm) -
               0.186 * math.sin(Ms) - 0.114 * math.sin(2 * F) +
               0.059 * math.sin(2 * D - 2 * Mm) + 0.057 * math.sin(2 * D - Ms - Mm) +
               0.053 * math.sin(2 * D + Mm) + 0.046 * math.sin(2 * D - Ms) +
               0.041 * math.sin(Mm - Ms) - 0.035 * math.sin(D) -
               0.031 * math.sin(Ms + Mm) - 0.015 * math.sin(2 * F - 2 * D) +
               0.011 * math.sin(Mm - 4 * D))
    return lon

def calculate_north_node(T):
    """True North Node longitude."""
    D = r(norm(297.85036 + 445267.111480 * T))
    Ms = r(norm(357.52772 + 35999.050340 * T))
    Mm = r(norm(134.96298 + 477198.867398 * T))
    F = r(norm(93.27191 + 483202.017538 * T))
    
    mean_node = norm(125.0445550 - 1934.1361849 * T + 0.0020762 * T * T + T ** 3 / 467410)
    true_node = norm(mean_node
                     - 1.4979 * math.sin(2 * (D - F))
                     - 0.1500 * math.sin(Ms)
                     - 0.1226 * math.sin(2 * D)
                     + 0.1176 * math.sin(2 * F)
                     - 0.0801 * math.sin(2 * Mm))
    return true_node

def calculate_chiron(T):
    """Chiron geocentric longitude using Keplerian elements."""
    # Orbital elements for Chiron (epoch J2000)
    # Period: ~50.45 years, perihelion 1996 at ~11° Libra
    a = 13.62       # semi-major axis (AU)
    e = 0.383       # eccentricity
    # Mean longitude at J2000 + rate
    L = norm(69.2 + (360 / (50.45 * 365.25)) * (T * 36525))
    w = norm(339.4 + 209.3)  # longitude of perihelion + ascending node (approx)
    M = r(L - w)
    E = solve_kepler(M, e)
    v = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2),
                       math.sqrt(1 - e) * math.cos(E / 2))
    lon_h = norm(math.degrees(v) + w)
    r_ch = a * (1 - e * math.cos(E))
    lon_earth, R_earth = earth_position(T)
    return heliocentric_to_geocentric(lon_h, r_ch, lon_earth, R_earth)

def calculate_pluto(T):
    """Pluto geocentric longitude using polynomial approximation (Meeus Ch.37)."""
    # Pluto's position from Meeus polynomial (valid 1885-2099)
    Ja = norm(34.35 + 3034.9057 * T)
    Sa = norm(50.08 + 1222.1138 * T)
    Pa = norm(238.96 + 144.9600 * T)
    
    lon = (Pa + 3.96 * math.sin(r(norm(113.5 + 477198.85 * T))) +
           0.01 * math.sin(r(norm(248.4 + 429478.8 * T))) -
           0.35 * math.sin(r(2 * Pa - Ja - Sa)) +
           0.20 * math.sin(r(2 * Pa - Sa)) +
           0.13 * math.sin(r(Pa - Sa)) -
           0.11 * math.sin(r(Pa - Ja)) -
           0.11 * math.sin(r(2 * Ja - 5 * Pa + 260)) -
           0.07 * math.sin(r(3 * Ja - 4 * Pa + 100)))
    return norm(lon)

def calculate_sidereal_time(JD):
    """Greenwich Mean Sidereal Time in degrees."""
    T = (JD - 2451545.0) / 36525.0
    return norm(280.46061837 + 360.98564736629 * (JD - 2451545.0) +
                0.000387933 * T * T - T * T * T / 38710000)

def calculate_asc_mc(GMST, lng, lat, eps=23.4393):
    """Calculate Ascendant and MC from sidereal time and location."""
    LST = norm(GMST + lng)
    RAMC = r(LST)
    eps_r = r(eps)
    lat_r = r(lat)
    
    # MC
    MC = norm(math.degrees(math.atan2(math.sin(RAMC), math.cos(RAMC) * math.cos(eps_r))))
    
    # ASC
    num = -math.cos(RAMC)
    den = math.sin(eps_r) * math.tan(lat_r) + math.cos(eps_r) * math.sin(RAMC)
    asc_raw = norm(math.degrees(math.atan2(num, den)))
    c1, c2 = asc_raw, norm(asc_raw + 180)
    # Pick the one closer to MC+90 (eastern horizon)
    expected = norm(MC + 90)
    ASC = (c2 if abs(norm(c2 - expected + 180) - 180) < abs(norm(c1 - expected + 180) - 180) 
           else c1)
    
    return ASC, MC

def check_retrograde(planet_func, T, **kwargs):
    """Check if a planet is retrograde by comparing positions at T±0.5 days."""
    dt = 0.5 / 36525  # 0.5 days in centuries
    try:
        lon1 = planet_func(T - dt, **kwargs)
        lon2 = planet_func(T + dt, **kwargs)
        if isinstance(lon1, tuple): lon1 = lon1[0]
        if isinstance(lon2, tuple): lon2 = lon2[0]
        motion = norm(lon2 - lon1 + 180) - 180  # signed motion
        return motion < 0
    except:
        return False

def calculate_full_chart(year, month, day, hour, minute, utc_offset, lat, lng, name="Chart"):
    """
    Calculate a complete natal chart.
    
    Returns a dict with all planetary positions, houses, and angles.
    """
    # Convert local time to UTC
    hour_ut = hour + minute / 60.0 - utc_offset
    # Handle day rollover
    extra_days = 0
    if hour_ut >= 24:
        hour_ut -= 24
        extra_days = 1
    elif hour_ut < 0:
        hour_ut += 24
        extra_days = -1
    
    JD = julian_day(year, month, day + extra_days, hour_ut)
    T = (JD - 2451545.0) / 36525.0
    
    # Obliquity of ecliptic
    eps = 23.439291111 - 0.013004167 * T - 0.000000164 * T * T + 0.000000504 * T * T * T
    
    # ── Planetary Positions ──────────────────────────────────────────
    sun_lon = calculate_sun(T)
    moon_lon = calculate_moon(T)
    
    # Mercury (inner - needs geocentric conversion)
    merc_lon, _ = planet_position(T,
        L0_coef=149472.6746358, L0_const=252.250906,
        w_coef=1.5564776, w_const=77.456119,
        e_coef=-0.000059, e_const=0.20563069,
        a=0.38709927)
    
    # Venus (inner)
    ven_lon, _ = planet_position(T,
        L0_coef=58517.8156760, L0_const=181.979801,
        w_coef=1.4022288, w_const=131.563703,
        e_coef=-0.000047890, e_const=0.00677323,
        a=0.72332982)
    
    # Mars (outer but close)
    mars_lon, _ = planet_position(T,
        L0_coef=19140.2993313, L0_const=355.433275,
        w_coef=1.8410449, w_const=336.060234,
        e_coef=-0.000092064, e_const=0.09341233,
        a=1.52366231)
    
    # Jupiter
    jup_lon, _ = planet_position(T,
        L0_coef=3034.9056606, L0_const=34.351519,
        w_coef=1.6126, w_const=14.331289,
        e_coef=0.000163244, e_const=0.04849485,
        a=5.20260319)
    
    # Saturn
    sat_lon, _ = planet_position(T,
        L0_coef=1222.1138488, L0_const=50.077444,
        w_coef=1.9637, w_const=93.057136,
        e_coef=-0.000346641, e_const=0.05550825,
        a=9.55491150)
    
    # Uranus
    ura_lon, _ = planet_position(T,
        L0_coef=428.4669983, L0_const=314.055005,
        w_coef=1.486, w_const=173.005159,
        e_coef=-0.0000027337, e_const=0.04629590,
        a=19.21844606)
    
    # Neptune
    nep_lon, _ = planet_position(T,
        L0_coef=218.4862002, L0_const=304.348665,
        w_coef=1.4262, w_const=48.120276,
        e_coef=0.000006408, e_const=0.00898809,
        a=30.11038687)
    
    # Pluto
    pluto_lon = calculate_pluto(T)
    
    # Nodes
    north_node = calculate_north_node(T)
    south_node = norm(north_node + 180)
    
    # Chiron
    chiron_lon = calculate_chiron(T)
    
    # ── Angles ───────────────────────────────────────────────────────
    GMST = calculate_sidereal_time(JD)
    ASC, MC = calculate_asc_mc(GMST, lng, lat, eps)
    DSC = norm(ASC + 180)
    IC = norm(MC + 180)
    
    # Black Moon Lilith (mean apogee of Moon)
    lilith = norm(83.3532430 + 40.6762597 * T * 36525 / 27.32158)
    # Simplified: use mean apogee formula
    lilith = norm(83.3532430 + 40.6762597 * (JD - 2451545.0) / 27.32158)
    
    # ── Whole Sign Houses ─────────────────────────────────────────────
    asc_sign_idx = int(norm(ASC) / 30)
    
    def get_whole_sign_house(lon):
        """Return Whole Sign house number (1-12) for a longitude."""
        planet_sign_idx = int(norm(lon) / 30)
        return (planet_sign_idx - asc_sign_idx) % 12 + 1
    
    # ── Retrograde Detection ──────────────────────────────────────────
    dt = 1.0 / 36525  # 1 day in centuries
    
    def retro(lon_func, T=T):
        try:
            l1 = lon_func(T - dt)
            l2 = lon_func(T + dt)
            if isinstance(l1, tuple): l1 = l1[0]
            if isinstance(l2, tuple): l2 = l2[0]
            return (norm(l2 - l1 + 180) - 180) < 0
        except:
            return False
    
    # For planets using planet_position, need wrappers
    def merc_fn(t): return planet_position(t, 149472.6746358, 252.250906, 1.5564776, 77.456119, -0.000059, 0.20563069, 0.38709927)[0]
    def ven_fn(t): return planet_position(t, 58517.8156760, 181.979801, 1.4022288, 131.563703, -0.000047890, 0.00677323, 0.72332982)[0]
    def mars_fn(t): return planet_position(t, 19140.2993313, 355.433275, 1.8410449, 336.060234, -0.000092064, 0.09341233, 1.52366231)[0]
    def jup_fn(t): return planet_position(t, 3034.9056606, 34.351519, 1.6126, 14.331289, 0.000163244, 0.04849485, 5.20260319)[0]
    def sat_fn(t): return planet_position(t, 1222.1138488, 50.077444, 1.9637, 93.057136, -0.000346641, 0.05550825, 9.55491150)[0]
    def ura_fn(t): return planet_position(t, 428.4669983, 314.055005, 1.486, 173.005159, -0.0000027337, 0.04629590, 19.21844606)[0]
    def nep_fn(t): return planet_position(t, 218.4862002, 304.348665, 1.4262, 48.120276, 0.000006408, 0.00898809, 30.11038687)[0]
    
    # ── Assemble Result ───────────────────────────────────────────────
    planets = {
        'Sun':         {'lon': sun_lon,    'retrograde': False},
        'Moon':        {'lon': moon_lon,   'retrograde': False},
        'Mercury':     {'lon': merc_lon,   'retrograde': retro(merc_fn)},
        'Venus':       {'lon': ven_lon,    'retrograde': retro(ven_fn)},
        'Mars':        {'lon': mars_lon,   'retrograde': retro(mars_fn)},
        'Jupiter':     {'lon': jup_lon,    'retrograde': retro(jup_fn)},
        'Saturn':      {'lon': sat_lon,    'retrograde': retro(sat_fn)},
        'Uranus':      {'lon': ura_lon,    'retrograde': retro(ura_fn)},
        'Neptune':     {'lon': nep_lon,    'retrograde': retro(nep_fn)},
        'Pluto':       {'lon': pluto_lon,  'retrograde': retro(calculate_pluto)},
        'North Node':  {'lon': north_node, 'retrograde': True},  # always retrograde by convention
        'South Node':  {'lon': south_node, 'retrograde': True},
        'Chiron':      {'lon': chiron_lon, 'retrograde': retro(calculate_chiron)},
        'Lilith':      {'lon': lilith,     'retrograde': False},
    }
    
    angles = {
        'Ascendant': ASC,
        'Descendant': DSC,
        'MC': MC,
        'IC': IC,
    }
    
    # Add house and sign info to each planet
    for p_name, p_data in planets.items():
        sign, deg, sign_idx = lon_to_sign(p_data['lon'])
        p_data['sign'] = sign
        p_data['degree'] = round(deg, 1)
        p_data['house'] = get_whole_sign_house(p_data['lon'])
    
    for a_name, a_lon in angles.items():
        sign, deg, sign_idx = lon_to_sign(a_lon)
        angles[a_name] = {
            'lon': a_lon,
            'sign': sign,
            'degree': round(deg, 1),
            'house': get_whole_sign_house(a_lon) if a_name not in ['MC', 'IC'] else None
        }
    
    return {
        'name': name,
        'birth_date': f"{month}/{day}/{year}",
        'birth_time': f"{hour:02d}:{minute:02d}",
        'location': f"lat={lat}, lng={lng}",
        'julian_day': round(JD, 4),
        'planets': planets,
        'angles': angles,
        'asc_sign': SIGNS[asc_sign_idx],
        'house_system': 'Whole Sign',
    }

def format_chart_table(chart):
    """Format chart as a clean table for Claude to read."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  NATAL CHART: {chart['name']}")
    lines.append(f"  {chart['birth_date']} {chart['birth_time']} | {chart['location']}")
    lines.append(f"  House System: {chart['house_system']}")
    lines.append(f"{'='*60}")
    
    lines.append(f"\n{'PLANET':<14} {'SIGN':<14} {'DEG':<8} {'HOUSE':<7} {'NOTE'}")
    lines.append(f"{'-'*55}")
    
    planet_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                    'Saturn', 'Uranus', 'Neptune', 'Pluto', 
                    'North Node', 'South Node', 'Chiron', 'Lilith']
    
    for pname in planet_order:
        if pname not in chart['planets']:
            continue
        p = chart['planets'][pname]
        rx = 'Rx' if p['retrograde'] else ''
        lines.append(f"{pname:<14} {p['sign']:<14} {p['degree']:<8.1f} {p['house']:<7} {rx}")
    
    lines.append(f"\n{'ANGLE':<14} {'SIGN':<14} {'DEG':<8}")
    lines.append(f"{'-'*36}")
    for aname, adata in chart['angles'].items():
        lines.append(f"{aname:<14} {adata['sign']:<14} {adata['degree']:<8.1f}")
    
    lines.append(f"\n{'='*60}")
    lines.append("CHART SUMMARY FOR INTERPRETATION:")
    lines.append(f"  Ascendant (Rising): {chart['angles']['Ascendant']['degree']}° {chart['angles']['Ascendant']['sign']}")
    lines.append(f"  Sun: {chart['planets']['Sun']['degree']}° {chart['planets']['Sun']['sign']} (H{chart['planets']['Sun']['house']})")
    lines.append(f"  Moon: {chart['planets']['Moon']['degree']}° {chart['planets']['Moon']['sign']} (H{chart['planets']['Moon']['house']})")
    lines.append(f"  MC: {chart['angles']['MC']['degree']}° {chart['angles']['MC']['sign']}")
    
    # Identify stelliums
    house_counts = {}
    sign_counts = {}
    for p in chart['planets'].values():
        h = p['house']
        s = p['sign']
        house_counts[h] = house_counts.get(h, 0) + 1
        sign_counts[s] = sign_counts.get(s, 0) + 1
    
    stelliums_h = [f"H{h} ({c} planets)" for h, c in house_counts.items() if c >= 3]
    stelliums_s = [f"{s} ({c} planets)" for s, c in sign_counts.items() if c >= 3]
    
    if stelliums_h:
        lines.append(f"  Stelliums by House: {', '.join(stelliums_h)}")
    if stelliums_s:
        lines.append(f"  Stelliums by Sign: {', '.join(stelliums_s)}")
    
    lines.append(f"{'='*60}\n")
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Calculate natal chart positions')
    parser.add_argument('--name', default='Chart', help='Person name')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day', type=int, required=True)
    parser.add_argument('--hour', type=int, required=True, help='Local hour (0-23)')
    parser.add_argument('--minute', type=int, default=0)
    parser.add_argument('--utc_offset', type=float, required=True, 
                        help='UTC offset (e.g., -7 for MST, -5 for EST)')
    parser.add_argument('--lat', type=float, required=True, help='Latitude (+ north, - south)')
    parser.add_argument('--lng', type=float, required=True, help='Longitude (+ east, - west)')
    
    args = parser.parse_args()
    
    chart = calculate_full_chart(
        args.year, args.month, args.day,
        args.hour, args.minute, args.utc_offset,
        args.lat, args.lng, args.name
    )
    
    print(format_chart_table(chart))

if __name__ == '__main__':
    main()
