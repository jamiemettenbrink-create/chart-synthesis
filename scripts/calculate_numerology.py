#!/usr/bin/env python3
"""
Numerology Calculator (Pythagorean system)
Calculates: Life Path, Expression (Destiny), Soul Urge (Heart's Desire),
Personality, Birthday, Maturity, and Personal Year numbers.
Also identifies Master Numbers (11, 22, 33) and Karmic Debt numbers (13, 14, 16, 19).

Usage:
    python3 calculate_numerology.py \
        --year 1986 --month 4 --day 24 \
        --name "Jane Elizabeth Smith" \
        --current_year 2026
"""

import argparse
import re
from datetime import datetime

# ── Pythagorean Letter-to-Number Map ─────────────────────────────────────────
LETTER_VALUES = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8
}
VOWELS = set('AEIOU')
# Y is treated as vowel when it acts as one (no adjacent vowel)
# For simplicity, Y is a vowel in standard Pythagorean when surrounded by consonants

# ── Master Numbers and Karmic Debt ────────────────────────────────────────────
MASTER_NUMBERS = {11, 22, 33}
KARMIC_DEBT    = {13, 14, 16, 19}

# ── Number Meanings ───────────────────────────────────────────────────────────
NUMBER_MEANINGS = {
    1:  {'theme': 'Independence & Leadership',    'gift': 'Originality, pioneering spirit, self-reliance', 'shadow': 'Ego, stubbornness, isolation'},
    2:  {'theme': 'Cooperation & Sensitivity',    'gift': 'Diplomacy, empathy, partnership', 'shadow': 'Over-dependence, indecision, martyrdom'},
    3:  {'theme': 'Creative Expression & Joy',    'gift': 'Creativity, communication, optimism', 'shadow': 'Scattered energy, superficiality, self-doubt'},
    4:  {'theme': 'Structure & Stability',        'gift': 'Discipline, reliability, building', 'shadow': 'Rigidity, limitation, over-work'},
    5:  {'theme': 'Freedom & Change',             'gift': 'Adaptability, curiosity, experience', 'shadow': 'Restlessness, impulsiveness, excess'},
    6:  {'theme': 'Responsibility & Nurturing',   'gift': 'Care, healing, beauty, harmony', 'shadow': 'Martyrdom, control, self-neglect'},
    7:  {'theme': 'Depth & Spiritual Truth',      'gift': 'Analysis, wisdom, introspection', 'shadow': 'Isolation, skepticism, aloofness'},
    8:  {'theme': 'Power & Abundance',            'gift': 'Ambition, material mastery, leadership', 'shadow': 'Control, materialism, workaholism'},
    9:  {'theme': 'Completion & Universal Love',  'gift': 'Compassion, humanitarian service, wisdom', 'shadow': 'Martyrdom, bitterness, difficulty letting go'},
    11: {'theme': 'Spiritual Illumination',       'gift': 'Intuition, inspiration, channel for higher truth', 'shadow': 'Anxiety, overwhelm, self-doubt about gifts'},
    22: {'theme': 'Master Builder',               'gift': 'Manifesting large visions into reality', 'shadow': 'Fear of responsibility, self-sabotage'},
    33: {'theme': 'Master Teacher & Healer',      'gift': 'Selfless service, compassionate wisdom', 'shadow': 'Over-sacrifice, impossible standards'},
}

KARMIC_DEBT_MEANINGS = {
    13: 'Karmic Debt 13/4: Past life laziness or misuse of creative energy. Lesson: sustained effort and discipline without resentment.',
    14: 'Karmic Debt 14/5: Past life misuse of freedom — indulgence or controlling others. Lesson: moderation and respect for others\' freedom.',
    16: 'Karmic Debt 16/7: Past life pride, ego collapse, or betrayal of love. Lesson: humility, rebuilding from within, trusting spiritual depth.',
    19: 'Karmic Debt 19/1: Past life misuse of power or self-centered leadership. Lesson: true independence that serves others, not at their expense.',
}

def reduce(n, preserve_master=True):
    """Reduce a number to a single digit, preserving master numbers if requested."""
    if preserve_master and n in MASTER_NUMBERS:
        return n
    while n > 9:
        if preserve_master and n in MASTER_NUMBERS:
            return n
        n = sum(int(d) for d in str(n))
    return n

def reduce_with_intermediate(n):
    """Reduce keeping track of the intermediate number (for karmic debt detection)."""
    original = n
    history = [n]
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
        history.append(n)
    return n, history

