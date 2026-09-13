#!/usr/bin/env python3
"""Regenerate _img/manteca-location-map.svg — the regional locator map on the homepage.

The map in the client's Canva design is flattened artwork that could not be exported, so
it is redrawn here. State outlines come from a public simplified US-states GeoJSON (cached
in this directory on first run), and every marker sits at its true latitude/longitude, so
the geography is real rather than traced by eye. The window is cropped to Northern and
Central California, as the design's map is; Los Angeles falls outside it and is drawn as a
directional callout on the southern edge, again following the design.

Label offsets and the two Stockton-area markers are placed by hand: at this scale Manteca,
the Port of Stockton and SCK are only a few miles apart and would otherwise overlap.

Usage:  python3 _tools/gen-location-map.py     (run from the repository root)
"""
import json
import math
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "us-states.geojson")
SOURCE = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
OUT = os.path.join(ROOT, "_img", "manteca-location-map.svg")

if not os.path.exists(CACHE):
    print(f"fetching {SOURCE}")
    with urllib.request.urlopen(SOURCE, timeout=60) as r:
        open(CACHE, "wb").write(r.read())

geo = {f["properties"]["name"]: f["geometry"] for f in json.load(open(CACHE))["features"]}

LON0, LON1 = -123.85, -118.85
LAT0, LAT1 = 35.85, 40.95
COSL = math.cos(math.radians(38.0))
PAD = 20
INNER_W = 480.0
SCALE = INNER_W / ((LON1 - LON0) * COSL)
INNER_H = (LAT1 - LAT0) * SCALE
W, H = INNER_W + PAD * 2, INNER_H + PAD * 2

def X(lon): return PAD + (lon - LON0) * COSL * SCALE
def Y(lat): return PAD + (LAT1 - lat) * SCALE
def P(lat, lon): return (round(X(lon), 1), round(Y(lat), 1))

INK, RED, SEA, LAND, ROAD, NVFILL = "#12131a", "#e02e2e", "#dbe6f0", "#ffffff", "#98a2b1", "#f1f4f8"

def poly(name):
    g = geo[name]
    rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
    return " ".join("M " + " L ".join(f"{X(lo):.1f},{Y(la):.1f}" for lo, la in r) + " Z" for r in rings)

def line(pts): return "M " + " L ".join(f"{X(lo):.1f},{Y(la):.1f}" for la, lo in pts)

HWY = {
 "I5":   [(40.95,-122.35),(40.6,-122.39),(39.7,-122.19),(38.8,-121.75),(38.35,-121.6),(37.95,-121.29),(37.3,-120.85),(36.7,-120.35),(36.1,-119.95),(35.85,-119.78)],
 "H99":  [(40.15,-122.24),(39.5,-121.95),(38.9,-121.6),(38.58,-121.49),(38.1,-121.32),(37.96,-121.28),(37.65,-120.99),(37.3,-120.48),(36.74,-119.79),(36.1,-119.42),(35.85,-119.28)],
 "I80":  [(37.79,-122.4),(37.97,-122.3),(38.1,-122.2),(38.35,-121.95),(38.58,-121.49),(38.9,-121.07),(39.15,-120.65),(39.34,-120.2),(39.53,-119.81)],
 "US101":[(40.95,-124.0),(40.0,-123.8),(39.15,-123.2),(38.5,-122.8),(38.1,-122.57),(37.79,-122.42),(37.5,-122.24),(37.34,-121.89),(36.9,-121.6),(36.5,-121.45),(35.95,-121.2),(35.85,-121.1)],
 "H120": [(37.83,-121.74),(37.81,-121.45),(37.80,-121.22),(37.79,-120.95),(37.77,-120.62)],
}
SHIELD = [("5",36.45,-120.15),("99",36.35,-119.55),("80",39.2,-120.45),("101",39.3,-123.02),
          ("80",38.46,-121.78),("120",37.77,-120.6)]

