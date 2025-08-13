from typing import List

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.common_models_pb2 import Pagination
from terrascope_api.models.toi_pb2 import TOI, TOIDeleteRequest, TOIGetRequest, \
    TOICreateRequest, TOIListRequest


class APIToi:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, toi: TOI) -> TOI:
        """
        This will call the Create Time of Interest (toi) service and create a new TOI for usage in a computation.
        When defining a TOI please use an instance of a TOIBuilder

        :param toi: TOI - use TOIBuilder to build TOIs
        :return: (toi_id, toi_recurrence_ids)
        """

        request = TOICreateRequest(start_local=toi.start_local, finish_local=toi.finish_local,
                                   recurrences=toi.recurrences, exclude_dates=toi.exclude_dates,
                                   description=toi.description)

        response = await self.__client.api.toi.create(request, timeout=self.__timeout)
        return response.toi

    async def get(self, ids: List, page_size: int = 2) -> List[TOI]:
        """
        Retrieve the TOI for the specified toi_id. The user must have permission to access the specified TOI.

        :param ids:
        :param page_size:
        :return: List[TOI]
        """
        pagination = Pagination(
            page_token="1",
            page_size=page_size,
            next_page_token="2"
        )
        request = TOIGetRequest(
            ids=ids,
            # pagination=pagination
        )
        response = await self.__client.api.toi.get(request)
        return response.toi_objects

    async def list(self, **kwargs) -> List[TOI]:
        """
        Retrieves the TOI for all tois that the user has permissions for and that match the provided search filters.
        :param kwargs:
        :return: List[TOI]
        """
        message_fragments = []
        for kwarg in kwargs.keys():
            if 'search_text' == kwarg:
                message_fragments.append(TOIListRequest(
                    search_text=kwargs[kwarg]
                ))
        request = TOIListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)

        response = await self.__client.api.toi.list(request, timeout=self.__timeout)
        return response.toi_objects

    async def delete(self, ids: List):
        """
        Deletes a list of TOIs

        :param ids: list of toi_id uuids
        :return: EmptyResponse
        """

        request = TOIDeleteRequest(
            ids=ids
        )
        await self.__client.api.toi.delete_toi(request, timeout=self.__timeout)
