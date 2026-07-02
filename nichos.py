"""Nichos ativos da prospeccao. Para escalar, basta adicionar um bloco novo.
Cada nicho define hashtags e termos de busca usados pelo modo keywordDiscovery.
Regiao alvo: Taubate, SJC, Tremembe, Pindamonhangaba, Santo Antonio do Pinhal,
Campos do Jordao e demais cidades do Vale do Paraiba."""

# Termos para classificar um perfil achado por geolocalizacao (bio/posts) em um nicho.
TERMOS_NICHO = {
    "nutrologia": ["nutrolog", "nutri", "emagrec", "medicina integrativa",
                   "longevidade", "metabol", "endocrin"],
    "estetica": ["estetic", "estética", "harmoniza", "botox", "preench",
                 "cirurgia plast", "cirurgiao plast", "dermato", "biomedic",
                 "nanopigment", "lipo", "rejuvenesc"],
    "arquitetura": ["arquitet", "interiores", "design de interiores",
                    "reforma", "projeto", "marcenaria", "paisagis"],
}


def classifica_nicho(item):
    """Dado um perfil (achado por geo), descobre a qual nicho pertence pela bio/posts."""
    texto = (item.get("Biography", "") or "")
    for i in range(1, 6):
        texto += " " + str(item.get(f"Post {i}", "") or "")
    texto = texto.lower()
    for nicho, termos in TERMOS_NICHO.items():
        if any(t in texto for t in termos):
            return nicho
    return None


NICHOS = {
    "nutrologia": {
        "rotulo": "Nutrologia / Medicina Integrativa",
        # Ancoras: leads bons ja encontrados. O Instagram traz contas similares
        # (mesmo nicho, tendem a ser da mesma regiao). Sem hashtag.
        "ancoras": ["dra.bruna.alfenas", "carolbonani_nutri",
                    "dra.dripavanitto", "rafabarbosacouto.nutri",
                    "renatoosorionutricionista"],
        "hashtags": [
            "nutrologia", "nutrologo", "nutrologa", "medicinaintegrativa",
            "nutrologosjc", "nutrologiasjc", "nutrologasjc", "medicinaintegrativasjc",
            "nutrologiataubate", "nutrologotaubate",
            "saojosedoscampos", "sjc", "valedoparaiba", "camposdojordao",
        ],
        "queries": [
            "nutrologo sao jose dos campos", "nutrologia sjc",
            "medicina integrativa sao jose dos campos", "nutrologa sjc",
            "nutrologo taubate", "nutrologo pindamonhangaba",
            "nutrologo vale do paraiba", "nutrologo campos do jordao",
            "nutrologo jacarei", "medicina integrativa vale do paraiba",
        ],
    },
    "estetica": {
        "rotulo": "Clinicas de Estetica / Cirurgia Plastica",
        "ancoras": ["dredgardcoutinhosjc", "vanessagomesclinic",
                    "tarcilataborda_dermato", "posoperatoriosjcampos",
                    "dramonicafadul",
                    # Anestesiologistas de Taubate (confirmado pelo Stefano, conhece
                    # pessoalmente). Nao sao alvo direto (trabalham por indicacao,
                    # sem captacao propria de paciente), mas servem de semente de rede
                    # regional confirmada: o Instagram tende a sugerir outros medicos
                    # da mesma orbita hospitalar (cirurgioes, dermatos) a partir deles.
                    "dra.marcelalemes", "anestesiologistas_associados_",
                    "dranaraderrico"],
        "hashtags": [
            "harmonizacaofacial", "esteticaavancada", "cirurgiaplastica",
            "preenchimento", "botox", "estetica",
            "esteticasjc", "esteticataubate", "harmonizacaofacialsjc",
            "cirurgiaplasticasjc", "saojosedoscampos", "valedoparaiba",
        ],
        "queries": [
            "clinica de estetica sao jose dos campos", "clinica de estetica taubate",
            "cirurgiao plastico sao jose dos campos", "cirurgiao plastico taubate",
            "harmonizacao facial sjc", "harmonizacao facial vale do paraiba",
            "clinica de estetica pindamonhangaba", "esteticista campos do jordao",
            "clinica de estetica jacarei", "biomedica esteta vale do paraiba",
        ],
    },
    "arquitetura": {
        "rotulo": "Arquitetura e Design de Interiores",
        "ancoras": [],   # sem lead-ancora ainda; entra pela geolocalizacao
        "hashtags": [
            "arquitetura", "designdeinteriores", "interiores",
            "projetodeinteriores", "arquiteturadeinteriores",
            "arquiteturasjc", "arquiteturataubate", "designdeinterioressjc",
            "saojosedoscampos", "valedoparaiba", "camposdojordao",
        ],
        "queries": [
            "arquiteto sao jose dos campos", "arquiteto taubate",
            "design de interiores sjc", "design de interiores vale do paraiba",
            "escritorio de arquitetura sao jose dos campos",
            "arquiteto campos do jordao", "arquiteto santo antonio do pinhal",
            "arquiteto pindamonhangaba", "designer de interiores jacarei",
            "arquitetura de interiores vale do paraiba",
        ],
    },
}
