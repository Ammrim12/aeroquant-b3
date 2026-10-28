# =============================================================================
# AeroQuant B3 — Dockerfile Otimizado para Render.com Free Tier (512 MB RAM)
# Compila o frontend durante o 'docker build' e roda em modo leve no runtime
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema para o build do Reflex (curl + unzip + Node.js 20)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garante permissão na pasta de persistência (carteira e favoritos)
RUN mkdir -p /app/data && chmod -R 777 /app

# Pré-compila o frontend (.web/build/client) durante o build da imagem (economiza RAM no runtime Free Tier)
ENV REFLEX_ENV_MODE=prod
RUN python -c "from pathlib import Path; from reflex.reflex import _init, _compile_app; from reflex.config import get_config; from reflex.utils import build, prerequisites; cfg = get_config(); cfg._set_persistent(frontend_port=10000, backend_port=10000); _init(name=cfg.app_name) if prerequisites.needs_reinit() else None; _compile_app(avoid_dirty_check=True); build.setup_frontend_prod(Path.cwd())"

ENV PORT=10000
EXPOSE 10000

# No runtime do Render Free Tier, sobe apenas o servidor Python unificado servindo o frontend já compilado + WebSockets
CMD ["python", "-c", "import os; from reflex.config import get_config, environment; from reflex.constants import Env; from reflex.reflex import _skip_compile; from reflex.utils import exec; port = int(os.environ.get('PORT', '10000')); cfg = get_config(); environment.REFLEX_ENV_MODE.set(Env.PROD); _skip_compile(); exec.run_backend_prod('0.0.0.0', port, cfg.loglevel.subprocess_level(), True)"]
