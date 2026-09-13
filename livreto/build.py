#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o livreto do vendeaqui → livreto/index.html (rota /livreto/).

    python3 livreto/build.py

Doutrina herdada do livreto da casa (repo do ERP, `livreto/CLAUDE.md`):
  - Long-scroll, capítulos alternando branco/névoa, storyboards de fluxo.
  - Selo só onde é verdade. Nunca vender roadmap como pronto → capítulo "O que não faz".
  - NUNCA editar o HTML gerado. Edita-se `content.py` (95% das mudanças) ou este arquivo.

O site é estático (GitHub Pages, sem runtime), então o PDF é gerado no CI por Chromium
headless (`livreto/build_pdf.sh`) e commitado de volta — ver `.github/workflows/livreto.yml`.

PEGADINHAS DO PRINT (quebram em silêncio — não mexer sem entender):
  - `@media print` PRECISA forçar `.rev{opacity:1}` — senão o PDF sai EM BRANCO.
  - `print-color-adjust:exact` — senão hero/CTA/fotos saem sem cor.
  - `break-inside:avoid` só nas unidades atômicas (card, painel). NUNCA por capítulo.
  - `@page{size:A4}` — senão o Chrome imprime em Letter.
  - Traço de SVG: `stroke` explícito no <g> do `scene()`, nunca classe utilitária.

