from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.struct_pb2 import Struct

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.tasking_order_pb2 import (
    TaskingOrderCreateRequest, TaskingOrder, TimeRange, TaskingOrderApproveRequest, TaskingOrderCancelRequest,
    TaskingOrderGetRequest, TaskingOrderListRequest
)
from terrascope_api.models.order_pb2 import OrderState
from terrascope.sdk.tools.sdk_support import SDKSupport

class APITaskingOrder:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client
        self.sdk_support = SDKSupport()

    async def create(self, data_source_id: str, product_spec_name: str, target_geom_wkb: bytes, start_ts: datetime,
                     end_ts: datetime, metadata: Struct = None) -> TaskingOrder:
        request = TaskingOrderCreateRequest(
            data_source_id=data_source_id,
            product_spec_name=product_spec_name,
            target_geom=target_geom_wkb,
            acq_window=TimeRange(
                start_utc=Timestamp(seconds=int(start_ts.replace(tzinfo=timezone.utc).timestamp())),
                finish_utc=Timestamp(seconds=int(end_ts.replace(tzinfo=timezone.utc).timestamp()))
            ),
            metadata=metadata
        )
        response = await self.__client.api.tasking_order.create(request)
        return response.order

    async def approve(self, tasking_order_id: str, comment: str) -> None:
        request = TaskingOrderApproveRequest(
            id=tasking_order_id,
            comment=comment
        )
        await self.__client.api.tasking_order.approve(request)

    async def cancel(self, tasking_order_id: str) -> None:
        request = TaskingOrderCancelRequest(
            id=tasking_order_id
        )
        await self.__client.api.tasking_order.cancel(request)

    async def get(self, tasking_order_id: str) -> TaskingOrder:
        request = TaskingOrderGetRequest(
            id=tasking_order_id
        )
        response = await self.__client.api.tasking_order.get(request)
        return response.order

    async def list(self, data_source_ids: list[str], states: list[OrderState], analysis_computation_ids: list[str],
                   algorithm_computation_ids: list[str]) -> list[TaskingOrder]:
        request = TaskingOrderListRequest(
            data_source_ids=data_source_ids,
            states=states if states else [],
            analysis_computation_ids=analysis_computation_ids,
            algorithm_computation_ids=algorithm_computation_ids
        )
        responses = await self.sdk_support.get_all_paginated_objects(request,
                                                                     api_function=self.__client.api.tasking_order.list,
                                                                     timeout=self.__timeout)
        tasking_orders = []
        for response in responses:
            tasking_orders.extend(response.orders)
        return tasking_orders
