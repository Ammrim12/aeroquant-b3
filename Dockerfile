# =============================================================================
# AeroQuant B3 — Dockerfile Ultra-Rápido para Render.com Free Tier (~20s de build)
# Não executa Node.js/Bun/Vite no Render (evita o travamento de CPU/lscpu e erro 143).
# Usa o bundle pré-compilado 'frontend_dist.tar.gz' + servidor Python unificado.
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Extrai o frontend já compilado localmente para .web/build/client em < 1 segundo
RUN mkdir -p /app/.web/build/client /app/data \
    && tar -xzf /app/frontend_dist.tar.gz -C /app/.web/build/client \
    && chmod -R 777 /app

ENV PORT=10000
ENV REFLEX_ENV_MODE=prod
EXPOSE 10000

# Inicia o servidor Python unificado (Frontend estático + WebSockets B3 na mesma porta)
CMD ["python", "-c", "import os; from reflex.config import get_config, environment; from reflex.constants import Env; from reflex.reflex import _skip_compile; from reflex.utils import exec; port = int(os.environ.get('PORT', '10000')); cfg = get_config(); environment.REFLEX_ENV_MODE.set(Env.PROD); _skip_compile(); exec.run_backend_prod('0.0.0.0', port, cfg.loglevel.subprocess_level(), True)"]
