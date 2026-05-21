<div align="center">

# 🔬 DEAM-PP — Avaliação de Impacto das Delegacias Especializadas de Atendimento à Mulher

**Violência contra Mulheres no Município de São Paulo:**
*Diagnóstico Espaço-Temporal e Avaliação de Impacto das DDMs*

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Basedosdados](https://img.shields.io/badge/Base_dos_Dados-BigQuery-150458?style=for-the-badge)]()

---

*Projeto de pesquisa focado na gestão de políticas públicas no município de São Paulo.*

</div>

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Problema de Pesquisa](#-problema-de-pesquisa)
- [Cadeia Causal](#-cadeia-causal)
- [Metodologia](#-metodologia)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Dados](#-dados)
- [Como Extrair os Dados](#-como-extrair-os-dados)
- [Roadmap](#-roadmap)

---

## 🎯 Sobre o Projeto

Este repositório contém o código-fonte, dados e relatórios do projeto de pesquisa que investiga a **eficácia das Delegacias de Defesa da Mulher (DDMs) com funcionamento 24 horas no município de São Paulo**.

O estudo combina **ciência de dados descritiva** (mapas de calor territoriais e funil da violência) com **avaliação de impacto causal** (Diferenças-em-Diferenças intra-municipal), produzindo evidências acionáveis para subsidiar a gestão de políticas públicas e otimizar a rede de proteção à mulher na capital paulista.

---

## 🔍 Problema de Pesquisa

A violência contra mulheres exige respostas capilarizadas e com disponibilidade ininterrupta, visto que grande parte das agressões em contexto doméstico ocorre durante madrugadas e finais de semana — períodos nos quais DDMs de horário comercial encontram-se fechadas.

O projeto busca responder à seguinte questão principal:
> **As DDMs que funcionam 24 hrs na cidade de São Paulo possuem maior impacto na ampliação de registros (redução da subnotificação) e na prevenção de feminicídios em seus distritos de abrangência, em comparação àquelas que funcionam apenas em horário comercial?**

---

## 🔗 Cadeia Causal

O projeto resolve o paradoxo econométrico da **causalidade reversa de registro**. Avaliar o sucesso de uma delegacia apenas pelo volume de denúncias é falho, pois a delegacia estimula o relato de crimes que já existiam (cifra oculta). 

Para contornar isso, o modelo possui duas variáveis dependentes:

```mermaid
flowchart LR
    A["🏛️ Inauguração/Conversão\nDDM 24h"] --> B["📈 Aumento de Acesso\n(Denúncias/SINAN)"]
    B --> C["🛡️ Proteção Ativa"]
    C --> D["📉 Redução de Letalidade\n(Feminicídios/SIM)"]

    style A fill:#4a90d9,color:#fff,stroke:#2c5f8a
    style B fill:#f5a623,color:#fff,stroke:#c48418
    style C fill:#7b68ee,color:#fff,stroke:#5b48ce
    style D fill:#50c878,color:#fff,stroke:#3a9a5a
```

> [!NOTE]
> Um coeficiente positivo na variável de denúncias (Ameaça/Lesão) indica **sucesso no acesso institucional**, e um coeficiente negativo na variável de óbitos indica **sucesso na eficácia protetiva da vida**.

---

## 📐 Metodologia

### Etapa 1 — Diagnóstico e Ciência de Dados
- **Análise Descritiva Espacial:** Mapas de densidade (Heatmaps) por Distrito Policial, Bairro e Subprefeitura.
- **Integração de Bases e Geolocalização (SINAN + CNES):** Como a base do SINAN omite endereços exatos para preservação da privacidade das vítimas, adotamos a **Hipótese de Proxy Espacial (Bairro de Atendimento)**. O SINAN é cruzado com o diretório geocodificado do CNES através da chave do estabelecimento notificador (`id_unidade_notificacao` = `id_estabelecimento_cnes`). Assume-se que a vítima de agressão grave busca socorro imediato no próprio bairro ou em bairros vizinhos. Desse modo, o bairro do estabelecimento de saúde serve como proxy geográfico do local da agressão.
- **Funil da Violência:** Evolução e correlação temporal entre denúncias de Ameaça (SSP), Lesão Corporal (SSP), Violência Física Notificada Grave (SINAN) e Feminicídios (SIM) na capital.
- **Sazonalidade:** Gráficos temporais cruzando horários e dias da semana.

### Etapa 2 — Avaliação de Impacto Causal
- **Método:** Diferenças-em-Diferenças (DiD) em nível intra-municipal.
- **Controle:** Bairros/Distritos paulistanos atendidos por DDMs em horário comercial (ou sem especializada) vs. DDMs 24h.
- **Pareamento:** Propensity Score Matching via indicadores socioeconômicos da Fundação SEADE.

### Produto Final
- 📊 Relatório técnico para tomada de decisão (Word).
- 🖥️ Dashboard interativo (Streamlit) com o mapa da capital e simulador de impactos.

---

## 📁 Estrutura do Repositório

```text
deams-pp-aps/
│
├── 📄 README.md                    # Este arquivo
├── 📄 pyproject.toml               # Dependências e metadados do projeto
│
├── 📂 codes/                       # Scripts organizados por fases de desenvolvimento
│   ├── 📂 extracao_filtragem/      # Extração (APIs/BigQuery) e higienização inicial
│   │   ├── bd_config.py            # ⚠️ LOCAL APENAS — credenciais GCP (Não versionado)
│   │   ├── extract_cnes_bd.py      # Query de estabelecimentos geolocalizados do CNES
│   │   ├── extract_sim_bd.py       # Query de feminicídios notificados no SIM/DataSUS
│   │   ├── extract_sinan_bd.py     # Query de notificações de agressões no SINAN/DataSUS
│   │   ├── merge_sinan_cnes.py     # Cruzamento SINAN + CNES usando a chave do hospital
│   │   ├── data_filter_sicpv.py    # Filtro da base SIPCV (Boletins de Ocorrência SSP-SP)
│   │   └── pipeline_feminicidio.py # Filtro e pré-processamento de feminicídios da SSP-SP
│   │
│   ├── 📂 analise_dados/           # Análise exploratória e visualizações
│   │   └── eda_funil_violencia.py  # Análise do Funil da Violência e geração de gráficos
│   │
│   ├── 📂 streamlit/               # Dashboard Interativo (Fase Futura)
│   │   └── .gitkeep
│   │
│   └── 📂 inferencia_causal/       # Estimação do modelo econométrico DiD (Fase Futura)
│       └── .gitkeep
│
├── 📂 dados/                       # Armazenamento estruturado de fontes e consolidações
│   ├── 📂 ssp/                     # Dados provenientes da Secretaria de Segurança Pública
│   │   ├── SIPCV_2026.xlsx         # Boletins de Ocorrência SSP (Bruto)
│   │   ├── data_sipcv.csv          # Boletins de Ocorrência SSP (Filtrado)
│   │   ├── Feminicidio_2015_2022.xlsx # Feminicídios SSP (Bruto)
│   │   └── dados_feminicidio.xlsx  # Feminicídios SSP (Filtrado)
│   │
│   ├── 📂 sim/                     # Dados provenientes do SIM (Sistema de Mortalidade)
│   │   └── sim_feminicidios_sp.csv # Óbitos por agressão contra mulheres (DataSUS)
│   │
│   ├── 📂 sinan/                   # Dados provenientes do SINAN (Notificações)
│   │   ├── sinan_violencia_sp.csv  # Microdados de agressões físicas (DataSUS)
│   │   └── sinan_cnes_merged.csv   # Base integrada espacialmente ao CNES
│   │
│   ├── 📂 cnes/                    # Cadastro Nacional de Estabelecimentos de Saúde
│   │   └── cnes_sp_geolocalizado.csv # Dicionário de geolocalização das unidades de saúde
│   │
│   └── 📂 consolidado/             # Bases prontas agregadas para visualização/modelagem
│       └── funil_violencia_ano.csv # Tabela agregada anual do Funil da Violência
│
└── 📂 relatorios/                  # Relatórios gerenciais e imagens geradas
    ├── PROJETO DE PESQUISA-VIOLENCIA SP.docx
    ├── PROJETO DE PESQUISA-VIOLENCIA SP.txt
    └── funil_violencia.png         # Gráfico temporal de evolução do funil
```

---

## 📊 Dados

Os microdados são obtidos diretamente via integração com o data lake público da **Base dos Dados (BigQuery)**, evitando downloads massivos de repositórios legados do DataSUS.

| Base | Fonte Original | Papel no Modelo | Filtros Aplicados |
|------|----------------|-----------------|-------------------|
| **SIM** | DataSUS | Eficácia (Feminicídios) | SP (3550308), Mulheres, CIDs Agressão (X85-Y09) |
| **SINAN** | DataSUS | Acesso (Ameaça/Lesão) | SP (3550308), Mulheres, com **Código CNES (Proxy Geográfico)** |
| **SEADE** | Gov. SP | Covariáveis (Controles) | Dados agregados por distrito (vulnerabilidade, renda) |

---

## 🚀 Como Extrair os Dados

Os scripts em Python dentro da pasta `codes/extracao_filtragem/` já possuem as *queries* SQL otimizadas para processar os dados em nuvem antes de baixar, trazendo apenas o escopo geográfico e de perfil do nosso estudo.

### Pré-requisitos

1. Ter Python 3.10+ instalado com Pandas, `basedosdados` e bibliotecas de excel:
   ```bash
   pip install pandas basedosdados openpyxl xlrd
   ```
2. Ter um projeto no **Google Cloud Platform (GCP)**.
3. Estar autenticado no GCP no seu terminal local:
   ```bash
   gcloud auth application-default login
   ```

### Extração e Processamento

1. Entre na pasta dos scripts de extração.
2. Crie o arquivo `codes/extracao_filtragem/bd_config.py` localmente com o seguinte conteúdo:
   ```python
   BILLING_ID = "seu-projeto-id-aqui"
   ```
   > **Atenção:** este arquivo está no `.gitignore` e não é enviado ao GitHub.
3. Execute no terminal a partir da raiz do repositório:
   ```bash
   python codes/extracao_filtragem/extract_cnes_bd.py
   python codes/extracao_filtragem/extract_sim_bd.py
   python codes/extracao_filtragem/extract_sinan_bd.py
   python codes/extracao_filtragem/merge_sinan_cnes.py
   ```
4. Os arquivos processados e consolidados aparecerão automaticamente organizados nas respectivas subpastas da pasta `dados/`.

---

## 🗺️ Roadmap

- [x] Reestruturação do escopo do projeto (Foco em São Paulo e DiD Intra-municipal)
- [x] Criação das *queries* otimizadas para extração SIM/SINAN via Base dos Dados
- [x] Extração dos microdados SIM (7.554 registros) e SINAN (108.427 registros)
- [x] Pré-processamento das bases SSP-SP (SIPCV e Feminicídio 2015-2022)
- [x] Construção do Funil da Violência e EDA Espaço-Temporal
- [ ] Estimação do modelo DiD
- [ ] Construção do Dashboard Interativo (Streamlit)