# Livreto do vendeaqui — playbook

Peça funda de vendas, servida em `/livreto/` com PDF espelho em `/livreto.pdf`. É o que o
comercial manda depois da primeira conversa. Nasceu em 13/09/2026 a partir do livreto de uma
marca irmã da casa (mesmo esqueleto: `content.py` + `build.py` + CI de espelho).

## A regra de ouro

> **Edite `content.py` e dê push. NÃO edite `livreto/index.html` à mão.**

O CI (`.github/workflows/livreto.yml`) regenera o HTML, gera o PDF por Chromium headless,
**abre o PDF e mede** se alguma página saiu em branco, e commita o espelho de volta. Rodar o
build localmente não é errado — o CI só confirma que já estava em dia.

⚠️ O passo de commit usa `git status --porcelain`, não `git diff --quiet`: o diff não enxerga
arquivo novo, e o primeiro PDF nunca seria commitado (cicatriz do repo de origem).

## Onde editar

| Quero mudar | Arquivo |
|---|---|
| Texto dos cards, storyboards, preço, "o que não faz", quadro ilustrativo | `content.py` — 95% das mudanças |
| Quais capítulos entram, hero, CTA, SEO | `build.py` → `build()` |
| Cenas dos storyboards (SVG line-art) | `build.py` → `SCENES` |
| Cores e CSS de tela e de impressão | `build.py` → `CSS` |

## As 4 travas do `@media print` (quebram em silêncio)

1. **`.rev{opacity:1}`** — sem isto o PDF sai **EM BRANCO**.
2. **`print-color-adjust:exact`** — sem isto hero, CTA e fotos saem sem cor.
3. **`break-inside:avoid` só nas unidades atômicas** (card, painel, quadro). Nunca por capítulo.
4. **`@page{size:A4}`** — sem isto o Chrome imprime em Letter.

## Conteúdo: só o que roda

A régua é a mesma da home e da KB do chatbot no ERP: o `seo.py` varre também este HTML e
reprova promessa falsa, prova social e **qualquer preço que não seja o canônico** (`PRECO` no
`content.py` tem que bater com `PRECO_CANONICO` do `seo.py`). O capítulo `NAO_FAZ` repete o
tópico `limites` da KB — se um mudar, mude o outro.

## Fotos

`foto("x")` gera `<img src="/assets/x.jpg">`; o `seo.py` reprova referência a asset que não
existe. As fotos são as mesmas da home (`hero.jpg`, `funil.jpg`) — trocar lá troca aqui, e o CI
refaz o PDF porque a impressão digital inclui `assets/`. Elenco das fotos desta marca: pessoas
**brancas** (decisão de 13/09/2026: os outros produtos da casa já usam pessoas negras).

A interface do produto (o quadro de vendas) é **HTML**, nunca imagem gerada, e sai sempre com o
rótulo "Exemplo ilustrativo".
