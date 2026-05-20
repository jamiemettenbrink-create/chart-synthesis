#!/usr/bin/env python3
"""
BaZi (Four Pillars of Destiny) Calculator
Implements full Heavenly Stems + Earthly Branches for Year, Month, Day, Hour pillars.
Calculates: Day Master, element balance, clashes, combinations, penalties, hidden stems.

Usage:
    python3 calculate_bazi.py --year 1986 --month 4 --day 24 --hour 6 --minute 10 --utc_offset -7

Reference: Traditional Chinese calendar system (Hsia calendar).
Solar terms used for month pillars (li chun = start of year, not lunar new year).
"""

import math
import argparse
from datetime import datetime, timedelta

# ── Heavenly Stems (天干) ─────────────────────────────────────────────────────
STEMS = ['Jiǎ','Yǐ','Bǐng','Dīng','Wù','Jǐ','Gēng','Xīn','Rén','Guǐ']
STEM_ELEMENT = ['Wood','Wood','Fire','Fire','Earth','Earth','Metal','Metal','Water','Water']
STEM_POLARITY = ['Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin']

# ── Earthly Branches (地支) ───────────────────────────────────────────────────
BRANCHES = ['Zǐ','Chǒu','Yín','Mǎo','Chén','Sì','Wǔ','Wèi','Shēn','Yǒu','Xū','Hài']
BRANCH_ELEMENT = ['Water','Earth','Wood','Wood','Earth','Fire','Fire','Earth','Metal','Metal','Earth','Water']
BRANCH_POLARITY = ['Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin']
BRANCH_ANIMAL  = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig']

# Hidden stems within each branch (primary, secondary, tertiary)
HIDDEN_STEMS = {
    'Zǐ':  ['Guǐ'],
    'Chǒu': ['Jǐ','Guǐ','Xīn'],
    'Yín':  ['Bǐng','Jiǎ','Wù'],
    'Mǎo':  ['Yǐ'],
    'Chén': ['Wù','Yǐ','Guǐ'],
    'Sì':   ['Bǐng','Wù','Gēng'],
    'Wǔ':   ['Dīng','Jǐ'],
    'Wèi':  ['Jǐ','Dīng','Yǐ'],
    'Shēn': ['Gēng','Rén','Wù'],
    'Yǒu':  ['Xīn'],
    'Xū':   ['Wù','Xīn','Dīng'],
    'Hài':  ['Rén','Jiǎ'],
}

# ── Six Clashes (六冲) ────────────────────────────────────────────────────────
# Each branch clashes with the one 6 positions away
BRANCH_CLASHES = {
    'Zǐ':'Wǔ','Wǔ':'Zǐ',
    'Chǒu':'Wèi','Wèi':'Chǒu',
    'Yín':'Shēn','Shēn':'Yín',
    'Mǎo':'Yǒu','Yǒu':'Mǎo',
    'Chén':'Xū','Xū':'Chén',
    'Sì':'Hài','Hài':'Sì',
}

# ── Three Harmony Combinations (三合) ─────────────────────────────────────────
THREE_HARMONY = [
    (['Shēn','Zǐ','Chén'], 'Water'),
    (['Hài','Mǎo','Wèi'], 'Wood'),
    (['Yín','Wǔ','Xū'], 'Fire'),
    (['Sì','Yǒu','Chǒu'], 'Metal'),
]

# ── Six Combinations (六合) ───────────────────────────────────────────────────
SIX_COMBINATIONS = [
    ('Zǐ','Chǒu','Earth'),
    ('Yín','Hài','Wood'),
    ('Mǎo','Xū','Fire'),
    ('Chén','Yǒu','Metal'),
    ('Sì','Shēn','Water'),
    ('Wǔ','Wèi','Fire'),  # some traditions say Earth
]

# ── Self-Penalty Branches ─────────────────────────────────────────────────────
SELF_PENALTIES = ['Zǐ','Wǔ','Yǒu','Hài']  # appear twice = self-penalty

# ── Stem Combinations (天干合) ────────────────────────────────────────────────
STEM_COMBINATIONS = [
    ('Jiǎ','Jǐ','Earth'),
    ('Yǐ','Gēng','Metal'),
    ('Bǐng','Xīn','Water'),
    ('Dīng','Rén','Wood'),
    ('Wù','Guǐ','Fire'),
]

