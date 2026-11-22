#!/usr/bin/env python3
"""Gera os papéis de parede originais do Konaro OS (SVG, 3840x2160).

- serra:    amanhecer com serras em camadas e neblina nos vales (usado na tela de login)
- serra-noite: a mesma paisagem à noite
- dunas:    ondas suaves de cor, abstrato
- fluxo:    faixas fluidas (laranja, marinho, ardósia, creme)
- terminal: minimalista escuro com o símbolo de terminal do Konaro
- anel:     noite estrelada sobre um lago com um anel de luz
- pinguim:  mascote original do Konaro (pinguim de gorro) numa placa de gelo sob a aurora
Uso: make-wallpapers.py <dir de saída>
Arte original do projeto.
"""
import math, os, random, sys

W, H = 3840, 2160


def ridge(seed, base, amp, rough=0.55, points=257):
    rnd = random.Random(seed)
    n = points - 1
    ys = [0.0] * points
    ys[0], ys[n] = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
    step, scale = n, 1.0
    while step > 1:
        half = step // 2
        for i in range(half, n, step):
            ys[i] = (ys[i - half] + ys[i + half]) / 2 + rnd.uniform(-1, 1) * scale
        step, scale = half, scale * rough
    pts = []
    for i, y in enumerate(ys):
        x = i * W / n
        pts.append((x, base - y * amp))
    return pts


def smooth(pts, passes=2):
    for _ in range(passes):
        pts = [pts[0]] + [((a[0] + b[0] + c[0]) / 3, (a[1] + 2 * b[1] + c[1]) / 4)
                          for a, b, c in zip(pts, pts[1:], pts[2:])] + [pts[-1]]
    return pts


def path(pts, bottom=H + 10):
    d = "M-10,%d L%.1f,%.1f " % (bottom, -10, pts[0][1])
    d += " ".join("L%.1f,%.1f" % p for p in pts)
    d += " L%d,%.1f L%d,%d Z" % (W + 10, pts[-1][1], W + 10, bottom)
    return d


def landscape(night=False):
    if night:
        sky = [("0", "#0B1020"), ("0.55", "#1B2340"), ("1", "#3A3D5C")]
        layers = ["#2E3350", "#262B45", "#1E2239", "#161A2D", "#0F1220", "#0A0C16"]
        fog, fog_op, glow = "#9AA6D6", 0.22, "#6F7BB8"
    else:
        sky = [("0", "#E7C59B"), ("0.45", "#F3D9B4"), ("0.62", "#F6E6CC"), ("1", "#DCE3EE")]
        layers = ["#B5A9B8", "#94879C", "#6E6478", "#3F4A4C", "#2B3733", "#1A2420"]
        fog, fog_op, glow = "#F7F8FC", 0.62, "#FFE2B0"
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
           '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">']
    out += ['<stop offset="%s" stop-color="%s"/>' % s for s in sky]
    out.append('</linearGradient>')
    out.append('<radialGradient id="sun" cx="0.62" cy="0.30" r="0.45"><stop offset="0" stop-color="%s" stop-opacity="0.85"/>'
               '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (glow, glow))
    out.append('<filter id="fog" filterUnits="userSpaceOnUse" x="-400" y="0" width="%d" height="%d"><feGaussianBlur stdDeviation="46"/></filter>' % (W + 800, H))
    out.append('<filter id="haze" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="3"/></filter>')
    out.append('<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
               '<stop offset="1" stop-color="#000" stop-opacity="0.35"/></linearGradient></defs>')
    out.append('<rect width="%d" height="%d" fill="url(#sky)"/><rect width="%d" height="%d" fill="url(#sun)"/>' % (W, H, W, H))
    if night:
        rnd = random.Random(7)
        for _ in range(260):
            out.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#fff" opacity="%.2f"/>'
                       % (rnd.uniform(0, W), rnd.uniform(0, H * 0.45), rnd.uniform(0.8, 2.6), rnd.uniform(0.2, 0.9)))
    bases = [0.40, 0.47, 0.55, 0.64, 0.75, 0.88]
    amps = [120, 140, 150, 160, 170, 180]
    for i, (b, a, c) in enumerate(zip(bases, amps, layers)):
        pts = ridge(11 + i * 7, H * b, a, rough=0.50, points=33 if i > 2 else 65)
        pts = smooth(pts)
        out.append('<path d="%s" fill="%s" filter="url(#haze)"/>' % (path(pts), c))
        if 1 <= i <= 3:
            # neblina deitada no vale entre esta serra e a próxima
            y = H * (b + 0.045)
            for k in range(4):
                r = random.Random(i * 10 + k)
                cx = (k + 0.5) * W / 4 + r.uniform(-300, 300)
                out.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="%s" opacity="%.2f" filter="url(#fog)"/>'
                           % (cx, y + r.uniform(-30, 30), r.uniform(W / 4.5, W / 3), 50 + i * 12, fog,
                              fog_op * (0.45 + 0.08 * i)))
    out.append('<rect width="%d" height="%d" fill="url(#shade)"/>' % (W, H))
    out.append('</svg>')
    return "\n".join(out)


