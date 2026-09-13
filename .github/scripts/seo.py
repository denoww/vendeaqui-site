#!/usr/bin/env python3
"""Gera o sitemap e trava os invariantes de SEO e de COPY das páginas estáticas.

Roda no CI (.github/workflows/seo.yml) e também na mão:

    python3 .github/scripts/seo.py            # gera + confere (sem rede)
    python3 .github/scripts/seo.py --check    # só confere, não escreve
    python3 .github/scripts/seo.py --http     # confere também se cada <loc> é 200 sem redirect

⚠️ Vive em `.github/` de propósito: o GitHub Pages não publica esse diretório.

Herdado do `acompanhaobra-site`, com as regras de OBRAS trocadas pelas promessas de CRM
que o ERP NÃO sustenta (conferidas no código em 13/09/2026 — ver o comentário
`⛔ NÃO PROMETER` no topo do index.html).

O `<loc>` de cada página é o **próprio canonical dela**, lido do HTML — não existe mapa
página → URL para envelhecer. Página com `noindex` fica fora do sitemap.
"""
from __future__ import annotations

import html as H
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

BASE = 'https://www.vendeaqui.app'
# Sem blog ainda (espera o preço público). Quando o blog existir E for virado para
# indexável, preencha — a ORDEM está no ROADMAP_multi_produto.md §7.2 do ERP: flip no
# ERP → deploy → este campo → sitemap do blog no Search Console. Preencher antes entrega
# ao Google um sitemap de páginas `noindex`.
# ⚠️ SEM `.xml`: a rota do Rails é `/sitemap`; `/sitemap.xml` responde 301.
SITEMAP_BLOG = None

PROIBIDAS = [
    ('prova social inventada',
     r'(mais\s+de|j[áa]\s+s[ãa]o|atendemos|usado\s+por|confiam|\+\s*)\s*\d[\d.]*\s*(mil\s+)?'
     r'(empresas|clientes|usu[áa]rios|vendedores|leads)\b'),
    ('métrica de resultado não medida',
     r'\d{1,3}[,.]?\d*\s*%\s*(a\s+mais\s+)?(de\s*)?(convers[ãa]o|vendas|acerto|precis[ãa]o|uptime|disponibilidade)|99[,.]9'),
    # `\b` obrigatório em todo nome curto (cicatriz da casa: nome curto casando dentro de palavra).
    ('concorrente pelo nome',
     r'\b(rd\s*station|pipedrive|hubspot|agendor|ploomes|piperun|salesforce|kommo|moskit|exact\s*sales|leads2b)\b'),
    # ── Promessas de CRM que o ERP não sustenta (13/09/2026) ──
    ('WhatsApp oficial / sem bloqueio',
     r'(api|canal|integra[çc][ãa]o)\s+oficial\s+d[oa]\s+whatsapp|whatsapp\s+(business\s+api|cloud\s+api)'
     r'|sem\s+risco\s+de\s+bloqueio|nunca\s+([ée]\s+)?bloquead'),
    ('app instalável nas lojas',
     r'(baix\w+|dispon[íi]vel|instal\w+)\s+[^.\n]{0,25}(play\s*store|app\s*store|google\s+play)'),
    ('proposta em PDF ou assinatura digital',
     r'propost\w*[^.\n]{0,30}\bpdf\b|assinatura\s+(digital|eletr[ôo]nica)'),
    ('IA analisando ligação telefônica',
     r'\bia\b[^.\n]{0,60}(liga[çc][ãa]o|telefonema)s?\s+(gravad|analisad|transcrit)'
     r'|(grava[çc][ãa]o|transcri[çc][ãa]o)\s+(de|da)\s+liga[çc]'),
    ('pontuação de lead ou jornada automática',
     r'(pontua[çc][ãa]o|score|scoring)\s+(de|do|dos)?\s*leads?|jornadas?\s+autom[áa]tic'),
    ('leads do Facebook/Instagram Lead Ads',
     r'lead\s*ads|instant\s*form|formul[áa]rio\s+instant[âa]neo'),
    ('sincronização com agenda externa',
     r'google\s+(agenda|calendar)|outlook\s+calendar'),
    ('autocadastro ou teste grátis',
     r'cadastre-se|teste\s+gr[áa]tis|comece\s+gr[áa]tis|crie\s+sua\s+conta|assine\s+agora'),
    ('preço (não definido)',
     r'R\$\s*\d'),
    ('certificação não confirmada',
     r'INPI|homologad\w+\s+(pelo|junto)|certificad\w+\s+pel[oa]'),
    ('garantia absoluta',
     r'garantimos que|100%\s*(seguro|garantido|livre)|nunca\s+falha|zero\s+risco'),
    ('marcador de rascunho',
     r'\[A VALIDAR|\[INSERIR|\[TODO|R\$\s*_+|XXX+|lorem ipsum'),
]
# A frase honesta NEGA a promessa ("não gera proposta em PDF") — então o trecho logo
# antes do match é olhado atrás de um negador.
NEGADORES = re.compile(r'\b(n[ãa]o|ningu[ée]m|nunca|nenhum[ao]?|jamais|sem)\b[^.\n]{0,60}$', re.I)

