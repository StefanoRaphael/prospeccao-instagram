"""Reprocessa leads.json existente aplicando as copies fixas (Parte 2) e a
correção de perna, sem chamar Apify/Groq de novo. Depois regenera o painel."""
import json
import os

import qualificar
import painel

ESTADO = os.path.join(os.path.dirname(__file__), "estado")
LEADS = os.path.join(ESTADO, "leads.json")


def main():
    with open(LEADS, encoding="utf-8") as f:
        leads = json.load(f)

    atualizados = 0
    for lead in leads:
        handle = lead["handle"]
        if handle in qualificar.COPIES_RODADA_02_07_2026:
            nova_q = qualificar.qualificar(lead["item"])
            lead["q"] = nova_q
            atualizados += 1
            print(f"  atualizado @{handle} -> {nova_q['perna']}")
        else:
            print(f"  sem copy fixa para @{handle}, mantendo qualificacao atual")

    with open(LEADS, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    painel.gerar(leads, {"reprocessamento": atualizados})
    print(f"Concluido. {atualizados}/{len(leads)} leads atualizados com copies fixas.")


if __name__ == "__main__":
    main()
