#!/usr/bin/env python3
"""
lanqing431 GitHub 主页 · SVG 生成器（弥散玻璃 · 深夜极光）
深色底 + 缓慢流动的青/靛/天蓝/紫弥散光斑 + 磨砂玻璃卡片
用法：python3 assets/generate.py   （无第三方依赖）
"""
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

SANS = ("'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC',"
        "'Noto Sans SC','WenQuanYi Zen Hei',-apple-system,Helvetica,Arial,sans-serif")

# ---------------- 配色 ----------------
BG = "#0f1424"
INK, SOFT, DIM = "#eef2ff", "#b4bcd6", "#7f89a8"
BLOB = {"teal": "#14b8a6", "indigo": "#6366f1", "sky": "#0ea5e9", "violet": "#7c3aed"}
ACC = "#5eead4"   # 全站唯一的强调色（青绿）
A = {k: ACC for k in ("violet", "indigo", "sky", "teal", "pink")}

BASE_CSS = """
.b1{animation:b1 24s ease-in-out infinite}.b2{animation:b2 28s ease-in-out infinite}
.b3{animation:b3 32s ease-in-out infinite}.b4{animation:b4 26s ease-in-out infinite}
@keyframes b1{50%{transform:translate(140px,40px)}}@keyframes b2{50%{transform:translate(-160px,30px)}}
@keyframes b3{50%{transform:translate(90px,-50px)}}@keyframes b4{50%{transform:translate(-80px,-40px)}}
.fade{opacity:0;animation:fade 1s ease-out forwards}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes grow{from{width:0}}
@keyframes show{from{opacity:0}}
@keyframes draw{from{stroke-dashoffset:1}}
.fl{animation:fl 6s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-12px)}}
"""
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}.fade{opacity:1!important}}"


def write(rel, svg):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(chr(10).join(line.rstrip() for line in svg.splitlines()))


def glass(x, y, w, h, r=16, op=".06", sop=".12", extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#ffffff" fill-opacity="{op}" '
            f'stroke="#ffffff" stroke-opacity="{sop}" {extra}/>')


def bubble(x, y, r, d):
    return (f'<g class="fl" style="animation-delay:{d}s"><circle cx="{x}" cy="{y}" r="{r}" fill="url(#orb)" '
            f'stroke="#ffffff" stroke-opacity=".3"/></g>')


