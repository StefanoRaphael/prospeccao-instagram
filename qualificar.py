"""Camada 2 — Qualificacao. A IA (Groq) aplica a rubrica do Stefano, da nota,
diagnostica o gap, aponta a perna da escada de valor e escreve a abordagem
multicanal (DM, WhatsApp, e-mail). Carrega copies fixas (Parte 2) quando disponíveis."""
import json
import re
from groq import Groq
import config
from outreach_copies import COPIES_RODADA_02_07_2026

ESCADA = """
ESCADA DE VALOR DO STEFANO (use para indicar o proximo passo):
- Perna 1 ESTRATEGIA (o cerebro): Consultoria R$2.800 unica / Assessoria R$2.500 mes / Growth R$5.000 mes.
  Para quem tem foto boa mas nao sabe o que postar, sem linha editorial.
- Perna 2 EXECUCAO/RRSS (as maos): Essencial R$1.350 / Profissional R$1.500 / Autoridade R$1.200 mes trimestral.
  Para quem sabe o que quer mas produz amador (feed baguncado, sem paleta).
- Perna 3 COMBOS (cerebro+maos): Combo Inicio R$3.490 / Operacao R$2.990 mes / Escala R$6.900 mes.
  Para quem esta perdido em tudo, ou ja anuncia sem retorno (Escala).
"""

TOM = """
TOM DE VOZ: direto, tecnico, focado em conversao. Sem jargao motivacional, sem clichê de coach.
Usa "voce" e "seu". Zero cortesia vazia. Nada de travessao no meio do texto (use ponto ou virgula).
NAO ofereca preco no primeiro contato: abra com uma observacao especifica do perfil dele (o gap real)
e plante a perna certa como proximo passo.
"""

REGRAS_CANAL = """
REGRAS OBRIGATORIAS DE COLD OUTREACH (nunca quebrar):

1. PROIBIDO fingir conversa anterior. Nunca escrever "continuar nossa conversa",
   "como mencionado anteriormente", "seguir em frente com" ou qualquer frase que sugira
   que ja houve troca de mensagem antes. Cada canal (DM, WhatsApp, e-mail) e o PRIMEIRO
   contato NAQUELE canal especifico.

2. No WhatsApp e no e-mail, referencie o canal anterior com honestidade, sem fingir resposta:
   "te mandei uma mensagem no Instagram [dias atras], mas direct de quem nao se segue
   costuma ficar invisivel / passar batido / sumir facil / nao ser visto" (varie a frase).
   No e-mail, referencie tanto Instagram quanto WhatsApp: "tentei contato por Instagram
   e WhatsApp; formalizo/envio por aqui".

3. DIAGNOSTICO NUNCA GENERICO. Proibido usar frases prontas tipo "boa qualidade visual,
   mas copy fraca, ausencia de CTA, mensagem confusa" literalmente. Calcule e cite um
   DADO REAL do perfil: numero de seguidores, % de engajamento (Median ER), e o numero
   aproximado de interacoes por post (seguidores x ER). Use esse numero como prova
   concreta do gap, nao como adjetivo vago.

4. Angulo de abordagem por faixa de ER (Median ER):
   - ER acima de 3%: audiencia pequena mas QUENTE. Angulo = "engajamento alto, falta so
     estrutura de conversao pra virar agenda" (ex: Combo Operacao/Escala).
   - ER entre 1% e 3%: "a audiencia responde, falta o sistema" (estrutura, linha editorial).
   - ER abaixo de 1%: "ativo parado". Se a base for grande (>8mil seguidores), reforce que
     e um patrimonio digital subutilizado. Se for pequena, foque no gap de conversao.

5. Estrutura da mensagem: elogio tecnico legitimo (algo real que o perfil faz bem) + gap
   com dado + convite para conversa. NUNCA emendar 3 criticas seguidas.

6. Fechamento leve na DM: pergunta respondivel com uma palavra (ex: "Faz sentido?",
   "Quer ver?"). NUNCA pedir reuniao na DM — isso fica pro WhatsApp/e-mail.

7. Slots PANDORA26: toda mensagem carrega um trecho literal no formato
   "(PANDORA26: <instrucao do que preencher>)" que fica VAZIO para preenchimento manual
   depois. NUNCA invente o conteudo do slot, apenas descreva o que deve entrar ali:
   - Na DM: "(PANDORA26: 1 frase citando um post/legenda especifico onde o gap aparece.)"
   - No WhatsApp: "(PANDORA26: achados principais.)"
   - No e-mail: "(PANDORA26: achado mais forte do PDF como amostra.)"

8. Se a conta for de clinica/negocio (nao pessoa fisica), endereце ao decisor identificado
   na bio ou nos posts, nunca a "marca" generica.

9. Limites: DM ate 4 frases. WhatsApp ate 6 frases. E-mail ate 8 frases + assinatura
   "Stefano Raphael · Marketing & Estrategias · +55 11 98646-8081".

10. Nunca citar preco ou nome de pacote na copy. A oferta se apresenta na reuniao.

11. Varie aberturas e fechamentos entre leads do mesmo nicho. Nao repita a mesma
    estrutura de frase para dois leads parecidos.
"""

