# vendeaqui-site — www.vendeaqui.app

Site estático (GitHub Pages) do **vendeaqui**, o CRM de vendas do ERP Seu Condomínio vendido
com marca própria. Nasceu em 13/09/2026 a partir do `acompanhaobra-site`.

- Marca, login e infra do produto: repo `denoww/seucondominio` →
  `app/services/atendimento/ROADMAP.md` → "Marca vendeaqui" e `ROADMAP_multi_produto.md` §7.
- Login: `https://app.vendeaqui.app/logar?no_layout=true` (fonte da verdade: `.login`).
- WhatsApp comercial: `.whatsapp`. Domínio: `CNAME`.

## ⛔ A régua da copy

**O site só promete o que o código do ERP sustenta.** A lista do que NÃO existe está no
comentário `⛔ NÃO PROMETER` no topo do `index.html` e é cobrada por
`.github/scripts/seo.py` (PROIBIDAS). Antes de acrescentar um recurso à página, confira
no código do ERP (`app/services/atendimento/`) — roadmap não é produto.

Resumo do que ficou de fora de propósito (13/09/2026): app nas lojas/PWA offline, proposta em
PDF e assinatura, WhatsApp oficial ou "sem risco de bloqueio", Instant Form do Facebook para
qualquer empresa, IA de ligação telefônica, pontuação de lead e jornadas (chave desligada),
Google Agenda, autocadastro e qualquer número de clientes.

**Preço canônico (13/09/2026): R$ 39 por usuário/mês, grátis para 1 usuário, sem fidelidade** —
abaixo do mercado medido (Agendor R$ 59, RD Station CRM R$ 73, mediana da entrada paga ≈ R$ 137).
Mora em três lugares que mudam JUNTOS: `PRECO_CANONICO` no `seo.py` (reprova qualquer outra cifra
na copy e `offers.price` divergente no JSON-LD), a KB do chatbot no ERP
(`db/seeds/chatbot/kb_produto_vendeaqui.json`) e o `precos` do blog (`Auto::Marcas::Vendeaqui`).

## Livreto (`/livreto/` + `/livreto.pdf`)

Peça funda de vendas, nascida em 13/09/2026. **Edite `livreto/content.py` e dê push** — o CI
`livreto.yml` regenera o HTML e o PDF e commita o espelho. Playbook e as 4 travas do
`@media print` em `livreto/CLAUDE.md`. O `seo.py` varre o livreto com a mesma régua da home.

## Regras que herdamos das irmãs

- **Sem analytics, fonte ou script de terceiro** — a política de privacidade afirma isso.
- **Interface é HTML/CSS, não imagem gerada** (o Kanban da home), e **sempre rotulada**
  "Exemplo ilustrativo".
- `sitemap.xml` é gerado pelo CI a partir dos canonicals; não edite à mão.
- **Blog indexável desde 16/09/2026** (`blog.vendeaqui.app`, servido pelo ERP): `SITEMAP_BLOG` no
  `seo.py` faz o CI gerar o `sitemap-index.xml`, e o `robots.txt` aponta o índice primeiro.
- **Search Console tem DUAS propriedades**: a de prefixo `https://www.vendeaqui.app/` (tag no
  `index.html`) e, desde 17/09/2026, a de **domínio** `vendeaqui.app` (TXT `google-site-verification`
  no apex, ao lado do SPF do SES). Só a de domínio cobre o `blog.` — é nela que o sitemap do blog
  está enviado. ⛔ Ao mexer no TXT do apex, mantenha os DOIS valores (SPF e verificação).
- **Search Console** (13/09/2026): propriedade de **prefixo de URL** `https://www.vendeaqui.app/`,
  conta rodrigo@seucondominio.com.br, verificada pela **tag** `google-site-verification` no `<head>`
  do `index.html`, com `sitemap.xml` enviado. ⛔ Não remova a tag num refactor: o Google
  desverifica a propriedade. Foi tag e não arquivo `google*.html` porque o `seo.py` varre todo
  `.html` e reprovaria uma página sem description/h1/canonical; e não foi propriedade de domínio
  porque a mudança de DNS foi barrada pelo modo automático do Claude Code.
- **Publicação se prova por conteúdo**, não pelo check verde:
  `diff <(curl -s https://www.vendeaqui.app/index.html) index.html`