def life_path(year, month, day):
    """
    Calculate Life Path using the correct method:
    Reduce month, day, and year separately, then add and reduce.
    This method properly detects master numbers.
    """
    m = reduce(month)
    d_val, d_hist = reduce_with_intermediate(day)
    
    # Year: reduce digit by digit
    y_sum = sum(int(d) for d in str(year))
    y_val, y_hist = reduce_with_intermediate(y_sum)
    
    total = m + d_val + y_val
    
    # Check for karmic debt in intermediate steps
    karmic = None
    for h in [d_hist, y_hist, [total]]:
        for val in h:
            if val in KARMIC_DEBT:
                karmic = val
                break
    
    lp, lp_hist = reduce_with_intermediate(total)
    
    return {
        'number': lp,
        'components': {'month': m, 'day': d_val, 'year': y_val},
        'total_before_reduce': total,
        'karmic_debt': karmic if karmic and karmic != lp else None,
        'is_master': lp in MASTER_NUMBERS,
        'calculation': f"{month}/{day}/{year} → {m}+{d_val}+{y_val}={total} → {lp}",
    }

def is_vowel(letter, position, word):
    """Determine if Y is a vowel based on context."""
    if letter in ('A','E','I','O','U'):
        return True
    if letter == 'Y':
        # Y is a vowel if no other vowel in the syllable
        # Simplified: Y is vowel if not adjacent to another vowel
        if position > 0 and word[position-1] in 'AEIOU':
            return False
        if position < len(word)-1 and word[position+1] in 'AEIOU':
            return False
        return True
    return False

def expression_number(full_name):
    """All letters in the full name."""
    name_clean = re.sub(r'[^A-Z]', '', full_name.upper())
    total = sum(LETTER_VALUES.get(c, 0) for c in name_clean)
    val, hist = reduce_with_intermediate(total)
    karmic = next((h for h in hist if h in KARMIC_DEBT and h != val), None)
    return {
        'number': val,
        'total': total,
        'karmic_debt': karmic,
        'is_master': val in MASTER_NUMBERS,
        'letters_used': name_clean,
    }

def soul_urge_number(full_name):
    """Vowels only (includes Y when acting as vowel)."""
    total = 0
    for word in full_name.upper().split():
        for i, c in enumerate(word):
            if is_vowel(c, i, word):
                total += LETTER_VALUES.get(c, 0)
    val, hist = reduce_with_intermediate(total)
    karmic = next((h for h in hist if h in KARMIC_DEBT and h != val), None)
    return {
        'number': val,
        'total': total,
        'karmic_debt': karmic,
        'is_master': val in MASTER_NUMBERS,
    }

def personality_number(full_name):
    """Consonants only."""
    total = 0
    for word in full_name.upper().split():
        for i, c in enumerate(word):
            if c.isalpha() and not is_vowel(c, i, word):
                total += LETTER_VALUES.get(c, 0)
    val, hist = reduce_with_intermediate(total)
    return {
        'number': val,
        'total': total,
        'is_master': val in MASTER_NUMBERS,
    }

def birthday_number(day):
    """The birth day reduced (but day itself is used, not fully reduced)."""
    if day in MASTER_NUMBERS:
        return {'number': day, 'is_master': True}
    if day <= 9:
        return {'number': day, 'is_master': False}
    reduced = sum(int(d) for d in str(day))
    if reduced in MASTER_NUMBERS:
        return {'number': reduced, 'is_master': True}
    return {'number': reduced, 'is_master': False}

def maturity_number(life_path_num, expression_num):
    """Life Path + Expression, reduced. Activated after mid-life (~35-45)."""
    total = life_path_num + expression_num
    val, _ = reduce_with_intermediate(total)
    return {'number': val, 'is_master': val in MASTER_NUMBERS}

def personal_year(birth_month, birth_day, current_year):
    """Personal year cycle (changes on birthday each year)."""
    total = birth_month + birth_day + sum(int(d) for d in str(current_year))
    val, _ = reduce_with_intermediate(total)
    return val

def pinnacles_and_challenges(month, day, year, life_path_num):
    """
    Four Pinnacles and Challenges (optional enrichment).
    Pinnacle 1: month + day | Pinnacle 2: day + year | 
    Pinnacle 3: P1 + P2 | Pinnacle 4: month + year
    Challenge: absolute difference of same components
    """
    m = reduce(month); d = reduce(day); y = reduce(sum(int(c) for c in str(year)))
    p1, _ = reduce_with_intermediate(m + d)
    p2, _ = reduce_with_intermediate(d + y)
    p3, _ = reduce_with_intermediate(p1 + p2)
    p4, _ = reduce_with_intermediate(m + y)
    c1 = abs(m - d)
    c2 = abs(d - y)
    c3 = abs(c1 - c2)
    c4 = abs(m - y)
    # Ages: P1 ends at 36-LP, P2 ends +9, P3 ends +9, P4 remainder
    p1_end = 36 - life_path_num
    return {
        'pinnacles': [
            {'num': p1, 'period': f'Birth to ~{p1_end}'},
            {'num': p2, 'period': f'~{p1_end} to ~{p1_end+9}'},
            {'num': p3, 'period': f'~{p1_end+9} to ~{p1_end+18}'},
            {'num': p4, 'period': f'~{p1_end+18} onward'},
        ],
        'challenges': [c1, c2, c3, c4],
    }

