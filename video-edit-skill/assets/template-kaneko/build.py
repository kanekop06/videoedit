#!/usr/bin/env python3
"""/video-edit "kaneko" template: the approved build of @paulokaneko.ia's first reel (teste-claude-code-v1, v6, PT-BR,
7.9s hook cut from one 4K phone clip). Copy it into a project, keep the machinery, rewrite the content.
Look spec: references/looks.md -> "Kaneko". Brand source: design-system-kaneko (Inter 800 + Instrument Serif italic,
azul #0592FA as the only accent).

Example beats (segments.json ids: hook 0-3.5 wide, fica 3.5-7.9 1.15x punch-in):
  0.00-1.42  notification slides down + "se VOCÊ, assim" + "COMO EU," behind the head; slam-in zoom, punch on "eu"
  1.42-3.50  zoom OUT to a rounded framed shot on beige grid paper, job-board card above; cursor clicks
             "Candidatar-se" on "estágio" -> green "Candidatura enviada" (fictional company, no real logo)
  3.50-4.40  zoom back in on the cut, "fica nesse / VÍDEO" behind the head
  4.40-5.56  "porque eu fiz / uma coisa" serif highlight, punch-in on "coisa"
  5.56-7.32  "com as minhas / candidaturas" serif + azul underline, behind the head
  7.32-end   "que eu acho que VAI..." slow push-in to the end (cliffhanger)

Machinery to keep: words() (per-word blur-pop, serif .ser word with drawn azul underline, back=True lines sit under
the cutout), camera() zoom helper z(), the framed-shot zoom out/in, notif(), job_card() (cursor + ripple live inside
the button so the click lands whatever the layout), audio() lane allocator, CSS tokens, SAFE_GUIDE.
Content to rewrite: LINES (word times from words.json), SPLIT_IN/OUT, CLICK, COISA, notif/job card copy, SFX,
segment ids in T[...].
Colour: run scripts/grade.py first; the <video> tags read assets/aroll_graded.mp4 + assets/subject_graded.webm
(GRADE stays 'none': CSS grades were too subtle).

PY build.py            writes index.html
PY build.py --safe     same + red Instagram safe-zone guide (snapshots only, never render with it)
"""
import json
import os
import shutil
import subprocess
import sys

