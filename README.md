# AeroTracker Core

> Plataforma modular de monitoramento aeroespacial em tempo real.

---

## 🚀 Sobre o Projeto

O **AeroTracker Core** é uma plataforma profissional de monitoramento aeroespacial desenvolvida em Python, capaz de rodar em múltiplos ambientes:

- 💻 Desktop (Windows, Linux, macOS)
- 🔌 ESP32-S3
- 🍓 Raspberry Pi

### Funcionalidades planejadas

- Radar de aeronaves em tempo real (OpenSky, ADS-B Exchange)
- Rastreamento da ISS
- Lançamentos espaciais (SpaceX, NASA, Launch Library 2)
- Clima em tempo real (OpenWeather, Open-Meteo)
- Fases da Lua e Sistema Solar
- Globo terrestre 3D
- Painel configurável estilo centro de monitoramento
- Temas claro e escuro
- Atualizações OTA para ESP32

---

## 📁 Estrutura do Projeto

```
AeroTracker/
├── config/          # Configurações globais (Settings, TOML)
├── core/            # Núcleo: bootstrap, event bus, module manager
├── api/             # Adapters para APIs externas
│   ├── aircraft/    # OpenSky, ADS-B Exchange, FlightAware, FR24
│   ├── weather/     # OpenWeather, Open-Meteo
│   └── space/       # NASA, SpaceX, ISS, Launch Library, N2YO
├── models/          # Entidades de domínio (Pydantic v2)
├── services/        # Lógica de negócio
├── display/         # Camada de apresentação
│   └── desktop/     # Renderer para Desktop (CustomTkinter)
├── scheduler/       # Agendador de tarefas (APScheduler)
├── cache/           # Cache inteligente com TTL por módulo
├── storage/         # Persistência local
├── utils/           # Utilitários: logger, geo, astronomia, formatadores
├── assets/          # Ícones, imagens, fontes
├── tests/           # Testes automatizados (pytest)
├── docs/            # Documentação técnica
├── logs/            # Arquivos de log (gerados automaticamente)
├── .env.example     # Template de configuração
├── requirements.txt # Dependências Python
├── pyproject.toml   # Metadados do projeto
└── main.py          # Entry point
```

---

## ⚙️ Configuração

### 1. Pré-requisitos

- Python 3.11 ou superior
- pip

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas chaves de API
```

### 4. Executar

```bash
python main.py
```

---

## 🏗️ Arquitetura

```
Display Layer
    ↓ (lê apenas Models)
Service Layer
    ↓ (orquestra)
API Layer ←→ Model Layer
    ↓
Infrastructure (Cache, Storage, Logging, Config, Scheduler)
```

O **Display** nunca se comunica diretamente com APIs.
Todo dado passa pela sequência: `API → Service → Model → Renderer`.

---

## 📦 APIs Integradas

| Categoria | API | Status |
|---|---|---|
| Aeronaves | OpenSky Network | ✅ Ativo |
| Aeronaves | ADS-B Exchange | 🔧 Estrutura |
| Aeronaves | FlightAware | 🔧 Estrutura |
| Aeronaves | FlightRadar24 | 🔧 Estrutura |
| Clima | OpenWeather | ✅ Ativo |
| Clima | Open-Meteo | ✅ Ativo |
| Espaço | NASA | ✅ Ativo |
| Espaço | SpaceX | ✅ Ativo |
| Espaço | Launch Library 2 | ✅ Ativo |
| Espaço | ISS Tracker | ✅ Ativo |
| Espaço | N2YO | 🔧 Estrutura |

---

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 📄 Licença

MIT License
