import asyncio
import calendar
import datetime
import os
import re
from dataclasses import fields, is_dataclass
from os import PathLike
from pathlib import Path
from typing import TypeVar, cast
from urllib.parse import urljoin
from uuid import UUID

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from cloudnet_api_client.containers import (
    PRODUCT_TYPE,
    SITE_TYPE,
    STATUS,
    Instrument,
    Model,
    Product,
    ProductMetadata,
    RawMetadata,
    RawModelMetadata,
    Site,
    VersionMetadata,
)
from cloudnet_api_client.dl import download_files

T = TypeVar("T")
MetadataList = list[ProductMetadata] | list[RawMetadata] | list[RawModelMetadata]
TMetadata = TypeVar("TMetadata", ProductMetadata, RawMetadata, RawModelMetadata)
DateParam = str | datetime.date | None
DateTimeParam = str | datetime.datetime | datetime.date | None
QueryParam = str | list[str] | None


class APIClient:
    def __init__(
        self,
        base_url: str = "https://cloudnet.fmi.fi/api/",
        session: requests.Session | None = None,
    ) -> None:
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.session = session or _make_session()

    def sites(
        self,
        site_id: str | None = None,
        type: SITE_TYPE | list[SITE_TYPE] | None = None,
    ) -> list[Site]:
        if site_id:
            res = self._get_response(f"sites/{site_id}")
        else:
            res = self._get_response("sites", {"type": type})
        return _build_objects(res, Site)

    def products(
        self, type: PRODUCT_TYPE | list[PRODUCT_TYPE] | None = None
    ) -> list[Product]:
        res = self._get_response("products")
        data = _build_objects(res, Product)
        if isinstance(type, str):
            data = [obj for obj in data if type in obj.type]
        elif isinstance(type, list):
            data = [obj for obj in data if any(t in obj.type for t in type)]
        return data

    def instruments(self) -> list[Instrument]:
        res = self._get_response("instrument-pids")
        return [
            Instrument(
                instrument_id=obj["instrument"]["id"],
                model=obj["model"],
                type=obj["type"],
                uuid=UUID(obj["uuid"]),
                pid=obj["pid"],
                owners=obj["owners"],
                serial_number=obj["serialNumber"],
                name=obj["name"],
            )
            for obj in res
        ]

    def file(
        self,
        uuid: str | UUID,
    ) -> ProductMetadata:
        res = self._get_response(f"files/{uuid}")
        return _build_meta_objects(res)[0]

    def versions(self, uuid: str | UUID) -> list[VersionMetadata]:
        res = self._get_response(
            f"files/{uuid}/versions",
            {"properties": ["pid", "dvasId", "legacy", "size", "checksum"]},
        )
        return [
            VersionMetadata(
                uuid=UUID(obj["uuid"]),
                created_at=_parse_datetime(obj["createdAt"]),
                pid=obj["pid"],
                dvas_id=obj["dvasId"],
                legacy=obj["legacy"],
                size=int(obj["size"]),
                checksum=obj["checksum"],
            )
            for obj in res
        ]

    def metadata(
        self,
        site_id: QueryParam = None,
        date: DateParam = None,
        date_from: DateParam = None,
        date_to: DateParam = None,
        updated_at: DateTimeParam = None,
        updated_at_from: DateTimeParam = None,
        updated_at_to: DateTimeParam = None,
        instrument_id: QueryParam = None,
        instrument_pid: QueryParam = None,
        model_id: QueryParam = None,
        product: QueryParam = None,
        show_legacy: bool = False,
    ) -> list[ProductMetadata]:
        params = {
            "site": site_id,
            "instrument": instrument_id,
            "instrumentPid": instrument_pid,
            "product": product,
            "showLegacy": show_legacy,
        }
        if show_legacy is not True:
            # API shows legacy files with any value (even <False>)
            del params["showLegacy"]

        _add_date_params(
            params, date, date_from, date_to, updated_at, updated_at_from, updated_at_to
        )

        _check_params(params, ("showLegacy",))

        no_instrument = instrument_id is None and instrument_pid is None

        if no_instrument and (product is None and model_id is not None):
            files_res = []
        else:
            files_res = self._get_response("files", params)

        # Add model files if requested
        if (
            (product is None and no_instrument)
            or (product is not None and "model" in product)
            or (model_id is not None and (product is None or "model" in product))
        ):
            for key in ("showLegacy", "product", "instrument", "instrumentPid"):
                if key in params:
                    del params[key]
            params["model"] = model_id
            files_res += self._get_response("model-files", params)

        return _build_meta_objects(files_res)

    def raw_metadata(
        self,
        site_id: QueryParam = None,
        date: DateParam = None,
        date_from: DateParam = None,
        date_to: DateParam = None,
        updated_at: DateTimeParam = None,
        updated_at_from: DateTimeParam = None,
        updated_at_to: DateTimeParam = None,
        instrument_id: QueryParam = None,
        instrument_pid: QueryParam = None,
        filename_prefix: QueryParam = None,
        filename_suffix: QueryParam = None,
        status: STATUS | list[STATUS] | None = None,
    ) -> list[RawMetadata]:
        params = {
            "site": site_id,
            "instrument": instrument_id,
            "instrumentPid": instrument_pid,
            "filenamePrefix": filename_prefix,
            "filenameSuffix": filename_suffix,
            "status": status,
        }
        _add_date_params(
            params, date, date_from, date_to, updated_at, updated_at_from, updated_at_to
        )
        res = self._get_response("raw-files", params)
        return _build_raw_meta_objects(res)

    def raw_model_metadata(
        self,
        site_id: QueryParam = None,
        model_id: QueryParam = None,
        date: DateParam = None,
        date_from: DateParam = None,
        date_to: DateParam = None,
        updated_at: DateTimeParam = None,
        updated_at_from: DateTimeParam = None,
        updated_at_to: DateTimeParam = None,
        filename_prefix: QueryParam = None,
        filename_suffix: QueryParam = None,
        status: STATUS | list[STATUS] | None = None,
    ) -> list[RawModelMetadata]:
        """For internal CLU use only. Will change in the future."""
        params = {
            "site": site_id,
            "filenamePrefix": filename_prefix,
            "filenameSuffix": filename_suffix,
            "status": status,
            "model": model_id,
        }
        _add_date_params(
            params, date, date_from, date_to, updated_at, updated_at_from, updated_at_to
        )

        _check_params(params)

        res = self._get_response("raw-model-files", params)
        return _build_raw_model_meta_objects(res)

    def download(
        self,
        metadata: MetadataList,
        output_directory: str | PathLike = ".",
        concurrency_limit: int = 5,
        progress: bool | None = None,
        validate_checksum: bool = False,
    ) -> list[Path]:
        return asyncio.run(
            self.adownload(
                metadata,
                output_directory,
                concurrency_limit,
                progress,
                validate_checksum,
            )
        )

    async def adownload(
        self,
        metadata: MetadataList,
        output_directory: str | PathLike = ".",
        concurrency_limit: int = 5,
        progress: bool | None = None,
        validate_checksum: bool = False,
    ) -> list[Path]:
        disable_progress = not progress if progress is not None else None
        output_directory = Path(output_directory).resolve()
        os.makedirs(output_directory, exist_ok=True)
        return await download_files(
            self.base_url,
            metadata,
            output_directory,
            concurrency_limit,
            disable_progress,
            validate_checksum,
        )

    @staticmethod
    def filter(
        metadata: list[TMetadata],
        include_pattern: str | None = None,
        exclude_pattern: str | None = None,
        include_tag_subset: set[str] | None = None,
        exclude_tag_subset: set[str] | None = None,
    ) -> list[TMetadata]:
        if include_pattern:
            metadata = [
                m for m in metadata if re.search(include_pattern, m.filename, re.I)
            ]
        if exclude_pattern:
            metadata = [
                m for m in metadata if not re.search(exclude_pattern, m.filename, re.I)
            ]
        if include_tag_subset:
            metadata = [
                m
                for m in metadata
                if isinstance(m, RawMetadata)
                and m.tags
                and include_tag_subset.issubset(m.tags)
            ]
        if exclude_tag_subset:
            metadata = [
                m
                for m in metadata
                if isinstance(m, RawMetadata)
                and m.tags
                and not exclude_tag_subset.issubset(m.tags)
            ]
        return metadata

    def _get_response(self, endpoint: str, params: dict | None = None) -> list[dict]:
        url = urljoin(self.base_url, endpoint)
        res = self.session.get(url, params=params, timeout=120)
        res.raise_for_status()
        data = res.json()
        if isinstance(data, dict):
            data = [data]
        return data


