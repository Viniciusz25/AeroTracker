"""
AeroTracker Core — Sistema de Logging
======================================
Configuração centralizada do Loguru para toda a aplicação.

Responsabilidades:
    - Configurar handlers para console e arquivo
    - Rotação automática de logs por tamanho e data
    - Separar níveis por arquivo (errors.log, app.log)
    - Expor logger global configurado

Uso:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Módulo inicializado")
    logger.warning("Atenção: algo inesperado")
    logger.error("Erro crítico: {detalhe}", detalhe=str(e))
"""

import sys
from pathlib import Path

from loguru import logger

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE_APP = LOG_DIR / "app.log"
LOG_FILE_ERROR = LOG_DIR / "errors.log"

# Formato padrão para console (colorido)
_FMT_CONSOLE = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)

# Formato para arquivo (sem cores, com mais detalhes)
_FMT_FILE = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} — "
    "{message}"
)

_CONFIGURED = False


def setup_logging(
    log_level: str = "DEBUG",
    enable_file_logging: bool = True,
) -> None:
    """
    Configura o sistema de logging da aplicação.

    Deve ser chamado UMA única vez no bootstrap da aplicação.
    Chamadas subsequentes são ignoradas (idempotente).

    Args:
        log_level: Nível mínimo de log para console. Ex: "DEBUG", "INFO".
        enable_file_logging: Se True, salva logs em arquivo.
    """
    global _CONFIGURED

    if _CONFIGURED:
        return

    # Remove handlers padrão do loguru
    logger.remove()

    # --- Handler: Console ---------------------------------------------------
    logger.add(
        sys.stderr,
        format=_FMT_CONSOLE,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    if enable_file_logging:
        # --- Handler: app.log (todos os logs) --------------------------------
        logger.add(
            str(LOG_FILE_APP),
            format=_FMT_FILE,
            level="DEBUG",
            rotation="10 MB",       # Rotaciona ao atingir 10 MB
            retention="30 days",    # Mantém logs por 30 dias
            compression="zip",      # Comprime logs antigos
            encoding="utf-8",
            backtrace=True,
            diagnose=False,         # Desativa em arquivo por segurança
            enqueue=True,           # Thread-safe (async-safe)
        )

        # --- Handler: errors.log (apenas WARNING+) ---------------------------
        logger.add(
            str(LOG_FILE_ERROR),
            format=_FMT_FILE,
            level="WARNING",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
            enqueue=True,
        )

    _CONFIGURED = True
    logger.info("Sistema de logging inicializado. Nível: {level} | Arquivo: {file}",
                level=log_level, file=str(LOG_FILE_APP))


def get_logger(name: str) -> "logger.__class__":
    """
    Retorna uma instância do logger contextualizada pelo nome do módulo.

    Args:
        name: Identificador do módulo. Use sempre __name__.

    Returns:
        Logger instância do Loguru com contexto binding.

    Exemplo:
        logger = get_logger(__name__)
        logger.info("Módulo carregado")
    """
    return logger.bind(module=name)
