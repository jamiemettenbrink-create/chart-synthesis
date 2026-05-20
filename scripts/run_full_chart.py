#!/usr/bin/env python3
"""
Master Natal Chart Runner
Runs all calculators in sequence and produces a unified data block
ready for Claude to synthesize.

Usage:
    python3 run_full_chart.py \
        --year 1986 --month 4 --day 24 \
        --hour 6 --minute 10 --utc_offset -7 \
        --lat 33.4942 --lng -111.9261 \
        --name "Jane Smith" \
        [--hd_type "Generator"] \
        [--hd_strategy "Responding"] \
        [--hd_authority "Emotional"] \
        [--hd_profile "3/5"] \
        [--hd_cross "Right Angle Cross of the Unexpected"] \
        [--hd_centers "Sacral,Solar Plexus"] \
        [--hd_channels "27-50,28-38"] \
        [--hd_gates "27,28,41,31,50,38"] \
        [--enneagram "2w3"] \
        [--enneagram_instinct "SP"]

The HD data block is populated from the Human Design Hub API call
(which happens in the browser/app layer before this script runs).
Pass HD data as arguments or leave blank for astrology-only reading.
"""

import sys
import os
import argparse
import json

# Add scripts dir to path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from calculate_chart import calculate_full_chart, format_chart_table
from calculate_bazi import calculate_bazi, format_bazi
from calculate_vedic import calculate_vedic, format_vedic
from calculate_numerology import calculate_numerology, format_numerology

def run_full_chart(year, month, day, hour, minute, utc_offset, lat, lng,
                   name="Chart", full_name=None, current_year=2026,
                   hd_data=None, enneagram=None, enneagram_instinct=None):
    """
    Run all calculators and return unified results dict.
    """
    results = {}
    errors = []
    
    # Western Astrology
    try:
        chart = calculate_full_chart(year, month, day, hour, minute, utc_offset, lat, lng, name)
        results['western'] = chart
    except Exception as e:
        errors.append(f"Western chart error: {e}")
        results['western'] = None
    
    # BaZi
    try:
        bazi = calculate_bazi(year, month, day, hour, minute, utc_offset)
        results['bazi'] = bazi
    except Exception as e:
        errors.append(f"BaZi error: {e}")
        results['bazi'] = None
    
    # Vedic
    try:
        vedic = calculate_vedic(year, month, day, hour, minute, utc_offset, lat, lng)
        results['vedic'] = vedic
    except Exception as e:
        errors.append(f"Vedic error: {e}")
        results['vedic'] = None
    
    # Numerology (only if name provided)
    if full_name:
        try:
            numerology = calculate_numerology(year, month, day, full_name, current_year)
            results['numerology'] = numerology
        except Exception as e:
            errors.append(f"Numerology error: {e}")
            results['numerology'] = None
    else:
        results['numerology'] = None
    
    # HD (passed in, not calculated here)
    results['hd'] = hd_data
    
    # Enneagram (passed in)
    results['enneagram'] = {
        'type': enneagram,
        'instinct': enneagram_instinct
    } if enneagram else None
    
    results['errors'] = errors
    results['meta'] = {
        'name': name,
        'full_name': full_name,
        'birth': f"{month}/{day}/{year} {hour:02d}:{minute:02d}",
        'utc_offset': utc_offset,
        'lat': lat,
        'lng': lng,
        'current_year': current_year,
    }
    
    return results

def format_full_chart(results):
    """
    Format all results into a single text block for Claude to read.
    This is the input Claude receives before writing the synthesis.
    """
    sections = []
    meta = results['meta']
    
    sections.append('=' * 70)
    sections.append(f"FULL MULTI-SYSTEM NATAL CHART")
    sections.append(f"Name: {meta['name']}")
    if meta.get('full_name') and meta['full_name'] != meta['name']:
        sections.append(f"Full birth name: {meta['full_name']}")
    sections.append(f"Birth: {meta['birth']} | UTC{'+' if meta['utc_offset'] >= 0 else ''}{meta['utc_offset']}")
    sections.append(f"Location: lat={meta['lat']}, lng={meta['lng']}")
    sections.append('=' * 70)
    
    # Western Chart
    if results['western']:
        sections.append(format_chart_table(results['western']))
    
    # BaZi
    if results['bazi']:
        sections.append(format_bazi(results['bazi']))
    
    # Vedic
    if results['vedic']:
        sections.append(format_vedic(results['vedic']))
    
    # Numerology
    if results['numerology']:
        sections.append(format_numerology(results['numerology'], meta.get('full_name', meta['name'])))
    
    # Human Design
    if results.get('hd'):
        hd = results['hd']
        sections.append('\n' + '=' * 60)
        sections.append('  HUMAN DESIGN')
        sections.append('=' * 60)
        fields = ['type','strategy','authority','profile','definition','incarnation_cross']
        for f in fields:
            if hd.get(f):
                sections.append(f"  {f.replace('_',' ').title()}: {hd[f]}")
        if hd.get('centers'):
            sections.append(f"  Defined Centers: {', '.join(hd['centers'])}")
        if hd.get('undefined_centers'):
            sections.append(f"  Undefined Centers: {', '.join(hd['undefined_centers'])}")
        if hd.get('channels_short'):
            sections.append(f"  Active Channels: {', '.join(hd['channels_short'])}")
        if hd.get('gates'):
            sections.append(f"  Active Gates: {', '.join(str(g) for g in hd['gates'])}")
        sections.append('=' * 60)
    
    # Enneagram
    if results.get('enneagram') and results['enneagram'].get('type'):
        en = results['enneagram']
        sections.append('\n' + '=' * 60)
        sections.append('  ENNEAGRAM')
        sections.append('=' * 60)
        sections.append(f"  Type: {en['type']}")
        if en.get('instinct'):
            sections.append(f"  Instinctual Variant: {en['instinct']}")
        sections.append('=' * 60)
    
    # Cross-System Convergence Summary (auto-generated hints for Claude)
    sections.append('\n' + '=' * 70)
    sections.append('  CROSS-SYSTEM CONVERGENCE NOTES (for synthesis)')
    sections.append('=' * 70)
    sections.append(generate_convergence_notes(results))
    
    if results.get('errors'):
        sections.append('\nCALCULATION WARNINGS:')
        for err in results['errors']:
            sections.append(f"  ! {err}")
    
    return '\n'.join(sections)

