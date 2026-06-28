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

# Actor de descoberta + enriquecimento de perfis do Instagram
APIFY_ACTOR = "afanasenko~instagram-profile-scraper"

# Modelo Groq usado na qualificacao
GROQ_MODEL = "llama-3.3-70b-versatile"

# Filtros de prospeccao (decididos com o Stefano)
MIN_SEGUIDORES = 1000
MAX_SEGUIDORES = 8000          # acima disso: ego de seguidor inflado, descarta
LOCALIZACAO = "Taubaté, São José dos Campos, Tremembé, Pindamonhangaba, Vale do Paraíba"
NOTA_CORTE = 7                  # leads com nota >= entram no painel

# Quantos candidatos buscar por nicho por rodada (teto do plano free = 5)
MAX_POR_NICHO = 5

# Trava geografica: so qualifica quem cita a regiao na bio ou nos posts.
# O modo hashtag e cego para localizacao, entao filtramos por estes termos.
REGIAO_TOKENS = [
    "taubate", "taubaté", "sao jose dos campos", "são josé dos campos", "sjc",
    "tremembe", "tremembé", "pindamonhangaba", "pinda", "jacarei", "jacareí",
    "cacapava", "caçapava", "vale do paraiba", "vale do paraíba", "redencao da serra",
    "ubatuba", "caraguatatuba", "tatui", "guaratingueta", "guaratinguetá", "lorena",
]
