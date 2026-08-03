"""
AeroTracker Core — Pacote de Modelos
=======================================
Exporta todas as entidades de domínio do AeroTracker.
"""

# Comuns
from models.common import (
    AeroBaseModel,
    Altitude,
    AltitudeUnit,
    BoundingBox,
    CardinalDirection,
    Coordinate,
    DataSource,
    Velocity,
    VelocityUnit,
)

# Aeronaves
from models.aircraft import (
    AircraftCategory,
    AircraftList,
    AircraftState,
    AircraftStatus,
    Airport,
    FlightRoute,
    PositionSource,
)

# Clima
from models.weather import (
    AlertSeverity,
    PrecipitationData,
    PrecipitationType,
    WeatherAlert,
    WeatherCondition,
    WeatherConditionGroup,
    WeatherForecast,
    WeatherSnapshot,
    WindData,
)

# Espaço
from models.space import (
    ISSPassPrediction,
    ISSPosition,
    Launch,
    LaunchPad,
    LaunchProvider,
    LaunchStatusCode,
    LaunchVehicle,
    NASAApod,
    NearEarthObject,
    OrbitType,
    Satellite,
    SatelliteCategory,
)

# Astronomia
from models.astronomy import (
    AstronomicalEvent,
    EventType,
    MoonData,
    MoonPhase,
    MoonPhaseType,
    PlanetData,
    PlanetName,
    SolarData,
    SolarSystemSnapshot,
)

__all__ = [
    # Common
    "AeroBaseModel", "Coordinate", "Altitude", "Velocity", "BoundingBox",
    "DataSource", "AltitudeUnit", "VelocityUnit", "CardinalDirection",
    # Aircraft
    "AircraftState", "AircraftCategory", "AircraftStatus", "AircraftList",
    "Airport", "FlightRoute", "PositionSource",
    # Weather
    "WeatherSnapshot", "WeatherCondition", "WeatherConditionGroup",
    "WindData", "PrecipitationData", "WeatherAlert", "WeatherForecast",
    "AlertSeverity", "PrecipitationType",
    # Space
    "ISSPosition", "ISSPassPrediction", "Launch", "LaunchProvider",
    "LaunchVehicle", "LaunchPad", "LaunchStatusCode", "OrbitType",
    "Satellite", "SatelliteCategory", "NASAApod", "NearEarthObject",
    # Astronomy
    "MoonPhase", "MoonPhaseType", "MoonData", "PlanetData", "PlanetName",
    "SolarData", "AstronomicalEvent", "EventType", "SolarSystemSnapshot",
]
