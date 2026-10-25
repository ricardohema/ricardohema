#!/usr/bin/env python3
"""Build self-contained animated SVG banners from assets/profile-photo.png."""
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
from html import escape
import random, math

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "assets/profile-photo.png"
OUTPUT = ROOT / "assets"
random.seed(41)

def points_from_photo():
    img = Image.open(PHOTO).convert("RGB")
    w,h = img.size
    side = min(w,h)
    img = img.crop(((w-side)//2,(h-side)//2,(w+side)//2,(h+side)//2))
    img = ImageOps.autocontrast(ImageOps.grayscale(img.resize((125,125))))
    img = ImageEnhance.Contrast(img).enhance(1.7)
    coords=[]
    for y in range(0,125,2):
        for x in range(0,125,2):
            v=img.getpixel((x,y))
            # Include shaded regions and selective highlights to form recognizable face.
            probability=.95 if v<105 else (.6 if v<155 else (.23 if v<205 else .035))
            if random.random()<probability:
                coords.append((x,y,int(v)))
    random.shuffle(coords)
    return coords[:1600]

def logo_points(text):
    mask=Image.new("L",(130,130))
    d=ImageDraw.Draw(mask)
    fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font=ImageFont.truetype(fontfile,69)
    bbox=d.textbbox((0,0),text,font=font)
    d.text(((130-(bbox[2]-bbox[0]))/2-bbox[0],(130-(bbox[3]-bbox[1]))/2-bbox[1]),text,font=font,fill=255)
    pts=[(x,y) for y in range(4,126,2) for x in range(4,126,2) if mask.getpixel((x,y))>90]
    random.shuffle(pts)
    return pts

def make(theme):
    dark=theme=="dark"
    bg,card,edge,fg,muted,accent,blue = (
        ("#09111f","#101c2d","#274057","#eaf4ff","#9cb4cb","#4de0c5","#73a8ff")
        if dark else
        ("#f1f6ff","#ffffff","#c5d7ea","#203046","#5b6f85","#008c80","#345dae"))
    src=points_from_photo()
    logos=[logo_points("PY"),logo_points("JS"),logo_points("SQL")]
    pieces=[]
    N=len(src)
    for idx,(x,y,v) in enumerate(src):
        orig_x=91+x*2.65
        orig_y=126+y*2.65
        targets=[]
        for j,shape in enumerate(logos):
            px,py=shape[idx%len(shape)]
            targets.append((91+px*2.65,126+py*2.65))
        xvals=[orig_x,orig_x,targets[0][0],targets[0][0],targets[1][0],targets[1][0],targets[2][0],targets[2][0],orig_x]
        yvals=[orig_y,orig_y,targets[0][1],targets[0][1],targets[1][1],targets[1][1],targets[2][1],targets[2][1],orig_y]
        dx=";".join(f"{a-orig_x:.1f}" for a in xvals)
        dy=";".join(f"{a-orig_y:.1f}" for a in yvals)
        brightness=(255-v)/255
        op=.27+.70*brightness
        color=accent if idx%5 else blue
        # Each dot moves from photographic halftone to language glyphs and back.
        pieces.append(f'<circle cx="{orig_x:.1f}" cy="{orig_y:.1f}" r="{1.0+brightness*.52:.1f}" fill="{color}" opacity="{op:.2f}"><animate attributeName="cx" values="{dx}" dur="18s" repeatCount="indefinite" additive="sum" calcMode="linear" keyTimes="0;.14;.27;.39;.51;.63;.75;.87;1"/><animate attributeName="cy" values="{dy}" dur="18s" repeatCount="indefinite" additive="sum" calcMode="linear" keyTimes="0;.14;.27;.39;.51;.63;.75;.87;1"/></circle>')
    lines=[
        ("name","Ricardo Hernández"),
        ("role","Tech Innovation Analyst"),
        ("mission","Technology + Business Solutions"),
        ("specialty","Process Automation"),
        ("builds","Apps · Extensions · Integrations"),
        ("languages","JavaScript · Python · SQL"),
        ("platform","Retool · APIs · Data"),
        ("infrastructure","VPS · Web Scraping · Cloud"),
        ("region","Mexico & LATAM")
    ]
    yaml=[]
    for i,(k,v) in enumerate(lines):
        y=179+i*31
        yaml.append(f'<text x="545" y="{y}" fill="{muted}" font-family="monospace" font-size="18">{escape(k)}: <tspan fill="{accent if i%2==0 else fg}">{escape(v)}</tspan></text>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="560" viewBox="0 0 1180 560" role="img" aria-label="Ricardo Hernandez portrait transforming into PY, JS and SQL using animated particles"><rect width="1180" height="560" rx="18" fill="{bg}"/><rect x="12" y="12" width="1156" height="536" rx="13" fill="none" stroke="{edge}" stroke-width="2"/><circle cx="38" cy="39" r="6" fill="#fb7185"/><circle cx="59" cy="39" r="6" fill="#eab764"/><circle cx="80" cy="39" r="6" fill="#34d399"/><text x="108" y="46" fill="{muted}" font-size="16" font-family="monospace">ricardohema@tech-business: ~ / profile</text><path d="M24 68H1156" stroke="{edge}"/><rect x="49" y="103" width="432" height="393" rx="12" fill="{card}" stroke="{edge}"/><text x="72" y="132" fill="{accent}" font-size="17" font-family="monospace">VISUAL.IDENTITY / 1-BIT PORTRAIT</text><g>{''.join(pieces)}</g><text x="263" y="478" font-size="14" text-anchor="middle" font-family="monospace" fill="{muted}">PORTRAIT → PYTHON → JS → SQL</text><rect x="515" y="103" width="620" height="393" rx="12" fill="{card}" stroke="{edge}"/><text x="545" y="139" fill="{blue}" font-size="21" font-family="monospace" font-weight="bold">$ cat business-solutions.yaml</text>{''.join(yaml)}<text x="52" y="529" fill="{muted}" font-family="monospace" font-size="14">AUTOMATION · INTEGRATION · BUSINESS VALUE</text><text x="1131" y="529" fill="{accent}" text-anchor="end" font-family="monospace" font-size="14">● MEXICO CITY</text></svg>'''
    (OUTPUT/f"portrait-banner-{theme}.svg").write_text(svg,encoding="utf-8")
    print(theme,N,len(svg))
if __name__=="__main__":
    if not PHOTO.exists():raise SystemExit("Missing assets/profile-photo.png")
    for theme in ("dark","light"):make(theme)