erros: list[str] = []


def falha(msg: str) -> None:
    erros.append(msg)
    print(f'::error::{msg}')


def excluidas_do_jekyll() -> list[str]:
    cfg = RAIZ / '_config.yml'
    if not cfg.exists():
        return []
    dentro, itens = False, []
    for linha in cfg.read_text(encoding='utf-8').splitlines():
        if re.match(r'^exclude:\s*$', linha):
            dentro = True
            continue
        if dentro:
            m = re.match(r'^\s*-\s*"?([^"#]+?)"?\s*(#.*)?$', linha)
            if m:
                itens.append(m.group(1).strip().rstrip('/'))
            elif linha.strip() and not linha.startswith((' ', '\t', '-')):
                break
    return itens


def paginas() -> list[Path]:
    saida = subprocess.run(['git', 'ls-files', '*.html'], cwd=RAIZ,
                           capture_output=True, text=True, check=True).stdout
    fora = excluidas_do_jekyll()
    return [RAIZ / p for p in saida.split()
            if p and not any(p == x or p.startswith(x + '/') for x in fora)]


def texto_visivel(bruto: str) -> str:
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', bruto, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s))


def lastmod(caminho: Path) -> str:
    """Data do último commit que tocou o arquivo (não mtime, que no runner é sempre hoje)."""
    r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', str(caminho.relative_to(RAIZ))],
                       cwd=RAIZ, capture_output=True, text=True)
    return r.stdout.strip() or '1970-01-01'


def confere_faq(arq: Path, bruto: str, visivel: str) -> None:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', bruto, re.S)
    if not m:
        return
    try:
        grafo = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        falha(f'{arq.name}: JSON-LD inválido ({e})')
        return

    bruto_json = m.group(1)
    for proibido in ('aggregateRating', '"review"', 'interactionStatistic', '"offers"'):
        if proibido in bruto_json:
            falha(f'{arq.name}: {proibido} em dado estruturado — prova social fabricada ou preço inexistente')

    for no in grafo.get('@graph', [grafo]):
        if no.get('@type') != 'FAQPage':
            continue
        for q in no.get('mainEntity', []):
            for rotulo, txt in (('pergunta', q.get('name', '')),
                                ('resposta', q.get('acceptedAnswer', {}).get('text', ''))):
                if re.sub(r'\s+', ' ', txt).strip() not in visivel:
                    falha(f'{arq.name}: {rotulo} do FAQPage não existe no texto visível: "{txt[:60]}…"')


def confere_assets(arq: Path, bruto: str) -> None:
    """Todo `/assets/...` referenciado tem que existir em disco (imagem ausente não quebra nada visível)."""
    vistos = set(m.group(1) for m in re.finditer(r'(?:src|href)="(/assets/[^"?#]+)"', bruto))
    for m in re.finditer(r'srcset="([^"]+)"', bruto):
        for parte in m.group(1).split(','):
            cand = parte.strip().split(' ')[0]
            if cand.startswith('/assets/'):
                vistos.add(cand)
    for ref in sorted(vistos):
        if not (RAIZ / ref.lstrip('/')).is_file():
            falha(f'{arq.name}: referencia {ref}, que NÃO existe em disco')