def calculate_numerology(year, month, day, full_name, current_year=None):
    if current_year is None:
        current_year = datetime.now().year
    lp   = life_path(year, month, day)
    expr = expression_number(full_name)
    soul = soul_urge_number(full_name)
    pers = personality_number(full_name)
    bday = birthday_number(day)
    mat  = maturity_number(lp['number'], expr['number'])
    py   = personal_year(month, day, current_year)
    pins = pinnacles_and_challenges(month, day, year, lp['number'])
    
    return {
        'life_path':    lp,
        'expression':   expr,
        'soul_urge':    soul,
        'personality':  pers,
        'birthday':     bday,
        'maturity':     mat,
        'personal_year': py,
        'personal_year_calendar': current_year,
        'pinnacles_challenges': pins,
        'name_used': full_name,
    }

def fmt_num(n, d):
    suffix = ' ✦ MASTER' if d.get('is_master') else ''
    karmic = f" ⚠ Karmic Debt {d.get('karmic_debt')}" if d.get('karmic_debt') else ''
    return f"{n}{suffix}{karmic}"

def format_numerology(num, full_name):
    lines = []
    lines.append('\n' + '='*60)
    lines.append('  NUMEROLOGY READING')
    lines.append(f"  Name: {full_name}")
    lines.append('='*60)
    
    lp = num['life_path']
    lines.append(f"\nLIFE PATH:      {fmt_num(lp['number'], lp)}")
    lines.append(f"  Calculation:  {lp['calculation']}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(lp['number'], {}).get('theme','')}")
    lines.append(f"  Gift:         {NUMBER_MEANINGS.get(lp['number'], {}).get('gift','')}")
    lines.append(f"  Shadow:       {NUMBER_MEANINGS.get(lp['number'], {}).get('shadow','')}")
    if lp['karmic_debt']:
        lines.append(f"  {KARMIC_DEBT_MEANINGS.get(lp['karmic_debt'],'')}")
    
    ex = num['expression']
    lines.append(f"\nEXPRESSION:     {fmt_num(ex['number'], ex)}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(ex['number'], {}).get('theme','')}")
    lines.append(f"  Gift:         {NUMBER_MEANINGS.get(ex['number'], {}).get('gift','')}")
    
    su = num['soul_urge']
    lines.append(f"\nSOUL URGE:      {fmt_num(su['number'], su)}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(su['number'], {}).get('theme','')}")
    lines.append(f"  Gift:         {NUMBER_MEANINGS.get(su['number'], {}).get('gift','')}")
    
    pe = num['personality']
    lines.append(f"\nPERSONALITY:    {fmt_num(pe['number'], pe)}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(pe['number'], {}).get('theme','')}")
    
    bd = num['birthday']
    lines.append(f"\nBIRTHDAY:       {fmt_num(bd['number'], bd)}")
    
    mat = num['maturity']
    lines.append(f"\nMATURITY:       {fmt_num(mat['number'], mat)}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(mat['number'], {}).get('theme','')}  (activates ~35-45)")
    
    py = num['personal_year']
    lines.append(f"\nPERSONAL YEAR {num['personal_year_calendar']}: {py}")
    lines.append(f"  Theme:        {NUMBER_MEANINGS.get(py, {}).get('theme','')}")
    
    pins = num['pinnacles_challenges']
    lines.append('\nPINNACLES:')
    for p in pins['pinnacles']:
        m = NUMBER_MEANINGS.get(p['num'], {})
        lines.append(f"  {p['period']}: {p['num']} — {m.get('theme','')}")
    lines.append(f"CHALLENGES: {pins['challenges'][0]}, {pins['challenges'][1]}, {pins['challenges'][2]}, {pins['challenges'][3]}")
    
    lines.append('='*60 + '\n')
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',  type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day',   type=int, required=True)
    parser.add_argument('--name',  type=str, required=True, help='Full legal birth name')
    parser.add_argument('--current_year', type=int, default=None)
    args = parser.parse_args()
    
    num = calculate_numerology(args.year, args.month, args.day, args.name, args.current_year)
    print(format_numerology(num, args.name))

if __name__ == '__main__':
    main()
