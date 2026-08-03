"""
Testes — JobScheduler
======================
Testa o comportamento do JobScheduler:
    - Inicialização e encerramento do agendador
    - Adição e remoção de jobs por módulo
    - Status de execução dos jobs
"""

import asyncio
import pytest

from scheduler.job_scheduler import JobScheduler


@pytest.fixture
async def scheduler() -> JobScheduler:
    sched = JobScheduler()
    sched.start()
    yield sched
    sched.stop()


class TestJobScheduler:
    @pytest.mark.asyncio
    async def test_start_and_stop(self) -> None:
        sched = JobScheduler()
        assert not sched.is_running
        sched.start()
        assert sched.is_running
        sched.stop()
        assert not sched.is_running

    @pytest.mark.asyncio
    async def test_add_and_remove_job(self, scheduler: JobScheduler) -> None:
        async def dummy_job():
            pass

        added = scheduler.add_module_job("aircraft", dummy_job, interval_seconds=10)
        assert added is True

        status = scheduler.get_status()
        assert status["jobs_count"] == 1
        assert "aircraft" in status["jobs"]

        removed = scheduler.remove_module_job("aircraft")
        assert removed is True
        assert scheduler.get_status()["jobs_count"] == 0
