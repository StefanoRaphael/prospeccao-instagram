"""Nichos ativos da prospeccao. Para escalar, basta adicionar um bloco novo.
Cada nicho define hashtags e termos de busca usados pelo modo keywordDiscovery."""

NICHOS = {
    "nutrologia": {
        "rotulo": "Nutrologia / Medicina Integrativa",
        "hashtags": [
            # Genericas (nicho certo, geografia pela trava)
            "nutrologia", "nutrologo", "nutrologa", "medicinaintegrativa",
            # Regionais (puxam direto quem e do Vale, SJC na frente por ser maior)
            "nutrologosjc", "nutrologiasjc", "nutrologasjc",
            "medicinaintegrativasjc", "saojosedoscampos", "sjc",
            "nutrologiataubate", "nutrologotaubate", "valedoparaiba",
        ],
        "queries": [
            "nutrologo sao jose dos campos", "nutrologia sjc",
            "medicina integrativa sao jose dos campos", "nutrologa sjc",
            "nutrologo vale do paraiba", "nutrologia vale do paraiba",
            "nutrologo taubate", "medicina integrativa vale do paraiba",
            "nutrologo jacarei", "nutrologo caraguatatuba",
        ],
    },
    # Prontos para ligar quando o nicho de nutri estiver calibrado:
    # "estetica": {
    #     "rotulo": "Clinicas de Estetica / Cirurgia Plastica",
    #     "hashtags": ["harmonizacaofacial", "esteticaavancada", "cirurgiaplastica",
    #                  "esteticataubate", "preenchimento", "botox"],
    #     "queries": ["clinica de estetica taubate", "cirurgiao plastico taubate",
    #                 "harmonizacao facial vale do paraiba"],
    # },
    # "arquitetura": {
    #     "rotulo": "Arquitetura e Design de Interiores",
    #     "hashtags": ["arquitetura", "designdeinteriores", "interiores",
    #                  "arquiteturataubate", "projetodeinteriores"],
    #     "queries": ["arquiteto taubate", "design de interiores vale do paraiba",
    #                 "escritorio de arquitetura sao jose dos campos"],
    # },
}
