"""Print what changed since a date for a list of product IDs (FR E-Phy AMM numbers or DE Kennnummern).

    python weekly_watch.py fr 2026-11-18 2100132 9800336
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cropauth import Client

country, since, *ids = sys.argv[1:]
c = Client()
for pid in ids:
    items = list(c.changes(country=country, since=since, product=pid))
    print(f"{pid}: {len(items)} change(s)")
    for ch in items:
        print(f"  {ch['first_seen'][:10]} {ch['op']:8} {ch['table']} {', '.join(ch.get('changed_columns') or [])}")
