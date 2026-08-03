"""
Testes — Base API Client
==========================
Testa o comportamento do BaseAPIClient:
    - Requisição GET com sucesso
    - Retry em erros 5xx
    - Sem retry em 401/404
    - APIRateLimitError em 429
    - APITimeoutError em timeout
    - Hierarquia de exceções
    - RetryConfig.delay_for_attempt
"""

import pytest
import respx
import httpx

from api.base_client import (
    APIAuthError,
    APIError,
    APINotFoundError,
    APIRateLimitError,
    APIServerError,
    APITimeoutError,
    BaseAPIClient,
    RetryConfig,
)


# ---------------------------------------------------------------------------
# Cliente concreto para testes
# ---------------------------------------------------------------------------


class ConcreteClient(BaseAPIClient):
    """Implementação concreta de BaseAPIClient para testes."""
    BASE_URL = "https://api.test.com"
    PROVIDER_NAME = "test_provider"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fast_retry() -> RetryConfig:
    """RetryConfig sem delay para testes rápidos."""
    return RetryConfig(
        max_attempts=3,
        base_delay_seconds=0.0,   # Sem delay nos testes
        max_delay_seconds=0.0,
    )


@pytest.fixture
def client(fast_retry: RetryConfig) -> ConcreteClient:
    return ConcreteClient(
        timeout_seconds=5.0,
        retry_config=fast_retry,
    )


# ---------------------------------------------------------------------------
# Testes: RetryConfig
# ---------------------------------------------------------------------------


class TestRetryConfig:
    def test_delay_increases_exponentially(self) -> None:
        cfg = RetryConfig(base_delay_seconds=1.0, max_delay_seconds=100.0)
        assert cfg.delay_for_attempt(0) == 1.0
        assert cfg.delay_for_attempt(1) == 2.0
        assert cfg.delay_for_attempt(2) == 4.0
        assert cfg.delay_for_attempt(3) == 8.0

    def test_delay_capped_at_max(self) -> None:
        cfg = RetryConfig(base_delay_seconds=1.0, max_delay_seconds=5.0)
        assert cfg.delay_for_attempt(10) == 5.0

    def test_default_retry_on_status(self) -> None:
        cfg = RetryConfig()
        assert 429 in cfg.retry_on_status
        assert 500 in cfg.retry_on_status
        assert 503 in cfg.retry_on_status


# ---------------------------------------------------------------------------
# Testes: Requisição GET com sucesso
# ---------------------------------------------------------------------------


