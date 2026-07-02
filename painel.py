"""Camada 3 — Painel. Gera docs/index.html com os leads qualificados, ordenados
por nota, com @ clicavel, metricas, contatos e mensagens prontas pra copiar."""
import html
import json
import os
from datetime import datetime, timezone, timedelta

DOCS = os.path.join(os.path.dirname(__file__), "docs")
BR = timezone(timedelta(hours=-3))


def _num(v):
    """Converte campo do actor em numero (aceita '7813', 7813, '0.29%')."""
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace("%", "").replace(",", ".").strip())
    except (ValueError, AttributeError):
        return 0.0


def classifica_audiencia(item):
    """Distingue audiencia real de suspeita (bot/comprada) pela coerencia dos
    numeros absolutos, nao pelo ER sozinho. ER baixo + profissional real = alvo."""
    seg = _num(item.get("Followers Count"))
    likes = _num(item.get("Avg Likes"))
    coment = _num(item.get("Avg Comments"))
    views = _num(item.get("Median Views"))
    if seg <= 0:
        return "Audiência: indefinida"
    taxa = (likes + coment) / seg
    # Suspeita: conta grande com engajamento absoluto morto e quase sem comentario.
    morta = taxa < 0.005 and coment < 3 and seg > 8000 and views < seg * 0.02
    return "Audiência: suspeita" if morta else "Audiência: real"


def _tel(item):
    tel = (item.get("Phone") or "").strip()
    if tel and tel != "N/A":
        return "".join(c for c in tel if c.isdigit())
    url = item.get("External URL") or ""
    m = "".join(c for c in url if c.isdigit())
    return m if "wa" in url.lower() and len(m) >= 10 else ""


def _destaca_pandora26(txt):
    """Destaca slots PANDORA26 no texto com uma cor diferente."""
    import re
    # Substitui (PANDORA26: ...) por uma versão destacada
    padrao = r'\(PANDORA26: ([^)]*)\)'
    substituido = re.sub(padrao, r'<mark class="pandora26">(PANDORA26: \1)</mark>', txt)
    return substituido


def _card(lead):
    it = lead["item"]
    q = lead["q"]
    handle = lead["handle"]
    tel = _tel(it)
    email = (it.get("Email") or "").strip()
    email = "" if email == "N/A" else email
    aud = classifica_audiencia(it)
    aud_cls = "ok" if aud.endswith("real") else ("bad" if aud.endswith("suspeita") else "")
    wa = f'<a class="btn wa" href="https://wa.me/{tel}" target="_blank">WhatsApp</a>' if tel else ""
    mail = (f'<a class="btn mail" href="mailto:{email}?subject={html.escape(q.get("email_assunto",""))}">E-mail</a>'
            if email else "")
    msgs = ""
    for rotulo, chave in [("DM Instagram", "dm_instagram"), ("WhatsApp", "msg_whatsapp"),
                          ("E-mail", "email_corpo")]:
        txt = q.get(chave, "") or ""
        txt_escaped = html.escape(txt)
        txt_highlighted = _destaca_pandora26(txt_escaped)
        msgs += f'''<div class="msg"><div class="mh">{rotulo}
          <button class="copy" onclick="cp(this)">copiar</button></div>
          <pre>{txt_highlighted}</pre></div>'''
    return f'''
    <div class="card nota{q.get('nota',0)}">
      <div class="top">
        <div>
          <a class="user" href="https://instagram.com/{handle}" target="_blank">@{handle}</a>
          <div class="nome">{html.escape(str(it.get('Full Name','')))}</div>
        </div>
        <div class="nota">{q.get('nota','?')}<span>/10</span></div>
      </div>
      <div class="met">
        <span>{it.get('Followers Count','?')} seg.</span>
        <span>ER {it.get('Median ER','?')}</span>
        <span class="aud {aud_cls}">{aud}</span>
        <span class="perna">{html.escape(str(q.get('perna','')))}</span>
      </div>
      <div class="motivo">{html.escape(str(q.get('motivo','')))}</div>
      <div class="acoes"><a class="btn ig" href="https://instagram.com/{handle}" target="_blank">Abrir perfil</a>{wa}{mail}</div>
      {msgs}
    </div>'''


def gerar(leads, resumo):
    leads = sorted(leads, key=lambda l: l["q"].get("nota", 0), reverse=True)
    agora = datetime.now(BR).strftime("%d/%m/%Y %H:%M")
    linhas_resumo = " · ".join(f"{k}: {v}" for k, v in resumo.items())
    cards = "\n".join(_card(l) for l in leads) or '<p class="vazio">Nenhum lead novo qualificado ainda. O cron acumula a cada rodada.</p>'
    doc = f'''<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prospecção Instagram — Stefano Raphael</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0d0f12;color:#e8eaed;margin:0;padding:24px}}
 header{{max-width:900px;margin:0 auto 20px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#9aa0a6;font-size:13px}}
 .wrap{{max-width:900px;margin:0 auto;display:grid;gap:16px}}
 .card{{background:#1a1d21;border:1px solid #2a2e33;border-radius:12px;padding:16px}}
 .card.nota9,.card.nota10{{border-color:#34a853}} .card.nota8{{border-color:#5b8c3e}}
 .top{{display:flex;justify-content:space-between;align-items:flex-start}}
 .user{{color:#8ab4f8;font-weight:600;font-size:16px;text-decoration:none}}
 .nome{{color:#9aa0a6;font-size:13px;margin-top:2px}}
 .nota{{font-size:26px;font-weight:700;color:#34a853}} .nota span{{font-size:13px;color:#9aa0a6}}
 .met{{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0;font-size:12px;color:#bdc1c6}}
 .met span{{background:#23272c;padding:3px 8px;border-radius:6px}} .perna{{background:#3c2f1a !important;color:#f7c873}}
 .aud.ok{{background:#16331f !important;color:#5bd17e}} .aud.bad{{background:#3a1a1a !important;color:#f08a8a}}
 .motivo{{font-size:13px;color:#cdd1d5;margin:8px 0;line-height:1.4}}
 .acoes{{display:flex;gap:8px;margin:10px 0}}
 .btn{{font-size:12px;padding:6px 12px;border-radius:6px;text-decoration:none;color:#fff}}
 .ig{{background:#5b3a8c}} .wa{{background:#25d366;color:#062b14}} .mail{{background:#3b6ea5}}
 .msg{{margin-top:10px}} .mh{{font-size:11px;color:#9aa0a6;text-transform:uppercase;letter-spacing:.5px;display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}}
 .copy{{background:#2a2e33;color:#e8eaed;border:0;border-radius:5px;padding:3px 8px;font-size:11px;cursor:pointer}}
 pre{{background:#0d0f12;border:1px solid #2a2e33;border-radius:6px;padding:10px;white-space:pre-wrap;font-size:13px;margin:0;line-height:1.45}}
 .vazio{{color:#9aa0a6;text-align:center;padding:40px}}
</style></head><body>
<header>
 <h1>Prospecção Instagram</h1>
 <div class="sub">Última rodada: {agora} (BRT) · {len(leads)} leads qualificados · {linhas_resumo}</div>
</header>
<div class="wrap">{cards}</div>
<script>
 function cp(b){{const t=b.parentElement.parentElement.querySelector('pre').innerText;
   navigator.clipboard.writeText(t);b.innerText='copiado';setTimeout(()=>b.innerText='copiar',1200);}}
</script>
</body></html>'''
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"  painel gerado com {len(leads)} leads")