SAFE = '--safe' in sys.argv or bool(os.environ.get('SAFE'))
DUR = float(subprocess.run([shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=duration', '-of', 'csv=p=0', 'assets/aroll.mp4'],
                           capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[0])
with open('segments.json', encoding='utf-8') as _f:
    SEG = {s['id']: s for s in json.load(_f)}
T = {k: s['frame'] / 30 - .002 if s['frame'] else 0.0 for k, s in SEG.items()}
FICA = T['fica']

# design-system-kaneko tokens
AZUL, AZUL_TXT, AZUL_TINT = '#0592FA', '#0062C4', '#E5F3FF'
INK, MUTED, HAIR, SURF_ALT = '#0A0A0B', '#5B6270', '#E2E6EC', '#F3F6FA'
GRADE = 'none'   # the cinematic grade is baked by scripts/grade.py (template-kaneko/grade.txt = approved 'neutro')
PAPER, PAPER_LINE = '#F3EDE2', 'rgba(70,52,30,.08)'   # beige grid paper behind UI inserts
LI_BLUE, LI_GREEN = '#0A66C2', '#057642'   # job-board UI colours for the insert (no logo, fictional company)
UI_FONT = "'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif"

SPLIT_IN, SPLIT_OUT = 1.42, FICA          # framed-shot section ("está aplicando para a vaga de estágio")
CLICK = 2.70                              # cursor click lands on "estágio" (2.74)
COISA = 5.36

C = 'left:0;right:0;text-align:center;'
# (id, start, end, style, back, [(t, text, span classes)], line class)
# line classes: cap = Inter 800 lead-in, big = Inter 800 behind-head word, ser = Instrument Serif italic + azul underline
LINES = [
    ('hA', 0.00, SPLIT_IN, C + 'top:405px', False, [(0.00, 'se', ''), (0.26, 'você,', 'az'), (0.80, 'assim', '')], 'cap'),
    ('hB', 1.00, SPLIT_IN, C + 'top:515px', True, [(1.00, 'como', ''), (1.20, 'eu,', '')], 'big'),
    ('jA', 1.50, SPLIT_OUT, C + 'top:236px', False, [(1.50, 'está', ''), (1.60, 'aplicando', ''), (2.12, 'para', ''), (2.28, 'a', '')], 'cap sm dark'),
    ('jB', 2.44, SPLIT_OUT, C + 'top:300px', False, [(2.44, 'vaga', ''), (2.56, 'de', ''), (2.74, 'estágio', 'ser')], 'cap md dark'),
    ('fA', FICA, 4.40, C + 'top:330px', False, [(3.56, 'fica', ''), (3.88, 'nesse', '')], 'cap'),
    ('fB', 4.06, 4.40, C + 'top:470px', True, [(4.10, 'vídeo', '')], 'big xl'),
    ('pA', 4.40, 5.56, C + 'top:300px', False, [(4.42, 'porque', ''), (4.74, 'eu', ''), (4.98, 'fiz', '')], 'cap'),
    ('pB', 5.06, 5.56, C + 'top:392px', False, [(5.10, 'uma', ''), (5.36, 'coisa', 'ser')], 'cap lg'),
    ('cA', 5.56, 7.32, C + 'top:300px', False, [(5.58, 'com', ''), (5.86, 'as', ''), (6.08, 'minhas', '')], 'cap'),
    ('cB', 6.26, 7.32, C + 'top:452px', True, [(6.30, 'candidaturas', 'ser')], 'cap ser-xl'),
    ('vA', 7.32, DUR, C + 'top:330px', False, [(7.36, 'que', ''), (7.48, 'eu', ''), (7.56, 'acho', ''), (7.70, 'que', ''),
                                                (7.78, 'vai...', 'az')], 'cap'),
]


def words():
    html, tw = [], []
    for lid, a, b, st, back, ws, cls in LINES:
        spans = []
        for k, (t, txt, wc) in enumerate(ws):
            wid = f'{lid}-{k}'
            if 'ser' in wc:   # serif highlight word: its own underline that draws in after the word lands
                spans.append(f'<span id="{wid}" class="w ser">{txt}<i id="{wid}u" class="ul"></i></span>')
                tw += [f"gsap.set('#{wid}u',{{scaleX:0}});",
                       f"tl.to('#{wid}u',{{scaleX:1,duration:.34,ease:'power3.out'}},{t + .14:.3f});"]
            else:
                spans.append(f'<span id="{wid}" class="w {wc}">{txt}</span>')
            tw.append(f"gsap.set('#{wid}',{{autoAlpha:0}});")
            tw.append(f"tl.fromTo('#{wid}',{{autoAlpha:0,scale:1.2,filter:'blur(18px)'}},{{autoAlpha:1,scale:1,filter:'blur(0px)',"
                      f"duration:.22,ease:'power3.out',immediateRender:false}},{max(a, t - .05):.3f});")
        html.append((back, f'<div id="{lid}" class="ln {cls}" style="{st}">{" ".join(spans)}</div>'))
        if b < DUR - .01:
            tw += [f"tl.to('#{lid}',{{autoAlpha:0,filter:'blur(12px)',duration:.12,ease:'power2.in'}},{b - .12:.3f});",
                   f"tl.set('#{lid}',{{autoAlpha:0}},{b:.3f});"]
    return html, tw


def notif():
    """hook image: a push notification slides down over the top band (generic job app, no logo)"""
    html = ['<div id="notif"><div class="nicon"><svg width="46" height="46" viewBox="0 0 24 24"><path d="M9 6V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V6h4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2zm1.5 0h3V4.5h-3z" fill="#fff"/></svg></div>'
            '<div class="ntx"><div class="nhd"><b>Vagas</b><span>agora</span></div><div class="nmsg">Novas vagas de <b>estágio</b> para você</div></div></div>']
    tw = ["gsap.set('#notif',{autoAlpha:0,y:-160,scale:.96});",
          "tl.to('#notif',{autoAlpha:1,y:0,scale:1,duration:.42,ease:'back.out(1.4)'},.12);",
          f"tl.to('#notif',{{y:-180,autoAlpha:0,duration:.24,ease:'power2.in'}},{SPLIT_IN - .3:.3f});",
          f"tl.set('#notif',{{autoAlpha:0}},{SPLIT_IN:.3f});"]
    return html, tw


def job_card():
    """job-board posting recreated from the reference layout; fictional company, generic mark, no real logo.
    Cursor + ripple live inside #apply, so the click lands on the button whatever the text wraps to."""
    chk = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z" fill="currentColor"/></svg>'
    sun = ('<svg width="46" height="46" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" fill="#fff"/><g stroke="#fff" stroke-width="2" '
           'stroke-linecap="round"><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></g></svg>')
    shield = ('<svg class="shield" width="40" height="40" viewBox="0 0 24 24"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z" fill="none" '
              'stroke="#666" stroke-width="1.8"/><path d="m8.5 12 2.4 2.4 4.6-4.8" fill="none" stroke="#666" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round"/></svg>')
    ext = ('<svg width="26" height="26" viewBox="0 0 24 24"><path d="M14 3h7v7h-2V6.4l-8.3 8.3-1.4-1.4L17.6 5H14zM5 5h6v2H5v12h12v-6h2v6a2 2 0 0 1-2 '
           '2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2" fill="#fff"/></svg>')
    html = f"""<div id="job"><div class="jc">
  <div class="jco"><div class="jlogo">{sun}</div><span>Grupo Solara</span></div>
  <div class="jt">Estagiário de Operações de Vendas e Marketing {shield}</div>
  <div class="jm">São Paulo e Região &middot; há 2 dias &middot; <b>93 pessoas</b> clicaram em Candidate-se</div>
  <div class="jchips"><span>{chk}Presencial</span><span>{chk}Meio período</span></div>
  <div class="jbtns"><div id="apply" class="jbtn"><span id="a1">Candidatar-se {ext}</span><span id="a2">{chk}Candidatura enviada</span>
  <div id="ripple"></div>
  <svg id="cursor" width="64" height="64" viewBox="0 0 24 24"><path d="M4 2l15 9.2-6.6 1.3 3.9 7.4-2.9 1.5-3.9-7.5L4 18.7z" fill="{INK}" stroke="#fff" stroke-width="1.3" stroke-linejoin="round"/></svg></div>
  <div class="jbtn ghost">Salvar</div></div>
</div></div>"""
    tw = ["gsap.set('#job',{autoAlpha:0,y:70,scale:.94});",
          f"tl.to('#job',{{autoAlpha:1,y:0,scale:1,duration:.5,ease:'back.out(1.5)'}},{SPLIT_IN + .12:.3f});",
          "gsap.set('#a2',{autoAlpha:0});",
          "gsap.set('#cursor',{x:560,y:190,autoAlpha:0});",
          f"tl.to('#cursor',{{autoAlpha:1,duration:.15}},{SPLIT_IN + .45:.3f});",
          f"tl.to('#cursor',{{x:150,y:22,duration:.62,ease:'power3.inOut'}},{CLICK - .72:.3f});",
          f"tl.to('#cursor',{{scale:.82,duration:.07,yoyo:true,repeat:1,ease:'power1.inOut'}},{CLICK - .04:.3f});",
          f"tl.to('#apply',{{scale:.95,duration:.07,yoyo:true,repeat:1,ease:'power1.inOut'}},{CLICK - .04:.3f});",
          "gsap.set('#ripple',{autoAlpha:0,scale:.2});",
          f"tl.fromTo('#ripple',{{autoAlpha:.5,scale:.2}},{{autoAlpha:0,scale:2.4,duration:.5,ease:'power2.out',immediateRender:false}},{CLICK:.3f});",
          f"tl.set('#a1',{{autoAlpha:0}},{CLICK + .06:.3f});",
          f"tl.set('#apply',{{backgroundColor:'{LI_GREEN}'}},{CLICK + .06:.3f});",
          f"tl.fromTo('#a2',{{autoAlpha:0,y:12}},{{autoAlpha:1,y:0,duration:.22,ease:'power2.out',immediateRender:false}},{CLICK + .06:.3f});",
          f"tl.to('#cursor',{{x:260,y:180,autoAlpha:0,duration:.4,ease:'power2.in'}},{CLICK + .35:.3f});",
          f"tl.to('#job',{{autoAlpha:0,y:-40,scale:.96,duration:.2,ease:'power2.in'}},{SPLIT_OUT - .2:.3f});",
          f"tl.set('#job',{{autoAlpha:0}},{SPLIT_OUT:.3f});"]
    return [html], tw


def camera():
    """zooms on #stage (origin 50% 45%): push-ins, the framed shot (zoom out), the punch on 'coisa'"""
    z = lambda a, b, t, d, ease: (f"tl.fromTo('#stage',{{scale:{a}}},{{scale:{b},duration:{d:.3f},ease:'{ease}',"
                                  f"immediateRender:false}},{t:.3f});")
    tw = [f"gsap.set('.g',{{filter:'{GRADE}'}});",
          # hook: slam-in zoom on frame 1, slow drift, punch on "eu"
          z(1.28, 1.0, 0, .5, 'expo.out'),
          z(1.0, 1.04, .5, 1.17 - .5, 'none'),
          z(1.04, 1.12, 1.18, .14, 'power3.out'),
          # zoom out to the framed shot: frame 562x998 centred at x 540, top ~889, rounded corners
          f"tl.to('#stage',{{scale:.52,y:474,borderRadius:58,boxShadow:'0 30px 70px rgba(70,52,30,.28)',duration:.5,ease:'expo.inOut'}},{SPLIT_IN - .1:.3f});",
          f"tl.to('#stage',{{scale:.545,duration:{SPLIT_OUT - SPLIT_IN - .45:.3f},ease:'none'}},{SPLIT_IN + .4:.3f});",
          # back in on the cut
          f"tl.fromTo('#stage',{{scale:.6,y:390,borderRadius:58}},{{scale:1,y:0,borderRadius:0,boxShadow:'0 0 0 rgba(0,0,0,0)',"
          f"duration:.42,ease:'expo.out',immediateRender:false}},{FICA:.3f});",
          z(1, 1.04, FICA + .43, 4.40 - FICA - .43, 'none'),
          z(1.04, 1.0, 4.40, .3, 'power2.out'),
          z(1.0, 1.15, COISA - .02, .2, 'power3.out'),
          z(1.15, 1.0, 5.56, .3, 'power3.out'),
          z(1.0, 1.035, 5.86, 7.32 - 5.86, 'none'),
          z(1.035, 1.11, 7.32, DUR - 7.32, 'power1.in')]
    return tw


SFX = [('whoosh-short', 0.0, .18), ('whoosh-short', SPLIT_IN - .12, .24), ('click', CLICK, .7),
       ('whoosh-short', FICA - .06, .24), ('pop', COISA, .16), ('pop', 6.30, .14)]
SFX_LEN = {'whoosh-short': .57, 'pop': .72, 'sparkle': 1.8, 'click': .3, 'click-soft': .37}
SFX_GAIN = 0.75   # sounds sit 25% under the original levels: subtle, never louder than the voice


def audio():
    out, lanes = [], []
    for k, (name, t, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
        t = max(t, 0.0)
        d = min(SFX_LEN[name], DUR - t)
        lane = next((i for i, end in enumerate(lanes) if end <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol * SFX_GAIN:.3f}"></audio>')
    return out


CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{PAPER}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background-color:{PAPER};
  background-image:linear-gradient({PAPER_LINE} 2px,transparent 2px),linear-gradient(90deg,{PAPER_LINE} 2px,transparent 2px);
  background-size:60px 60px;background-position:30px 30px}}
#stage{{position:absolute;inset:0;transform-origin:50% 45%;overflow:hidden;background:#000}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#bgv{{z-index:0}}
#cutwrap{{position:absolute;inset:0;z-index:4}}

/* type: Inter 800 ink on the light wall; serif italic highlight with the azul underline */
.ln{{position:absolute;z-index:8;color:#fff;font-family:Inter;font-weight:800;white-space:nowrap;
  text-shadow:0 3px 18px rgba(0,0,0,.42),0 1px 4px rgba(0,0,0,.38)}}
.ln.back{{z-index:3}}
.ln.dark{{color:{INK};text-shadow:none}}
#tone{{position:absolute;inset:0;z-index:5;pointer-events:none;mix-blend-mode:soft-light;
  background:linear-gradient(180deg,rgba(20,70,110,.16),rgba(255,190,150,.10))}}