REGRA_PERNA_SOLO = """
CLASSIFICACAO DE PERNA (regra critica):
Perna 1 Consultoria SOMENTE se houver sinal explicito de equipe de marketing/social
media interno na bio (ex: "nossa equipe", "agencia", "gestor de trafego"). Profissional
liberal solo (sem esse sinal) NUNCA recebe Perna 1: vai para Perna 2 Profissional
(se falta so execucao/visual) ou Combo Operacao/Escala (se falta tudo, estrategia e execucao).
"""

RUBRICA = """
Voce qualifica leads para um estudio de comunicacao premium. O ALVO e a conta que
TEM material visual bom mas COMUNICA mal (sem gancho, sem CTA, feed sem paleta,
video sem roteiro, aposta em visualizacao mas nao converte).

Pontue de 0 a 10 somando 5 criterios (0 a 2 cada):
1. Qualidade visual aparente (foto/video tem potencial estetico)
2. Fraqueza de copy (legenda vaga, sem gancho, sem estrutura) -> quanto pior, MAIOR a nota
3. Ausencia de CTA (nao pede acao, nao direciona pra venda) -> nota alta
4. Mensagem confusa (nao da pra entender o diferencial em 5s) -> nota alta
5. Sinal de verba (servico de ticket alto, indicio de que pode pagar marketing)

DESCARTE (nota 0) se: parece bot/seguidor comprado (engajamento incoerente com o tamanho),
ja e redondo/profissional (provavelmente tem agencia), ou nao e da regiao de Taubate/Vale do Paraiba.
"""

SCHEMA = """
Responda APENAS um JSON valido, sem texto fora dele, com as chaves:
{
  "nota": <int 0-10>,
  "motivo": "<1 frase citando o DADO REAL do perfil (seguidores, ER, interacoes por post), nunca generica>",
  "perna": "<Perna 1 Consultoria | Perna 2 Profissional | Combo Operacao | Combo Escala | DESCARTE>",
  "dm_instagram": "<DM ate 4 frases, com dado real + gap + fechamento leve + slot PANDORA26>",
  "msg_whatsapp": "<mensagem ate 6 frases, referencia honesta a DM anterior + dado + slot PANDORA26 + convite pra 15min>",
  "email_assunto": "<assunto curto citando o handle e o achado principal>",
  "email_corpo": "<e-mail ate 8 frases + slot PANDORA26 + assinatura 'Stefano Raphael · Marketing & Estrategias · +55 11 98646-8081'>"
}
"""