# marker lat/lon -> (label, sub, dx, dy, anchor)
AIRPORT = {
  "SMF": (38.70,-121.59, -12, -3,  "end"),
  "SFO": (37.62,-122.38, -12,  4,  "end"),
  "OAK": (37.72,-122.22,  13,  4,  "start"),
  "SJC": (37.36,-121.93,  13,  4,  "start"),
  "SCK": (38.03,-121.03,  13, -2,  "start"),
}
# (label, distance, lat, lon, dx, dy, anchor)
PLACES = [
  ("Redding",     "221mi", 40.58,-122.39,  13, -2, "start"),
  ("Sacramento",  None,    38.58,-121.49,  13, 12, "start"),
  ("Reno",        "188mi", 39.53,-119.81,  13, -4, "start"),
  ("Lake Tahoe",  "59mi",  39.05,-120.05,  13, 16, "start"),
  ("Fresno",      "111mi", 36.74,-119.79,  13,  4, "start"),
  ("San Francisco",   None,   37.77,-122.42, -13,  1, "end"),
  ("Port of Oakland", "76mi", 37.80,-122.32, -13,-24, "end"),
  ("Port of Stockton",None,   38.03,-121.42, -13, -8, "end"),
]
SJ = (37.34,-121.89)   # two-line label, placed in the ocean to the south-west

o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
  f'role="img" aria-labelledby="mapTitle mapDesc" font-family="Inter, Segoe UI, Helvetica, sans-serif">')
a('<title id="mapTitle">Manteca in the heart of California</title>')
a('<desc id="mapDesc">Map of Northern and Central California showing Manteca on Highway 120 between '
  'Interstate 5 and Highway 99. Driving distances: Port of Oakland 76 miles, San Jose and Silicon Valley '
  '75 miles, Lake Tahoe 59 miles, Fresno 111 miles, Reno 188 miles, Redding 221 miles, Los Angeles 330 miles. '
  'Nearby airports: SMF Sacramento, SFO San Francisco, OAK Oakland, SJC San Jose, SCK Stockton.</desc>')
a(f'<defs><clipPath id="frame"><rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" rx="16"/></clipPath>'
  f'<clipPath id="ca"><path d="{poly("California")}"/></clipPath></defs>')
a(f'<rect width="{W:.0f}" height="{H:.0f}" fill="{SEA}" rx="16"/>')
a('<g clip-path="url(#frame)">')
for nb in ("Nevada", "Oregon"):
    a(f'<path d="{poly(nb)}" fill="{NVFILL}" stroke="#ccd6e0" stroke-width="1.2"/>')
a(f'<path d="{poly("California")}" fill="{LAND}" stroke="#c3d0dc" stroke-width="1.6" stroke-linejoin="round"/>')
a(f'<text x="{X(-121.3):.1f}" y="{Y(40.68):.1f}" fill="#aab7c4" font-size="13.5" font-weight="600" letter-spacing="3.5">CALIFORNIA</text>')
a(f'<text x="{X(-119.75):.1f}" y="{Y(40.3):.1f}" fill="#bcc6d1" font-size="12" font-weight="600" letter-spacing="3">NEVADA</text>')
a('<g clip-path="url(#ca)">')
for k, pts in HWY.items():
    if k == "H120": continue
    a(f'<path d="{line(pts)}" fill="none" stroke="{ROAD}" stroke-width="{3.6 if k in ("I5","H99") else 2.8}" '
      f'stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
a('</g>')
a(f'<path d="{line(HWY["I80"])}" fill="none" stroke="{ROAD}" stroke-width="2.8" stroke-linecap="round" opacity="0.9"/>')
a(f'<path d="{line(HWY["H120"])}" fill="none" stroke="{RED}" stroke-width="4.2" stroke-linecap="round"/>')
for num, lat, lon in SHIELD:
    x, y = P(lat, lon); w = 16 if len(num) < 3 else 22
    a(f'<g><rect x="{x-w/2:.1f}" y="{y-9:.1f}" width="{w}" height="18" rx="4.5" fill="#fff" stroke="{ROAD}" stroke-width="1.3"/>'
      f'<text x="{x:.1f}" y="{y+4.4:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#5b6472">{num}</text></g>')

def label(x, y, anc, text, sub=None, size=12.5):
    a(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" font-size="{size}" font-weight="600" fill="{INK}" '
      f'stroke="#fff" stroke-width="3" paint-order="stroke">{text}</text>')
    if sub:
        a(f'<text x="{x:.1f}" y="{y+14:.1f}" text-anchor="{anc}" font-size="11.5" font-weight="500" fill="#6d7684" '
          f'stroke="#fff" stroke-width="3" paint-order="stroke">({sub})</text>')

for name, dist, lat, lon, dx, dy, anc in PLACES:
    x, y = P(lat, lon)
    if name.startswith("Port of"):
        a(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="#fff" stroke="#7d8794" stroke-width="1.4"/>'
          f'<path d="M{x:.1f},{y-4.2:.1f} v7.4 M{x-3.4:.1f},{y-1.6:.1f} h6.8 M{x-4.4:.1f},{y+1.1:.1f} '
          f'a4.4,4.4 0 0 0 8.8,0" stroke="#5b6472" stroke-width="1.5" fill="none" stroke-linecap="round"/></g>')
    else:
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{INK}"/>')
    label(x + dx, y + dy, anc, name, dist)

sx, sy = P(*SJ)
a(f'<path d="M{sx:.1f},{sy:.1f} L{sx-30:.1f},{sy+34:.1f}" stroke="#98a2b1" stroke-width="1.1" fill="none"/>')
label(sx - 34, sy + 36, "end", "San Jose/Silicon Valley", "75mi")

for code, (lat, lon, dx, dy, anc) in AIRPORT.items():
    x, y = P(lat, lon)
    a(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#fff" stroke="#7d8794" stroke-width="1.4"/>'
      f'<path d="M{x-3.6:.1f},{y+0.4:.1f} l3.2,-3.4 l0.1,2.1 l2.6,-2.7 a0.9,0.9 0 0 1 1.3,1.3 l-2.7,2.6 '
      f'l2.1,0.1 l-3.4,3.2 z" fill="#5b6472"/>'
      f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}" font-size="11.5" font-weight="700" fill="#414a57" '
      f'stroke="#fff" stroke-width="3" paint-order="stroke">{code}</text></g>')