def dunes(dark=False):
    bg = ("#0E0F13", "#1C1F2A") if dark else ("#EEF0F6", "#DADFEA")
    cols = (["#3A3F55", "#4C4466", "#2B4A5E", "#5A4A63"] if dark else
            ["#C9D3EA", "#D9CDE6", "#C3DEE6", "#E8D5D0"])
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
           '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
           '<stop offset="1" stop-color="%s"/></linearGradient>' % bg,
           '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>',
           '<filter id="shadow" x="-10%%" y="-30%%" width="120%%" height="160%%"><feDropShadow dx="0" dy="-18" stdDeviation="40" flood-opacity="%s"/></filter></defs>' % ("0.55" if dark else "0.18"),
           '<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H)]
    for i, c in enumerate(cols):
        y0 = H * (0.30 + i * 0.16)
        d = "M-200,%d " % (H + 200)
        pts = []
        for s in range(0, 9):
            x = -200 + s * (W + 400) / 8
            y = y0 + math.sin(s * 0.8 + i * 1.9) * 180
            pts.append((x, y))
        d += "L%.0f,%.0f " % pts[0]
        for a, b in zip(pts, pts[1:]):
            mx = (a[0] + b[0]) / 2
            d += "C%.0f,%.0f %.0f,%.0f %.0f,%.0f " % (mx, a[1], mx, b[1], b[0], b[1])
        d += "L%d,%d Z" % (W + 200, H + 200)
        out.insert(3, '<linearGradient id="w%d" x1="0" y1="0" x2="1" y2="0.4"><stop offset="0" stop-color="%s"/>'
                      '<stop offset="1" stop-color="%s"/></linearGradient>' % (i, c, cols[(i + 1) % len(cols)]))
        out.append('<path d="%s" fill="url(#w%d)" filter="url(#shadow)"/>' % (d, i))
    out.append('</svg>')
    return "\n".join(out)