# ── Elements: production and control cycles ───────────────────────────────────
PRODUCES = {'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
CONTROLS = {'Wood':'Earth','Earth':'Water','Water':'Fire','Fire':'Metal','Metal':'Wood'}
PRODUCED_BY = {v:k for k,v in PRODUCES.items()}
CONTROLLED_BY = {v:k for k,v in CONTROLS.items()}

# ── Solar Terms for Month Stems/Branches ─────────────────────────────────────
# Month branch is determined by solar term (not lunar month)
# Month 1 (Yín/Tiger) starts at Li Chun ~Feb 4
# We use approximate solar longitude for the 12 months
MONTH_SOLAR_LONGITUDE = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
# Month branch index (0=Yín for month 1, cycling)
# Yín=2 in BRANCHES, so month 1 branch index = 2

def julian_day(year, month, day, hour_ut=12.0):
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + hour_ut/24.0 + B - 1524.5

def sun_longitude(jd):
    """Approximate geocentric solar longitude (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    M = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360
    M_r = math.radians(M)
    C = ((1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(M_r) +
         (0.019993 - 0.000101*T)*math.sin(2*M_r) +
         0.000289*math.sin(3*M_r))
    return (280.46646 + 36000.76983*T + 0.0003032*T*T + C) % 360

def get_solar_month(year, month, day, hour_ut):
    """
    Determine the Chinese solar month (1-12) based on solar longitude.
    Month 1 (Yín) begins when sun enters 315° (approx Feb 4).
    Returns month index 0-11 where 0=Yín.
    """
    jd = julian_day(year, month, day, hour_ut)
    sun_lon = sun_longitude(jd)
    # Solar month starts at: 315, 345, 15, 45, ... (every 30°)
    # Find which 30° segment we're in, offset so 315° = month 0
    adjusted = (sun_lon - 315 + 360) % 360
    return int(adjusted / 30)

def year_pillar(year, month, day, hour_ut):
    """
    Year pillar changes at Li Chun (~Feb 4), not Jan 1 or lunar new year.
    Returns (stem_idx, branch_idx).
    """
    jd = julian_day(year, month, day, hour_ut)
    sun_lon = sun_longitude(jd)
    # Li Chun = sun at 315°. Before that in the year = previous year's pillar.
    # Determine the BaZi year
    adjusted = (sun_lon - 315 + 360) % 360
    if adjusted >= 360:  # just past Li Chun
        bazi_year = year
    else:
        # Check if we're before Li Chun this calendar year
        # Li Chun is ~Feb 4; if month<2 or (month==2 and day<4), use prev year
        li_chun_approx = 35  # roughly day 35 of year
        day_of_year = sum([31,28,31,30,31,30,31,31,30,31,30,31][:month-1]) + day
        if day_of_year < li_chun_approx:
            bazi_year = year - 1
        else:
            bazi_year = year
    
    # Year stem: (year - 4) % 10, Year branch: (year - 4) % 12
    stem_idx = (bazi_year - 4) % 10
    branch_idx = (bazi_year - 4) % 12
    return stem_idx, branch_idx

def month_pillar(solar_month_idx, year_stem_idx):
    """
    Month branch is fixed: solar month 0 = Yín (branch index 2).
    Month stem depends on year stem (5-year cycle).
    """
    branch_idx = (solar_month_idx + 2) % 12  # month 0=Yín=branch 2
    
    # Month stem formula: based on year stem group
    # Year stems 0,5 (Jiǎ/Jǐ): month 1 starts at Bǐng (stem 2)
    # Year stems 1,6 (Yǐ/Gēng): month 1 starts at Wù (stem 4)
    # Year stems 2,7 (Bǐng/Xīn): month 1 starts at Gēng (stem 6)
    # Year stems 3,8 (Dīng/Rén): month 1 starts at Rén (stem 8)
    # Year stems 4,9 (Wù/Guǐ): month 1 starts at Jiǎ (stem 0)
    month1_stems = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    start_stem = month1_stems[year_stem_idx]
    stem_idx = (start_stem + solar_month_idx) % 10
    return stem_idx, branch_idx

def day_pillar(year, month, day, hour_ut):
    """
    Day pillar using JD-based formula.
    Day changes at midnight local time (we use UTC hour).
    """
    jd = int(julian_day(year, month, day, hour_ut) + 0.5)
    # Day stem: (JD + 9) % 10 (calibrated to known dates)
    # Day branch: (JD + 11) % 12
    stem_idx = (jd + 9) % 10
    branch_idx = (jd + 11) % 12
    return stem_idx, branch_idx

def hour_pillar(hour, day_stem_idx):
    """
    Hour branch: 2-hour segments starting at Zǐ (23:00-01:00).
    Hour stem depends on day stem.
    """
    # Hour branch: Zǐ=23-1, Chǒu=1-3, Yín=3-5, Mǎo=5-7, Chén=7-9,
    # Sì=9-11, Wǔ=11-13, Wèi=13-15, Shēn=15-17, Yǒu=17-19, Xū=19-21, Hài=21-23
    if hour == 23 or hour == 0:
        branch_idx = 0  # Zǐ
    else:
        branch_idx = (hour + 1) // 2
    
    # Hour stem: based on day stem group (same pattern as month stems)
    hour1_stems = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]  # Jiǎ/Jǐ day starts at Jiǎ hour
    start_stem = hour1_stems[day_stem_idx]
    stem_idx = (start_stem + branch_idx) % 10
    return stem_idx, branch_idx

def element_analysis(pillars):
    """Count elements across all stems and branches."""
    counts = {'Wood':0,'Fire':0,'Earth':0,'Metal':0,'Water':0}
    for p in pillars:
        s_idx, b_idx = p['stem_idx'], p['branch_idx']
        counts[STEM_ELEMENT[s_idx]] += 1
        counts[BRANCH_ELEMENT[b_idx]] += 1
        # Hidden stems (weighted at 0.5 each)
        branch_name = BRANCHES[b_idx]
        for hs in HIDDEN_STEMS.get(branch_name, []):
            hs_idx = STEMS.index(hs)
            counts[STEM_ELEMENT[hs_idx]] += 0.5
    return counts

def find_clashes(branches):
    """Find clash pairs among the four pillars."""
    clashes = []
    branch_names = [BRANCHES[b] for b in branches]
    for i in range(len(branch_names)):
        for j in range(i+1, len(branch_names)):
            if BRANCH_CLASHES.get(branch_names[i]) == branch_names[j]:
                clashes.append((branch_names[i], branch_names[j]))
    return clashes

def find_combinations(branches):
    """Find three-harmony and six-combination groups."""
    found = []
    branch_names = set(BRANCHES[b] for b in branches)
    # Three harmony
    for combo, element in THREE_HARMONY:
        present = [b for b in combo if b in branch_names]
        if len(present) >= 2:
            found.append({'type':'Three Harmony', 'branches':present, 'forms':element, 'complete': len(present)==3})
    # Six combinations
    for b1, b2, element in SIX_COMBINATIONS:
        if b1 in branch_names and b2 in branch_names:
            found.append({'type':'Six Combination', 'branches':[b1,b2], 'forms':element, 'complete':True})
    return found

def find_stem_combinations(stems):
    """Find stem combination pairs."""
    found = []
    stem_names = [STEMS[s] for s in stems]
    for s1, s2, element in STEM_COMBINATIONS:
        if s1 in stem_names and s2 in stem_names:
            found.append({'stems':[s1,s2], 'forms':element})
    return found

def day_master_relationships(day_stem_idx, all_stems, all_branches):
    """
    Analyze what the chart does to/for the Day Master.
    Returns: resource, output, wealth, power, companion counts.
    """
    dm_element = STEM_ELEMENT[day_stem_idx]
    dm_polarity = STEM_POLARITY[day_stem_idx]
    
    counts = {'resource':0, 'output':0, 'wealth':0, 'power':0, 'companion':0}
    
    all_elements = []
    for s in all_stems:
        all_elements.append((STEM_ELEMENT[s], STEM_POLARITY[s]))
    for b in all_branches:
        all_elements.append((BRANCH_ELEMENT[b], BRANCH_POLARITY[b]))
        for hs in HIDDEN_STEMS.get(BRANCHES[b],[]):
            hs_idx = STEMS.index(hs)
            all_elements.append((STEM_ELEMENT[hs_idx], STEM_POLARITY[hs_idx]))
    
    for element, polarity in all_elements:
        if element == dm_element:
            counts['companion'] += 1  # same element = Rob Wealth or Friend
        elif element == PRODUCED_BY[dm_element]:
            counts['resource'] += 1   # produces DM = Resource/Seal
        elif element == PRODUCES[dm_element]:
            counts['output'] += 1     # DM produces = Output/Hurting Officer
        elif element == CONTROLLED_BY[dm_element]:
            counts['power'] += 1      # controls DM = Power/Officer
        elif element == CONTROLS[dm_element]:
            counts['wealth'] += 1     # DM controls = Wealth
    
    return counts

def strength_assessment(dm_element, element_counts, season_element):
    """
    Rough Day Master strength assessment.
    Strong if: supported by resource element OR in season OR many companions.
    """
    resource_el = PRODUCED_BY[dm_element]
    companion_count = element_counts.get(dm_element, 0)
    resource_count = element_counts.get(resource_el, 0)
    
    score = companion_count + resource_count
    if season_element == dm_element:
        score += 3
    elif season_element == resource_el:
        score += 1.5
    
    total = sum(element_counts.values())
    if total == 0:
        return 'Moderate'
    ratio = score / total
    if ratio >= 0.45:
        return 'Strong'
    elif ratio >= 0.25:
        return 'Moderate'
    else:
        return 'Weak'

SEASON_ELEMENTS = {
    'Yín':'Wood','Mǎo':'Wood','Chén':'Earth',
    'Sì':'Fire','Wǔ':'Fire','Wèi':'Earth',
    'Shēn':'Metal','Yǒu':'Metal','Xū':'Earth',
    'Hài':'Water','Zǐ':'Water','Chǒu':'Earth',
}

def calculate_bazi(year, month, day, hour, minute, utc_offset):
    """
    Main BaZi calculation. Returns full four pillars chart.
    """
    # Convert to UTC hour for solar calculations
    hour_ut = hour + minute/60.0 - utc_offset
    
    # Adjust day if hour_ut rolls over
    adj_day = day
    adj_month = month
    adj_year = year
    if hour_ut >= 24:
        hour_ut -= 24
        adj_day += 1
    elif hour_ut < 0:
        hour_ut += 24
        adj_day -= 1
    
    # Solar month for month pillar
    solar_month_idx = get_solar_month(adj_year, adj_month, adj_day, hour_ut)
    
    # Year pillar
    yr_s, yr_b = year_pillar(adj_year, adj_month, adj_day, hour_ut)
    
    # Month pillar
    mo_s, mo_b = month_pillar(solar_month_idx, yr_s)
    
    # Day pillar (use local noon for stability — day changes at midnight)
    dy_s, dy_b = day_pillar(year, month, day, hour + minute/60.0 - utc_offset + 12)
    # Recalculate more carefully: day pillar based on local calendar day
    dy_s, dy_b = day_pillar(year, month, day, 12.0)  # noon UTC equivalent
    
    # Hour pillar
    hr_s, hr_b = hour_pillar(hour, dy_s)
    
    pillars_raw = [
        {'name':'Year',  'stem_idx':yr_s, 'branch_idx':yr_b},
        {'name':'Month', 'stem_idx':mo_s, 'branch_idx':mo_b},
        {'name':'Day',   'stem_idx':dy_s, 'branch_idx':dy_b},
        {'name':'Hour',  'stem_idx':hr_s, 'branch_idx':hr_b},
    ]
    
    # Enrich pillars with names and hidden stems
    pillars = []
    for p in pillars_raw:
        s, b = p['stem_idx'], p['branch_idx']
        branch_name = BRANCHES[b]
        pillars.append({
            'name': p['name'],
            'stem_idx': s,
            'branch_idx': b,
            'stem': STEMS[s],
            'branch': branch_name,
            'stem_element': STEM_ELEMENT[s],
            'stem_polarity': STEM_POLARITY[s],
            'branch_element': BRANCH_ELEMENT[b],
            'branch_polarity': BRANCH_POLARITY[b],
            'animal': BRANCH_ANIMAL[b],
            'hidden_stems': HIDDEN_STEMS.get(branch_name, []),
        })
    
    # Day Master
    dm_stem = pillars[2]['stem']
    dm_element = pillars[2]['stem_element']
    dm_polarity = pillars[2]['stem_polarity']
    
    # Element balance
    el_counts = element_analysis(pillars)
    
    # Season (month branch element)
    season_el = SEASON_ELEMENTS.get(pillars[1]['branch'], 'Earth')
    
    # Day Master strength
    strength = strength_assessment(dm_element, el_counts, season_el)
    
    # Interactions
    all_branches = [p['branch_idx'] for p in pillars]
    all_stems = [p['stem_idx'] for p in pillars]
    clashes = find_clashes(all_branches)
    combinations = find_combinations(all_branches)
    stem_combos = find_stem_combinations(all_stems)
    
    # Ten Gods (relationships to Day Master)
    dm_relationships = day_master_relationships(pillars[2]['stem_idx'], all_stems, all_branches)
    
    # Missing elements
    present = {el for el, cnt in el_counts.items() if cnt > 0}
    missing = [el for el in ['Wood','Fire','Earth','Metal','Water'] if el not in present]
    dominant = max(el_counts, key=el_counts.get)
    
    return {
        'pillars': pillars,
        'day_master': {
            'stem': dm_stem,
            'element': dm_element,
            'polarity': dm_polarity,
            'strength': strength,
        },
        'element_counts': el_counts,
        'season_element': season_el,
        'dominant_element': dominant,
        'missing_elements': missing,
        'clashes': clashes,
        'combinations': combinations,
        'stem_combinations': stem_combos,
        'ten_gods': dm_relationships,
    }

def format_bazi(bazi):
    lines = []
    lines.append('\n' + '='*60)
    lines.append('  BAZI FOUR PILLARS CHART')
    lines.append('='*60)
    
    # Pillars table
    headers = ['','Year','Month','Day','Hour']
    lines.append('\n' + '  '.join(f'{h:<12}' for h in headers))
    lines.append('-'*60)
    
    stems_row = ['Heavenly Stem']
    branches_row = ['Earthly Branch']
    animal_row = ['Animal']
    element_row = ['Element']
    hidden_row = ['Hidden Stems']
    
    for p in bazi['pillars']:
        stems_row.append(f"{p['stem']} ({p['stem_element'][:2]}{p['stem_polarity'][0]})")
        branches_row.append(f"{p['branch']} ({p['branch_element'][:2]}{p['branch_polarity'][0]})")
        animal_row.append(p['animal'])
        element_row.append(f"{p['stem_element']}/{p['branch_element']}")
        hidden_row.append(', '.join(p['hidden_stems']) or '—')
    
    for row in [stems_row, branches_row, animal_row, element_row, hidden_row]:
        lines.append('  '.join(f'{cell:<12}' for cell in row))
    
    lines.append('\n' + '-'*60)
    dm = bazi['day_master']
    lines.append(f"DAY MASTER: {dm['stem']} — {dm['polarity']} {dm['element']}")
    lines.append(f"Strength: {dm['strength']}")
    lines.append(f"Season Element: {bazi['season_element']}")
    
    lines.append('\nELEMENT BALANCE:')
    for el, cnt in sorted(bazi['element_counts'].items(), key=lambda x: -x[1]):
        bar = '█' * int(cnt) + ('▌' if cnt % 1 >= 0.5 else '')
        lines.append(f"  {el:<8} {cnt:>4.1f}  {bar}")
    
    if bazi['missing_elements']:
        lines.append(f"\nMissing Elements: {', '.join(bazi['missing_elements'])}")
    lines.append(f"Dominant Element: {bazi['dominant_element']}")
    
    if bazi['clashes']:
        lines.append(f"\nBranch Clashes: {', '.join(f'{a}↔{b}' for a,b in bazi['clashes'])}")
    if bazi['combinations']:
        for c in bazi['combinations']:
            status = '(complete)' if c['complete'] else '(partial)'
            lines.append(f"{c['type']}: {'+'.join(c['branches'])} → {c['forms']} {status}")
    if bazi['stem_combinations']:
        for sc in bazi['stem_combinations']:
            lines.append(f"Stem Combo: {'+'.join(sc['stems'])} → {sc['forms']}")
    
    tg = bazi['ten_gods']
    lines.append('\nTEN GODS DISTRIBUTION (relationships to Day Master):')
    lines.append(f"  Resource/Seal:  {tg['resource']:.1f}  (nourishes DM)")
    lines.append(f"  Output:         {tg['output']:.1f}  (DM expresses)")
    lines.append(f"  Wealth:         {tg['wealth']:.1f}  (DM controls)")
    lines.append(f"  Power/Officer:  {tg['power']:.1f}  (controls DM)")
    lines.append(f"  Companion:      {tg['companion']:.1f}  (same element)")
    
    lines.append('='*60 + '\n')
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='BaZi Four Pillars Calculator')
    parser.add_argument('--year',  type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day',   type=int, required=True)
    parser.add_argument('--hour',  type=int, required=True)
    parser.add_argument('--minute',type=int, default=0)
    parser.add_argument('--utc_offset', type=float, required=True)
    args = parser.parse_args()
    
    bazi = calculate_bazi(args.year, args.month, args.day, args.hour, args.minute, args.utc_offset)
    print(format_bazi(bazi))

if __name__ == '__main__':
    main()
