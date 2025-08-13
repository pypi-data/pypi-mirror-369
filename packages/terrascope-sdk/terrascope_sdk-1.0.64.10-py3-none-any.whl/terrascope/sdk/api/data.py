from typing import List

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.data_source_pb2 import DataSourceGetRequest, DataSourceListRequest, DataSource
from terrascope_api.models.data_type_pb2 import DataTypeGetRequest, DataTypeListRequest, DataType, DataTypeCreateRequest


class APIDataSource:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def get(self, ids: List[str]) -> List[DataSource]:
        """
        Retrieves all the details about the specified data source.
        :param ids:
        :return: List[DataSource]
        """
        request = DataSourceGetRequest(
            ids=ids
        )
        response = await self.__client.api.data_source.get(request, timeout=self.__timeout)
        return response.data_sources

    async def list(self, **kwargs) -> List[DataSource]:
        """
        List all available data sources that the user has access to.
        :param kwargs:
            - search_text: str
        :return: List[DataSource]
        """
        message_fragments = []
        for kwarg in kwargs.keys():
            if 'search_text' == kwarg:
                message_fragments.append(DataSourceListRequest(
                    search_text=kwargs[kwarg]
                ))
        request = DataSourceListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)

        response = await self.__client.api.data_source.list(request, timeout=self.__timeout)
        return response.data_sources


class APIDataType:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, name: str, description: str, schema: str, data_source_ids: List,
                     sensor_type: str) -> DataType:
        """

        :param name:
        :param description:
        :param schema:
        :param sensor_type:
        :return:
        """
        request = DataTypeCreateRequest(
            name=name,
            description=description,
            schema=schema,
            sensor_type=sensor_type
        )
        response = await self.__client.api.data_type.create(request)
        return response.data_type

    async def get(self, names: List[str]) -> List[DataType]:
        """
        Gets a data type that the user has access to.

        :param ids: These are the name fields for the data source
        :return: List[DataType]
        """
        request = DataTypeGetRequest(
            names=names
        )
        response = await self.__client.api.data_type.get(request, timeout=self.__timeout)
        return response.data_types

    async def list(self, **kwargs) -> List[DataType]:
        """
        List all registered data_types.

        :param kwargs:
            - search_text: str
        :return: List[DataType]
        """
        message_fragments = []
        for kwarg in kwargs.keys():
            if 'search_text' == kwarg:
                message_fragments.append(DataTypeListRequest(
                    search_text=kwargs[kwarg]
                ))
        request = DataTypeListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)

        response = await self.__client.api.data_type.list(request, timeout=self.__timeout)
        return response.data_types
