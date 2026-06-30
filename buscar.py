"""Camada 1 — Descoberta. Chama o actor da Apify por nicho, com filtros e
lista de exclusao (dedup), e devolve os perfis brutos enriquecidos."""
import requests
import config

API = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"


def buscar_nicho(nome, nicho, ja_vistos):
    """Roda o actor para um nicho. ja_vistos = lista de @ que nao devem repetir."""
    url = API.format(actor=config.APIFY_ACTOR)
    payload = {
        "operationMode": "keywordDiscovery",
        "searchHashtags": nicho["hashtags"],
        "searchQueries": nicho["queries"],
        "maxSearchPagesPerQuery": config.PAGINAS_BUSCA,
        "maxCountDiscovery": config.MAX_POR_NICHO,
        "minFollowers": config.MIN_SEGUIDORES,
        "maxFollowers": config.MAX_SEGUIDORES,
        # Sem locationKeywords (filtro duro de endereco estruturado e raro nos perfis).
        # A regiao mora na bio; a checagem geografica fica na IA (qualificar.py).
        "analyzeQuality": True,
        "extractEmail": True,
        "extractPhoneNumber": True,
        "extractWebsiteUrl": True,
        "extractBusinessCategory": True,
        "extractPosts": True,
        "excludeAccounts": ja_vistos,   # nao reanalisa nem cobra quem ja vimos
    }
    resp = requests.post(
        url,
        params={"token": config.APIFY_TOKEN, "timeout": 240, "memory": 512},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    itens = resp.json()
    print(f"  [{nome}] {len(itens)} perfis retornados")
    return itens


def buscar_localizacao(ja_vistos):
    """Segunda rede: perfis da regiao por geolocalizacao (independe de hashtag).
    No plano free traz ate 5 perfis aleatorios da regiao por rodada."""
    url = API.format(actor=config.APIFY_ACTOR)
    payload = {
        "operationMode": "locationDiscovery",
        "locationSeeds": ["São José dos Campos, Brazil", "Taubaté, Brazil"],
        "maxCountLocation": config.MAX_POR_NICHO,
        "minFollowers": config.MIN_SEGUIDORES,
        "maxFollowers": config.MAX_SEGUIDORES,
        "accountType": "business",
        "analyzeQuality": True,
        "extractEmail": True,
        "extractPhoneNumber": True,
        "extractWebsiteUrl": True,
        "extractBusinessCategory": True,
        "extractPosts": True,
        "excludeAccounts": ja_vistos,
    }
    resp = requests.post(
        url,
        params={"token": config.APIFY_TOKEN, "timeout": 240, "memory": 512},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    itens = resp.json()
    print(f"  [geolocalizacao] {len(itens)} perfis retornados")
    return itens


def handle_de(item):
    """Extrai o @ a partir do campo Account (URL do perfil)."""
    conta = item.get("Account", "") or ""
    return conta.rstrip("/").split("/")[-1].lower()


def e_da_regiao(item):
    """True se a bio ou os posts citam algum termo da regiao de Taubate."""
    texto = (item.get("Biography", "") or "")
    for i in range(1, 9):
        texto += " " + str(item.get(f"Post {i}", "") or "")
    texto = texto.lower()
    return any(tok in texto for tok in config.REGIAO_TOKENS)
