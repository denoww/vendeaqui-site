# -*- coding: utf-8 -*-
"""Conteúdo do livreto do vendeaqui — 95% das mudanças acontecem AQUI.

VOCÊ SÓ PRECISA EDITAR ESTE ARQUIVO. O HTML e o PDF se regeneram sozinhos no CI
(.github/workflows/livreto.yml) assim que você der push — o PDF é um ESPELHO
automático. O CI ainda abre o PDF e barra o build se alguma página sair EM BRANCO.

Fonte da verdade factual, nesta ordem de precedência:
  1. `app/services/atendimento/ROADMAP.md` no repo do ERP (denoww/seucondominio) —
     seção "Marca vendeaqui" e o que está ENTREGUE no CRM. Roadmap não é produto.
  2. A página inicial deste site (`index.html`), cuja copy foi conferida contra o
     código em 13/09/2026 e é cobrada pelo `.github/scripts/seo.py`.
  3. A KB do chatbot no ERP (`db/seeds/chatbot/kb_produto_vendeaqui.json`) — o
     tópico `limites` é a mesma lista do capítulo NAO_FAZ abaixo.

⛔ REGRAS DE COPY — o que NÃO pode ser prometido (o `seo.py` reprova o push):
  • aplicativo nas lojas ou modo offline — é tela no navegador, inclusive no celular;
  • proposta em PDF, assinatura de documento, funil de renovação, contrato ligado ao lead;
  • WhatsApp pela API oficial ou "sem risco de bloqueio" — o envio sai do número da
    empresa por conector não oficial, com limite diário;
  • formulário de anúncio do Facebook/Instagram para qualquer empresa (depende da Meta);
  • IA ouvindo ligação telefônica — o que existe é a avaliação da reunião online;
  • pontuação de lead, jornada automática, agenda externa, editor de e-mail marketing;
  • autocadastro ou teste — a conta é aberta pela nossa equipe;
  • qualquer preço que não seja o canônico (R$ 39 por usuário/mês, grátis para 1).
  Como em todas as peças da casa: nada de prova social, nada de concorrente pelo nome,
  nada de número de resultado que não foi medido.
"""

# O número vive em UM lugar só: o arquivo `.whatsapp` na raiz do repo. O workflow
# `guarda.yml` barra o push se algum `wa.me` divergir dele.
from pathlib import Path

WA = "https://wa.me/" + (Path(__file__).parent.parent / ".whatsapp").read_text().strip()
# Prefixo próprio: o texto é o único sinal de origem que atravessa o WhatsApp.
WA_TXT = "?text=Vi%20o%20livreto%20do%20vendeaqui%20e%20quero%20ver%20rodando"
SITE = "https://www.vendeaqui.app"
PRECO = "39"  # tem que bater com PRECO_CANONICO do .github/scripts/seo.py

# ---------------------------------------------------------------- hero / credo
HERO = {
    "eyebrow": "Livreto",
    "h1": "O funil anda sozinho.",
    "sub": "O time registra a ligação, a demonstração e a proposta — e a etapa do lead avança "
           "sem ninguém arrastar card. A próxima ação vem sugerida e a conversa abre no WhatsApp.",
}

CREDO = ('CRM que exige disciplina extra é CRM que ninguém preenche. Aqui a etapa é '
         '<span class="g">consequência do que o time já faz</span>.')

# Quadro ilustrativo — INTERFACE em HTML, nunca imagem gerada (o gerador inventa texto
# em tela). Rotulado "exemplo ilustrativo" no build: sem o rótulo, os nomes leriam como
# clientes reais, e a casa não fabrica prova social.
KANBAN = [
    ("Lead", "38", [("Clínica Bem-Estar", "veio pelo WhatsApp · hoje", "ninguém falou ainda", ""),
                    ("Loja Ponto Norte", "importado da planilha", "", "frio")]),
    ("Contato", "21", [("Escritório Andrade", "ligação feita · ontem", "próxima ação: mensagem", ""),
                       ("Studio Forma", "reunião marcada · qui 10h", "", "")]),
    ("Proposta", "9", [("Contabilidade Silva", "proposta enviada · 3 dias", "follow-up sugerido", "")]),
    ("Ganho", "6", [("Imobiliária Lago", "fechado · esta semana", "", "ganho")]),
]

