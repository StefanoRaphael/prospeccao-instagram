"""Camada 1 — Descoberta. Chama os actors oficiais da Apify (instagram-search-scraper
e instagram-profile-scraper), com filtros e lista de exclusao (dedup), e devolve os
perfis brutos adaptados para o formato de item esperado por qualificar.py/painel.py."""
import re
import statistics

import requests
import config

API = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _chama_actor(actor, payload):
    """POST generico de run-sync-get-dataset-items, mesmo padrao ja usado no projeto."""
    url = API.format(actor=actor)
    resp = requests.post(
        url,
        params={"token": config.APIFY_TOKEN, "timeout": 240, "memory": 512},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()


def _adapta_item(perfil):
    """Traduz um perfil do instagram-search-scraper (ou profile-scraper, mesmo schema
    de campos) para o formato antigo de item (Account, Followers Count, Median ER, ...)."""
    username = perfil.get("username", "") or ""
    posts = perfil.get("latestPosts") or []
    seguidores = perfil.get("followersCount") or 0

    ers = []
    likes, comments = [], []
    for p in posts:
        l = p.get("likesCount") or 0
        c = p.get("commentsCount") or 0
        likes.append(l)
        comments.append(c)
        if seguidores:
            ers.append((l + c) / seguidores)

    median_er = f"{statistics.median(ers) * 100:.2f}%" if ers else "0.00%"
    avg_likes = round(sum(likes) / len(likes)) if likes else 0
    avg_comments = round(sum(comments) / len(comments)) if comments else 0

    bio = perfil.get("biography", "") or ""
    email_match = EMAIL_RE.search(bio)

    item = {
        "Account": f"https://instagram.com/{username}",
        "Full Name": perfil.get("fullName", ""),
        "Followers Count": seguidores,
        "Following Count": perfil.get("followsCount") or 0,
        "Biography": bio,
        "Category": perfil.get("businessCategoryName", ""),
        "External URL": perfil.get("externalUrl", ""),
        "Median ER": median_er,
        "Avg Likes": avg_likes,
        "Avg Comments": avg_comments,
        "Quality": "N/A",
        "Email": email_match.group(0) if email_match else "N/A",
        "Phone": "N/A",
    }
    for i, p in enumerate(posts, start=1):
        item[f"Post {i}"] = p.get("caption", "") or ""
    return item


def _dentro_do_filtro(item):
    """Aplica MIN_SEGUIDORES/MAX_SEGUIDORES apos receber os dados (o actor novo
    nao filtra por seguidores nativamente)."""
    seg = item.get("Followers Count") or 0
    return config.MIN_SEGUIDORES <= seg <= config.MAX_SEGUIDORES


def buscar_por_keyword(nome, queries, ja_vistos):
    """Roda instagram-search-scraper (searchType=user) para cada query do nicho,
    agrega, dedup e filtra por seguidores."""
    encontrados = {}
    for query in queries:
        payload = {"search": query, "searchType": "user", "searchLimit": 10}
        try:
            perfis = _chama_actor(config.APIFY_ACTOR_SEARCH, payload)
        except requests.HTTPError as e:
            print(f"  [{nome}] erro na query '{query}': {e}")
            continue
        for perfil in perfis:
            username = (perfil.get("username", "") or "").lower()
            if not username or username in ja_vistos or username in encontrados:
                continue
            item = _adapta_item(perfil)
            if _dentro_do_filtro(item):
                encontrados[username] = item
    itens = list(encontrados.values())
    print(f"  [{nome}] {len(itens)} perfis retornados")
    return itens


def buscar_similar(nome, ancoras, ja_vistos):
    """Expansao de rede: usa relatedProfiles das ancoras (via instagram-profile-scraper)
    como lista de candidatos, depois enriquece cada candidato com uma segunda chamada
    ao mesmo actor (relatedProfiles nao vem com bio/seguidores).
    Atencao: relatedProfiles e ruidoso (mistura contas do nicho com lojas locais,
    saloes de beleza etc. sem relacao) — o filtro e_relevante/e_da_regiao corta isso depois."""
    if not ancoras:
        return []

    try:
        perfis_ancora = _chama_actor(config.APIFY_ACTOR_PROFILE, {"usernames": ancoras})
    except requests.HTTPError as e:
        print(f"  [{nome} similares] erro ao buscar ancoras: {e}")
        return []

    candidatos = []
    for perfil in perfis_ancora:
        for rel in perfil.get("relatedProfiles") or []:
            username = (rel.get("username", "") or "").lower()
            if username and username not in ja_vistos and username not in candidatos:
                candidatos.append(username)
    candidatos = candidatos[:30]  # teto para nao estourar custo

    if not candidatos:
        print(f"  [{nome} similares] 0 perfis retornados (relatedProfiles vazio)")
        return []

    try:
        perfis_candidatos = _chama_actor(config.APIFY_ACTOR_PROFILE, {"usernames": candidatos})
    except requests.HTTPError as e:
        print(f"  [{nome} similares] erro ao enriquecer candidatos: {e}")
        return []

    itens = []
    for perfil in perfis_candidatos:
        username = (perfil.get("username", "") or "").lower()
        if not username or username in ja_vistos:
            continue
        item = _adapta_item(perfil)
        if _dentro_do_filtro(item):
            itens.append(item)
    print(f"  [{nome} similares] {len(itens)} perfis retornados")
    return itens


def buscar_localizacao(ja_vistos):
    """Segunda rede: o instagram-search-scraper nao tem modo de geolocalizacao
    estruturado equivalente ao actor antigo (locationDiscovery). Aproximamos
    reaproveitando buscar_por_keyword com queries genericas de cidade da regiao."""
    queries_cidade = [
        "Taubaté", "São José dos Campos", "Tremembé", "Pindamonhangaba",
        "Vale do Paraíba", "Jacareí", "Caçapava", "Campos do Jordão",
    ]
    return buscar_por_keyword("geolocalizacao", queries_cidade, ja_vistos)


def handle_de(item):
    """Extrai o @ a partir do campo Account (URL do perfil)."""
    conta = item.get("Account", "") or ""
    return conta.rstrip("/").split("/")[-1].lower()


def e_relevante(item):
    """True se o perfil tem sinal de saude/estetica/arquitetura (corta piscina,
    biscoitaria e outros ramos que a expansao de rede traz por engano)."""
    texto = (item.get("Biography", "") or "") + " " + (item.get("Full Name", "") or "")
    for i in range(1, 4):
        texto += " " + str(item.get(f"Post {i}", "") or "")
    texto = texto.lower()
    return any(tok in texto for tok in config.RELEVANCIA_TOKENS)


def e_da_regiao(item):
    """True se a bio ou os posts citam algum termo da regiao de Taubate."""
    texto = (item.get("Biography", "") or "")
    for i in range(1, 9):
        texto += " " + str(item.get(f"Post {i}", "") or "")
    texto = texto.lower()
    return any(tok in texto for tok in config.REGIAO_TOKENS)
