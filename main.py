"""Orquestrador. Roda todos os nichos: busca -> qualifica -> acumula -> painel.
Mantem estado (seen.json) para nao repetir leads entre rodadas (dedup)."""
import json
import os
import sys

import config
import nichos
import buscar
import qualificar
import painel

ESTADO = os.path.join(os.path.dirname(__file__), "estado")
SEEN = os.path.join(ESTADO, "seen.json")
LEADS = os.path.join(ESTADO, "leads.json")


def _carrega(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return padrao


def _salva(caminho, dado):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dado, f, ensure_ascii=False, indent=2)


def main():
    if not config.APIFY_TOKEN or not config.GROQ_API_KEY:
        sys.exit("Faltam APIFY_TOKEN ou GROQ_API_KEY no ambiente.")

    vistos = _carrega(SEEN, [])
    leads = _carrega(LEADS, [])
    resumo = {}

    for nome, nicho in nichos.NICHOS.items():
        print(f"Nicho: {nome}")
        try:
            itens = buscar.buscar_nicho(nome, nicho, vistos)
        except Exception as e:
            print(f"  erro na busca: {e}")
            resumo[nome] = 0
            continue
        novos = 0
        for it in itens:
            h = buscar.handle_de(it)
            if not h or h in vistos:
                continue
            vistos.append(h)
            if not buscar.e_da_regiao(it):
                print(f"  - @{h} fora da regiao (sem mencao a Taubate/Vale)")
                continue
            try:
                q = qualificar.qualificar(it)
            except Exception as e:
                print(f"  erro ao qualificar {h}: {e}")
                continue
            if q.get("nota", 0) >= config.NOTA_CORTE and q.get("perna") != "DESCARTE":
                leads.append({"handle": h, "item": it, "q": q, "nicho": nicho["rotulo"]})
                novos += 1
                print(f"  + @{h} nota {q['nota']} ({q.get('perna')})")
        resumo[nome] = novos

    _salva(SEEN, vistos)
    _salva(LEADS, leads)
    painel.gerar(leads, resumo)
    print(f"Concluido. Total acumulado: {len(leads)} leads. Vistos: {len(vistos)}.")


if __name__ == "__main__":
    main()
