from google.protobuf.struct_pb2 import Struct

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.filter_pb2 import (
    Filter, FilterCreateRequest, FilterDeleteRequest, FilterListRequest, FilterMappingCreateRequest
)
from terrascope_api.models.project_filter_pb2 import (
    ProjectFilter, ProjectFilterMappingCreateRequest
)
from terrascope.sdk.tools.sdk_support import SDKSupport

class APIFilter:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client
        self.sdk_support = SDKSupport()

    async def create(self, expression: str, filter_language: str, data_type: str = None, name: str = None,
                     description: str = None, metadata: Struct = None) -> str:
        request = FilterCreateRequest(
            expression=expression,
            data_type=data_type,
            name=name,
            description=description,
            filter_language=filter_language,
            metadata=metadata
        )
        response = await self.__client.api.filter.create(request)
        return response.filter_id

    async def delete(self, filter_ids: list[str]) -> None:
        request = FilterDeleteRequest(
            ids=filter_ids,
        )
        await self.__client.api.filter.delete(request)

    async def list(self, data_types: list[str], search_text: str) -> list[Filter]:
        request = FilterListRequest(
            data_types=data_types,
            search_text=search_text
        )
        responses = await self.sdk_support.get_all_paginated_objects(request,
                                                                     api_function=self.__client.api.filter.list,
                                                                     timeout=self.__timeout)
        filters = []
        for response in responses:
            filters.extend(response.filters)
        return filters

    async def create_mapping(self, computation_id: str, filter_id: str) -> None:
        request = FilterMappingCreateRequest(
            computation_id=computation_id,
            filter_id=filter_id
        )
        await self.__client.api.filter.create_mapping(request)


class APIProjectFilter:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client
        self.sdk_support = SDKSupport()

    async def create_mapping(self, filter_id: str, analysis_config_id: str, node_name: str, project_id: str,
                             input_filter: bool) -> None:
        request = ProjectFilterMappingCreateRequest(
            project_filters=[
                ProjectFilter(
                    filter=Filter(id=filter_id),
                    analysis_config_id=analysis_config_id,
                    node_name=node_name,
                    project_id=project_id,
                    input_filter=input_filter
                )
            ]
        )
        await self.__client.api.project_filter.create_mapping(request)