def frame(w, h, body, blobs, defs="", css="", radius=24, inset=False, faint=True):
    """深色底 + 模糊光斑 + 磨砂玻璃层 + 顶部高光 + 细描边。blobs: [(颜色名, cx, cy, r), ...]（最多 4 个）"""
    if faint:  # 普通卡片：角落一团静止的淡光
        c, x, y, r = blobs[0]
        bl, bop = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{BLOB[c]}"/>', ".22"
    else:      # 横幅：多团缓慢流动的光斑
        bl = "".join(f'<g class="b{i + 1}"><circle cx="{x}" cy="{y}" r="{r}" fill="{BLOB[c]}"/></g>'
                     for i, (c, x, y, r) in enumerate(blobs))
        bop = ".40"
    pane = (glass(28, 28, w - 56, h - 56, 20, ".05", ".16", 'stroke-width="1.5"') if inset
            else f'<rect width="{w}" height="{h}" fill="#ffffff" fill-opacity=".03"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
  <clipPath id="clip"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>
  <linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
  <radialGradient id="orb" cx=".35" cy=".3"><stop offset="0" stop-color="#ffffff" stop-opacity=".5"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".12"/><stop offset="1" stop-color="#ffffff" stop-opacity=".04"/></radialGradient>
  {defs}
</defs>
<style>{BASE_CSS}{css}{REDUCED}</style>
<g clip-path="url(#clip)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <g filter="url(#blur)" opacity="{bop}">{bl}</g>
  {pane}
  {body}
</g>
<rect x="{w * .15:.0f}" y=".75" width="{w * .7:.0f}" height="1" fill="url(#sheen)"/>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{radius - .75}" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-width="1.5"/>
</svg>'''


STAGE_DELAY = [0, -6, -4, -2]   # 四个阶段在 8 秒循环里依次高亮
ACT_CSS = ".act{opacity:0;animation:act 8s ease-in-out infinite}@keyframes act{0%,100%{opacity:1}20%,80%{opacity:0}}"


# ============================================================
# 1. 顶部横幅
# ============================================================
def banner():
    W, H = 1200, 340
    stages = [("思考", "violet"), ("规划", "indigo"), ("行动", "sky"), ("反思", "teal")]
    row = []
    for i, (s, col) in enumerate(stages):
        x = 76 + i * 96
        row.append(glass(x, 252, 80, 36, 18, ".06", ".16")
                   + f'<rect x="{x}" y="252" width="80" height="36" rx="18" fill="#ffffff" fill-opacity=".16" class="act" style="animation-delay:{STAGE_DELAY[i]}s"/>'
                   f'<circle cx="{x + 18}" cy="270" r="4" fill="{A[col]}"/><text x="{x + 28}" y="276" font-size="16" fill="{INK}">{s}</text>')
    body = f'''{bubble(960, 160, 54, 0)}{bubble(1070, 236, 24, -3)}
<g font-family="{SANS}">
  <g class="fade"><text x="76" y="94" font-size="18" fill="{SOFT}">你好，我是</text></g>
  <g class="fade" style="animation-delay:.15s"><text x="70" y="176" font-size="84" font-weight="800" fill="{INK}">lanqing431</text></g>
  <g class="fade" style="animation-delay:.3s"><text x="76" y="228" font-size="23" fill="{SOFT}">Agent 开发者 · 让模型学会思考、规划与行动</text></g>
  <g class="fade" style="animation-delay:.45s">{''.join(row)}</g>
</g>'''
    blobs = [("teal", 240, 60, 200), ("indigo", 900, 80, 220), ("sky", 620, 330, 200), ("violet", 1150, 300, 180)]
    write("banner.svg", frame(W, H, body, blobs, css=ACT_CSS, inset=True, faint=False))


# ============================================================
# 2. 关于我：循环图 + 四步说明（同步高亮）
# ============================================================
def about():
    W, H = 1200, 420
    CX, CY, R = 250, 210, 128
    css = (f".trail{{transform-origin:{CX}px {CY}px;animation:spin 8s linear infinite}}"
           f"@keyframes spin{{from{{transform:rotate(-90deg)}}to{{transform:rotate(270deg)}}}}" + ACT_CSS)
    stages = [("思考", "violet", "先弄清楚问题的本质，而不是急着动手"),
              ("规划", "indigo", "把目标拆成小步骤，为每一步选好工具"),
              ("行动", "sky", "调用工具，一步一步把事情做完"),
              ("反思", "teal", "检查结果、记下经验，下一轮做得更好")]
    nodes, rows = [], []
    for i, (zh, col, desc) in enumerate(stages):
        a = math.radians(i * 90 - 90)
        x, y = CX + R * math.cos(a), CY + R * math.sin(a)
        c, dl = A[col], STAGE_DELAY[i]
        nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="40" fill="{BG}" fill-opacity=".6"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="40" fill="#ffffff" fill-opacity=".06" stroke="{c}" stroke-opacity=".45" stroke-width="1.5"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="40" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="2" class="act" style="animation-delay:{dl}s"/>'
            f'<text x="{x:.1f}" y="{y + 7:.1f}" text-anchor="middle" font-size="20" font-weight="700" fill="{INK}">{zh}</text>')
        ry = 52 + i * 80
        rows.append(
            f'<g class="fade" style="animation-delay:{.2 + i * .15:.2f}s">'
            + glass(520, ry, 632, 68, 14, ".05", ".10")
            + f'<rect x="520" y="{ry}" width="632" height="68" rx="14" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".35" class="act" style="animation-delay:{dl}s"/>'
            f'<circle cx="560" cy="{ry + 34}" r="16" fill="{c}" fill-opacity=".18"/>'
            f'<text x="560" y="{ry + 40}" text-anchor="middle" font-size="15" font-weight="700" fill="{c}">{i + 1}</text>'
            f'<text x="592" y="{ry + 41}" font-size="19" font-weight="700" fill="{INK}">{zh}</text>'
            f'<text x="652" y="{ry + 41}" font-size="16" fill="{SOFT}">{desc}</text></g>')
    body = f'''
<g font-family="{SANS}">
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-dasharray="2 6"/>
  <g class="trail">
    <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{ACC}" stroke-opacity=".6" stroke-width="2.5" stroke-linecap="round" pathLength="100" stroke-dasharray="12 88" stroke-dashoffset="12"/>
    <circle cx="{CX + R}" cy="{CY}" r="6" fill="#ffffff"/>
  </g>
  {''.join(nodes)}
  <text x="{CX}" y="{CY - 2}" text-anchor="middle" font-size="22" font-weight="800" fill="{INK}">Agent Loop</text>
  <text x="{CX}" y="{CY + 22}" text-anchor="middle" font-size="14" fill="{DIM}">我的工作方式</text>
  {''.join(rows)}
</g>'''
    blobs = [("violet", 200, 60, 220), ("indigo", 760, 0, 200), ("teal", 1100, 420, 220), ("sky", 120, 420, 160)]
    write("about.svg", frame(W, H, body, blobs, css=css))


# ============================================================
# 3. 关注方向
# ============================================================
ICONS = {
    "tool": '<g transform="translate(-13,-13) scale(1.08)"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>',
    "plan": '<g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="-10" cy="-9" r="4"/><circle cx="10" cy="0" r="4"/><circle cx="-10" cy="10" r="4"/><path d="M-6 -7.5 L6 -1.8 M-6 8.5 L6 1.8"/></g>',
    "mem": '<g fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="0" cy="-9" rx="12" ry="4.5"/><path d="M-12 -9 v18 a12 4.5 0 0 0 24 0 v-18 M-12 0 a12 4.5 0 0 0 24 0"/></g>',
    "multi": '<g fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="0" cy="-9" r="5.5"/><circle cx="-11" cy="9" r="5.5"/><circle cx="11" cy="9" r="5.5"/><path d="M-3 -4 L-8 4 M3 -4 L8 4 M-5 9 h10" stroke-linecap="round"/></g>',
}


def focus():
    W, H = 1200, 250
    tiles = [("tool", "sky", "工具调用", "让模型安全地使用外部能力"),
             ("plan", "violet", "任务规划", "把模糊目标拆成可执行步骤"),
             ("mem", "teal", "记忆系统", "短期上下文与长期经验"),
             ("multi", "indigo", "多智能体", "分工、协作与相互校验")]
    tw, th, y0 = 258, 170, 40
    gap = (W - 96 - 4 * tw) / 3
    body = []
    for i, (ic, col, title, desc) in enumerate(tiles):
        x = 48 + i * (tw + gap)
        body.append(f'<g class="fade" style="animation-delay:{i * .12:.2f}s">'
                    + glass(f"{x:.1f}", y0, tw, th, 18, ".06", ".14")
                    + f'<circle cx="{x + 46:.1f}" cy="{y0 + 48}" r="24" fill="{A[col]}" fill-opacity=".16"/>'
                    f'<g transform="translate({x + 46:.1f},{y0 + 48})" style="color:{A[col]}">{ICONS[ic]}</g>'
                    f'<text x="{x + 24:.1f}" y="{y0 + 112}" font-size="21" font-weight="700" fill="{INK}">{title}</text>'
                    f'<text x="{x + 24:.1f}" y="{y0 + 142}" font-size="15" fill="{SOFT}">{desc}</text></g>')
    blobs = [("sky", 100, 0, 200), ("violet", 500, 260, 200), ("teal", 820, 0, 180), ("indigo", 1150, 250, 200)]
    write("focus.svg", frame(W, H, f'<g font-family="{SANS}">{"".join(body)}</g>', blobs))


# ============================================================
# 4. 此刻
# ============================================================
def now():
    W, H = 1200, 250
    rows = [("在做", "sky", "更可靠的 Agent 工作流"),
            ("在学", "teal", "长期记忆与自我反思"),
            ("在想", "violet", "Agent 如何与人更好地协作")]
    bars = [("好奇心", 1.00, "∞", "violet", "pink"),
            ("专注力", .88, "88%", "indigo", "sky"),
            ("咖啡因", .72, "72%", "sky", "teal"),
            ("调试耐心", .61, "61%", "teal", "indigo")]
    defs, body = [], []
    for i, (tag, col, text) in enumerate(rows):
        y = 68 + i * 58
        body.append(f'<g class="fade" style="animation-delay:{i * .12:.2f}s">'
                    f'<rect x="56" y="{y - 17}" width="64" height="34" rx="17" fill="{A[col]}" fill-opacity=".16" stroke="{A[col]}" stroke-opacity=".35"/>'
                    f'<text x="88" y="{y + 6}" text-anchor="middle" font-size="15" font-weight="700" fill="{A[col]}">{tag}</text>'
                    f'<text x="140" y="{y + 7}" font-size="19" fill="{INK}">{text}</text></g>')
    body.append('<line x1="620" y1="44" x2="620" y2="206" stroke="#ffffff" stroke-opacity=".10"/>')
    BX, BW = 770, 300
    for i, (label, v, val, c1, c2) in enumerate(bars):
        y = 62 + i * 44
        defs.append(f'<linearGradient id="g{i}" x1="0" x2="1"><stop offset="0" stop-color="{A[c1]}"/><stop offset="1" stop-color="{A[c2]}"/></linearGradient>')
        body.append(
            f'<text x="664" y="{y + 6}" font-size="16" fill="{SOFT}">{label}</text>'
            f'<rect x="{BX}" y="{y - 4}" width="{BW}" height="8" rx="4" fill="#ffffff" fill-opacity=".08"/>'
            f'<rect x="{BX}" y="{y - 4}" width="{BW * v:.1f}" height="8" rx="4" fill="url(#g{i})" '
            f'style="animation:grow 1.6s cubic-bezier(.2,.8,.2,1) {.3 + i * .15:.2f}s both"/>'
            f'<text x="1144" y="{y + (8 if val == "∞" else 6)}" text-anchor="end" font-size="{24 if val == "∞" else 16}" '
            f'font-weight="700" fill="{A[c1]}">{val}</text>')
    blobs = [("sky", 80, 250, 200), ("violet", 640, -20, 200), ("teal", 1120, 250, 200)]
    write("now.svg", frame(W, H, f'<g font-family="{SANS}">{"".join(body)}</g>', blobs, "".join(defs)))


# ============================================================
# 5. 分区标题（深色玻璃胶囊，浅色/深色页面上都清晰）
# ============================================================
def titles():
    items = [("about", "01", "关于我", "violet"), ("focus", "02", "关注方向", "sky"),
             ("now", "03", "此刻", "teal"), ("stats", "04", "数据概览", "indigo"),
             ("contrib", "05", "贡献足迹", "violet")]
    for key, num, zh, col in items:
        W, H = 1200, 64
        cap = 96 + len(zh) * 21 + 22
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="cap" x1="0" x2="1"><stop offset="0" stop-color="#16203a"/><stop offset="1" stop-color="#1c1a3e"/></linearGradient>
  <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{A['teal']}" stop-opacity=".7"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="1" y="10" width="{cap}" height="44" rx="22" fill="url(#cap)" stroke="#ffffff" stroke-opacity=".14"/>
<circle cx="32" cy="32" r="14" fill="{A[col]}" fill-opacity=".18"/>
<text x="32" y="37" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="{A[col]}">{num}</text>
<text x="58" y="39" font-family="{SANS}" font-size="19" font-weight="700" fill="{INK}">{zh}</text>
<rect x="{cap + 16}" y="31" width="{W - cap - 20}" height="2" rx="1" fill="url(#ln)"/>
</svg>'''
        write(f"title-{key}.svg", svg)


# ============================================================
# 6. 底部
# ============================================================
def footer():
    W, H = 1200, 150
    body = f'''<text x="600" y="70" text-anchor="middle" font-family="{SANS}" font-size="21" fill="{INK}">让每一次调用，都离目标更近一步</text>
<text x="600" y="98" text-anchor="middle" font-family="{SANS}" font-size="14" fill="{DIM}">感谢来访</text>'''
    blobs = [("teal", 200, 150, 180), ("indigo", 620, 0, 200), ("violet", 1050, 150, 180)]
    write("footer.svg", frame(W, H, body, blobs))


# ============================================================
# 7. 数据卡片（scripts/update_stats.py 填入真实数据；无数据时输出占位版）
# ============================================================
def _fmt(n):
    return "—" if n is None else f"{n:,}"


def _smooth(pts, lo, hi):
    cl = lambda y: max(lo, min(hi, y))  # noqa: E731
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, cl(p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, cl(p2[1] - (p3[1] - p1[1]) / 6))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def stats_card(d=None):
    d = d or {}
    W, H = 1200, 420
    metrics = [("过去一年贡献", d.get("total"), "violet"), ("提交", d.get("commits"), "indigo"),
               ("Pull Request", d.get("prs"), "sky"), ("Issue", d.get("issues"), "teal"),
               ("获得 Star", d.get("stars"), "pink")]
    body = []
    bw = (W - 96) / 5
    for i, (label, val, col) in enumerate(metrics):
        x = 48 + i * bw
        if i:
            body.append(f'<line x1="{x:.1f}" y1="52" x2="{x:.1f}" y2="124" stroke="#ffffff" stroke-opacity=".10"/>')
        body.append(f'<g class="fade" style="animation-delay:{i * .08:.2f}s">'
                    f'<text x="{x + bw / 2:.1f}" y="94" text-anchor="middle" font-size="38" font-weight="800" fill="{INK}">{_fmt(val)}</text>'
                    f'<text x="{x + bw / 2:.1f}" y="122" text-anchor="middle" font-size="14" fill="{DIM}">{label}</text></g>')

    GX, GY, GW, GH = 72, 192, 760, 140
    weeks = d.get("weeks") or []
    body.append(f'<text x="{GX - 24}" y="172" font-size="14" fill="{DIM}">每周贡献 · 过去 52 周</text>')
    for k in range(3):
        y = GY + GH * k / 2
        body.append(f'<line x1="{GX}" y1="{y:.1f}" x2="{GX + GW}" y2="{y:.1f}" stroke="#ffffff" stroke-opacity=".08" stroke-dasharray="3 6"/>')
    if weeks and max(weeks) > 0:
        m, n = max(weeks), len(weeks)
        pts = [(GX + GW * i / (n - 1), GY + GH - GH * v / m) for i, v in enumerate(weeks)]
        line = _smooth(pts, GY, GY + GH)
        area = line + f" L{GX + GW},{GY + GH} L{GX},{GY + GH} Z"
        lx, ly = pts[-1]
        body.append(
            f'<path d="{area}" fill="url(#area)" style="animation:show 1.2s 1s both"/>'
            f'<path d="{line}" fill="none" stroke="url(#lineg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
            f'pathLength="1" stroke-dasharray="1" style="animation:draw 2.2s cubic-bezier(.4,0,.2,1) .3s both"/>'
            f'<g style="animation:show .4s 2.4s both">'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="#ffffff" stroke="{A["teal"]}" stroke-width="2"/>'
            f'<text x="{lx - 10:.1f}" y="{max(ly - 12, GY + 4):.1f}" text-anchor="end" font-size="12" fill="{SOFT}">本周 {weeks[-1]}</text></g>'
            f'<text x="{GX - 10}" y="{GY + 5}" text-anchor="end" font-size="11" fill="{DIM}">{m}</text>'
            f'<text x="{GX - 10}" y="{GY + GH + 4}" text-anchor="end" font-size="11" fill="{DIM}">0</text>')
        for wi, label in d.get("months", []):
            x = GX + GW * wi / (n - 1)
            if GX + 12 < x < GX + GW - 12:
                body.append(f'<text x="{x:.1f}" y="{GY + GH + 26}" text-anchor="middle" font-size="12" fill="{DIM}">{label}</text>')
    else:
        body.append(f'<text x="{GX + GW / 2}" y="{GY + GH / 2 + 6}" text-anchor="middle" font-size="16" fill="{DIM}">数据将在首次运行 GitHub Action 后生成</text>')

    PX, PY, PW, PH = 880, 158, 272, 214
    rows = [("当前连续", d.get("cur_streak"), "teal"), ("最长连续", d.get("max_streak"), "violet"),
            ("活跃天数", d.get("active_days"), "sky")]
    body.append(glass(PX, PY, PW, PH, 16, ".06", ".12"))
    for i, (label, val, col) in enumerate(rows):
        y = PY + 48 + i * 62
        body.append(f'<g class="fade" style="animation-delay:{.4 + i * .1:.2f}s">'
                    f'<circle cx="{PX + 28}" cy="{y - 5}" r="4.5" fill="{A[col]}"/>'
                    f'<text x="{PX + 44}" y="{y}" font-size="15" fill="{SOFT}">{label}</text>'
                    f'<text x="{PX + PW - 46}" y="{y + 2}" text-anchor="end" font-size="26" font-weight="800" fill="{INK}">{_fmt(val)}</text>'
                    f'<text x="{PX + PW - 24}" y="{y}" text-anchor="end" font-size="14" fill="{DIM}">天</text></g>')
        if i < 2:
            body.append(f'<line x1="{PX + 22}" y1="{y + 28}" x2="{PX + PW - 22}" y2="{y + 28}" stroke="#ffffff" stroke-opacity=".08"/>')
    if d.get("updated"):
        body.append(f'<text x="{W - 30}" y="{H - 16}" text-anchor="end" font-size="11" fill="{DIM}">更新于 {d["updated"]}</text>')
    defs = (f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".18"/>'
            f'<stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="lineg" x1="0" x2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="{ACC}"/></linearGradient>')
    blobs = [("violet", 120, 30, 220), ("teal", 640, 440, 220), ("indigo", 1100, 60, 220)]
    write("generated/stats.svg", frame(W, H, f'<g font-family="{SANS}">{"".join(body)}</g>', blobs, defs))


def snake_placeholder():
    for name in ("snake-dark.svg", "snake-light.svg"):
        rel = f"generated/{name}"
        if os.path.exists(os.path.join(OUT, rel)):
            continue
        body = (f'<text x="600" y="106" text-anchor="middle" font-family="{SANS}" font-size="17" fill="{DIM}">'
                f'贡献足迹将在首次运行 GitHub Action 后出现</text>')
        write(rel, frame(1200, 200, body, [("teal", 200, 200, 180), ("indigo", 1000, 0, 180)]))


if __name__ == "__main__":
    banner(); about(); focus(); now(); titles(); footer()
    # 数据卡片和贡献蛇由 Action 每天生成；这里只在文件不存在时写入占位图，避免首次运行前出现破图
    if not os.path.exists(os.path.join(OUT, "generated", "stats.svg")):
        stats_card(None)
    snake_placeholder()
    print("done →", OUT)