def penguin():
    """Mascote original do Konaro: pinguim minimalista numa placa de gelo, sob uma aurora."""
    cx, gy = W * 0.5, H * 0.74          # centro e linha do chão
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
           '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070B18"/>'
           '<stop offset="0.7" stop-color="#14213D"/><stop offset="1" stop-color="#1E3352"/></linearGradient>',
           '<linearGradient id="aur" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3DF2B5" stop-opacity="0"/>'
           '<stop offset="0.35" stop-color="#3DF2B5" stop-opacity="0.55"/><stop offset="0.7" stop-color="#7B8CFF" stop-opacity="0.45"/>'
           '<stop offset="1" stop-color="#7B8CFF" stop-opacity="0"/></linearGradient>',
           '<linearGradient id="ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EAF3FF"/><stop offset="1" stop-color="#A9C2E0"/></linearGradient>',
           '<linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2B3245"/><stop offset="1" stop-color="#11141D"/></linearGradient>',
           '<radialGradient id="belly" cx="0.45" cy="0.35" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#DCE4F0"/></radialGradient>',
           '<filter id="blur" filterUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d"><feGaussianBlur stdDeviation="55"/></filter>' % (W, H),
           '<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="18"/></filter></defs>',
           '<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H)]
    rnd = random.Random(3)
    for _ in range(220):
        out.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#fff" opacity="%.2f"/>'
                   % (rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(0.8, 2.4), rnd.uniform(0.2, 0.8)))
    for k, (y, amp, op) in enumerate([(0.22, 160, 0.9), (0.30, 120, 0.6), (0.17, 90, 0.5)]):
        d = "M-200,%.0f " % (H * y)
        for s_ in range(1, 9):
            x = -200 + s_ * (W + 400) / 8
            d += "S%.0f,%.0f %.0f,%.0f " % (x - 240, H * y + math.sin(s_ * 1.3 + k) * amp, x, H * y + math.cos(s_ + k) * amp * 0.6)
        out.append('<path d="%s" stroke="url(#aur)" stroke-width="%d" fill="none" opacity="%.2f" filter="url(#blur)"/>' % (d, 220 - k * 50, op))
    # mar escuro e placa de gelo
    out.append('<rect y="%.0f" width="%d" height="%.0f" fill="#0C1426"/>' % (gy + 40, W, H - gy))
    out.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" fill="url(#ice)"/>'
               % (cx - 760, gy + 40, cx - 600, gy - 10, cx + 640, gy - 20, cx + 780, gy + 40))
    out.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" fill="#8FA9CC"/>'
               % (cx - 760, gy + 40, cx + 780, gy + 40, cx + 740, gy + 110, cx - 720, gy + 100))
    # pinguim (formas simples e originais: corpo em gota alongada, rosto em máscara, gorro de lã)
    bh, bw = 760, 400
    top = gy - bh
    out.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="30" fill="#000" opacity="0.35" filter="url(#shadow)"/>' % (cx, gy, bw * 0.7))
    out.append('<path d="M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f Z" fill="url(#body)"/>'
               % (cx, top, cx + bw * 0.75, top, cx + bw * 0.62, gy, cx, gy, cx - bw * 0.62, gy, cx - bw * 0.75, top, cx, top))
    out.append('<path d="M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f Z" fill="url(#belly)"/>'
               % (cx, top + 120, cx + bw * 0.5, top + 140, cx + bw * 0.42, gy - 10, cx, gy - 10,
                  cx - bw * 0.42, gy - 10, cx - bw * 0.5, top + 140, cx, top + 120))
    for side in (-1, 1):  # olhos e asas
        out.append('<circle cx="%.0f" cy="%.0f" r="15" fill="#11141D"/>' % (cx + side * 52, top + 175))
        out.append('<circle cx="%.0f" cy="%.0f" r="5" fill="#fff"/>' % (cx + side * 52 + 5, top + 170))
        out.append('<path d="M%.0f,%.0f q%.0f,140 %.0f,260 q%.0f,-60 %.0f,-250 Z" fill="#1A1F2C"/>'
                   % (cx + side * bw * 0.52, top + 230, side * 80, side * 40, side * -30, side * -60))
    out.append('<path d="M%.0f,%.0f l40,22 l-40,22 l-40,-22 Z" fill="#F5A524"/>' % (cx, top + 195))
    for side in (-1, 1):
        out.append('<ellipse cx="%.0f" cy="%.0f" rx="55" ry="20" fill="#F5A524"/>' % (cx + side * 70, gy - 4))
    # gorro de lã com pompom
    out.append('<path d="M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f Z" fill="#E5484D"/>'
               % (cx - 150, top + 70, cx - 120, top - 120, cx + 120, top - 120, cx + 150, top + 70))
    out.append('<rect x="%.0f" y="%.0f" width="320" height="56" rx="28" fill="#F2F2F7"/>' % (cx - 160, top + 50))
    out.append('<circle cx="%.0f" cy="%.0f" r="42" fill="#F2F2F7"/>' % (cx, top - 85))
    out.append('</svg>')
    return "\n".join(out)


def flow():
    """Faixas fluidas em laranja, azul-marinho, ardósia e creme (composição procedural)."""
    pal = ["#0E1726", "#F2542D", "#E8DCC4", "#3E6A8A", "#B8321E", "#13233A", "#F6EBD9"]
    rnd = random.Random(42)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
           '<defs><filter id="grain" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/>'
           '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.06 0"/></filter></defs>',
           '<rect width="%d" height="%d" fill="%s"/>' % (W, H, pal[0])]
    bands = 26
    for i in range(bands):
        y0 = -300 + i * (H + 600) / bands
        amp = rnd.uniform(160, 420)
        ph = rnd.uniform(0, 6.28)
        fr = rnd.uniform(1.2, 2.4)
        pts = []
        for k in range(0, 41):
            x = -200 + k * (W + 400) / 40
            y = y0 + math.sin(k / 40 * fr * 6.28 + ph) * amp + math.sin(k / 40 * 3.1 * 6.28 + ph * 2) * amp * 0.18
            pts.append((x, y))
        d = "M%.0f,%.0f " % pts[0] + " ".join("L%.0f,%.0f" % p for p in pts[1:])
        color = pal[1 + (i * 3 + rnd.randrange(3)) % (len(pal) - 1)]
        width = rnd.uniform(140, 300)
        out.append('<path d="%s" fill="none" stroke="#0A0F18" stroke-width="%.0f" stroke-linejoin="round" stroke-linecap="round"/>' % (d, width + 18))
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.0f" stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, width))
        if rnd.random() < 0.5:   # fio fino de luz dentro da faixa
            out.append('<path d="%s" fill="none" stroke="#F6EBD9" stroke-opacity="0.55" stroke-width="3" transform="translate(0,%.0f)"/>' % (d, rnd.uniform(-width / 3, width / 3)))
    out.append('<rect width="%d" height="%d" filter="url(#grain)"/>' % (W, H))
    out.append('</svg>')
    return "\n".join(out)