class TestBaseClientGet:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_returns_json_on_200(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/data").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        async with client:
            result = await client.get("/data")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_with_params(self, client: ConcreteClient) -> None:
        route = respx.get("https://api.test.com/states").mock(
            return_value=httpx.Response(200, json={"states": []})
        )
        async with client:
            result = await client.get("/states", params={"lat": -23.5, "lon": -46.6})
        assert result["states"] == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_list_response(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/items").mock(
            return_value=httpx.Response(200, json=[1, 2, 3])
        )
        async with client:
            result = await client.get("/items")
        assert result == [1, 2, 3]


# ---------------------------------------------------------------------------
# Testes: Tratamento de erros HTTP
# ---------------------------------------------------------------------------


class TestBaseClientErrors:
    @pytest.mark.asyncio
    @respx.mock
    async def test_401_raises_api_auth_error(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/secure").mock(
            return_value=httpx.Response(401, text="Unauthorized")
        )
        async with client:
            with pytest.raises(APIAuthError) as exc_info:
                await client.get("/secure")
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @respx.mock
    async def test_403_raises_api_auth_error(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/secure").mock(
            return_value=httpx.Response(403, text="Forbidden")
        )
        async with client:
            with pytest.raises(APIAuthError) as exc_info:
                await client.get("/secure")
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_raises_api_not_found(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/missing").mock(
            return_value=httpx.Response(404, text="Not Found")
        )
        async with client:
            with pytest.raises(APINotFoundError) as exc_info:
                await client.get("/missing")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @respx.mock
    async def test_429_raises_rate_limit_error(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/rate").mock(
            return_value=httpx.Response(429, text="Too Many Requests",
                                        headers={"Retry-After": "60"})
        )
        async with client:
            with pytest.raises(APIRateLimitError) as exc_info:
                await client.get("/rate")
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_raises_server_error_after_retry(
        self, client: ConcreteClient
    ) -> None:
        respx.get("https://api.test.com/broken").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        async with client:
            with pytest.raises(APIServerError) as exc_info:
                await client.get("/broken")
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_raises_server_error(self, client: ConcreteClient) -> None:
        respx.get("https://api.test.com/unavailable").mock(
            return_value=httpx.Response(503, text="Service Unavailable")
        )
        async with client:
            with pytest.raises(APIServerError):
                await client.get("/unavailable")


# ---------------------------------------------------------------------------
# Testes: Retry automático
# ---------------------------------------------------------------------------


class TestBaseClientRetry:
    @pytest.mark.asyncio
    @respx.mock
    async def test_retries_on_500_then_succeeds(self, client: ConcreteClient) -> None:
        """Deve tentar 2 vezes com 500 e ter sucesso na 3ª."""
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return httpx.Response(500, text="Error")
            return httpx.Response(200, json={"success": True})

        respx.get("https://api.test.com/flaky").mock(side_effect=side_effect)

        async with client:
            result = await client.get("/flaky")

        assert result == {"success": True}
        assert call_count == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_retry_on_401(self, client: ConcreteClient) -> None:
        """Não deve fazer retry em 401 — falha imediatamente."""
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return httpx.Response(401, text="Unauthorized")

        respx.get("https://api.test.com/auth").mock(side_effect=side_effect)

        async with client:
            with pytest.raises(APIAuthError):
                await client.get("/auth")

        assert call_count == 1  # Apenas 1 tentativa

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_retry_on_404(self, client: ConcreteClient) -> None:
        """Não deve fazer retry em 404 — falha imediatamente."""
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return httpx.Response(404, text="Not Found")

        respx.get("https://api.test.com/missing").mock(side_effect=side_effect)

        async with client:
            with pytest.raises(APINotFoundError):
                await client.get("/missing")

        assert call_count == 1


# ---------------------------------------------------------------------------
# Testes: Timeout
# ---------------------------------------------------------------------------


class TestBaseClientTimeout:
    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises_api_timeout_error(
        self, client: ConcreteClient
    ) -> None:
        respx.get("https://api.test.com/slow").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )
        async with client:
            with pytest.raises(APITimeoutError):
                await client.get("/slow")


# ---------------------------------------------------------------------------
# Testes: Hierarquia de Exceções
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    def test_all_errors_inherit_from_api_error(self) -> None:
        assert issubclass(APITimeoutError, APIError)
        assert issubclass(APIRateLimitError, APIError)
        assert issubclass(APIAuthError, APIError)
        assert issubclass(APINotFoundError, APIError)
        assert issubclass(APIServerError, APIError)

    def test_api_error_str_with_status(self) -> None:
        err = APIError("mensagem", status_code=503, provider="opensky")
        assert "503" in str(err)
        assert "opensky" in str(err)

    def test_api_error_str_without_status(self) -> None:
        err = APIError("mensagem", provider="nasa")
        assert "nasa" in str(err)
        assert "mensagem" in str(err)


# ---------------------------------------------------------------------------
# Testes: Context Manager
# ---------------------------------------------------------------------------


class TestBaseClientContextManager:
    @pytest.mark.asyncio
    @respx.mock
    async def test_context_manager_opens_and_closes(
        self, client: ConcreteClient
    ) -> None:
        respx.get("https://api.test.com/ping").mock(
            return_value=httpx.Response(200, json={"pong": True})
        )
        assert client._client is None

        async with client:
            assert client._client is not None
            assert not client._client.is_closed
            result = await client.get("/ping")

        # Após sair do context manager, cliente deve estar fechado
        assert client._client is None or client._client.is_closed
        assert result == {"pong": True}