def _interacoes_por_post(item):
    """Calcula interacoes aproximadas por post: seguidores x ER."""
    seg = item.get("Followers Count") or 0
    er_raw = str(item.get("Median ER", "0") or "0").replace("%", "").replace(",", ".").strip()
    try:
        er = float(er_raw) / 100
    except ValueError:
        er = 0.0
    try:
        seg = float(seg)
    except (ValueError, TypeError):
        seg = 0.0
    return round(seg * er)


def _resumo_lead(item):
    posts = " | ".join(
        str(item.get(f"Post {i}", "") or "")[:200] for i in range(1, 6)
    )
    interacoes = _interacoes_por_post(item)
    return f"""
Conta: {item.get('Account')}
Nome: {item.get('Full Name')}
Seguidores: {item.get('Followers Count')}
Categoria: {item.get('Category')}
Engajamento (Median ER): {item.get('Median ER')}  Quality: {item.get('Quality')}
Interacoes estimadas por post (seguidores x ER): {interacoes}
Likes medios: {item.get('Avg Likes')}  Comentarios: {item.get('Avg Comments')}  Views: {item.get('Median Views')}
Bio: {item.get('Biography')}
Ultimos posts: {posts}
"""


def _extract_handle(item):
    """Extrai handle do campo Account."""
    conta = item.get("Account", "") or ""
    return conta.rstrip("/").split("/")[-1].lower()


def _detecta_solo_freelancer(item):
    """True se nao ha sinal de equipe de marketing (ex: 'agencia', 'studio', 'team').
    Solo freelancers devem ir para Pacotes ou Combo, nao Perna 1."""
    texto = (item.get("Biography", "") or "") + " " + (item.get("Full Name", "") or "")
    texto = texto.lower()
    sinais_equipe = ["agencia", "studio", "equipe", "team", "gestor", "marketing",
                     "empresa", "consultoria", "profissional marketing"]
    return not any(sinal in texto for sinal in sinais_equipe)


def _median_er(item):
    """Extrai Median ER como float (%), ex: '0.80%' -> 0.80."""
    raw = str(item.get("Median ER", "0") or "0").replace("%", "").replace(",", ".").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _seguidores(item):
    seg = item.get("Followers Count") or 0
    try:
        return float(seg)
    except (ValueError, TypeError):
        return 0.0


# Regra de corte numerica e fixa (auditavel). Nao varia por lead nem por "achismo".
# Operador em todos os cortes e >= (maior ou igual). Um lead com ER exatamente 5.00%
# cai em Combo Escala, nao em Combo Operacao; ER exatamente 3.00% cai em Combo Operacao,
# nao em Perna 2; seguidores exatamente 10000 conta como "base grande". O Median ER
# do actor vem com 2 casas decimais, entao a fronteira e estavel (nao ha ambiguidade
# de arredondamento: 4.995 nao existe como valor de entrada, o dado real seria 5.00 ou 4.99).
LIMIAR_BASE_GRANDE = 10000      # seguidores >= este valor conta como "ativo grande"
LIMIAR_ER_ESCALA = 5.0          # % Median ER >= este valor -> audiencia muito quente
LIMIAR_ER_COMBO = 3.0           # % Median ER >= este valor -> audiencia quente

# Piso estatistico: ER alto com base muito pequena costuma ser ruido (1 post viral
# isolado, nao um padrao real de engajamento). Abaixo deste piso de seguidores, ER
# alto NAO justifica oferta recorrente (Combo) por falta de amostra: um perfil de
# 300 seguidores com 12 curtidas num post ja bate 4% de ER sem nenhuma base real.
# Esses casos caem em Perna 2 (oferta pontual) ate a base crescer o suficiente pra
# validar o padrao de engajamento.
LIMIAR_SEGUIDORES_MINIMO_ER = 1500