#vig{{position:absolute;inset:0;z-index:5;pointer-events:none;background:radial-gradient(110% 70% at 50% 45%,rgba(0,0,0,0) 60%,rgba(0,0,0,.18) 100%)}}
.w{{display:inline-block;transform-origin:50% 60%}}
.cap{{font-size:76px;letter-spacing:-.03em;line-height:.95}}
.cap.sm{{font-size:60px}}
.cap.md{{font-size:104px}}
.cap.lg{{font-size:128px}}
.big{{font-size:200px;letter-spacing:-.045em;line-height:.9}}
.big.xl{{font-size:236px}}
.ser{{position:relative;font-family:'Instrument Serif';font-style:italic;font-weight:400;letter-spacing:-.01em;font-size:1.22em;padding:0 .04em}}
.ser-xl{{font-size:156px}}
.ul{{position:absolute;left:.06em;right:.04em;bottom:.02em;height:.075em;min-height:8px;border-radius:8px;background:{AZUL};
  transform-origin:0 50%;display:block}}
.az{{color:{AZUL}}}

/* hook notification */
#notif{{position:absolute;left:50px;right:50px;top:232px;z-index:9;display:flex;gap:24px;align-items:center;padding:26px 30px;
  background:rgba(250,250,252,.96);border-radius:40px;box-shadow:0 20px 50px rgba(0,0,0,.28)}}
