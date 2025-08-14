"""Utilities for interacting with the DoData API."""

import uuid
from collections.abc import Iterable
from typing import Any

import pandas as pd

from gdsfactoryhub import helpers
from gdsfactoryhub.api_client import ApiClient
from gdsfactoryhub.errors import DoDataError
from gdsfactoryhub.query_client import QueryClient
from gdsfactoryhub.schemas import Analysis, DeviceData


class DeviceDataUtils:
    """Utility class for handling device data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def get_as_dataframe(self, pk: str | uuid.UUID) -> pd.DataFrame:
        """Fetch device data as a pandas DataFrame."""
        res = self._query_client.table("device_data").select("data_file").eq("pk", str(pk)).execute()

        if not res.data:
            msg = f"No device data found for pk: {pk}"
            raise DoDataError(msg)

        if not res.data[0]["data_file"]:
            msg = f"No data file found for device data with pk: {pk}"
            raise DoDataError(msg)

        device_data_file_content = self._api_client.download_file(res.data[0]["data_file"]["path"])

        return helpers.df_from_bytes(device_data_file_content)


class DieUtils:
    """Utility class for handling die data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client
        self._device_data_utils: DeviceDataUtils = DeviceDataUtils(api_client, query_client)

    def get_device_data_objects(self, pk: str | uuid.UUID) -> list[tuple[DeviceData, pd.DataFrame]]:
        """Fetch device data objects for a given die."""
        res = self._query_client.device_data().eq("die_pk", str(pk)).execute()
        if not res.data:
            msg = f"No device data found for die: {pk}"
            raise DoDataError(msg)

        device_data_objects = []
        for device_data_dict in res.data:
            device_data = DeviceData.model_validate(device_data_dict)
            df = self._device_data_utils.get_as_dataframe(device_data.pk)
            device_data_objects.append((device_data, df))
        return device_data_objects


class WaferUtils:
    """Utility class for handling wafer data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def get_die_analyses(
        self, pk: str | uuid.UUID, filter_clauses: Iterable[tuple[str, str, Any]] = ()
    ) -> dict[tuple[float, float], list[Analysis]]:
        """Fetch analyses for all dies on a wafer."""
        base_query = self._query_client.analyses().not_.is_("die", None).eq("die.wafer.pk", str(pk))
        for column, operator, value in filter_clauses:
            base_query = base_query.filter(column, operator, value)
        res = base_query.execute()
        if not res.data:
            msg = f"No die analyses found for wafer: {pk}"
            raise DoDataError(msg)
        analyses_per_die: dict[tuple[float, float], list[Analysis]] = {}
        for data in res.data:
            analysis = Analysis.model_validate(data)
            die = analysis.die
            if die is not None:
                key = (die.x, die.y)
                if key not in analyses_per_die:
                    analyses_per_die[key] = []
                analyses_per_die[key].append(analysis)
        return analyses_per_die


class CommonUtils:
    """Utility class for common operations."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def display_remote_image(self, file_path: str) -> None:
        """Display an image from a remote file path."""
        from IPython.display import Image, display

        file_bytes = self._api_client.download_file(file_path)
        display(Image(data=file_bytes))


class Utils:
    """Main utility class for accessing various utility functions."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def device_data(self) -> DeviceDataUtils:
        """Return an instance of DeviceDataUtils."""
        return DeviceDataUtils(self._api_client, self._query_client)

    def die(self) -> DieUtils:
        """Return an instance of DieUtils."""
        return DieUtils(self._api_client, self._query_client)

    def wafer(self) -> WaferUtils:
        """Return an instance of WaferUtils."""
        return WaferUtils(self._api_client, self._query_client)

    def common(self) -> CommonUtils:
        """Return an instance of CommonUtils."""
        return CommonUtils(self._api_client, self._query_client)
