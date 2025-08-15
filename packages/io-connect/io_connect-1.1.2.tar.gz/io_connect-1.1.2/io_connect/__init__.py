from .connectors.alerts_handler import AlertsHandler
from .connectors.bruce_handler import BruceHandler
from .connectors.data_access import DataAccess
from .connectors.events_handler import EventsHandler
from .connectors.mqtt_handler import MQTTHandler
from .connectors.file_logger import LoggerConfigurator
from .connectors.weather_handler import WeatherHandler
from importlib import import_module
import io_connect.constants as c

# Controls Versioning
__version__ = c.VERSION
__author__ = "Faclon-Labs"
__contact__ = "datascience@faclon.com"

# Base imports always available
__all__ = [
    "AlertsHandler",
    "BruceHandler",
    "DataAccess",
    "EventsHandler",
    "MQTTHandler",
    "LoggerConfigurator",
    "WeatherHandler",
    "AsyncLoggerConfigurator",
    "AsyncDataAccess",
    "AsyncAlertsHandler",
    "AsyncWeatherHandler",
    "AsyncEventsHandler",
]


# Lazy import for async connectors (require optional dependencies)
def __getattr__(name):
    """Lazy import for async connectors that require optional dependencies."""
    async_imports = {
        "AsyncLoggerConfigurator",
        "AsyncDataAccess",
        "AsyncAlertsHandler",
        "AsyncEventsHandler",
        "AsyncWeatherHandler",
    }

    if name in async_imports:
        try:
            module = import_module("io_connect.async_connectors")
            return getattr(module, name)
        except ImportError as e:
            raise ImportError(
                f"Cannot import {name}. Please install optional dependencies with: "
                f"pip install io_connect[all]"
            ) from e

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
