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
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

BASE = 'https://www.vendeaqui.app'
# Preço público canônico, em reais por usuário/mês. Única cifra que a copy e o JSON-LD podem dizer.
PRECO_CANONICO = '39'
# Sem blog ainda (espera o preço público). Quando o blog existir E for virado para
# indexável, preencha — a ORDEM está no ROADMAP_multi_produto.md §7.2 do ERP: flip no
# ERP → deploy → este campo → sitemap do blog no Search Console. Preencher antes entrega
# ao Google um sitemap de páginas `noindex`.
# ⚠️ SEM `.xml`: a rota do Rails é `/sitemap`; `/sitemap.xml` responde 301.
SITEMAP_BLOG = 'https://blog.vendeaqui.app/sitemap'  # blog indexável desde 16/09/2026

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
    # Preço CANÔNICO (13/09/2026): R$ 39 por usuário/mês, grátis para 1 usuário. Qualquer outra
    # cifra é reprovada — é a mesma lógica do `RegrasDeCopy.violacao_de_preco` do blog do ERP.
    # ⚠️ Ao mudar o preço, mude PRECO_CANONICO aqui, a KB do chatbot e o `precos` do blog juntos.
    ('preço diferente do canônico',
     r'R\$\s*(?!' + '39' + r'(?![\d,.]))\d[\d.,]*'),  # ⚠️ o '39' literal tem que bater com PRECO_CANONICO (a lista vem antes da constante)
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
avisos: list[str] = []


def falha(msg: str) -> None:
    erros.append(msg)
    print(f'::error::{msg}')


def aviso(msg: str) -> None:
    """Reprova NADA — só aparece no log e no resumo.

    ⚠️ Severidade escolhida por MEDIÇÃO (19/09/2026), e promovida a ERRO em 23/09: quando a
    regra nasceu, **toda** página indexável dos sites estourava a de description e 6 estouravam
    a de título — subir isso pra erro entregaria todos os CIs vermelhos de uma vez, e guard que
    nasce vermelho é guard que o time aprende a ignorar (foi o que aconteceu com o `guarda.yml`
    do atendeaqui, 8 dias no vermelho por uma crase). As 14 páginas foram reescritas, os 5 sites
    ficaram limpos, e aí sim o limite virou `falha`. Quem continua avisando é só a description
    CURTA demais, que não quebra nada.
    """
    avisos.append(msg)
    print(f'::warning::{msg}')


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
    for proibido in ('aggregateRating', '"review"', 'interactionStatistic'):
        if proibido in bruto_json:
            falha(f'{arq.name}: {proibido} em dado estruturado — prova social fabricada')

    # O `offers` do dado estruturado tem que dizer o MESMO preço da copy. Preço divergente no
    # JSON-LD é o que o Google mostra no resultado — e ninguém lê o JSON pra perceber.
    for no in grafo.get('@graph', [grafo]):
        oferta = no.get('offers')
        if oferta is None:
            continue
        for o in (oferta if isinstance(oferta, list) else [oferta]):
            if str(o.get('price')) not in (PRECO_CANONICO, '0'):
                falha(f'{arq.name}: offers.price {o.get("price")!r} diferente do canônico R$ {PRECO_CANONICO}')

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

    # ⚠️ ANTES DO PUSH, não `HEAD`. Se o autor regenerou o sitemap e o commitou junto com
    # a página — que é o que acontece ao rodar este script na mão antes de commitar —, a
    # URL nova JÁ ESTÁ no `HEAD:sitemap.xml`, a proteção logo abaixo não a reconhece como
    # nova, e o job reprova exatamente o commit que adiciona a página. Foi o que derrubou
    # o CI dos 3 sites que ganharam `/perguntas-antes-de-escolher` em 24/09/2026.
    ja_existiam: set[str] = set()
    for ref in (os.environ.get('GITHUB_EVENT_BEFORE') or '', 'HEAD~1', 'HEAD'):
        if not ref or set(ref) == {'0'}:
            continue
        anterior = subprocess.run(['git', 'show', f'{ref}:sitemap.xml'], cwd=RAIZ,
                                  capture_output=True, text=True)
        if anterior.returncode == 0:
            ja_existiam = set(re.findall(r'<loc>([^<]+)</loc>', anterior.stdout))
            break

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


def rotulo(arq: Path) -> str:
    """Caminho relativo à raiz do site.

    `arq.name` é 'index.html' tanto pra home quanto pra /livreto/ — a mensagem fica
    ambígua justamente nas duas páginas que mais mudam.
    """
    try:
        return str(arq.relative_to(RAIZ))
    except ValueError:
        return arq.name


def confere_titulo(arq: Path, bruto: str, titulos: dict[str, str]) -> None:
    """`<title>` existe, não repete entre páginas, e cabe no resultado de busca.

    O `<title>` é o que o buscador mostra como link e o que um assistente lê como "nome
    desta página". Faltar é erro; passar de ~60 caracteres é recomendação (o Google corta,
    mas não penaliza).
    """
    m = re.search(r'<title>(.*?)</title>', bruto, re.S)
    if not m:
        falha(f'{rotulo(arq)}: página indexável sem <title>')
        return

    titulo = ' '.join(m.group(1).split())
    if titulo in titulos:
        falha(f'{rotulo(arq)}: <title> idêntico ao de {titulos[titulo]} — duas páginas, um nome só')
    titulos[titulo] = rotulo(arq)

    if len(titulo) > 60:
        falha(f'{rotulo(arq)}: <title> com {len(titulo)} caracteres (o buscador corta perto de 60)')