def _add_date_params(
    params: dict,
    date: DateParam,
    date_from: DateParam,
    date_to: DateParam,
    updated_at: DateTimeParam,
    updated_at_from: DateTimeParam,
    updated_at_to: DateTimeParam,
):
    if date is not None and (date_from is not None or date_to is not None):
        msg = "Cannot use 'date' with 'date_from' and 'date_to'"
        raise ValueError(msg)
    if date is not None:
        start, stop = _parse_date_param(date)
        params["dateFrom"] = start.isoformat()
        params["dateTo"] = stop.isoformat()
    if date_from is not None:
        params["dateFrom"] = _parse_date_param(date_from)[0].isoformat()
    if date_to is not None:
        params["dateTo"] = _parse_date_param(date_to)[1].isoformat()

    if updated_at is not None and (
        updated_at_from is not None or updated_at_to is not None
    ):
        msg = "Cannot use 'updated_at' with 'updated_at_from' and 'updated_at_to'"
        raise ValueError(msg)
    if updated_at is not None:
        start, stop = _parse_datetime_param(updated_at)
        params["updatedAtFrom"] = start.isoformat()
        params["updatedAtTo"] = stop.isoformat()
    if updated_at_from is not None:
        params["updatedAtFrom"] = _parse_datetime_param(updated_at_from)[0].isoformat()
    if updated_at_to is not None:
        params["updatedAtTo"] = _parse_datetime_param(updated_at_to)[1].isoformat()