def classifica_perna(item):
    """Classificacao deterministica de perna, unica fonte de verdade.
    Ignora qualquer valor de 'perna' vindo de copy manual ou da IA: sempre recalcula
    a partir de seguidores e Median ER com os limiares acima.

    Regra (nessa ordem):
    - Perna 1 Consultoria: só se houver equipe de marketing/social media na bio.
    - Seguidores < 1.500: sempre Perna 2 Profissional, mesmo com ER alto (amostra
      pequena demais pra sustentar oferta recorrente; ver LIMIAR_SEGUIDORES_MINIMO_ER).
    - ER >= 5%: Combo Escala (audiencia muito quente, estruturar + escalar com trafego).
    - ER >= 3%: Combo Operacao (audiencia quente, falta so estrutura de conversao).
    - Seguidores >= 10.000 (com ER abaixo de 3%): Combo Operacao (ativo grande parado
      ou base grande sem sistema, seguidores como criterio isolado).
    - Resto (ER < 3% e seguidores entre 1.500 e 10.000): Perna 2 Profissional.
    """
    if not _detecta_solo_freelancer(item):
        return "Perna 1 Consultoria"

    er = _median_er(item)
    seg = _seguidores(item)

    if seg < LIMIAR_SEGUIDORES_MINIMO_ER:
        return "Perna 2 Profissional"
    if er >= LIMIAR_ER_ESCALA:
        return "Combo Escala"
    if er >= LIMIAR_ER_COMBO:
        return "Combo Operacao"
    if seg >= LIMIAR_BASE_GRANDE:
        return "Combo Operacao"
    return "Perna 2 Profissional"


def _gera_motivo(item):
    """Diagnostico especifico por lead, sempre com dado real (nunca frase generica)."""
    seg = int(_seguidores(item))
    er = _median_er(item)
    interacoes = _interacoes_por_post(item)
    if seg < LIMIAR_SEGUIDORES_MINIMO_ER and er >= LIMIAR_ER_COMBO:
        angulo = "ER alto mas base pequena demais para validar o padrão (amostra insuficiente)"
    elif er >= LIMIAR_ER_COMBO:
        angulo = "audiência pequena mas quente: engajamento acima da média e sem estrutura de conversão"
    elif er >= 1.0:
        angulo = "audiência responde, mas falta sistema (linha editorial e CTA) para converter"
    elif seg >= LIMIAR_BASE_GRANDE:
        angulo = "ativo digital grande e subutilizado, engajamento não acompanha o tamanho da base"
    else:
        angulo = "engajamento baixo indica ausência de estrutura de conversão nas legendas"
    return f"{seg} seguidores, ER {er}% (~{interacoes} interações por post): {angulo}."


def qualificar(item):
    handle = _extract_handle(item)

    # Verifica se há copy fixa disponível (Parte 2)
    if handle in COPIES_RODADA_02_07_2026:
        copia_fixa = COPIES_RODADA_02_07_2026[handle]
        return {
            "nota": 8,
            "motivo": _gera_motivo(item),
            "perna": classifica_perna(item),
            "dm_instagram": copia_fixa.get("dm_instagram", ""),
            "msg_whatsapp": copia_fixa.get("msg_whatsapp", ""),
            "email_assunto": copia_fixa.get("email_assunto", ""),
            "email_corpo": copia_fixa.get("email_corpo", ""),
        }

    # Sem copy fixa: gera via Groq seguindo as regras permanentes (Parte 1)
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = (f"{RUBRICA}\n{ESCADA}\n{TOM}\n{REGRAS_CANAL}\n{REGRA_PERNA_SOLO}\n{SCHEMA}"
              f"\n\nLEAD:\n{_resumo_lead(item)}")
    resp = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    texto = resp.choices[0].message.content
    try:
        resultado = json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texto, re.DOTALL)
        if not m:
            return {"nota": 0, "perna": "DESCARTE", "motivo": "falha ao qualificar"}
        resultado = json.loads(m.group(0))

    # Perna e motivo nunca vem da IA nem de copy manual: sempre recalculados pela
    # regra numerica fixa, para o criterio ser sempre o mesmo e auditavel.
    if resultado.get("perna") != "DESCARTE":
        resultado["perna"] = classifica_perna(item)
        resultado["motivo"] = _gera_motivo(item)
    return resultado
