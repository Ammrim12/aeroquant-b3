# 🌿 AeroQuant — Terminal B3 & Mercado Brasileiro

Dashboard financeiro em **Python + [Reflex](https://reflex.dev)**, inspirado no design system editorial **Coffra** (*Sage / Cream / Forest*, com alternância instantânea entre **Modo Claro** e **Modo Escuro**), 100% em **português** e conectado ao mercado brasileiro em tempo real.

## ✨ Destaques

1. **100% em Português (pt-BR)** — saudações dinâmicas, datas por extenso, setores e subsetores traduzidos, formatação numérica (`R$ 1.234,56`, `mi` / `bi` / `tri`) e central de notícias econômicas brasileiras.
2. **Cobertura Completa da B3 (~1.626 Ativos em 4 Classes + 20 Segmentos)**:
   - **Ações de Empresas (~385)**: Bancos, Petróleo & Gás, Energia Elétrica, Mineração & Siderurgia, Fábricas & Indústria, Lojas & Varejo, Alimentos & Bebidas, Construção Civil, Saúde, Tecnologia, Telecom, Logística, Educação, Agro e Papel & Celulose.
   - **Fundos Imobiliários — FIIs (~354)**: `HGLG11`, `KNCR11`, `MXRF11`, `XPML11`, Fiagros e Fi-Infra.
   - **ETFs & Índices (~232)**: `BOVA11`, `IVVB11`, `SMAL11`, `HASH11`, `DIVO11`...
   - **BDRs Globais (~655)**: `AAPL34`, `NVDC34`, `MSFT34`, `AMZO34`, `MELI34`...
3. **Mapa de Calor da B3 (Heatmap Matrix)** — matriz cromática em tempo real (verde sálvia a terracota) na Visão Geral e como 3º modo de exibição no diretório `/empresas`.
4. **Command Palette / Busca Rápida Global** — modal instantâneo acionado pela barra superior ou pelo ícone de lupa lateral para pesquisar qualquer um dos ~1.626 ativos da B3 e abrir seu Raio-X ou adicioná-lo à carteira com 1 clique.
5. **Minha Carteira Avançada (`/carteira`)**:
   - **Cartões Visuais de Estratégia (Cofres)**: *Renda & Dividendos*, *Valor & Crescimento* e *Caixa Tático & Proteção*.
   - **Comparador Carteira vs. Ibovespa vs. CDI (90 dias)** em rentabilidade percentual acumulada + cálculo automático de *Alpha*.
   - **Persistência em Disco (`data/portfolio.json`) + Exportação CSV (`;`, UTF-8 BOM para Excel)**.
6. **Agenda do Mercado & Dividendos B3 (`/calendario`)** — cronograma filtrável de *Data-Com de Dividendos/JCP*, *Temporada de Balanços 3T*, *Reuniões do Copom/IPCA* e *Rendimentos de FIIs*.
7. **Indicador Técnico `MM20` (Média Móvel de 20 pregões)** — linha pontilhada de tendência tanto no gráfico principal quanto no painel lateral (`rx.drawer`) de cada empresa.
8. **Qualidade de Software (Pytest + GitHub Actions CI)** — suíte automatizada em `tests/test_aeroquant.py` validando formatação pt-BR, catálogo B3, cálculos de P&L, persistência e compilação completa do Reflex.

## 🗂️ Estrutura do Projeto

```
AeroQuant/
├── .github/workflows/ci.yml     # Pipeline CI (Pytest + Compilação Reflex)
├── rxconfig.py                  # Configuração do Reflex + RadixThemesPlugin (jade / sage)
├── requirements.txt
├── assets/
│   └── aeroquant.css            # Variáveis CSS (Modo Claro & Escuro Coffra) e animações
├── data/
│   └── portfolio.json           # Persistência automática das posições da carteira
├── tests/
│   └── test_aeroquant.py        # Suíte de testes automatizados (pytest)
└── aeroquant/
    ├── aeroquant.py             # Registro das 5 rotas (/, /empresas, /carteira, /calendario, /noticias)
    ├── state.py                 # Estado reativo global, filtros, Command Palette, drawer e carteira
    ├── services/
    │   ├── formatting.py        # Formatação numérica pt-BR, datas e status do pregão B3
    │   └── market_data.py       # Catálogo completo B3 (brapi.dev), histórico + MM20 (yfinance), benchmark CDI/IBOV e RSS pt-BR
    ├── components/
    │   ├── styles.py            # Tokens visuais Coffra (cards, pílulas, tons pastéis)
    │   ├── sidebar.py           # Rail vertical de ícones (5 páginas + busca global + auto-refresh)
    │   ├── header.py            # Breadcrumb, Command Palette trigger, timer 60s, tema Lua/Sol e alertas
    │   ├── chart.py             # Card 'Fluxo e Desempenho do Mercado' (barras + linha / área + MM20)
    │   ├── kpi_cards.py         # Card 'Raio-X Setorial', 'Mapa de Calor da B3' + 4 cards pastéis
    │   ├── table.py             # Destaques do pregão + giro de notícias na Visão Geral
    │   ├── companies.py         # Explorador (~1.626 ativos: Ações, FIIs, ETFs, BDRs em Grade/Tabela/Mapa de Calor)
    │   ├── portfolio.py         # Cofres de estratégia, comparador vs. Ibovespa/CDI, posições, CSV e rosca
    │   ├── calendar.py          # Agenda corporativa de Dividendos, JCP, Balanços e Copom
    │   ├── news.py              # Feed estilo Inbox com manchetes brasileiras por editoria
    │   ├── drawer.py            # Slide-over de ficha da empresa + Modal 'Simular Aporte' + Modal 'Busca Global'
    │   └── layout.py            # Layout base compartilhado
    └── pages/
        ├── market.py            # /           — Visão Geral
        ├── companies.py         # /empresas   — Diretório Completo de Empresas & Ativos da B3
        ├── portfolio.py         # /carteira   — Minha Carteira
        ├── calendar.py          # /calendario — Agenda do Mercado & Dividendos B3
        └── news.py              # /noticias   — Central de Notícias (Brasil)
```

## 🚀 Como Executar e Testar

```powershell
.\.venv\Scripts\activate
pytest -v
reflex run --env prod --single-port
```
*(Em máquinas Windows sem Node.js instalado globalmente, utilize `--env prod --single-port` para servir Frontend + WebSockets na mesma porta).*

---

## 🌐 Opções de Deploy 100% Gratuito (Sem Cartão de Crédito)

### Opção 1 — Link Público HTTPS Instantâneo (Direto do seu PC via Cloudflare Tunnel)
Dê dois cliques em [`publicar_link_gratuito.bat`](file:///c:/Users/acacio.faria/Documents/AeroQuant/publicar_link_gratuito.bat) ou execute no terminal:
```powershell
.\.venv\Scripts\reflex.exe run --env prod --single-port --frontend-port 3000
.\.venv\Scripts\cloudflared.exe tunnel --url http://localhost:3000
```
Isso gera em segundos um link `https://....trycloudflare.com` com certificado SSL válido, acessível de qualquer celular (4G/5G) ou computador externo.

### Opção 2 — Hospedagem 24/7 na Nuvem 100% Gratuita (Hugging Face Spaces — Docker)
O projeto já inclui o [`Dockerfile`](file:///c:/Users/acacio.faria/Documents/AeroQuant/Dockerfile) pré-configurado na porta `7860` (`--single-port`):
1. Crie uma conta gratuita em [huggingface.co/spaces](https://huggingface.co/spaces) (não pede cartão de crédito e oferece **2 vCPUs + 16 GB de RAM gratuitos**).
2. Clique em **New Space** -> escolha o SDK **Docker** (Blank) -> **Create Space**.
3. Envie os arquivos deste diretório (excluindo `.venv` e `.web`) pelo próprio navegador (*Files -> Add file -> Upload files*) ou via Git.
4. O container será construído automaticamente e seu dashboard ficará online 24/7 em `https://huggingface.co/spaces/<seu-usuario>/aeroquant-b3`.

### Opção 3 — Render.com (Free Web Service via GitHub)
O arquivo [`render.yaml`](file:///c:/Users/acacio.faria/Documents/AeroQuant/render.yaml) já está configurado com `plan: free` e `runtime: docker`. Basta subir este projeto para um repositório no GitHub e conectá-lo em *New -> Web Service* no [render.com](https://render.com).
