"""
AeroTracker Core — Cliente HTTP Base
=======================================
Cliente HTTP assíncrono base utilizado por todos os adapters de API.

Responsabilidades:
    - Encapsular httpx.AsyncClient com configurações padronizadas
    - Implementar retry automático com backoff exponencial
    - Definir timeouts globais configuráveis
    - Tratar erros HTTP de forma consistente
    - Logar todas as requisições e respostas
    - Medir tempo de resposta de cada chamada

Design:
    Cada adapter de API herda de BaseAPIClient e implementa
    seus próprios métodos de busca e parsing.

    O cliente suporta autenticação via:
    - Header (Authorization: Bearer <token>)
    - Query param (?apikey=<key>)
    - Basic auth (usuário + senha)

Uso:
    class MyAPIClient(BaseAPIClient):
        BASE_URL = "https://api.example.com"

        async def fetch_data(self) -> dict:
            return await self.get("/endpoint", params={"key": "val"})
"""

import time
from abc import ABC
from typing import Any, Optional

import httpx

from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Exceções customizadas da API Layer
# ---------------------------------------------------------------------------


class APIError(Exception):
    """Erro genérico de API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        provider: str = "unknown",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.provider = provider

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.provider}] HTTP {self.status_code}: {super().__str__()}"
        return f"[{self.provider}] {super().__str__()}"


class APITimeoutError(APIError):
    """Erro de timeout na requisição."""


class APIRateLimitError(APIError):
    """Erro de rate limit (HTTP 429)."""


class APIAuthError(APIError):
    """Erro de autenticação (HTTP 401/403)."""


class APINotFoundError(APIError):
    """Recurso não encontrado (HTTP 404)."""


class APIServerError(APIError):
    """Erro interno do servidor da API (HTTP 5xx)."""


# ---------------------------------------------------------------------------
# Configuração de Retry
# ---------------------------------------------------------------------------


class RetryConfig:
    """
    Configuração de retry automático com backoff exponencial.

    Attributes:
        max_attempts: Número máximo de tentativas (incluindo a primeira).
        base_delay_seconds: Delay inicial entre tentativas.
        max_delay_seconds: Delay máximo entre tentativas.
        retry_on_status: Códigos HTTP que acionam retry.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 10.0,
        retry_on_status: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.retry_on_status = retry_on_status

    def delay_for_attempt(self, attempt: int) -> float:
        """
        Calcula o delay para uma tentativa usando backoff exponencial.

        Args:
            attempt: Número da tentativa atual (0-indexed).

        Returns:
            Delay em segundos.
        """
        delay = self.base_delay_seconds * (2 ** attempt)
        return min(delay, self.max_delay_seconds)


# ---------------------------------------------------------------------------
# Cliente Base
# ---------------------------------------------------------------------------