def generate_convergence_notes(results):
    """
    Auto-generate convergence hints to help Claude identify cross-system patterns.
    These are signals, not conclusions — Claude synthesizes the full picture.
    """
    notes = []
    
    w = results.get('western')
    b = results.get('bazi')
    v = results.get('vedic')
    n = results.get('numerology')
    hd = results.get('hd')
    
    # Earth/Stability convergence
    earth_signals = []
    if w:
        sun_sign = w['planets']['Sun']['sign']
        asc_sign = w['angles']['Ascendant']['sign']
        if sun_sign in ['Taurus','Virgo','Capricorn']: earth_signals.append(f"Western Sun in {sun_sign} (earth)")
        if asc_sign in ['Taurus','Virgo','Capricorn']: earth_signals.append(f"Western ASC in {asc_sign} (earth)")
    if b:
        dm = b['day_master']['element']
        if dm in ['Earth','Metal']: earth_signals.append(f"BaZi Day Master {b['day_master']['polarity']} {dm}")
        if b['dominant_element'] in ['Earth','Metal']: earth_signals.append(f"BaZi dominant element: {b['dominant_element']}")
    if len(earth_signals) >= 2:
        notes.append(f"EARTH/STABILITY CONVERGENCE ({len(earth_signals)} signals): {' | '.join(earth_signals)}")
    
    # Depth/Transformation convergence
    depth_signals = []
    if w:
        if w['planets']['Moon']['sign'] == 'Scorpio': depth_signals.append("Western Moon in Scorpio")
        if w['planets'].get('Pluto',{}).get('house') in [1,7,8]: depth_signals.append(f"Pluto in angular/8th house")
        if w['planets']['Moon']['house'] == 7: depth_signals.append("Moon in 7th (depth through relationship)")
    if v:
        moon_nak = v.get('moon_nakshatra',{}).get('name','')
        if moon_nak in ['Ashlesha','Jyeshtha','Mula','Purva Bhadra','Uttara Bhadra']:
            depth_signals.append(f"Vedic Moon in {moon_nak} (depth nakshatra)")
    if len(depth_signals) >= 2:
        notes.append(f"DEPTH/TRANSFORMATION CONVERGENCE ({len(depth_signals)} signals): {' | '.join(depth_signals)}")
    
    # Leadership/Influence convergence
    lead_signals = []
    if w:
        mc_sign = w['angles']['MC']['sign']
        if mc_sign in ['Capricorn','Leo','Aries','Sagittarius']: lead_signals.append(f"Western MC in {mc_sign}")
    if hd and hd.get('gates'):
        gates = [int(g) for g in hd['gates'] if str(g).isdigit()]
        leader_gates = {7,13,31,45}
        found = leader_gates.intersection(set(gates))
        if found: lead_signals.append(f"HD leadership gates: {found}")
    if n and n.get('life_path',{}).get('number') in [1,8,9]:
        lead_signals.append(f"Life Path {n['life_path']['number']} (leadership orientation)")
    if len(lead_signals) >= 2:
        notes.append(f"LEADERSHIP/INFLUENCE CONVERGENCE ({len(lead_signals)} signals): {' | '.join(lead_signals)}")
    
    # Nodal/Evolutionary direction convergence
    nodal_signals = []
    if w:
        nn = w['planets']['North Node']['sign']
        sn = w['planets']['South Node']['sign']
        nodal_signals.append(f"Western NN {nn} / SN {sn}")
    if v:
        rahu = v['planets'].get('Rahu',{})
        if rahu:
            nodal_signals.append(f"Vedic Rahu {rahu['sign']} H{rahu['house']}")
    if len(nodal_signals) >= 2:
        notes.append(f"EVOLUTIONARY DIRECTION: {' | '.join(nodal_signals)}")
    
    # Current timing convergence
    timing_signals = []
    if v:
        cd = v.get('current_dasha',{})
        if cd: timing_signals.append(f"Vedic: {cd['planet']} mahadasha (until age {cd['end_age']:.0f})")
    if n:
        py = n.get('personal_year')
        if py: timing_signals.append(f"Numerology Personal Year {py} ({n['personal_year_calendar']})")
    if timing_signals:
        notes.append(f"CURRENT TIMING: {' | '.join(timing_signals)}")
    
    # Missing element flags
    if b and b.get('missing_elements'):
        notes.append(f"BAZI MISSING ELEMENTS (require conscious cultivation): {', '.join(b['missing_elements'])}")
    
    # BaZi clash flag
    if b and b.get('clashes'):
        clash_str = ', '.join(f"{a}↔{b_}" for a,b_ in b['clashes'])
        notes.append(f"BAZI CLASHES (psychological tension axes): {clash_str}")
    
    if not notes:
        notes.append("No strong cross-system convergences auto-detected. Proceed with section-by-section synthesis.")
    
    return '\n'.join(f"  • {n}" for n in notes)

