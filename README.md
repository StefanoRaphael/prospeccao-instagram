# Prospecção Instagram

Ecossistema que descobre, qualifica e prepara abordagem de leads no Instagram
(Taubaté e região), girando na nuvem sem intervenção. Painel privado abre no Mac às 10h.

## Como funciona
1. **GitHub Actions** (cron 08h BRT) roda `main.py` de madrugada, sem o Mac ligado.
2. `buscar.py` chama o actor Apify por nicho (modo hashtag + trava de localização),
   com `excludeAccounts` para não repetir leads.
3. `qualificar.py` usa a IA (Groq) com a rubrica do Stefano: nota 0-10, gap,
   perna da escada de valor e mensagens prontas (DM, WhatsApp, e-mail).
4. `painel.py` gera `docs/index.html`. O Action commita painel e estado de volta.
5. **launchd no Mac** (`com.stefano.prospeccao.plist`) às 10h faz `git pull` e abre o painel.

Nada de automação logada no Instagram. O disparo é manual (regra de ouro:
automatizar a inteligência, nunca a ação logada).

## Configuração de secrets (GitHub)
- `APIFY_TOKEN` — token cron-prospeccao da Apify
- `GROQ_API_KEY` — chave Groq

## Escalar nichos
Descomente os blocos em `nichos.py`. Cada nicho vira uma rodada independente
(teto de 5 candidatos/rodada no plano gratuito da Apify; crédito ~US$5/mês renova).

## Rodar manualmente
- Na nuvem: aba Actions > Prospeccao Instagram > Run workflow.
- Local: criar `.env` com as duas chaves e rodar `python main.py`.

## Instalar o abre-painel no Mac (uma vez)
```
cp com.stefano.prospeccao.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.stefano.prospeccao.plist
```
