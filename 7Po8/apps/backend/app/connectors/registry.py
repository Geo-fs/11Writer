from app.connectors.base import ConnectorRunner
from app.connectors.rss_news import RSSNewsConnector
from app.connectors.sample_news import SampleNewsConnector
from app.connectors.weather import WeatherConnector


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, ConnectorRunner] = {}
        self.register(SampleNewsConnector())
        self.register(RSSNewsConnector())
        self.register(WeatherConnector())

    def register(self, connector: ConnectorRunner) -> None:
        self._connectors[connector.type_name] = connector

    def get(self, type_name: str) -> ConnectorRunner | None:
        return self._connectors.get(type_name)


registry = ConnectorRegistry()
