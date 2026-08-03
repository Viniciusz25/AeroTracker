"""
AeroTracker Core — Storage Local
===================================
Persistência local de dados históricos em formato JSON/JSONL.

Responsabilidades:
    - Salvar snapshots de dados por módulo
    - Recuperar histórico de dados
    - Rotação automática de arquivos por data
    - Não depende de banco de dados externo

Design:
    Cada módulo possui seu próprio subdiretório em storage_data/.
    Dados são salvos como JSON Lines (JSONL) por data.
    Snapshots individuais são salvos como JSON.

Estrutura de diretórios gerada:
    storage_data/
    ├── aircraft/
    │   ├── 2026-08-03.jsonl    ← histórico do dia (um JSON por linha)
    │   └── latest.json         ← último snapshot
    ├── iss/
    │   ├── 2026-08-03.jsonl
    │   └── latest.json
    └── weather/
        ├── 2026-08-03.jsonl
        └── latest.json

Uso:
    from storage.local_storage import local_storage

    # Salvar dado
    local_storage.save("aircraft", data_dict)

    # Recuperar último dado salvo
    data = local_storage.load_latest("aircraft")

    # Recuperar histórico do dia
    history = local_storage.load_history("aircraft", date="2026-08-03")
"""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class LocalStorage:
    """
    Gerenciador de persistência local baseado em arquivos JSON/JSONL.

    Cada módulo possui seu próprio subdiretório.
    Os dados são salvos em formato JSONL (um JSON por linha),
    com rotação diária automática.

    Args:
        base_dir: Diretório raiz para todos os dados persistidos.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        logger.info(
            "LocalStorage inicializado em: {path}",
            path=str(self._base_dir)
        )

    # -------------------------------------------------------------------------
    # API Pública — Escrita
    # -------------------------------------------------------------------------

    def save(
        self,
        module: str,
        data: Any,
        append_history: bool = True,
    ) -> None:
        """
        Salva um dado para o módulo especificado.

        Sempre atualiza o `latest.json`. Se `append_history=True`,
        também adiciona uma linha ao arquivo JSONL do dia atual.

        Args:
            module: Nome do módulo (ex: "aircraft", "iss", "weather").
            data: Dado a persistir (dict, list ou Pydantic model).
            append_history: Se True, adiciona ao histórico diário.
        """
        module_dir = self._get_module_dir(module)
        payload = self._serialize(data)

        with self._lock:
            # Salvar snapshot mais recente
            latest_path = module_dir / "latest.json"
            self._write_json(latest_path, payload)

            # Salvar no histórico diário (JSONL)
            if append_history:
                history_path = module_dir / f"{date.today().isoformat()}.jsonl"
                self._append_jsonl(history_path, payload)

        logger.debug(
            "Storage SAVE: módulo='{module}', history={hist}",
            module=module, hist=append_history
        )

    # -------------------------------------------------------------------------
    # API Pública — Leitura
    # -------------------------------------------------------------------------

    def load_latest(self, module: str) -> Optional[Any]:
        """
        Recupera o último dado salvo para o módulo.

        Args:
            module: Nome do módulo.

        Returns:
            Dado deserializado, ou None se não houver dado salvo.
        """
        latest_path = self._get_module_dir(module) / "latest.json"

        if not latest_path.exists():
            logger.debug(
                "Storage LOAD_LATEST: módulo='{module}' — sem dados",
                module=module
            )
            return None

        try:
            with open(latest_path, encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(
                "Storage LOAD_LATEST: módulo='{module}' — OK",
                module=module
            )
            return data
        except (json.JSONDecodeError, OSError) as e:
            logger.error(
                "Storage LOAD_LATEST: erro ao ler módulo='{module}': {err}",
                module=module, err=str(e)
            )
            return None

    def load_history(
        self,
        module: str,
        target_date: Optional[str] = None,
        max_entries: int = 1000,
    ) -> list[Any]:
        """
        Recupera o histórico de um módulo para uma data.

        Args:
            module: Nome do módulo.
            target_date: Data no formato 'YYYY-MM-DD'.
                         Se None, usa o dia atual.
            max_entries: Número máximo de entradas retornadas
                         (as mais recentes).

        Returns:
            Lista de entradas históricas ordenadas por inserção.
        """
        dt = target_date or date.today().isoformat()
        history_path = self._get_module_dir(module) / f"{dt}.jsonl"

        if not history_path.exists():
            logger.debug(
                "Storage LOAD_HISTORY: módulo='{module}' data='{dt}' — sem dados",
                module=module, dt=dt
            )
            return []

        entries: list[Any] = []
        try:
            with open(history_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError as e:
            logger.error(
                "Storage LOAD_HISTORY: erro ao ler módulo='{module}': {err}",
                module=module, err=str(e)
            )
            return []

        # Retornar apenas as últimas N entradas
        return entries[-max_entries:]

    def list_history_dates(self, module: str) -> list[str]:
        """
        Lista todas as datas com histórico disponível para o módulo.

        Args:
            module: Nome do módulo.

        Returns:
            Lista de strings 'YYYY-MM-DD' ordenadas cronologicamente.
        """
        module_dir = self._get_module_dir(module)
        dates = sorted([
            f.stem for f in module_dir.glob("*.jsonl")
            if f.stem != "latest"
        ])
        return dates

    def get_storage_size(self, module: Optional[str] = None) -> int:
        """
        Retorna o tamanho total em bytes do storage.

        Args:
            module: Se informado, retorna apenas o tamanho desse módulo.

        Returns:
            Tamanho em bytes.
        """
        if module:
            target_dir = self._get_module_dir(module)
        else:
            target_dir = self._base_dir

        return sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())

    def delete_history_before(self, module: str, before_date: str) -> int:
        """
        Remove arquivos de histórico anteriores a uma data.

        Args:
            module: Nome do módulo.
            before_date: Data limite no formato 'YYYY-MM-DD'.

        Returns:
            Número de arquivos removidos.
        """
        module_dir = self._get_module_dir(module)
        removed = 0

        for jsonl_file in module_dir.glob("*.jsonl"):
            if jsonl_file.stem < before_date:
                jsonl_file.unlink()
                removed += 1
                logger.debug(
                    "Storage DELETE: {file} removido",
                    file=jsonl_file.name
                )

        if removed:
            logger.info(
                "Storage CLEANUP: módulo='{module}' — {n} arquivos removidos",
                module=module, n=removed
            )
        return removed

    # -------------------------------------------------------------------------
    # Métodos privados
    # -------------------------------------------------------------------------

    def _get_module_dir(self, module: str) -> Path:
        """Retorna e garante existência do diretório do módulo."""
        module_dir = self._base_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        return module_dir

    @staticmethod
    def _serialize(data: Any) -> dict[str, Any]:
        """
        Serializa o dado para um formato persistível.
        Adiciona timestamp de gravação automaticamente.
        """
        if hasattr(data, "model_dump"):
            # Pydantic model
            payload = data.model_dump(mode="json")
        elif isinstance(data, dict):
            payload = data.copy()
        elif isinstance(data, list):
            payload = {"items": data}  # type: ignore[assignment]
        else:
            payload = {"value": str(data)}  # type: ignore[assignment]

        payload["_saved_at"] = datetime.now(UTC).isoformat()
        return payload

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        """Escreve um arquivo JSON de forma atômica."""
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp_path.replace(path)

    @staticmethod
    def _append_jsonl(path: Path, data: dict[str, Any]) -> None:
        """Adiciona uma linha JSON ao arquivo JSONL."""
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Singleton — instância criada com o diretório das settings
# ---------------------------------------------------------------------------

def _create_local_storage() -> LocalStorage:
    """Cria LocalStorage com o diretório configurado nas settings."""
    from config.settings import settings
    return LocalStorage(base_dir=settings.storage_dir)


local_storage: LocalStorage = _create_local_storage()