.nicon{{width:84px;height:84px;border-radius:20px;background:{AZUL};display:flex;align-items:center;justify-content:center;flex:none}}
.ntx{{flex:1;font-family:{UI_FONT};color:#111}}
.nhd{{display:flex;justify-content:space-between;font-size:28px;color:#6b6b70}}
.nhd b{{color:#111;font-weight:700}}
.nmsg{{font-size:33px;margin-top:4px}}

/* job card: job-board layout from the reference, fictional company */
#job{{position:absolute;left:50px;top:452px;width:980px;z-index:9}}
.jc{{background:#fff;border-radius:28px;padding:40px 42px 44px;font-family:{UI_FONT};color:rgba(0,0,0,.9);box-shadow:0 26px 60px rgba(70,52,30,.20),0 2px 0 rgba(70,52,30,.06)}}
.jco{{display:flex;gap:20px;align-items:center;font-size:30px;font-weight:600}}
.jlogo{{width:76px;height:76px;border-radius:10px;background:#E8590C;display:flex;align-items:center;justify-content:center}}
.jt{{font-size:46px;line-height:1.18;font-weight:600;margin:26px 0 18px;letter-spacing:-.01em}}
.shield{{vertical-align:-6px}}
.jm{{font-size:25px;white-space:nowrap;color:#666;line-height:1.45}}
.jm b{{color:#666;font-weight:600}}
.jchips{{display:flex;gap:16px;margin:28px 0 30px}}
.jchips span{{display:flex;align-items:center;gap:8px;font-size:29px;font-weight:600;color:#333;border:2px solid #666;border-radius:999px;padding:10px 24px}}
.jbtns{{display:flex;gap:18px}}
.jbtn{{position:relative;height:82px;border-radius:999px;background:{LI_BLUE};color:#fff;font-size:31px;font-weight:600;display:flex;
  align-items:center;justify-content:center;padding:0 36px;min-width:430px}}
.jbtn span{{position:absolute;white-space:nowrap;display:flex;align-items:center;gap:10px}}
.jbtn.ghost{{background:#fff;color:{LI_BLUE};border:2px solid {LI_BLUE};min-width:0;padding:0 36px}}
#ripple{{position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;background:#fff;z-index:2}}
#cursor{{position:absolute;left:0;top:0;z-index:3;filter:drop-shadow(0 6px 10px rgba(0,0,0,.3))}}
'''

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def build():
    w_html, w_tw = words()
    back = [h for b, h in w_html if b]
    front = [h for b, h in w_html if not b]
    j_html, j_tw = job_card()
    n_html, n_tw = notif()
    tweens = camera() + w_tw + j_tw + n_tw
    nl = '\n'
    return f'''<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio())}
  <div id="stage">
    <video id="bgv" class="full g" src="assets/aroll_graded.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="0"></video>
{nl.join(back)}
    <div id="cutwrap"><video id="cut" class="full g" src="assets/subject_graded.webm" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="1"></video></div>

  </div>
{nl.join(front)}
{nl.join(j_html)}
{nl.join(n_html)}
{SAFE_GUIDE if SAFE else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(tweens)}
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''


with open('index.html', 'w', encoding='utf-8', newline='\n') as _f:
    _f.write(build())
print(f'wrote index.html {DUR:.3f}s  cut {FICA:.3f}  split {SPLIT_IN}-{SPLIT_OUT:.3f}  click {CLICK}')
