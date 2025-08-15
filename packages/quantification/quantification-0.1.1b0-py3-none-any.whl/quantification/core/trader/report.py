import json
import gzip
from typing import TYPE_CHECKING

import requests
from pydantic import BaseModel

from ..logger import Record
from ..configure import config

if TYPE_CHECKING:
    from .base_order import Result
    from ..asset import BaseAsset


class AssetData(BaseModel):
    type: str
    name: str
    amount: float
    extra: dict

    @classmethod
    def from_asset(cls, asset: "BaseAsset", **kwargs) -> "AssetData":
        return cls(
            type=asset.type(),
            name=asset.__class__.class_name(),
            amount=asset.amount,
            extra={**asset.extra, **kwargs}
        )


class OrderResultData(BaseModel):
    order_type: str
    order_category: str
    order_asset: str
    order_extra: dict
    result_brought: list[AssetData]
    result_sold: list[AssetData]

    @classmethod
    def from_result(cls, result: "Result", **kwargs) -> "OrderResultData":
        return cls(
            order_type=result.order.type(),
            order_asset=str(result.order.asset),
            order_category=result.order.category,
            order_extra={**result.order.extra, **kwargs},
            result_brought=[AssetData.from_asset(i) for i in result.brought],
            result_sold=[AssetData.from_asset(i) for i in result.sold],
        )


class PeriodData(BaseModel):
    datetime: str
    liquidating_value: float

    logs: list[Record]
    portfolios: list[AssetData]
    transactions: list[OrderResultData]


class PointData(BaseModel):
    datetime: str
    value: float


class BenchmarkData(BaseModel):
    name: str
    init_value: float
    points: list[PointData]


class ReportData(BaseModel):
    title: str
    description: str
    base: float
    scale: float
    start_date: str
    end_date: str

    benchmark: BenchmarkData
    periods: list[PeriodData]

    def submit(self):
        url = f"{config.genesis_api}/back/report/"
        compressed = gzip.compress(json.dumps(self.model_dump_json(indent=2)).encode("utf-8"))

        print(f"Endpoint {url}")

        return requests.post(
            url=f"{config.genesis_api}/back/report/",
            files={'full_report': ('report.json.gz', compressed, 'application/gzip')},
            headers={"Authorization": f"Token {config.genesis_token}"}
        ).json()