def _parse_date_param(date: DateParam) -> tuple[datetime.date, datetime.date]:
    if isinstance(date, datetime.date):
        return date, date
    error = ValueError(f"Invalid date format: {date}")
    if isinstance(date, str):
        try:
            parts = [int(part) for part in date.split("-")]
        except ValueError:
            raise error from None
        match parts:
            case [year, month, day]:
                date = datetime.date(year, month, day)
                return date, date
            case [year, month]:
                last_day_number = calendar.monthrange(year, month)[1]
                return datetime.date(year, month, 1), datetime.date(
                    year, month, last_day_number
                )
            case [year]:
                return datetime.date(year, 1, 1), datetime.date(year, 12, 31)
    raise error


def _parse_datetime_param(
    dt: DateTimeParam,
) -> tuple[datetime.datetime, datetime.datetime]:
    if isinstance(dt, datetime.datetime):
        return dt, dt
    if isinstance(dt, datetime.date):
        return datetime.datetime.combine(
            dt, datetime.time(0, 0, 0, 0)
        ), datetime.datetime.combine(dt, datetime.time(23, 59, 59, 999999))
    if isinstance(dt, str):
        patterns = {
            ("%Y", "years"),
            ("%Y-%m", "months"),
            ("%Y-%m-%d", "days"),
            ("%Y-%m-%dT%H", "hours"),
            ("%Y-%m-%dT%H:%M", "minutes"),
            ("%Y-%m-%dT%H:%M:%S", "seconds"),
            ("%Y-%m-%dT%H:%M:%S.%f", "microseconds"),
        }
        for fmt, unit in patterns:
            try:
                start_date = datetime.datetime.strptime(dt, fmt)
            except ValueError:
                continue
            if unit == "years":
                end_date = start_date.replace(year=start_date.year + 1)
            elif unit == "months":
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1)
            elif unit == "days":
                end_date = start_date + datetime.timedelta(days=1)
            elif unit == "hours":
                end_date = start_date + datetime.timedelta(hours=1)
            elif unit == "minutes":
                end_date = start_date + datetime.timedelta(minutes=1)
            elif unit == "seconds":
                end_date = start_date + datetime.timedelta(seconds=1)
            elif unit == "microseconds":
                return start_date, start_date
            return start_date, end_date - datetime.timedelta(microseconds=1)
    msg = f"Invalid datetime format: {dt}"
    raise ValueError(msg)


def _build_objects(res: list[dict], object_type: type[T]) -> list[T]:
    assert is_dataclass(object_type)
    field_names = {f.name for f in fields(object_type)}
    objects = [
        object_type(
            **{_to_snake(k): v for k, v in obj.items() if _to_snake(k) in field_names}
        )
        for obj in res
    ]
    return cast(list[T], objects)


CONVERTED = {"measurement_date", "created_at", "updated_at", "size", "uuid"}