def confere_copy(arq: Path, visivel: str) -> None:
    for nome, padrao in PROIBIDAS:
        for m in re.finditer(padrao, visivel, re.I):
            antes = visivel[max(0, m.start() - 80):m.start()]
            if NEGADORES.search(antes):
                continue
            trecho = visivel[max(0, m.start() - 50):m.end() + 50].strip()
            falha(f'{arq.name}: copy proibida ({nome}): "…{trecho}…"')
            break


def confere_http(urls: list[str]) -> None:
    """Cada <loc> responde 200 SEM redirect. URL nova vira aviso (o Pages pode não ter publicado)."""
    import urllib.error
    import urllib.request

    anterior = subprocess.run(['git', 'show', 'HEAD:sitemap.xml'], cwd=RAIZ, capture_output=True, text=True)
    ja_existiam = set(re.findall(r'<loc>([^<]+)</loc>', anterior.stdout))

    class SemRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(SemRedirect)
    for u in urls:
        req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'seo.py/1.0 (CI)'})
        try:
            with opener.open(req, timeout=20) as r:
                if r.status != 200:
                    raise urllib.error.HTTPError(u, r.status, 'status', r.headers, None)
        except Exception as e:
            codigo = getattr(e, 'code', type(e).__name__)
            if u in ja_existiam:
                falha(f'<loc> {u} respondeu {codigo} — sitemap não pode listar redirect nem erro')
            else:
                print(f'::warning::<loc> {u} respondeu {codigo}, mas é URL NOVA — o Pages pode não ter publicado ainda')


def main() -> int:
    so_confere = '--check' in sys.argv
    urls: list[tuple[str, str]] = []

    for arq in sorted(paginas()):
        bruto = arq.read_text(encoding='utf-8')
        visivel = texto_visivel(bruto)

        confere_copy(arq, visivel)
        confere_faq(arq, bruto, visivel)
        confere_assets(arq, bruto)

        if re.search(r'name="robots"[^>]*content="[^"]*noindex', bruto):
            continue

        if not re.search(r'name="description"', bruto):
            falha(f'{arq.name}: página indexável sem meta description')
        n_h1 = len(re.findall(r'<h1[\s>]', bruto))
        if n_h1 != 1:
            falha(f'{arq.name}: {n_h1} <h1> (tem que ser exatamente 1)')

        mc = re.search(r'rel="canonical"\s+href="([^"]+)"', bruto)
        if not mc:
            falha(f'{arq.name}: página indexável sem canonical — não entra no sitemap')
            continue
        if not mc.group(1).startswith(BASE + '/'):
            falha(f'{arq.name}: canonical {mc.group(1)} fora de {BASE} — resto de blueprint?')
        urls.append((mc.group(1), lastmod(arq)))

    if len(urls) != len({u for u, _ in urls}):
        falha('duas páginas declaram o MESMO canonical')

    if not so_confere and not erros:
        gravar(urls)

    if '--http' in sys.argv and not erros:
        confere_http([u for u, _ in urls])

    print(f'{len(urls)} URLs, {len(erros)} erro(s)')
    return 1 if erros else 0


def gravar(urls: list[tuple[str, str]]) -> None:
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in sorted(urls):
        linhas += ['  <url>', f'    <loc>{loc}</loc>', f'    <lastmod>{mod}</lastmod>', '  </url>']
    linhas.append('</urlset>')
    (RAIZ / 'sitemap.xml').write_text('\n'.join(linhas) + '\n', encoding='utf-8')

    if not SITEMAP_BLOG:
        return  # sem blog ainda: não há índice a escrever (e o robots.txt aponta só o sitemap.xml)
    idx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s in (f'{BASE}/sitemap.xml', SITEMAP_BLOG):
        idx += ['  <sitemap>', f'    <loc>{s}</loc>', '  </sitemap>']
    idx.append('</sitemapindex>')
    (RAIZ / 'sitemap-index.xml').write_text('\n'.join(idx) + '\n', encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())