def main():
    parser = argparse.ArgumentParser(description='Full multi-system natal chart runner')
    parser.add_argument('--year',   type=int, required=True)
    parser.add_argument('--month',  type=int, required=True)
    parser.add_argument('--day',    type=int, required=True)
    parser.add_argument('--hour',   type=int, required=True)
    parser.add_argument('--minute', type=int, default=0)
    parser.add_argument('--utc_offset', type=float, required=True)
    parser.add_argument('--lat',    type=float, required=True)
    parser.add_argument('--lng',    type=float, required=True)
    parser.add_argument('--name',   type=str, default='Chart')
    parser.add_argument('--full_name', type=str, default=None, help='Full legal birth name for numerology')
    parser.add_argument('--current_year', type=int, default=2026)
    # HD arguments
    parser.add_argument('--hd_type',      type=str, default=None)
    parser.add_argument('--hd_strategy',  type=str, default=None)
    parser.add_argument('--hd_authority', type=str, default=None)
    parser.add_argument('--hd_profile',   type=str, default=None)
    parser.add_argument('--hd_cross',     type=str, default=None)
    parser.add_argument('--hd_definition',type=str, default=None)
    parser.add_argument('--hd_centers',   type=str, default=None)
    parser.add_argument('--hd_channels',  type=str, default=None)
    parser.add_argument('--hd_gates',     type=str, default=None)
    # Enneagram
    parser.add_argument('--enneagram',    type=str, default=None)
    parser.add_argument('--enneagram_instinct', type=str, default=None)
    # Output format
    parser.add_argument('--json', action='store_true', help='Output raw JSON instead of formatted text')
    
    args = parser.parse_args()
    
    # Build HD data dict
    hd_data = None
    if any([args.hd_type, args.hd_authority, args.hd_profile]):
        hd_data = {
            'type':             args.hd_type,
            'strategy':         args.hd_strategy,
            'authority':        args.hd_authority,
            'profile':          args.hd_profile,
            'incarnation_cross':args.hd_cross,
            'definition':       args.hd_definition,
            'centers':          args.hd_centers.split(',') if args.hd_centers else [],
            'undefined_centers':[],
            'channels_short':   args.hd_channels.split(',') if args.hd_channels else [],
            'gates':            args.hd_gates.split(',') if args.hd_gates else [],
        }
    
    results = run_full_chart(
        args.year, args.month, args.day, args.hour, args.minute,
        args.utc_offset, args.lat, args.lng,
        name=args.name,
        full_name=args.full_name or args.name,
        current_year=args.current_year,
        hd_data=hd_data,
        enneagram=args.enneagram,
        enneagram_instinct=args.enneagram_instinct,
    )
    
    if args.json:
        # Serialize (remove non-JSON-serializable elements)
        safe = {k: v for k, v in results.items() if k not in ['western']}
        if results.get('western'):
            safe['western_summary'] = {
                'sun': f"{results['western']['planets']['Sun']['degree']}° {results['western']['planets']['Sun']['sign']} H{results['western']['planets']['Sun']['house']}",
                'moon': f"{results['western']['planets']['Moon']['degree']}° {results['western']['planets']['Moon']['sign']} H{results['western']['planets']['Moon']['house']}",
                'asc': f"{results['western']['angles']['Ascendant']['degree']}° {results['western']['angles']['Ascendant']['sign']}",
                'mc': f"{results['western']['angles']['MC']['degree']}° {results['western']['angles']['MC']['sign']}",
            }
        print(json.dumps(safe, indent=2, default=str))
    else:
        print(format_full_chart(results))

if __name__ == '__main__':
    main()