class BaseAPIClient(ABC):
    """
    Cliente HTTP base para todos os adapters de API do AeroTracker.

    Todos os clientes de API devem herdar desta classe e definir
    a constante BASE_URL.

    Args:
        base_url: URL base da API. Se None, usa self.BASE_URL.
        timeout_seconds: Timeout para todas as requisições.
        retry_config: Configuração de retry. None desativa retry.
        default_headers: Headers adicionais enviados em todas as requisições.
        auth: Tupla (usuário, senha) para autenticação Basic.
    """

    BASE_URL: str = ""      # Definir na subclasse
    PROVIDER_NAME: str = "unknown"  # Nome do provedor para logs

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: float = 15.0,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[dict[str, str]] = None,
        auth: Optional[tuple[str, str]] = None,
    ) -> None:
        self._base_url = (base_url or self.BASE_URL).rstrip("/")
        self._timeout = timeout_seconds
        self._retry = retry_config or RetryConfig()
        self._default_headers: dict[str, str] = {
            "User-Agent": "AeroTracker-Core/0.1.0",
            "Accept": "application/json",
            **(default_headers or {}),
        }
        self._auth = auth
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            "{provider}: cliente inicializado | url={url} | timeout={t}s",
            provider=self.PROVIDER_NAME,
            url=self._base_url,
            t=timeout_seconds,
        )

    # -------------------------------------------------------------------------
    # Gerenciamento do cliente httpx (context manager)
    # -------------------------------------------------------------------------

    async def __aenter__(self) -> "BaseAPIClient":
        """Suporte a `async with client:` — abre o httpx.AsyncClient."""
        await self._ensure_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Fecha o httpx.AsyncClient ao sair do context manager."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Garante que o httpx.AsyncClient está aberto."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._default_headers,
                timeout=httpx.Timeout(self._timeout),
                auth=self._auth,
                follow_redirects=True,
            )

    async def close(self) -> None:
        """Fecha o httpx.AsyncClient explicitamente."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # -------------------------------------------------------------------------
    # Métodos HTTP principais
    # -------------------------------------------------------------------------

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        """
        Realiza uma requisição GET com retry automático.

        Args:
            endpoint: Caminho relativo ao BASE_URL (ex: "/states/all").
            params: Query parameters da requisição.
            headers: Headers adicionais específicos desta requisição.

        Returns:
            JSON decodificado como dict ou list.

        Raises:
            APITimeoutError: Se a requisição exceder o timeout após todas as tentativas.
            APIRateLimitError: Se a API retornar 429 após todas as tentativas.
            APIAuthError: Se a API retornar 401 ou 403.
            APINotFoundError: Se a API retornar 404.
            APIServerError: Se a API retornar 5xx após todas as tentativas.
            APIError: Para outros erros de HTTP.
        """
        await self._ensure_client()
        return await self._request_with_retry("GET", endpoint, params=params, headers=headers)

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        json_body: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Executa uma requisição HTTP com retry e backoff exponencial.

        Args:
            method: Método HTTP ("GET", "POST", etc.).
            endpoint: Caminho relativo.
            params: Query parameters.
            headers: Headers adicionais.
            json_body: Body JSON para POST/PUT.

        Returns:
            JSON decodificado.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self._retry.max_attempts):
            start_time = time.monotonic()
            try:
                response = await self._client.request(  # type: ignore[union-attr]
                    method=method,
                    url=endpoint,
                    params=params,
                    headers=headers,
                    json=json_body,
                )

                elapsed_ms = (time.monotonic() - start_time) * 1000

                logger.debug(
                    "{provider} {method} {endpoint} → HTTP {status} ({ms:.0f}ms) [tentativa {n}/{max}]",
                    provider=self.PROVIDER_NAME,
                    method=method,
                    endpoint=endpoint,
                    status=response.status_code,
                    ms=elapsed_ms,
                    n=attempt + 1,
                    max=self._retry.max_attempts,
                )

                # Tratar erros HTTP
                if response.status_code == 200:
                    return response.json()

                await self._handle_http_error(response, attempt)

            except httpx.TimeoutException as e:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                last_exception = APITimeoutError(
                    f"Timeout após {self._timeout}s",
                    provider=self.PROVIDER_NAME,
                )
                logger.warning(
                    "{provider}: timeout na tentativa {n}/{max} para {endpoint}",
                    provider=self.PROVIDER_NAME,
                    n=attempt + 1,
                    max=self._retry.max_attempts,
                    endpoint=endpoint,
                )

            except (APIAuthError, APINotFoundError) as e:
                # Não faz retry para erros de auth ou not found
                raise

            except APIError as e:
                last_exception = e
                logger.warning(
                    "{provider}: erro na tentativa {n}/{max}: {err}",
                    provider=self.PROVIDER_NAME,
                    n=attempt + 1,
                    max=self._retry.max_attempts,
                    err=str(e),
                )

            except httpx.RequestError as e:
                last_exception = APIError(
                    f"Erro de rede: {e}",
                    provider=self.PROVIDER_NAME,
                )
                logger.warning(
                    "{provider}: erro de rede na tentativa {n}/{max}: {err}",
                    provider=self.PROVIDER_NAME,
                    n=attempt + 1,
                    max=self._retry.max_attempts,
                    err=str(e),
                )

            # Delay antes da próxima tentativa (exceto na última)
            if attempt < self._retry.max_attempts - 1:
                delay = self._retry.delay_for_attempt(attempt)
                logger.debug(
                    "{provider}: aguardando {delay:.1f}s antes da próxima tentativa",
                    provider=self.PROVIDER_NAME,
                    delay=delay,
                )
                import asyncio
                await asyncio.sleep(delay)

        # Todas as tentativas falharam
        raise last_exception or APIError(
            f"Todas as {self._retry.max_attempts} tentativas falharam",
            provider=self.PROVIDER_NAME,
        )

    async def _handle_http_error(
        self, response: httpx.Response, attempt: int
    ) -> None:
        """
        Converte respostas HTTP de erro em exceções adequadas.

        Args:
            response: Resposta HTTP com status de erro.
            attempt: Número da tentativa atual.

        Raises:
            Exceção adequada ao código HTTP.
        """
        status = response.status_code

        if status == 401 or status == 403:
            raise APIAuthError(
                f"Acesso negado: {response.text[:200]}",
                status_code=status,
                provider=self.PROVIDER_NAME,
            )
        elif status == 404:
            raise APINotFoundError(
                f"Recurso não encontrado: {response.url}",
                status_code=status,
                provider=self.PROVIDER_NAME,
            )
        elif status == 429:
            retry_after = response.headers.get("Retry-After", "?")
            raise APIRateLimitError(
                f"Rate limit atingido. Retry-After: {retry_after}s",
                status_code=status,
                provider=self.PROVIDER_NAME,
            )
        elif status >= 500:
            raise APIServerError(
                f"Erro do servidor: HTTP {status} — {response.text[:200]}",
                status_code=status,
                provider=self.PROVIDER_NAME,
            )
        else:
            raise APIError(
                f"HTTP {status}: {response.text[:200]}",
                status_code=status,
                provider=self.PROVIDER_NAME,
            )