# Los Angeles sits below the window - directional callout on the southern edge, as in the draft
lx, ly = X(-119.55), H - PAD + 2
a(f'<g><path d="M{lx:.1f},{ly-30:.1f} v16 M{lx-5:.1f},{ly-19:.1f} l5,6 l5,-6" stroke="#6d7684" '
  f'stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
  f'<text x="{lx+10:.1f}" y="{ly-22:.1f}" font-size="12.5" font-weight="600" fill="{INK}" '
  f'stroke="#fff" stroke-width="3" paint-order="stroke">Los Angeles</text>'
  f'<text x="{lx+10:.1f}" y="{ly-8:.1f}" font-size="11.5" font-weight="500" fill="#6d7684" '
  f'stroke="#fff" stroke-width="3" paint-order="stroke">(330mi)</text></g>')

mx, my = P(37.80, -121.22)
a(f'<g><circle cx="{mx:.1f}" cy="{my:.1f}" r="34" fill="{RED}" opacity="0.12"/>'
  f'<path d="M{mx:.1f},{my+7:.1f} c-10,-13 -14,-18.5 -14,-24.5 a14,14 0 1 1 28,0 c0,6 -4,11.5 -14,24.5 z" '
  f'fill="{RED}" stroke="#fff" stroke-width="2"/>'
  f'<circle cx="{mx:.1f}" cy="{my-17.5:.1f}" r="5.2" fill="#fff"/>'
  f'<text x="{mx:.1f}" y="{my+28:.1f}" text-anchor="middle" font-size="18" font-weight="700" fill="{INK}" '
  f'stroke="#fff" stroke-width="4" paint-order="stroke">Manteca</text></g>')
a('</g>')

cx, cy = W - 48, 52
a(f'<g><circle cx="{cx:.0f}" cy="{cy}" r="23" fill="#fff" opacity="0.88"/>'
  f'<path d="M{cx:.0f},{cy-17} l5.2,13 l-5.2,-3.4 l-5.2,3.4 z" fill="{RED}"/>'
  f'<path d="M{cx:.0f},{cy+17} l5.2,-13 l-5.2,3.4 l-5.2,-3.4 z" fill="#98a2b1"/>'
  f'<text x="{cx:.0f}" y="{cy-20}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{INK}">N</text>'
  f'<text x="{cx:.0f}" y="{cy+28}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#98a2b1">S</text>'
  f'<text x="{cx-27:.0f}" y="{cy+4}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#98a2b1">W</text>'
  f'<text x="{cx+27:.0f}" y="{cy+4}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#98a2b1">E</text></g>')
a('</svg>')
open(OUT, "w").write("\n".join(o))
print(f"wrote {os.path.relpath(OUT, ROOT)}  ({W:.0f}x{H:.0f})")
