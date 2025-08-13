from typing import Optional

from shapely.geometry.base import BaseGeometry
from terrascope.sdk.tools.sdk_support import SDKSupport

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.order_pb2 import Order, OrderCreateRequest, Item, OrderApproveRequest, OrderCancelRequest, \
    OrderGetRequest, OrderListRequest, OrderState


class APIOrder:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client
        self.sdk_support = SDKSupport()

    async def create(self, data_source_id: str, product_spec_name: str,
                     scene_id: str,
                     clip_geom: Optional[BaseGeometry] = None,
                     metadata: Optional[dict] = None) -> Order:
        request = OrderCreateRequest(
            data_source_id=data_source_id,
            product_spec_name=product_spec_name,
            metadata=metadata,
            items=[
                Item(scene_id=scene_id,
                     target_geom=clip_geom.wkb if clip_geom is not None else None)
            ]
        )
        response = await self.__client.api.order.create(request)
        return response.order

    async def approve(self, order_id: str, comment: str) -> None:
        request = OrderApproveRequest(
            id=order_id,
            comment=comment
        )
        await self.__client.api.order.approve(request)

    async def cancel(self, order_id: str) -> None:
        request = OrderCancelRequest(
            id=order_id
        )
        await self.__client.api.order.cancel(request)

    async def get(self, order_id: str) -> Order:
        request = OrderGetRequest(
            id=order_id
        )
        response = await self.__client.api.order.get(request)
        return response.order

    async def list(self,
                   data_source_ids: list[str],
                   states: Optional[list[str]] = None,
                   analysis_computation_ids: Optional[list[str]] = None,
                   algorithm_computation_ids: Optional[list[str]] = None) -> list[Order]:
        ord_states = [OrderState.Value(s) for s in states] if states else []
        request = OrderListRequest(
            data_source_ids=data_source_ids,
            states=ord_states,
            analysis_computation_ids=analysis_computation_ids,
            algorithm_computation_ids=algorithm_computation_ids
        )
        responses = await self.sdk_support.get_all_paginated_objects(request,
                                                                     api_function=self.__client.api.order.list,
                                                                     timeout=self.__timeout)
        orders = []
        for response in responses:
            orders.extend(response.orders)
        return orders
