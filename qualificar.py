"""Camada 2 — Qualificacao. A IA (Groq) aplica a rubrica do Stefano, da nota,
diagnostica o gap, aponta a perna da escada de valor e escreve a abordagem
multicanal (DM, WhatsApp, e-mail)."""
import json
import re
from groq import Groq
import config

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
  "motivo": "<1 frase: por que essa nota, citando o gap concreto>",
  "perna": "<Perna 1 Consultoria | Perna 2 Profissional | Perna 3 Combo Inicio | Combo Escala | DESCARTE>",
  "dm_instagram": "<DM curto e especifico, 2-3 frases, abre com observacao do perfil dele>",
  "msg_whatsapp": "<mensagem de follow-up pro WhatsApp, tom proximo, cita que viu o Instagram>",
  "email_assunto": "<assunto curto e direto>",
  "email_corpo": "<e-mail mais elaborado, 4-6 linhas, pode anexar mini diagnostico>"
}
"""


def _resumo_lead(item):
    posts = " | ".join(
        str(item.get(f"Post {i}", "") or "")[:200] for i in range(1, 6)
    )
    return f"""
Conta: {item.get('Account')}
Nome: {item.get('Full Name')}
Seguidores: {item.get('Followers Count')}
Categoria: {item.get('Category')}
Engajamento (Median ER): {item.get('Median ER')}  Quality: {item.get('Quality')}
Likes medios: {item.get('Avg Likes')}  Comentarios: {item.get('Avg Comments')}  Views: {item.get('Median Views')}
Bio: {item.get('Biography')}
Ultimos posts: {posts}
"""


def qualificar(item):
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = f"{RUBRICA}\n{ESCADA}\n{TOM}\n{SCHEMA}\n\nLEAD:\n{_resumo_lead(item)}"
    resp = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    texto = resp.choices[0].message.content
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texto, re.DOTALL)
        return json.loads(m.group(0)) if m else {"nota": 0, "perna": "DESCARTE",
                                                 "motivo": "falha ao qualificar"}
