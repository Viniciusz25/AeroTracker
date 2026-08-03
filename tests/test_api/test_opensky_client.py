"""
Testes — OpenSky Client
=========================
Testa o OpenSkyClient com respostas mockadas:
    - Parsing correto de resposta completa
    - Aeronave com campos None
    - Resposta vazia (zero aeronaves)
    - Cache: evita chamada duplicada
    - Busca por ICAO24
    - Integração com BoundingBox
"""

import pytest
import respx
import httpx

from api.aircraft.opensky_client import OpenSkyClient
from cache.cache_manager import CacheManager
from models.aircraft import AircraftList, AircraftState
from models.common import BoundingBox


# ---------------------------------------------------------------------------
# Resposta de exemplo da API OpenSky
# ---------------------------------------------------------------------------

# Formato real: [icao24, callsign, country, time_pos, last_contact,
#                lon, lat, baro_alt, on_ground, velocity,
#                true_track, vert_rate, sensors, geo_alt, squawk,
#                spi, pos_src, category]
MOCK_OPENSKY_RESPONSE = {
    "time": 1722689000,
    "states": [
        ["abc123", "LA3501  ", "Brazil", 1722688990, 1722689000,
         -46.63, -23.55, 10668.0, False, 240.0,
         90.0, 2.5, None, 10600.0, "1234",
         False, 0, 4],
        ["def456", "GLO1234 ", "Brazil", 1722688985, 1722689000,
         -45.10, -22.90, 9000.0, False, 220.0,
         180.0, -1.0, None, 8800.0, "2345",
         False, 0, 4],
        ["ghi789", None, "USA", 1722688980, 1722689000,
         -47.50, -24.00, None, True, 0.0,
         None, None, None, None, None,
         False, 0, 0],
    ]
}

MOCK_EMPTY_RESPONSE = {
    "time": 1722689000,
    "states": None,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_cache() -> CacheManager:
    """Cache isolado para testes do OpenSky."""
    return CacheManager(persist_dir=None)


@pytest.fixture
def client(isolated_cache: CacheManager, monkeypatch: pytest.MonkeyPatch) -> OpenSkyClient:
    """OpenSkyClient com cache isolado e sem credenciais."""
    import api.aircraft.opensky_client as module
    monkeypatch.setattr(module, "cache_manager", isolated_cache)

    c = OpenSkyClient(username=None, password=None, use_cache=True)
    return c


# ---------------------------------------------------------------------------
# Testes: Parsing da resposta
# ---------------------------------------------------------------------------


class TestOpenSkyParsing:
    @pytest.mark.asyncio
    @respx.mock
    async def test_parse_full_response(self, client: OpenSkyClient) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        assert isinstance(result, AircraftList)
        assert result.total_count == 3
        assert result.query_time == 1722689000

    @pytest.mark.asyncio
    @respx.mock
    async def test_aircraft_fields_correctly_parsed(
        self, client: OpenSkyClient
    ) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        first = result.aircraft[0]
        assert first.icao24 == "abc123"
        assert first.callsign == "LA3501"
        assert first.origin_country == "Brazil"
        assert first.on_ground is False
        assert first.position is not None
        assert first.position.latitude == -23.55
        assert first.position.longitude == -46.63

    @pytest.mark.asyncio
    @respx.mock
    async def test_aircraft_on_ground_parsed(self, client: OpenSkyClient) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        on_ground = [a for a in result.aircraft if a.on_ground]
        assert len(on_ground) == 1
        assert on_ground[0].icao24 == "ghi789"

    @pytest.mark.asyncio
    @respx.mock
    async def test_aircraft_with_none_callsign(self, client: OpenSkyClient) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        no_callsign = [a for a in result.aircraft if a.callsign is None]
        assert len(no_callsign) == 1
        # display_id deve fallback para ICAO24
        assert no_callsign[0].display_id == "GHI789"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response_returns_empty_list(
        self, client: OpenSkyClient
    ) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_EMPTY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        assert isinstance(result, AircraftList)
        assert result.total_count == 0
        assert result.airborne_count == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_airborne_count_correct(self, client: OpenSkyClient) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        assert result.airborne_count == 2
        assert result.on_ground_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_bounding_box_set_correctly(self, client: OpenSkyClient) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        assert result.bounding_box is not None
        assert isinstance(result.bounding_box, BoundingBox)


# ---------------------------------------------------------------------------
# Testes: Cache
# ---------------------------------------------------------------------------


class TestOpenSkyCache:
    @pytest.mark.asyncio
    @respx.mock
    async def test_cache_prevents_second_request(
        self, client: OpenSkyClient, isolated_cache: CacheManager
    ) -> None:
        route = respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            result1 = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)
            result2 = await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)

        # Deve ter feito apenas 1 requisição (a 2ª vem do cache)
        assert route.call_count == 1
        assert result1.total_count == result2.total_count

    @pytest.mark.asyncio
    @respx.mock
    async def test_different_coords_make_separate_requests(
        self, client: OpenSkyClient
    ) -> None:
        route = respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_OPENSKY_RESPONSE)
        )
        async with client:
            await client.get_aircraft_in_area(-23.5, -46.6, radius_km=200)
            await client.get_aircraft_in_area(-22.9, -43.2, radius_km=200)

        # Coordenadas diferentes = chaves de cache diferentes = 2 requisições
        assert route.call_count == 2


# ---------------------------------------------------------------------------
# Testes: Busca por ICAO24
# ---------------------------------------------------------------------------


class TestOpenSkyByIcao24:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_aircraft_by_icao24_found(self, client: OpenSkyClient) -> None:
        single_response = {
            "time": 1722689000,
            "states": [MOCK_OPENSKY_RESPONSE["states"][0]]
        }
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=single_response)
        )
        async with client:
            result = await client.get_aircraft_by_icao24("abc123")

        assert result is not None
        assert isinstance(result, AircraftState)
        assert result.icao24 == "abc123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_aircraft_by_icao24_not_found(
        self, client: OpenSkyClient
    ) -> None:
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=MOCK_EMPTY_RESPONSE)
        )
        async with client:
            result = await client.get_aircraft_by_icao24("xyz999")

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_icao24_normalized_to_lowercase(
        self, client: OpenSkyClient
    ) -> None:
        single_response = {
            "time": 1722689000,
            "states": [MOCK_OPENSKY_RESPONSE["states"][0]]
        }
        respx.get("https://opensky-network.org/api/states/all").mock(
            return_value=httpx.Response(200, json=single_response)
        )
        async with client:
            # Passar em maiúsculas
            result = await client.get_aircraft_by_icao24("ABC123")

        assert result is not None
        assert result.icao24 == "abc123"  # Normalizado para minúsculas
