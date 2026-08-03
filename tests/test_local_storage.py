"""
Testes — Local Storage
========================
Testa todas as operações do LocalStorage:
    - save e load_latest
    - histórico diário (JSONL)
    - listagem de datas
    - tamanho do storage
    - deleção de histórico antigo
    - serialização de dicts e objetos Pydantic
"""

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import BaseModel

from storage.local_storage import LocalStorage


# ---------------------------------------------------------------------------
# Modelos de teste
# ---------------------------------------------------------------------------


class SampleModel(BaseModel):
    name: str
    value: float
    active: bool = True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_storage(tmp_path: Path) -> LocalStorage:
    """Retorna um LocalStorage usando diretório temporário do pytest."""
    return LocalStorage(base_dir=tmp_path / "storage_test")


# ---------------------------------------------------------------------------
# Testes: save e load_latest
# ---------------------------------------------------------------------------


class TestLocalStorageSaveLoad:
    def test_save_and_load_dict(self, tmp_storage: LocalStorage) -> None:
        data = {"lat": -23.5, "lon": -46.6, "aircraft_count": 42}
        tmp_storage.save("aircraft", data)
        result = tmp_storage.load_latest("aircraft")
        assert result is not None
        assert result["lat"] == -23.5
        assert result["aircraft_count"] == 42

    def test_save_and_load_pydantic_model(self, tmp_storage: LocalStorage) -> None:
        model = SampleModel(name="ISS", value=408.0)
        tmp_storage.save("iss", model)
        result = tmp_storage.load_latest("iss")
        assert result is not None
        assert result["name"] == "ISS"
        assert result["value"] == 408.0
        assert result["active"] is True

    def test_load_latest_nonexistent_returns_none(self, tmp_storage: LocalStorage) -> None:
        result = tmp_storage.load_latest("modulo_inexistente")
        assert result is None

    def test_save_overwrites_latest(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("weather", {"temp": 20.0})
        tmp_storage.save("weather", {"temp": 25.0})
        result = tmp_storage.load_latest("weather")
        assert result["temp"] == 25.0

    def test_save_adds_saved_at_timestamp(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("moon", {"phase": "waxing"})
        result = tmp_storage.load_latest("moon")
        assert "_saved_at" in result

    def test_save_creates_module_directory(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("launch", {"name": "Falcon 9"})
        module_dir = tmp_storage._base_dir / "launch"
        assert module_dir.exists()
        assert module_dir.is_dir()


# ---------------------------------------------------------------------------
# Testes: Histórico JSONL
# ---------------------------------------------------------------------------


class TestLocalStorageHistory:
    def test_save_appends_to_history(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("iss", {"lat": 10.0, "lon": 20.0})
        tmp_storage.save("iss", {"lat": 11.0, "lon": 21.0})
        tmp_storage.save("iss", {"lat": 12.0, "lon": 22.0})

        history = tmp_storage.load_history("iss")
        assert len(history) == 3

    def test_load_history_correct_order(self, tmp_storage: LocalStorage) -> None:
        for i in range(5):
            tmp_storage.save("iss", {"index": i})

        history = tmp_storage.load_history("iss")
        indices = [h["index"] for h in history]
        assert indices == [0, 1, 2, 3, 4]

    def test_load_history_empty_for_wrong_date(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("iss", {"lat": 0.0})
        result = tmp_storage.load_history("iss", target_date="1999-01-01")
        assert result == []

    def test_load_history_max_entries(self, tmp_storage: LocalStorage) -> None:
        for i in range(10):
            tmp_storage.save("iss", {"index": i})

        history = tmp_storage.load_history("iss", max_entries=3)
        assert len(history) == 3
        # Deve retornar as últimas 3
        assert history[-1]["index"] == 9

    def test_save_without_history(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("aircraft", {"count": 10}, append_history=False)
        history = tmp_storage.load_history("aircraft")
        assert len(history) == 0
        # Mas latest ainda deve existir
        latest = tmp_storage.load_latest("aircraft")
        assert latest is not None

    def test_list_history_dates(self, tmp_storage: LocalStorage) -> None:
        tmp_storage.save("weather", {"temp": 25.0})
        dates = tmp_storage.list_history_dates("weather")
        today = date.today().isoformat()
        assert today in dates

    def test_list_history_dates_empty_for_new_module(
        self, tmp_storage: LocalStorage
    ) -> None:
        # Cria o módulo sem histórico
        tmp_storage.save("empty_module", {"x": 1}, append_history=False)
        dates = tmp_storage.list_history_dates("empty_module")
        assert dates == []


# ---------------------------------------------------------------------------
# Testes: Tamanho e Limpeza
# ---------------------------------------------------------------------------


class TestLocalStorageCleanup:
    def test_get_storage_size_nonzero_after_save(
        self, tmp_storage: LocalStorage
    ) -> None:
        tmp_storage.save("aircraft", {"data": "test"})
        size = tmp_storage.get_storage_size("aircraft")
        assert size > 0

    def test_delete_history_before_removes_old_files(
        self, tmp_path: Path
    ) -> None:
        storage = LocalStorage(base_dir=tmp_path / "cleanup_test")
        module_dir = storage._base_dir / "aircraft"
        module_dir.mkdir(parents=True, exist_ok=True)

        # Criar arquivos JSONL "antigos" manualmente
        old_dates = ["2024-01-01", "2024-06-15", "2025-12-31"]
        for d in old_dates:
            jsonl = module_dir / f"{d}.jsonl"
            jsonl.write_text('{"test": true}\n', encoding="utf-8")

        removed = storage.delete_history_before("aircraft", before_date="2026-01-01")
        assert removed == 3

    def test_delete_history_before_keeps_newer_files(
        self, tmp_path: Path
    ) -> None:
        storage = LocalStorage(base_dir=tmp_path / "keep_test")
        module_dir = storage._base_dir / "iss"
        module_dir.mkdir(parents=True, exist_ok=True)

        dates = ["2026-07-01", "2026-07-15", "2026-08-01"]
        for d in dates:
            (module_dir / f"{d}.jsonl").write_text('{"x": 1}\n', encoding="utf-8")

        # Remove apenas antes de 2026-07-15
        removed = storage.delete_history_before("iss", before_date="2026-07-15")
        assert removed == 1

        remaining = list(module_dir.glob("*.jsonl"))
        remaining_names = [f.stem for f in remaining]
        assert "2026-07-15" in remaining_names
        assert "2026-08-01" in remaining_names