def _build_meta_objects(res: list[dict]) -> list[ProductMetadata]:
    field_names = (
        {f.name for f in fields(ProductMetadata)}
        - CONVERTED
        - {"product", "instrument", "model", "site"}
    )
    return [
        ProductMetadata(
            **{_to_snake(k): v for k, v in obj.items() if _to_snake(k) in field_names},
            product=Product(
                id=obj["product"]["id"],
                human_readable_name=obj["product"]["humanReadableName"],
                type=obj["product"]["type"],
                experimental=obj["product"]["experimental"],
            ),
            instrument=_create_instrument_object(obj["instrument"])
            if "instrument" in obj and obj["instrument"] is not None
            else None,
            model=_create_model_object(obj["model"])
            if "model" in obj and obj["model"] is not None
            else None,
            measurement_date=datetime.date.fromisoformat(obj["measurementDate"]),
            created_at=_parse_datetime(obj["createdAt"]),
            updated_at=_parse_datetime(obj["updatedAt"]),
            size=int(obj["size"]),
            uuid=UUID(obj["uuid"]),
            site=_create_site_object(obj["site"]),
        )
        for obj in res
    ]


def _build_raw_meta_objects(res: list[dict]) -> list[RawMetadata]:
    field_names = (
        {f.name for f in fields(RawMetadata)} - CONVERTED - {"instrument", "site"}
    )
    return [
        RawMetadata(
            **{_to_snake(k): v for k, v in obj.items() if _to_snake(k) in field_names},
            instrument=_create_instrument_object(obj["instrument"]),
            measurement_date=datetime.date.fromisoformat(obj["measurementDate"]),
            created_at=_parse_datetime(obj["createdAt"]),
            updated_at=_parse_datetime(obj["updatedAt"]),
            size=int(obj["size"]),
            uuid=UUID(obj["uuid"]),
            site=_create_site_object(obj["site"]),
        )
        for obj in res
    ]


def _build_raw_model_meta_objects(res: list[dict]) -> list[RawModelMetadata]:
    field_names = (
        {f.name for f in fields(RawModelMetadata)} - CONVERTED - {"model", "site"}
    )
    return [
        RawModelMetadata(
            **{_to_snake(k): v for k, v in obj.items() if _to_snake(k) in field_names},
            model=_create_model_object(obj["model"]),
            measurement_date=datetime.date.fromisoformat(obj["measurementDate"]),
            created_at=_parse_datetime(obj["createdAt"]),
            updated_at=_parse_datetime(obj["updatedAt"]),
            size=int(obj["size"]),
            uuid=UUID(obj["uuid"]),
            site=_create_site_object(obj["site"]),
        )
        for obj in res
    ]


def _create_model_object(metadata: dict) -> Model:
    return Model(
        model_id=metadata["id"],
        name=metadata["humanReadableName"],
        optimum_order=int(metadata["optimumOrder"]),
        source_model_id=metadata["sourceModelId"],
        forecast_start=int(metadata["forecastStart"])
        if metadata["forecastStart"] is not None
        else None,
        forecast_end=int(metadata["forecastEnd"])
        if metadata["forecastEnd"] is not None
        else None,
    )


def _create_site_object(metadata: dict) -> Site:
    return Site(
        id=metadata["id"],
        human_readable_name=metadata["humanReadableName"],
        station_name=metadata["stationName"],
        latitude=metadata["latitude"],
        longitude=metadata["longitude"],
        altitude=metadata["altitude"],
        dvas_id=metadata["dvasId"],
        actris_id=metadata["actrisId"],
        country=metadata["country"],
        country_code=metadata["countryCode"],
        country_subdivision_code=metadata["countrySubdivisionCode"],
        type=metadata["type"],
        gaw=metadata["gaw"],
    )


def _create_instrument_object(metadata: dict) -> Instrument:
    return Instrument(
        instrument_id=metadata.get("instrumentId"),  # not in api/files/:uuid
        model=metadata["model"],
        type=metadata["type"],
        uuid=UUID(metadata["uuid"]),
        pid=metadata["pid"],
        owners=metadata["owners"],
        serial_number=metadata["serialNumber"],
        name=metadata["name"],
    )


def _to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _make_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(total=10, backoff_factor=0.1, status_forcelist=[524])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _parse_datetime(dt: str) -> datetime.datetime:
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ")


def _check_params(params: dict, ignore: tuple = ()) -> None:
    if sum(1 for key, value in params.items() if key not in ignore and value) == 0:
        raise TypeError("At least one of the parameters must be set.")