# ---------------------------------------------------------------- storyboards
# (chave, cor, título, [(cena, título, legenda)]) — as cenas vivem em build.py > SCENES
BOARDS = {
    "funil": ("verde", "Da primeira mensagem à venda, sem arrastar card", [
        ("conversa",  "O lead chega",          "Pela conversa no chatbot, pelo formulário do site ou pela planilha."),
        ("atividade", "O time registra",       "A ligação, a demonstração, a proposta — o que já faria de qualquer jeito."),
        ("etapa",     "A etapa avança",        "Cada atividade diz o que prova, e o lead sobe para a etapa certa."),
        ("proxima",   "A próxima ação aparece","Com um clique, a IA sugere ligar ou mandar mensagem, com o texto pronto."),
        ("ganho",     "A venda entra no painel","Fechados, em aberto e conversão do mês, sem planilha paralela."),
    ]),
    "entrada": ("petroleo", "O lead chega sem ninguém digitar", [
        ("conversa", "Conversa no chatbot", "Quem fala com o setor comercial vira lead, ligado à conversa."),
        ("site",     "Formulário do site",  "Um webhook com token recebe o lead da sua página."),
        ("planilha", "A planilha antiga",   "A IA lê planilha, PDF ou foto, tira os duplicados e mostra a prévia."),
        ("time",     "Vai para o vendedor", "O de menos leads abertos — ou a distribuição fica na mão."),
    ]),
}

# ---------------------------------------------------------------- capítulos
# (título, descrição, selo) — selo "" = produção; "IA" onde a IA decide. Nunca roadmap.
FUNIL = [
    ("A etapa vem das atividades",
     "Cada tipo de atividade e cada status dizem o que provam — contato feito, demonstração, "
     "proposta, venda. O lead sobe sozinho quando a prova entra.", ""),
    ("Nunca regride",
     "Uma ligação registrada depois da proposta não puxa o lead de volta. O funil só avança, e "
     "sair dele é decisão explícita.", ""),
    ("“Não atendeu” não é “perdido”",
     "Tentativa sem resposta não mata o lead. Só um status marcado por uma pessoa encerra a "
     "venda — e o sistema pede confirmação antes.", ""),
    ("Fora do perfil é outra coisa",
     "Lead que não era o seu público sai do funil separado dos perdidos. A taxa de conversão "
     "mede vendas, e não o anúncio que trouxe gente errada.", ""),
    ("Etapas com o seu nome",
     "Cada empresa cria e renomeia as próprias etapas, status e tipos de atividade. Uma tela "
     "mostra, degrau por degrau, o que faz o lead avançar.", ""),
    ("O quadro conta de verdade",
     "O número no topo de cada coluna vem do banco, não só do que está carregado na tela. "
     "Coluna cheia não aparece vazia.", ""),
]

DIA = [
    ("Próxima ação sugerida",
     "Com um clique, a IA lê o histórico do lead e sugere ligar ou mandar mensagem — já com o "
     "roteiro e o texto. Você edita antes de enviar. Ela não roda sozinha.", "IA"),
    ("WhatsApp a partir do lead",
     "O botão abre o WhatsApp com a mensagem pronta, ou uma conversa nova no atendimento, sem "
     "copiar número.", ""),
    ("Linha do tempo única",
     "Criação, anotações, atividades e mudanças de etapa num histórico só. Quem assume o lead "
     "não começa do zero.", ""),
    ("Ninguém fica sem resposta",
     "Lead novo que ninguém tocou no prazo gera aviso para o dono e, depois, para o gestor. O "
     "prazo conta só o horário útil — sexta à noite não estoura no sábado.", ""),
    ("Reunião ligada ao lead",
     "A reunião online é agendada no próprio lead ou na atividade, e a próxima aparece no card.", ""),
    ("Avaliação da reunião",
     "A partir da transcrição da reunião online, a IA dá nota e aponta o que o vendedor pode "
     "melhorar, seguindo o roteiro que você definir para aquele tipo de atividade.", "IA"),
]

ENTRADA = [
    ("Conversa vira lead",
     "Quem fala com o setor comercial no chatbot vira lead sozinho, com o vínculo à conversa. É "
     "uma opção que se liga no setor — o morador pedindo segunda via não entope o funil.", ""),
    ("Formulário do seu site",
     "Um webhook com token recebe os leads do site ou da landing page, sem ninguém copiar e colar.", ""),
    ("API para o seu sistema",
     "Listar, criar e atualizar leads e registrar anotações a partir de outro sistema.", ""),
    ("A planilha bagunçada",
     "A IA lê planilha, PDF ou foto, tira os duplicados e mostra uma prévia antes de gravar.", "IA"),
    ("Distribuição no time",
     "Lead novo pode ir para o vendedor com menos leads abertos. Ou fica na distribuição manual, "
     "se você preferir.", ""),
]

PAINEL = [
    ("O mês numa tela",
     "Em aberto, fechados, taxa de conversão e tempo médio — com o funil, a origem dos leads e as "
     "atividades das próximas 24 horas.", ""),
    ("Conversão que não mente",
     "Atendimento de quem já é cliente fica fora do funil comercial. A taxa mede venda, não suporte.", ""),
    ("Mapa dos leads",
     "Um pino por cidade, com a quantidade de leads — para ver onde a prospecção está concentrada.", ""),
    ("Envio com horário e limite",
     "Mensagens automáticas só saem nos dias e no horário escolhidos, pulando feriado, com limite "
     "diário por número de WhatsApp.", ""),
]