def terminal():
    """Minimalista escuro com o símbolo de terminal do Konaro (K num quadrado com cursor)."""
    cx, cy, s = W / 2, H / 2, 300
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H)
            + '<rect width="%d" height="%d" fill="#272C35"/>' % (W, H)
            + '<rect x="%.0f" y="%.0f" width="%d" height="%d" rx="70" fill="none" stroke="#ECEFF4" stroke-width="22"/>' % (cx - s / 2, cy - s / 2, s, s)
            + '<path d="M%.0f,%.0f l70,60 l-70,60" fill="none" stroke="#ECEFF4" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>' % (cx - 85, cy - 70)
            + '<rect x="%.0f" y="%.0f" width="90" height="22" rx="11" fill="#7BD88F"/>' % (cx + 5, cy + 50)
            + '</svg>')


def ring():
    """Noite estrelada sobre um lago, serras escuras e um anel de luz refletido na água."""
    horizon = H * 0.66
    rnd = random.Random(11)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
           '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B1F4A"/>'
           '<stop offset="0.7" stop-color="#4A4F8C"/><stop offset="1" stop-color="#8C86B8"/></linearGradient>'
           '<linearGradient id="lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3E6E"/><stop offset="1" stop-color="#0E1028"/></linearGradient>'
           '<filter id="glow" x="-20%%" y="-20%%" width="140%%" height="140%%"><feGaussianBlur stdDeviation="18"/></filter>'
           '<filter id="mist" filterUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d"><feGaussianBlur stdDeviation="40"/></filter>'
           '<clipPath id="above"><rect width="%d" height="%.0f"/></clipPath></defs>' % (W, H, W, horizon),
           '<rect width="%d" height="%.0f" fill="url(#sky)"/>' % (W, horizon)]
    for _ in range(700):
        out.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#fff" opacity="%.2f"/>'
                   % (rnd.uniform(0, W), rnd.uniform(0, horizon * 0.95), rnd.uniform(0.6, 2.4), rnd.uniform(0.25, 0.95)))
    far = smooth(ridge(5, horizon - 120, 90, points=33))
    near = smooth(ridge(9, horizon - 30, 60, points=33))
    peak = "M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" % (W * 0.42, horizon - 40, W * 0.5, horizon - 330, W * 0.58, horizon - 40)
    r = H * 0.25
    ringc = (W / 2, horizon - r * 0.55)
    scene = [
        '<path d="%s" fill="#5B5A8E"/>' % peak,
        '<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" fill="#E6E4F2" opacity="0.85"/>' % (W * 0.475, horizon - 250, W * 0.5, horizon - 330, W * 0.525, horizon - 250),
        '<path d="%s" fill="#2C2D55"/>' % path(far, bottom=horizon + 2),
        '<path d="%s" fill="#14152E"/>' % path(near, bottom=horizon + 2),
    ]
    ring_svg = ('<circle cx="%.0f" cy="%.0f" r="%.0f" fill="none" stroke="#FFFFFF" stroke-width="30" opacity="0.6" filter="url(#glow)"/>'
                '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="none" stroke="#FFFFFF" stroke-width="22"/>' % (ringc + (r,) + ringc + (r,)))
    out += scene
    out.append('<g clip-path="url(#above)">%s</g>' % ring_svg)
    out.append('<rect y="%.0f" width="%d" height="%.0f" fill="url(#lake)"/>' % (horizon, W, H - horizon))
    out.append('<g transform="translate(0,%.0f) scale(1,-1)" opacity="0.35">%s<g clip-path="url(#above)">%s</g></g>'
               % (2 * horizon, "".join(scene), ring_svg))
    out.append('<rect y="%.0f" width="%d" height="120" fill="#9AA0D8" opacity="0.25" filter="url(#mist)"/>' % (horizon - 40, W))
    out.append('</svg>')
    return "\n".join(out)


def main(out):
    os.makedirs(out, exist_ok=True)
    jobs = {"serra": landscape(False), "serra-noite": landscape(True), "dunas": dunes(False), "dunas-noite": dunes(True),
            "pinguim": penguin(), "fluxo": flow(), "terminal": terminal(), "anel": ring()}
    for name, svg in jobs.items():
        with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("papel de parede", name)


if __name__ == "__main__":
    main(sys.argv[1])
