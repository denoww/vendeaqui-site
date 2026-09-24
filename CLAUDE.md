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

## IndexNow — a chave que faltava na raiz

O arquivo `7b3e9c1a4f6d24b8e0a5c7d9f1234567.txt` na raiz é o token de posse do **IndexNow**:
ele prova ao Bing que este host é nosso, e é o que permite AVISAR o buscador de uma página
nova em vez de esperar o rastreio. ⛔ Não apagar, não renomear, não esconder — o protocolo
exige que ele seja público, e o valor é o mesmo em todos os nossos hosts, por design.

⚠️ **Ele só chegou aqui em 24/09/2026.** Até então a chave existia apenas nos hosts servidos
pelo ERP (os blogs, via `BlogRootFiles`), e os SITES respondiam 404 nela — ou seja, nenhuma
página deste site jamais pôde ser submetida ao IndexNow. O Bing é o índice que o ChatGPT
consulta, e o ChatGPT é de onde vêm ~50% das sessões das marcas
(`ROADMAP_multi_produto.md` §8.6), então isso não é detalhe de SEO: é o canal principal.

Para avisar o Bing de uma página nova ou alterada deste site:

```bash
curl -s -X POST https://api.indexnow.org/IndexNow \
  -H 'Content-Type: application/json' \
  -d '{"host":"www.vendeaqui.app","key":"7b3e9c1a4f6d24b8e0a5c7d9f1234567",
       "keyLocation":"https://www.vendeaqui.app/7b3e9c1a4f6d24b8e0a5c7d9f1234567.txt",
       "urlList":["https://www.vendeaqui.app/a-pagina"]}' -w '%{http_code}\n'
```

`200` ou `202` = aceito. `403` = a chave não está respondendo na raiz (confira o link acima
antes de investigar qualquer outra coisa).

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