# Para quem é — os modelos prontos que a equipe aplica ao abrir a conta.
VERTICAIS = ["Contabilidade", "Imobiliária", "Clínica de estética", "Consultório",
             "Administradora de condomínio", "Instaladores", "Portaria remota", "Mídia indoor",
             "Genérico"]

DORES = [
    "O lead chegou no WhatsApp de um vendedor e ninguém mais sabe que ele existe.",
    "O CRM está desatualizado porque mover card é trabalho a mais que ninguém faz.",
    "O vendedor saiu e levou junto o histórico de cada conversa.",
    "A planilha do evento ficou numa pasta e nunca virou contato.",
    "O gestor só descobre que o lead esfriou quando pergunta.",
    "A taxa de conversão mistura venda com suporte, e ninguém confia no número.",
]

# ---------------------------------------------------------------- preço
# (nome, valor, unidade, descrição) — o valor do plano "Time" é o canônico.
PLANOS = [
    ("Sozinho", "Grátis", "1 usuário",
     "O funil, a próxima ação sugerida, o WhatsApp a partir do lead e o painel — tudo, para quem "
     "vende sozinho."),
    ("Time", "R$ " + PRECO, "por usuário, por mês",
     "Distribuição de leads no time, aviso de lead sem contato e o gestor vendo o funil de todos."),
    ("O que não custa à parte", "Incluso", "no mesmo preço",
     "Webhook e API, importação de planilha por IA e a sugestão de próxima ação."),
]

NAOS = [
    ("Sem cobrar por lead",
     "A cobrança é por vendedor que usa o sistema — não por lead, por mensagem ou por integração."),
    ("Sozinho é grátis",
     "Uma pessoa vendendo sozinha usa sem pagar. A conta cresce quando o time cresce."),
    ("Sem fidelidade",
     "Mês a mês. O produto tem que segurar você — não o contrato."),
]

# ---------------------------------------------------------------- honestidade
# O capítulo mais importante. Mesma lista do tópico `limites` da KB do chatbot.
NAO_FAZ = [
    ("Não tem app para instalar",
     "Funciona no navegador, inclusive no do celular, com o quadro e o botão para mover o lead de "
     "etapa. Mas não há aplicativo para baixar nem modo offline.", ""),
    ("Não gera proposta em PDF",
     "A proposta é registrada como atividade no lead e move o funil. Montar o documento e colher "
     "as assinaturas ainda fica fora do sistema.", ""),
    ("WhatsApp não é o canal oficial da Meta",
     "As mensagens automáticas saem do número da sua empresa por um conector não oficial. O limite "
     "diário existe para reduzir o risco de bloqueio — mas o risco não é zero.", ""),
    ("Anúncio do Facebook não entra sozinho",
     "O formulário dos anúncios do Facebook e do Instagram ainda não chega ao funil de qualquer "
     "empresa: depende de uma aprovação da Meta que não saiu.", ""),
    ("A IA não escuta telefonema",
     "O que a IA avalia é a reunião online transcrita. Ligação feita pelo celular do vendedor não "
     "passa por ela.", ""),
    ("Não é ferramenta de e-mail marketing",
     "Não há editor de campanha nem sincronização com agenda externa. O foco é o funil de vendas.", ""),
    ("A conta é aberta com a gente",
     "Não existe cadastro pelo site. Quem abre a conta, cria os acessos do time e escolhe o modelo "
     "do seu mercado é a nossa equipe, junto com você, numa conversa.", ""),
]

# ---------------------------------------------------------------- lineup
# (nome, descrição, cor, selo)
TILES = [
    ("Funil automático",     "A etapa avança pelo que o time registra.",               "verde",    ""),
    ("Próxima ação",         "Sugestão com roteiro e texto, gerada no clique.",        "petroleo", "IA"),
    ("WhatsApp no lead",     "Mensagem pronta ou conversa no atendimento.",            "verde",    ""),
    ("Aviso de primeiro contato", "Dono e gestor avisados, contando horário útil.",    "ambar",    ""),
    ("Entrada de leads",     "Chatbot, webhook, API e importação por IA.",             "petroleo", ""),
    ("Distribuição",         "Para quem tem menos leads abertos, ou na mão.",          "verde",    ""),
    ("Reunião avaliada",     "Nota e pontos de melhoria a partir da transcrição.",     "ambar",    "IA"),
    ("Painel de vendas",     "Conversão, origem, funil e mapa dos leads.",             "petroleo", ""),
    ("Modelo do seu mercado","Nove modelos prontos, tudo editável depois.",            "verde",    ""),
]

CTA = ("Vamos colocar o seu funil para andar.",
       "Conte como o seu time vende hoje e a gente mostra o vendeaqui rodando com o seu jeito de vender.")
