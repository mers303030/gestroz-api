"""
GESTROZ - Carte de bienvenue avec affichage temporaire non bloquant
Adapté pour Windows (polices de secours)
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os
import sys
import subprocess

# --- Configuration polices Windows ---
WIN_FONTS = r"C:\Windows\Fonts"
FONT_ALIAS = {
    "IBMPlexSerif-Bold.ttf":   "georgiab.ttf",
    "IBMPlexSerif-Italic.ttf": "georgiai.ttf",
    "CrimsonPro-Regular.ttf":  "georgia.ttf",
    "CrimsonPro-Italic.ttf":   "georgiai.ttf",
    "Italiana-Regular.ttf":    "MTCORSVA.TTF",
    "Jura-Light.ttf":          "segoeui.ttf",
}

def load_font(name, size):
    if sys.platform == "win32" and name in FONT_ALIAS:
        alt = FONT_ALIAS[name]
        path = os.path.join(WIN_FONTS, alt)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# --- Couleurs ---
BG         = (250, 245, 235)
GOLD_DARK  = (139, 101, 8)
GOLD_MID   = (180, 138, 30)
GOLD_LIGHT = (212, 175, 55)
GOLD_PALE  = (240, 215, 130)
BROWN_DEEP = (80, 50, 15)
INK        = (40, 25, 5)

W, H = 1600, 900
MARGIN = 60

# --- Helpers décoratifs ---
def draw_arabesque_corner(draw, cx, cy, size, angle_offset=0, color=GOLD_MID):
    n_petals = 8
    for i in range(n_petals):
        angle = math.radians(angle_offset + i * 360 / n_petals)
        for r_frac in [0.35, 0.55, 0.75]:
            r = size * r_frac
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            petal_r = size * 0.18 * (1 - r_frac * 0.4)
            draw.ellipse([px-petal_r, py-petal_r, px+petal_r, py+petal_r], fill=color)
    draw.ellipse([cx-size*0.12, cy-size*0.12, cx+size*0.12, cy+size*0.12], fill=GOLD_DARK)

def draw_star_rosette(draw, cx, cy, size, color=GOLD_LIGHT):
    pts = []
    for i in range(16):
        angle = math.radians(i * 22.5 - 90)
        r = size if i % 2 == 0 else size * 0.42
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=color, outline=GOLD_DARK)
    draw.ellipse([cx-size*0.2, cy-size*0.2, cx+size*0.2, cy+size*0.2], fill=GOLD_DARK)

def draw_wave_ribbon(draw, y_center, width, amplitude=12, freq=0.025, color=GOLD_MID, lw=3):
    prev = None
    for x in range(width):
        y = y_center + amplitude * math.sin(freq * x)
        if prev:
            draw.line([prev, (x, y)], fill=color, width=lw)
        prev = (x, y)

def draw_dotted_line(draw, x0, y, x1, gap=14, r=2, color=GOLD_PALE):
    x = x0
    while x < x1:
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        x += gap

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def draw_centered_text(draw, text, font, y, color, max_width, line_spacing=8):
    lines = wrap_text(text, font, max_width, draw)
    for ln in lines:
        bbox = draw.textbbox((0,0), ln, font=font)
        tw = bbox[2]-bbox[0]
        x = (W - tw)//2
        draw.text((x, y), ln, font=font, fill=color)
        y += (bbox[3]-bbox[1]) + line_spacing
    return y

# --- Génération de l'image ---
def generate_welcome_image(message_parts, output_path="GESTROZ_Message_Bienvenue.png"):
    if isinstance(message_parts, str):
        parts = message_parts.split('\n\n')
        while len(parts) < 4: parts.append("")
        paras = parts[:4]
    else:
        paras = list(message_parts)
        while len(paras) < 4: paras.append("")
        paras = paras[:4]

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    for i in range(H):
        t = i / H
        draw.rectangle([0,i,W,i+1], fill=(int(250-15*t), int(245-18*t), int(235-22*t)))

    OB = 28
    draw.rectangle([MARGIN,MARGIN,W-MARGIN,H-MARGIN], outline=GOLD_DARK, width=OB)
    IB = MARGIN+OB+10
    draw.rectangle([IB,IB,W-IB,H-IB], outline=GOLD_MID, width=2)
    draw.rectangle([IB+6,IB+6,W-IB-6,H-IB-6], outline=GOLD_PALE, width=1)

    cs = 70
    corners = [(MARGIN+OB//2,MARGIN+OB//2), (W-MARGIN-OB//2,MARGIN+OB//2),
               (MARGIN+OB//2,H-MARGIN-OB//2), (W-MARGIN-OB//2,H-MARGIN-OB//2)]
    for cx,cy in corners:
        draw_arabesque_corner(draw,cx,cy,cs,22.5,GOLD_LIGHT)
        draw_star_rosette(draw,cx,cy,cs*0.55,GOLD_MID)
    for cx,cy in [(W//2,MARGIN+OB//2), (W//2,H-MARGIN-OB//2),
                  (MARGIN+OB//2,H//2), (W-MARGIN-OB//2,H//2)]:
        draw_star_rosette(draw,cx,cy,cs*0.45,GOLD_LIGHT)

    TOP_RIB = IB+40
    BOT_RIB = H-IB-40
    for yr in (TOP_RIB, BOT_RIB):
        draw_wave_ribbon(draw, yr, W, 10, 0.028, GOLD_MID, 2)
        draw_dotted_line(draw, IB+20, yr-16, W-IB-20, gap=14, r=2, color=GOLD_PALE)
        draw_dotted_line(draw, IB+20, yr+16, W-IB-20, gap=14, r=2, color=GOLD_PALE)

    font_title_big = load_font("IBMPlexSerif-Bold.ttf", 56)
    font_title_sub = load_font("IBMPlexSerif-Italic.ttf", 32)
    font_body      = load_font("CrimsonPro-Regular.ttf", 34)
    font_body_it   = load_font("CrimsonPro-Italic.ttf", 34)
    font_sig       = load_font("Italiana-Regular.ttf", 30)
    font_small     = load_font("Jura-Light.ttf", 22)

    TEXT_W = (W - IB - 50) - (IB + 50)
    lx0, lx1 = W//2-280, W//2+280
    y = TOP_RIB+36

    t1 = "Fédération Marocaine des Éleveurs Bovins"
    bbox = draw.textbbox((0,0), t1, font=font_title_big)
    draw.text(((W-(bbox[2]-bbox[0]))//2, y), t1, font=font_title_big, fill=GOLD_DARK)
    y += bbox[3]-bbox[1]+6
    t2 = "Race Oulmès-Zaër"
    bbox = draw.textbbox((0,0), t2, font=font_title_sub)
    draw.text(((W-(bbox[2]-bbox[0]))//2, y), t2, font=font_title_sub, fill=BROWN_DEEP)
    y += bbox[3]-bbox[1]+18

    draw.rectangle([lx0,y,lx1,y+2], fill=GOLD_MID)
    draw_star_rosette(draw, W//2, y+1, 14, GOLD_DARK)
    y += 22

    styles = [(font_body, INK, 14), (font_body_it, BROWN_DEEP, 20),
              (font_body, INK, 18), (font_body_it, GOLD_DARK, 26)]
    for text, (font, color, after) in zip(paras, styles):
        if text.strip():
            y = draw_centered_text(draw, text, font, y, color, TEXT_W, line_spacing=10)
        y += after

    draw.rectangle([lx0,y,lx1,y+2], fill=GOLD_MID)
    draw_star_rosette(draw, W//2, y+1, 14, GOLD_DARK)
    y += 16

    sig = "Conçu et réalisé par   MOUMEN Idriss"
    bbox = draw.textbbox((0,0), sig, font=font_sig)
    draw.text(((W-(bbox[2]-bbox[0]))//2, y), sig, font=font_sig, fill=BROWN_DEEP)
    y += bbox[3]-bbox[1]+10
    label = "— GESTROZ  ·  Gestion Zootechnique & Nutritionnelle des Bovins —"
    bbox = draw.textbbox((0,0), label, font=font_small)
    draw.text(((W-(bbox[2]-bbox[0]))//2, y), label, font=font_small, fill=GOLD_MID)

    img.save(output_path, dpi=(300,300))
    return output_path

# --- Splash screen non bloquant ---
def start_splash_screen(message_parts, image_path="GESTROZ_Splash.png"):
    generate_welcome_image(message_parts, image_path)
    if sys.platform == "win32":
        proc = subprocess.Popen(['start', image_path], shell=True)
    else:
        proc = subprocess.Popen(['xdg-open', image_path])
    return proc, image_path

def stop_splash_screen(proc, image_path=None):
    if sys.platform == "win32":
        os.system('taskkill /IM Microsoft.Photos.exe /F 2>nul')
        os.system('taskkill /IM rundll32.exe /F 2>nul')
    else:
        proc.terminate()
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except:
            pass