Sem Google Fonts de propósito (mesma doutrina da home): a política de privacidade afirma
que o site não entrega o IP do visitante a terceiros.
"""
import pathlib, importlib.util, datetime, hashlib

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
OUT  = REPO / "livreto" / "index.html"

sp = importlib.util.spec_from_file_location("content", str(ROOT / "content.py"))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)

WA = C.WA + C.WA_TXT

# --------------------------------------------------------------------- cenas
# Line-art 56×44. As chaves casam 1:1 com as cenas citadas em `content.py > BOARDS`.
SCENES = {
 "conversa":  '<path d="M10 11h36v21H25l-8 6v-6h-7z"/><path d="M17 19h22M17 25h14"/>',
 "atividade": '<rect x="13" y="8" width="26" height="30" rx="2"/><path d="M19 16h14M19 22h14M19 28h7"/>'
              '<path d="M33 31l3 3 7-7"/>',
 "etapa":     '<path d="M9 37h10v-8h10v-8h10v-8h7"/><path d="M40 8h6v6"/>',
 "proxima":   '<path d="M22 30c-4-3-6-6-6-10a12 12 0 0 1 24 0c0 4-2 7-6 10z"/><path d="M23 34h10M24 38h8"/>',
 "ganho":     '<circle cx="28" cy="22" r="13"/><path d="M22 22l4 4 8-8"/>',
 "site":      '<rect x="9" y="9" width="38" height="27" rx="3"/><path d="M9 16h38"/><path d="M15 23h14M15 29h9"/>'
              '<rect x="33" y="22" width="8" height="8" rx="1"/>',
 "planilha":  '<rect x="11" y="9" width="34" height="27" rx="2"/><path d="M11 18h34M11 27h34M23 9v27M34 9v27"/>',
 "time":      '<circle cx="20" cy="16" r="5"/><circle cx="36" cy="16" r="5"/>'
              '<path d="M10 36c0-6 4-10 10-10s10 4 10 10"/><path d="M29 29c1-2 4-3 7-3 6 0 10 4 10 10"/>',
}
def scene(n):
    return ('<svg class="scene" viewBox="0 0 56 44" aria-hidden="true">'
            f'<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round">{SCENES[n]}</g></svg>')

# ---------------------------------------------------------------- componentes
_CHAP = [0]
def chapter(cid, eyebrow, h2, lead, *blocks):
    bg = "nevoa" if _CHAP[0] % 2 else ""   # alterna sozinho — não passe bg
    _CHAP[0] += 1
    return f'''<section class="cap {bg}" id="{cid}" aria-label="{eyebrow}">
  <div class="cap-in">
    <div class="cap-head rev"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    {"".join(blocks)}
  </div>
</section>'''

def tag(t):
    return f'<span class="tg">{t}</span>' if t else ''

def cards(items, cor):
    cs = "".join(f'<article class="fc"><span class="fc-mk"></span><h3>{t}{tag(g)}</h3><p>{d}</p></article>'
                 for t, d, g in items)
    return f'<div class="fgrid c-{cor} rev">{cs}</div>'

def board(key):
    cor, titulo, panels = C.BOARDS[key]
    cells = []
    for i, (sc, h, cap) in enumerate(panels):
        cells.append(f'<li class="bp"><span class="bp-n">{i+1}</span>'
                     f'<span class="bp-art">{scene(sc)}</span><b>{h}</b><i>{cap}</i></li>')
        if i < len(panels) - 1:
            cells.append('<li class="bp-arr" aria-hidden="true">→</li>')
    return (f'<figure class="board c-{cor} rev"><figcaption class="board-cap">'
            f'<span class="eyebrow">Como funciona</span><b>{titulo}</b></figcaption>'
            f'<ol class="board-strip">{"".join(cells)}</ol></figure>')

def foto(slug, alt):
    return (f'<figure class="shot"><img src="/assets/{slug}.jpg" alt="{alt}" '
            f'loading="lazy" decoding="async"></figure>')

def mrow(media, h, p, flip=False):
    return (f'<div class="mrow{" flip" if flip else ""} rev"><div class="m-media">{media}</div>'
            f'<div class="m-copy"><h3>{h}</h3><p>{p}</p></div></div>')

def lista(items):
    return ('<ul class="check rev">' +
            "".join(f'<li><span class="ck"></span>{t}</li>' for t in items) + '</ul>')

def kanban():
    cols = []
    for nome, total, leads in C.KANBAN:
        cs = "".join(
            f'<div class="kb-card {cls}"><strong>{n}</strong><span>{sub}</span>'
            f'{f"<span class=kb-pulso>{pulso}</span>" if pulso else ""}</div>'
            for n, sub, pulso, cls in leads)
        cols.append(f'<div class="kb-col"><h4>{nome} <b>{total}</b></h4>{cs}</div>')
    return ('<figure class="kanban rev" role="img" aria-label="Exemplo ilustrativo de um quadro de '
            'vendas com as colunas Lead, Contato, Proposta e Ganho.">' + "".join(cols) +
            '<figcaption class="kb-leg">Exemplo ilustrativo — nomes e números não são de clientes '
            'reais.</figcaption></figure>')

# ---------------------------------------------------------------------- CSS
CSS = """
:root{
  --branco:#fff;--nevoa:#f5f5f7;--preto:#000;
  --tinta:#1d1d1f;--tinta-2:#6e6e73;--claro:#f5f5f7;--claro-2:#a1a1a6;
  /* #16A34A com branco = 3,30:1 → só decorativo. Texto e botão = #15803D (5,02:1). */
  --verde:#16A34A;--verde-texto:#15803D;--verde-esc:#166534;--verde-claro:#4ADE80;--verde-leve:#E8F5EC;
  --linha:rgba(0,0,0,.12);--maxw:1120px;
  --sec:var(--verde-texto);
  --ease:cubic-bezier(.45,0,.55,1);
}
.c-verde{--sec:#15803D;--soft:#E8F5EC}
.c-petroleo{--sec:#0F766E;--soft:#E0F2F1}
.c-ambar{--sec:#A16207;--soft:#FEF6D8}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--branco);color:var(--tinta);
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter','Segoe UI',Roboto,system-ui,sans-serif;
  font-size:17px;line-height:1.4705882353;letter-spacing:-.022em;-webkit-font-smoothing:antialiased}
h1,h2,h3{margin:0;font-weight:600;line-height:1.06;letter-spacing:-.015em;text-wrap:balance}
p{margin:0}ul,ol{margin:0;padding:0;list-style:none}
a{color:var(--verde-texto);text-decoration:none}
img{display:block;max-width:100%}
:focus-visible{outline:3px solid var(--verde);outline-offset:3px;border-radius:6px}
.eyebrow{display:block;font-size:21px;font-weight:600;letter-spacing:.011em;color:var(--sec);margin-bottom:8px}
.lead{font-size:21px;line-height:1.381;letter-spacing:.011em;color:var(--tinta-2);margin-top:14px}

.nav{position:sticky;top:0;z-index:50;height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(20px,4vw,40px);background:rgba(255,255,255,.72);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(0,0,0,.08)}
.nav .brand{display:flex;align-items:center;gap:8px;font-weight:600;font-size:17px;color:var(--tinta);letter-spacing:-.02em}
.nav .brand img{width:24px;height:24px;border-radius:6px}
.nav .brand .tld{color:var(--verde-texto)}
.nav-r{display:flex;align-items:center;gap:clamp(14px,3vw,26px);font-size:13px}
/* os <a> vivem DENTRO de .nav-links — sem display:flex aqui eles saem colados. */
.nav-links{display:inline-flex;align-items:center;gap:clamp(14px,2.2vw,24px)}
.nav-r a{color:var(--tinta);opacity:.85}
.nav-r a:hover{opacity:1;color:var(--verde-texto)}
.nav-cta{background:var(--verde-texto);color:#fff!important;padding:6px 14px;border-radius:980px;font-weight:500}
@media(max-width:760px){.nav-links{display:none}}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--verde-texto);color:#fff;
  padding:12px 22px;border-radius:980px;font-weight:400;font-size:17px;letter-spacing:-.022em;
  transition:background-color .1s linear}
.btn:hover{background:var(--verde-esc)}
.btn-branco{background:#fff;color:var(--tinta)}
.btn-branco:hover{background:#e8e8ed}
.btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:32px}

/* hero */
.hero{background:var(--preto);color:var(--claro);text-align:center;padding:clamp(64px,9vh,104px) 24px 0;overflow:hidden;
  background-image:radial-gradient(900px 500px at 50% -10%,rgba(22,163,74,.45),transparent 62%)}
.hero .eyebrow{color:var(--verde-claro)}
.hero h1{font-size:clamp(40px,4.4vw+14px,76px);color:#fff;max-width:16ch;margin:0 auto}
.hero .sub{margin:22px auto 0;max-width:56ch;font-size:21px;line-height:1.4;color:var(--claro-2);letter-spacing:.011em}
.hero-stage{margin:56px auto 0;max-width:900px}
/* a foto sobe do hero e é cortada pelo fim da seção; object-position segura as cabeças. */
/* ⚠️ `height:auto` obrigatório: o atributo height="1067" do <img> vira altura CSS e anula o
   aspect-ratio — a foto saía com 1067px e ocupava uma página inteira do PDF. */
.hero-stage img{width:100%;height:auto;aspect-ratio:16/8;object-fit:cover;object-position:center 22%;
  border-radius:24px 24px 0 0;box-shadow:0 -10px 60px rgba(22,163,74,.28)}

.credo{max-width:960px;margin:0 auto;padding:clamp(80px,10vw,130px) 24px;text-align:center}
.credo h2{font-size:clamp(30px,3.4vw+10px,52px);letter-spacing:-.02em}
.credo .g{color:var(--verde-texto)}

/* quadro ilustrativo */
.kanban{max-width:var(--maxw);margin:0 auto clamp(64px,8vw,110px);padding:22px;background:#0f1411;border-radius:28px;
  color:var(--claro);display:grid;gap:14px;grid-template-columns:repeat(4,minmax(0,1fr));font-variant-numeric:tabular-nums;
  break-inside:avoid}
@media(max-width:860px){.kanban{grid-template-columns:repeat(2,minmax(0,1fr));margin-left:24px;margin-right:24px}}
.kb-col h4{margin:0 0 10px;font-size:13px;font-weight:600;color:var(--claro-2);display:flex;justify-content:space-between}
.kb-col h4 b{color:var(--claro)}
.kb-card{background:#1a211c;border-radius:14px;padding:12px 12px 10px;margin-bottom:10px;border-left:3px solid var(--verde)}
.kb-card strong{display:block;font-size:14px;font-weight:600;letter-spacing:-.01em}
.kb-card span{display:block;font-size:12px;color:var(--claro-2);margin-top:3px}
.kb-card .kb-pulso{color:var(--verde-claro)}
.kb-card.frio{border-left-color:#71717a}
.kb-card.ganho{border-left-color:#FACC15}
.kb-leg{grid-column:1/-1;margin:4px 0 0;font-size:13px;color:var(--claro-2)}

/* capítulos */
.cap{padding:clamp(72px,9vw,120px) 0}
.cap.nevoa{background:var(--nevoa)}
.cap-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.cap-head{max-width:760px}
.cap-head h2{font-size:clamp(30px,2.4vw+14px,48px);letter-spacing:-.01em;margin-top:2px}

.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:44px}
.fc{background:var(--branco);border:1px solid var(--linha);border-radius:20px;padding:26px 24px;break-inside:avoid}
.cap.nevoa .fc{background:#fff;border-color:rgba(0,0,0,.06)}
.fc-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--sec);margin-bottom:16px}
.fc h3{font-size:20px;letter-spacing:-.01em}
.fc p{margin-top:8px;color:var(--tinta-2);font-size:16px;line-height:1.5}
.tg{display:inline-block;margin-left:8px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--sec);background:var(--soft);padding:3px 8px;border-radius:980px;vertical-align:middle}

/* storyboard */
.board{margin:48px 0 0;padding:30px;border-radius:24px;background:var(--soft);break-inside:avoid}
.board-cap{margin-bottom:22px}
.board-cap b{display:block;font-size:22px;font-weight:600;letter-spacing:-.01em}
.board-strip{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.bp{flex:1 1 170px;background:#fff;border-radius:16px;padding:20px 18px;position:relative;break-inside:avoid}
.bp-n{position:absolute;top:14px;right:16px;font-size:12px;font-weight:700;color:var(--sec)}
.bp-art{display:block;color:var(--sec)}
.scene{width:56px;height:44px}
.bp b{display:block;margin-top:12px;font-size:17px;font-weight:600;letter-spacing:-.01em}
.bp i{display:block;margin-top:6px;font-style:normal;font-size:14.5px;line-height:1.45;color:var(--tinta-2)}
.bp-arr{display:flex;align-items:center;color:var(--sec);font-size:20px;opacity:.55}
@media(max-width:860px){.bp-arr{display:none}}

/* media row */
.mrow{display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center;margin-top:48px}
.mrow.flip .m-media{order:2}
@media(max-width:860px){.mrow{grid-template-columns:1fr}.mrow.flip .m-media{order:0}}
.m-copy h3{font-size:26px;letter-spacing:-.012em}
.m-copy p{margin-top:12px;color:var(--tinta-2);font-size:17px;line-height:1.5}
.shot img{width:100%;aspect-ratio:3/2;object-fit:cover;object-position:center 28%;border-radius:20px}

/* checklist */
.check{margin-top:36px;display:grid;gap:14px}
.check li{display:flex;gap:12px;align-items:flex-start;font-size:17px;line-height:1.45;break-inside:avoid}
.ck{flex:0 0 auto;width:20px;height:20px;margin-top:2px;border-radius:50%;background:var(--verde-leve);position:relative}
.ck::after{content:"";position:absolute;left:6px;top:5px;width:5px;height:9px;border:2px solid var(--verde-esc);
  border-top:0;border-left:0;transform:rotate(42deg)}

/* verticais */
.verticais{display:flex;flex-wrap:wrap;gap:10px;margin-top:36px}
.verticais span{background:#fff;border:1px solid var(--linha);border-radius:980px;padding:8px 16px;font-size:15px;letter-spacing:-.01em}

/* preço */
.planos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:44px}
@media(max-width:860px){.planos{grid-template-columns:1fr}}
.plano{border:1px solid var(--linha);border-radius:24px;padding:30px 26px;background:#fff;break-inside:avoid}
.plano .nome{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta-2)}
.plano .v{margin-top:14px;font-size:46px;font-weight:600;letter-spacing:-.03em;line-height:1}
.plano .u{margin-top:6px;font-size:14px;color:var(--tinta-2)}
.plano p{margin-top:14px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}
.plano.hi{background:var(--preto);border-color:var(--preto);color:var(--claro)}
.plano.hi .nome{color:var(--verde-claro)}
.plano.hi .v{color:#fff}
.plano.hi .u,.plano.hi p{color:var(--claro-2)}
.naos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:20px}
@media(max-width:860px){.naos{grid-template-columns:1fr}}
.nao{border-radius:20px;padding:24px;background:#fff;border:1px solid var(--linha);break-inside:avoid}
.nao h4{margin:0;font-size:18px;font-weight:600;letter-spacing:-.01em}
.nao p{margin-top:8px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}

/* lineup */
.lineup{background:var(--preto);color:var(--claro);padding:clamp(80px,10vw,130px) 0}
.lineup-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.lineup h2{font-size:clamp(30px,2.4vw+14px,48px);color:#fff}
.lineup .lead{color:var(--claro-2)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:44px}
.tile{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:24px;break-inside:avoid}
.tile h3{font-size:18px;color:#fff}
.tile p{margin-top:8px;font-size:15px;line-height:1.5;color:var(--claro-2)}
.tile-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--verde-claro);margin-bottom:14px}
.tile .tg{color:var(--verde-claro);background:rgba(74,222,128,.14)}

/* cta / download / rodapé */
.cta{text-align:center;padding:clamp(88px,11vw,140px) 24px;background:
  radial-gradient(1100px 560px at 50% 0%,rgba(22,163,74,.42),transparent 65%),#0a0d0b;color:var(--claro)}
.cta h2{font-size:clamp(30px,3vw+12px,52px);color:#fff;max-width:18ch;margin:0 auto}
.cta p{margin:20px auto 0;max-width:52ch;font-size:19px;line-height:1.5;color:var(--claro-2)}
.dl{text-align:center;padding:clamp(64px,8vw,96px) 24px;background:var(--nevoa)}
.dl h2{font-size:30px}
.dl p{margin-top:12px;color:var(--tinta-2)}
.foot{border-top:1px solid var(--linha);padding:36px 24px;background:var(--nevoa)}
.foot-in{max-width:var(--maxw);margin:0 auto;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
  color:var(--tinta-2);font-size:13px}

/* reveal */
.rev{opacity:0;transform:translateY(30px);transition:opacity .9s var(--ease),transform .9s var(--ease)}
.rev.vis{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rev{opacity:1;transform:none}html{scroll-behavior:auto}}

/* ======================= IMPRESSÃO / PDF =======================
   As quatro travas do playbook. Mexer aqui quebra o PDF em silêncio. */
@media print{
  /* 1. sem isto o PDF sai EM BRANCO (o reveal nunca dispara sem scroll) */
  .rev{opacity:1!important;transform:none!important}
  /* 2. sem isto hero/CTA/fotos saem sem cor */
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  /* 3. só nas unidades atômicas — NUNCA por capítulo (gera página quase vazia) */
  .fc,.bp,.plano,.nao,.tile,.board,.kanban,.check li,.mrow{break-inside:avoid}
  .nav,.dl,.btns{display:none!important}
  .cap{padding:28px 0}
  .hero{padding-top:36px}
  .credo{padding:44px 24px}
  .kanban{margin-bottom:28px}
  .hero-stage{margin-top:28px}
  /* o olho ("O funil") ficava sozinho no pé da página, separado do título */
  h2,.eyebrow,.cap-head,.board-cap{break-after:avoid}
  .cap-head{break-inside:avoid}
  /* grid não fragmenta bem entre páginas no Chrome: o bloco inteiro pulava e deixava o
     título "Tudo o que ele faz" sozinho numa página preta. Em colunas, ele quebra. */
  .tiles{display:block;column-count:2;column-gap:16px}
  .tile{margin-bottom:16px}
  .lineup{padding:32px 0}
  .cta{padding:48px 24px}
  body{font-size:11.5pt}
  a{color:inherit;text-decoration:none}
  /* 4. sem isto o Chrome imprime em Letter (padrão americano) — no Brasil é A4 */
  @page{size:A4;margin:14mm}
}
"""

SCRIPT = """<script>
(function(){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)){
    document.querySelectorAll(".rev").forEach(function(e){e.classList.add("vis")});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add("vis");io.unobserve(e.target)}})},
    {threshold:0,rootMargin:"0px 0px -12% 0px"});
  document.querySelectorAll(".rev").forEach(function(e){io.observe(e)});
})();
</script>"""

# --------------------------------------------------------------------- montagem
def build():
    _CHAP[0] = 0
    wa_svg = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="width:18px;height:18px">'
              '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2'
              'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Z"/></svg>')

    nav = f'''<nav class="nav" aria-label="Navegação do livreto">
  <a class="brand" href="/"><img src="/assets/brand-mark.png" width="24" height="24" alt="">
    <span>vendeaqui<span class="tld">.app</span></span></a>
  <span class="nav-r"><span class="nav-links">
    <a href="#funil">O funil</a><a href="#dia">O dia do vendedor</a>
    <a href="#preco">Preço</a><a href="#limites">O que não faz</a></span>
  <a class="nav-cta" href="{WA}">Falar no WhatsApp</a></span>
</nav>'''

    hero = f'''<header class="hero">
  <span class="eyebrow">{C.HERO["eyebrow"]}</span>
  <h1>{C.HERO["h1"]}</h1>
  <p class="sub">{C.HERO["sub"]}</p>
  <div class="btns"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
  <div class="hero-stage rev"><img src="/assets/hero.jpg" width="1600" height="1067"
    alt="Dona de uma pequena loja sorri e aperta a mão de um cliente no balcão, fechando uma venda."></div>
</header>'''

    credo = f'<section class="credo rev"><h2>{C.CREDO}</h2></section>'

    cap_funil = chapter("funil", "O funil", "Registrou, avançou.",
        "A demonstração registrada leva o lead para a etapa certa. A proposta enviada, para a seguinte. "
        "E o funil nunca anda para trás por causa de uma ligação atrasada.",
        mrow(foto("funil", "Dois vendedores numa mesa compartilhada revisam anotações juntos, com os notebooks virados para longe."),
             "Ninguém precisa lembrar de mover o card.",
             "O vendedor faz o trabalho dele — liga, demonstra, manda a proposta — e registra. É isso "
             "que move o lead. O quadro deixa de ser uma tarefa a mais que ninguém cumpre."),
        board("funil"), cards(C.FUNIL, "verde"))

    cap_dia = chapter("dia", "O dia do vendedor", "Abrir o lead e já saber o que fazer.",
        "A história inteira numa linha do tempo, a próxima ação escrita e o WhatsApp a um clique.",
        cards(C.DIA, "petroleo"))

    cap_entrada = chapter("entrada", "De onde vem o lead", "O lead entra sem ninguém digitar.",
        "Da conversa no WhatsApp, do formulário do seu site, da planilha antiga — e já vai para alguém do time.",
        board("entrada"), cards(C.ENTRADA, "petroleo"))

    cap_painel = chapter("painel", "No comando", "O mês de vendas numa tela.",
        "O gestor vê o funil de todos sem pedir relatório a ninguém.",
        cards(C.PAINEL, "ambar"))

    verticais = "".join(f'<span>{v}</span>' for v in C.VERTICAIS)
    cap_quem = chapter("quem", "Para quem é", "Começa com o jeito do seu mercado.",
        "Ao abrir a conta, a nossa equipe aplica com você um modelo pronto de etapas, categorias e "
        "tipos de atividade — e o resto você ajusta.",
        f'<div class="verticais rev">{verticais}</div>',
        '<div class="cap-head rev" style="margin-top:64px"><h2 style="font-size:30px">'
        'O que dói hoje.</h2></div>',
        lista(C.DORES))

    planos = "".join(
        f'<div class="plano{" hi" if i == 1 else ""}"><div class="nome">{n}</div>'
        f'<div class="v">{v}</div><div class="u">{u}</div><p>{d}</p></div>'
        for i, (n, v, u, d) in enumerate(C.PLANOS))
    naos = "".join(f'<div class="nao"><h4>{t}</h4><p>{d}</p></div>' for t, d in C.NAOS)
    cap_preco = chapter("preco", "Preço", f"R$ {C.PRECO} por usuário, por mês.",
        "Sozinho, você usa grátis. Paga quando o time cresce — por vendedor que usa o sistema. "
        "Sem fidelidade.",
        f'<div class="planos rev">{planos}</div>',
        f'<div class="naos rev">{naos}</div>')

    cap_limites = chapter("limites", "Honestidade", "O que o vendeaqui não faz.",
        "Um livreto que só lista virtude não ajuda ninguém a decidir. Isto aqui é o que ele "
        "<b>não</b> resolve — para você não descobrir depois de começar.",
        cards(C.NAO_FAZ, "ambar"))

    tiles = "".join(f'<article class="tile c-{c}"><span class="tile-mk"></span>'
                    f'<h3>{n}{tag(g)}</h3><p>{d}</p></article>' for n, d, c, g in C.TILES)
    lineup = f'''<section class="lineup" id="recursos">
  <div class="lineup-in">
    <h2 class="rev">Tudo o que ele faz.</h2>
    <p class="lead rev">No mesmo preço por usuário — nada aqui é módulo pago à parte.</p>
    <div class="tiles rev">{tiles}</div>
  </div>
</section>'''

    h2, p = C.CTA
    cta = f'''<section class="cta">
  <h2 class="rev">{h2}</h2>
  <p class="rev">{p}</p>
  <div class="btns rev"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
</section>'''

    dl = '''<section class="dl">
  <h2>Leve o livreto com você.</h2>
  <p>Baixe o arquivo para apresentar ao seu time ou mandar por e-mail.</p>
  <div class="btns"><a class="btn" href="/livreto.pdf" download="livreto-vendeaqui.pdf">
    Baixar o livreto (PDF)</a></div>
</section>'''

    body = "\n".join([nav, hero, credo, kanban(), cap_funil, cap_dia, cap_entrada, cap_painel,
                      cap_quem, cap_preco, cap_limites, lineup, cta, dl])

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    sha = hashlib.sha1(body.encode()).hexdigest()[:7]
    foot = (f'<footer class="foot"><div class="foot-in">'
            f'<span>vendeaqui · CRM de vendas · um produto do Seu Condomínio · '
            f'<a href="/privacidade">Privacidade</a></span>'
            f'<span>Livreto v{hoje} · {sha}</span></div></footer>')

    desc = ("Livreto do vendeaqui: o CRM de vendas em que o funil anda a partir do que o time já "
            "registra, com a próxima ação sugerida por IA, o WhatsApp a partir do lead e a entrada de "
            f"leads por chatbot, site e planilha. R$ {C.PRECO} por usuário por mês, grátis para 1 usuário.")
    url = f"{C.SITE}/livreto/"
    head = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Livreto do vendeaqui — CRM de vendas com funil que anda sozinho</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="vendeaqui">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{url}">
<meta property="og:title" content="Livreto do vendeaqui">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{C.SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SoftwareApplication",
"name":"vendeaqui","applicationCategory":"BusinessApplication","operatingSystem":"Web",
"url":"{url}","inLanguage":"pt-BR","description":"{desc}",
"offers":{{"@type":"Offer","price":"{C.PRECO}","priceCurrency":"BRL","description":"Por usuário por mês. Grátis para 1 usuário, sem fidelidade."}},
"featureList":["Funil de vendas que avança a partir das atividades e dos status registrados",
"Etapas, status e tipos de atividade editáveis por empresa",
"Próxima ação sugerida por IA, gerada sob demanda",
"WhatsApp e atendimento abertos a partir do lead",
"Aviso de lead sem primeiro contato, contando horário útil",
"Leads por conversa no chatbot, webhook, API e importação de planilha",
"Painel de vendas com conversão, funil, origem e mapa dos leads"]}}</script>
<style>{CSS}</style>
</head>
<body>
'''
    doc = head + body + "\n" + foot + "\n" + SCRIPT + "\n</body>\n</html>\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"[livreto] {OUT} — {len(doc)//1024} KB · v{hoje} · {sha}")

build()