def confere_descricao(arq: Path, bruto: str) -> None:
    """Comprimento da meta description. A EXISTÊNCIA já é cobrada no `main` como erro."""
    m = re.search(r'name="description"\s+content="([^"]*)"', bruto)
    if not m:
        return
    n = len(m.group(1).strip())
    if n > 160:
        falha(f'{rotulo(arq)}: meta description com {n} caracteres (o buscador corta perto de 160)')
    elif n < 70:
        aviso(f'{rotulo(arq)}: meta description com só {n} caracteres — cabe mais argumento')


def blocos_jsonld(bruto: str) -> list[dict]:
    """Os nós do JSON-LD da página, já achatando o `@graph`."""
    saida: list[dict] = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', bruto, re.S):
        try:
            dados = json.loads(m.group(1))
        except Exception:
            continue  # JSON inválido já é erro no confere_faq
        nos = dados.get('@graph', [dados]) if isinstance(dados, dict) else dados
        saida.extend(n for n in nos if isinstance(n, dict))
    return saida


def confere_no_de_produto(arq: Path, bruto: str, canonical: str) -> None:
    """A HOME precisa dizer, em dado estruturado, O QUE é vendido.

    ⚠️ Medido em 17-18/09/2026 (ROADMAP_multi_produto.md §8.6): o assistente de IA entrega
    ~50% do tráfego de uma marca nova e cita o PRODUTO pelo nome. O corpflix ficou meses só
    com Organization + WebSite + FAQPage — nada no dado estruturado dizia o que era vendido.
    Só a home é cobrada: página de público ou de privacidade não vende produto.
    """
    if canonical.rstrip('/') != BASE.rstrip('/'):
        return
    tipos = {n.get('@type') for n in blocos_jsonld(bruto)}
    if not ({'SoftwareApplication', 'Service', 'Product'} & tipos):
        falha(f'{rotulo(arq)}: a home não tem nó de produto no JSON-LD '
              '(SoftwareApplication/Service/Product) — o assistente não tem o que citar')


def confere_arquivos_de_raiz() -> None:
    """`robots.txt` e `llms.txt` existem, e o robots aponta o sitemap."""
    robots = RAIZ / 'robots.txt'
    if not robots.exists():
        falha('robots.txt não existe')
    elif 'Sitemap:' not in robots.read_text(encoding='utf-8'):
        falha('robots.txt sem linha `Sitemap:` — o crawler tem que adivinhar onde está o mapa')

    if not (RAIZ / 'llms.txt').exists():
        falha('llms.txt não existe — é o que diz ao assistente o que o produto é, '
              'quanto custa e o que ele NÃO faz (ROADMAP_multi_produto.md §7.6)')


def confere_preco_coerente() -> None:
    """O preço do `llms.txt` tem que bater com o `offers.price` da home.

    ☠️ O `llms.txt` do www é escrito à MÃO (o do blog é gerado do registry pelo ERP) e já
    derivou uma vez em menos de 24 h: em 18/09/2026 o do atendeaqui afirmava que o app não
    estava nas lojas quando estava desde 11/08. Esta é a versão local do guard — a completa
    é `rake marcas:auditar_seo`, que compara com o registry.
    """
    llms = RAIZ / 'llms.txt'
    home = RAIZ / 'index.html'
    if not llms.exists() or not home.exists():
        return

    precos = [str(n['offers'].get('price'))
              for n in blocos_jsonld(home.read_text(encoding='utf-8'))
              if isinstance(n.get('offers'), dict) and n['offers'].get('price')]
    if not precos:
        return  # marca sem preço público (corpflix) não tem o que conferir

    texto = llms.read_text(encoding='utf-8')
    for preco in precos:
        inteiro = preco.split('.')[0]
        if inteiro and inteiro not in texto:
            falha(f'llms.txt não cita o preço que a home declara no JSON-LD ({preco}) — '
                  'cópia manual que derivou')


def main() -> int:
    so_confere = '--check' in sys.argv
    urls: list[tuple[str, str]] = []
    titulos: dict[str, str] = {}

    confere_arquivos_de_raiz()
    confere_preco_coerente()

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
        confere_titulo(arq, bruto, titulos)
        confere_descricao(arq, bruto)
        confere_no_de_produto(arq, bruto, mc.group(1))
        urls.append((mc.group(1), lastmod(arq)))

    if len(urls) != len({u for u, _ in urls}):
        falha('duas páginas declaram o MESMO canonical')

    if not so_confere and not erros:
        gravar(urls)

    if '--http' in sys.argv and not erros:
        confere_http([u for u, _ in urls])

    print(f'{len(urls)} URLs, {len(erros)} erro(s), {len(avisos)} aviso(s)')
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
