"""Configuracoes globais. Chaves vem de variaveis de ambiente (GitHub Secrets).
Localmente, defina no shell ou crie um arquivo .env (que NAO vai pro git)."""
import os

# Carrega .env se existir (uso local). No GitHub Actions vem dos secrets.
def _carrega_env_local():
    caminho = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    chave, _, valor = linha.partition("=")
                    os.environ.setdefault(chave.strip(), valor.strip())

_carrega_env_local()

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "")

# Actor antigo (cota promocional de 15 execucoes gratis/mes, estourada em jul/2026).
# Mantido comentado so como referencia historica.
# APIFY_ACTOR = "afanasenko~instagram-profile-scraper"

# Actors oficiais da Apify (sem cota promocional, cobranca normal ~US$0,0027/perfil)
APIFY_ACTOR_SEARCH = "apify~instagram-search-scraper"
APIFY_ACTOR_PROFILE = "apify~instagram-profile-scraper"

# Provedor de IA para qualificacao. "cerebras" tem teto de 1 milhao de tokens/dia
# (10x o Groq); "groq" fica de reserva. Troca aqui em uma linha. Mesmo modelo
# (Llama 3.3 70B) nos dois, so muda o provedor, entao a qualidade nao muda.
PROVIDER = "cerebras"
CEREBRAS_MODEL = "gpt-oss-120b"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Filtros de prospeccao (decididos com o Stefano)
MIN_SEGUIDORES = 1000
MAX_SEGUIDORES = 25000         # teto ampliado p/ recuperar volume no Vale
LOCALIZACAO = "Taubaté, São José dos Campos, Tremembé, Pindamonhangaba, Vale do Paraíba"
NOTA_CORTE = 7                  # leads com nota >= entram no painel

# Quantos candidatos buscar por nicho por rodada (teto do plano free = 5)
MAX_POR_NICHO = 5

# --- Motores de descoberta (controle de custo da Apify) ---
# Expansao de rede (relatedProfiles das ancoras) e cara e rende pouco: analisa
# dezenas de perfis por rodada e o Instagram sugere contas famosas de fora da
# regiao, quase tudo cortado pelo filtro. Desligada por padrao. Reativa com True.
USAR_EXPANSAO_REDE = False

# Geo generica (busca so por nome de cidade) traz muito lixo de outro ramo
# (loja de celular, salao). As queries de nicho ja embutem a cidade e sao mais
# direcionadas, entao a geo generica fica desligada por padrao.
USAR_GEO_GENERICA = False

# Resultados por query na busca por keyword. O custo da rodada e proporcional a
# (numero de queries dos nichos) x SEARCH_LIMIT x US$0,0027 por perfil. Menor =
# mais barato, cobre menos. Ajustar junto com a frequencia do cron para caber no
# teto de US$5/mes do plano free da Apify.
SEARCH_LIMIT = 5

# Profundidade da busca: quantas paginas por hashtag/query. Mais paginas = mais
# autores distintos alem dos top posts, evita o poco secar pelo dedup. Nao
# aumenta custo (cobranca e por perfil analisado, limitada por MAX_POR_NICHO).
PAGINAS_BUSCA = 10

# Filtro de relevancia: a expansao de rede as vezes traz conta de outro ramo
# (piscina, biscoitaria). So vira lead quem tem sinal de saude/estetica/arquitetura
# na bio, nome ou posts. Corta o joio antes de gastar qualificacao.
RELEVANCIA_TOKENS = [
    "medic", "médic", "dra", "dr.", "clinic", "clínic", "consultorio", "consultório",
    "saude", "saúde", "estetic", "estétic", "dermat", "gineco", "nutri", "nutrolog",
    "endocrin", "cirurg", "harmoniz", "botox", "preench", "odonto", "fisio",
    "biomedic", "spa", "longevidade", "emagrec", "crm", "crn", "crefito", "rqe",
    "arquitet", "interiores", "design de interior", "paisagis", "marcenaria",
]

# Trava geografica: so qualifica quem cita a regiao na bio ou nos posts.
# O modo hashtag e cego para localizacao, entao filtramos por estes termos.
REGIAO_TOKENS = [
    "taubate", "taubaté", "sao jose dos campos", "são josé dos campos", "sjc",
    "tremembe", "tremembé", "pindamonhangaba", "pinda",
    "santo antonio do pinhal", "santo antônio do pinhal",
    "campos do jordao", "campos do jordão", "campos de jordao", "campos de jordão",
    "jacarei", "jacareí", "cacapava", "caçapava",
    "vale do paraiba", "vale do paraíba", "redencao da serra",
    "ubatuba", "caraguatatuba", "guaratingueta", "guaratinguetá", "lorena",
]
