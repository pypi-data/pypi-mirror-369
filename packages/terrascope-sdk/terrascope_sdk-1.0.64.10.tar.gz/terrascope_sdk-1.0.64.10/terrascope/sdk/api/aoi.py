from __future__ import annotations

# ^^ postpones type checking, evaluation of annotations - does on run time NOT on import
from typing import List

from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.aoi_collection_pb2 import AOICollectionCreateRequest, AOICollectionCloneRequest, \
    AOICollectionGetRequest, AOIInfo, AOICollectionAddRequest, \
    AOICollectionRemoveRequest, AOICollection
from terrascope_api.models.aoi_pb2 import AOIUploadRequest, AOIGetRequest, AOIInput, \
    AOICreateRequest, AOIVersion, AOITransaction
from terrascope_api.models.aoi_version_pb2 import AOIField
from terrascope_api.models.aoi_version_pb2 import AOIVersionListRequest, AOIVersionCreateRequest, AOIVersionGetRequest
from terrascope_api.models.common_models_pb2 import Pagination


class APIAOI:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def upload(self, aoi_collection_id: str, file_path: str) -> AOITransaction:
        """
        Upload new AOIs to the system by passing in the raw bytes. Acceptable file formats are .zip (i.e. shapefile),
        geojson, kml, kmz, and wkt. The aoi_id and aoi_version of the created AOIs are returned. This call is
        asynchronous. It will return a aoi_upload_transaction_id that can be used to check the state of the upload.

        :param aoi_collection_id: The collection ID to upload AOIs to.
        :param file_path: File path to your aois
        :return: list of AOI identifiers
        """
        response = await self.__client.api.aoi.upload(self.__get_bytes_iterator(file_name=file_path,
                                                                                aoi_collection_id=aoi_collection_id))

        return response.aoi_transaction

    @staticmethod
    async def __get_bytes_iterator(file_name: str, aoi_collection_id: str):
        eof = False
        with open(file_name, 'rb') as f:
            while not eof:
                chunk = f.read(1024 * 1024)
                if chunk:
                    # Yield the new chunk of the file for the latest bytes
                    yield AOIUploadRequest(aoi_collection_id=aoi_collection_id, chunk=chunk)
                else:
                    # No more to read. End iteration.
                    eof = True

    async def create(self, aoi_collection_id: str,
                     aoi_inputs: List[AOIInput]) -> List:
        """
        Create a new AOI in the system by passing in the required components. Pass in an optional aoi_id to act
        as the parent and create an updated version of the AOI, which will copy fields from the parent unless explicitly
        overridden by the input parameters. The aoi_id and aoi_version of the created AOI are returned. This endpoint
        is currently limited to 100 AOIs or less. If you would like to upload more, refer to aoi.upload.

        :param aoi_inputs: AOIInput Object
        :param aoi_collection_id: The collection to create the AOI

        :return: aoi_identifiers: List
        """
        request = AOICreateRequest(
            aoi_collection_id=aoi_collection_id,
            aoi_inputs=aoi_inputs
        )
        response = await self.__client.api.aoi.create(request)
        return response.aoi_identifiers

    async def get(self, ids: List, verbose: bool = False) -> List[AOIVersion]:
        """
        Get the metadata about the specified AOIs. Setting the verbose flag will also include the bytes
        in wkt format describing the geometry.

        :param ids:
        :param verbose:
        :return: List[AOIVersion]
        """
        request = AOIGetRequest(
            aoi_ids=ids,
            verbose=verbose
        )
        response = await self.__client.api.aoi.get(request)
        return response.aoi_versions

    async def delete(self):
        pass


class APIAOITransaction:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client


class APIAOIVersion:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, aoi_id: str, aoi_modification_input: AOIInput) -> int:
        """
        Create a new aoi_version that is tied to the original aoi by reference of the aoi_id. After specifying the
        aoi modifications, the original is copied and modified. Further, aoi_versions are immutable.
        :param aoi_id:
        :param aoi_modification_input:
        :return: aoi_version_id: the uint32 version id
        """
        request = AOIVersionCreateRequest(
            aoi_id=aoi_id,
            aoi_modification_input=aoi_modification_input
        )
        response = await self.__client.api.aoi_version.create(request)
        return response.aoi_version_id

    async def get(self, aoi_version_ids: List[int], aoi_fields: List[AOIField]) -> List[AOIVersion]:
        # Problem is with List[AOIField] --- didn't like list of enums
        # added import annotations
        # Python version issue?
        # Either passing in not AOIField
        # async def get(self, aoi_version_ids: List[int], aoi_fields: List[int]) -> List[AOIVersion]:
        # async def get(self, aoi_version_ids: List[int], aoi_fields: List[AOIField]) -> List[AOIVersion]:
        """
        Get the actual AOI details specified by the provided version. Additionally, choose which metadata fields
        should be returned. A list of aoi_collections that they aoi_version is a part of is also returned.
        :param aoi_version_ids:
        :param aoi_fields:
        :return: List[AOIVersion]
        """
        request = AOIVersionGetRequest(
            ids=aoi_version_ids,
            aoi_fields=aoi_fields
        )
        response = await self.__client.api.aoi_version.get(request)
        return response.aoi_versions

    async def list(self, **kwargs) -> List[AOIVersion]:
        """
        List the available aois, including on the latest versions by default that match the specific filters.
        Additional options include the ability to list out all fields of the aoi_version
        by setting the verbose flag to True.

        :param kwargs
            - geom_wkt: str
            - category: str
            - tags: List
            - search_text: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - aoi_fields: AOIField
            - pagination: Pagination
            - verbose: bool

        :return:
        """
        fragments = []
        if 'pagination' not in kwargs.keys():
            fragments.append(AOIVersionListRequest(pagination=Pagination(
                page_token="1",
                page_size=1000,
                next_page_token="2"
            )))

        for key in kwargs.keys():
            if key == 'geom_wkt':
                fragments.append(AOIVersionListRequest(geom_wkt=kwargs[key]))
            if key == 'category':
                fragments.append(AOIVersionListRequest(category=kwargs[key]))
            if key == 'tags':
                fragments.append(AOIVersionListRequest(tags=kwargs[key]))
            if key == 'search_text':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                fragments.append(AOIVersionListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                fragments.append(AOIVersionListRequest(max_created_on=max_created_on))
            if key == 'aoi_fields':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))
            if key == 'verbose':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))
            if key == 'pagination':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))

        request = AOIVersionListRequest()
        for param in fragments:
            request.MergeFrom(param)

        response = await self.__client.api.aoi_version.list(request)
        return response.aoi_versions


class APIAOICollection:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, aoi_collection_name: str) -> AOICollection:
        """
        Description:
        API call to create a new AOI collection.

        :param aoi_collection_name: The human-readable name of the collection that will be associated with a UUID for
        further usages.
        :return: id
        """
        request = AOICollectionCreateRequest(
            name=aoi_collection_name
        )
        response = await self.__client.api.aoi_collection.create(
            request, timeout=self.__timeout
        )

        return response.aoi_collection

    async def get(self,
                  aoi_collection_id: str,
                  pagination: Pagination = None) -> List[AOIInfo]:
        """
        Get the metadata about the collection and the AOIs that belong to the specified AOI collection..
        Setting the verbose flag will also include the bytes in wkt format describing the geometry.
        :param pagination:
        :param aoi_collection_id: the aoi collection id

        :return: List[AOIInfo]
        """

        request = AOICollectionGetRequest(
            id=aoi_collection_id
        )
        response = await self.__client.api.aoi_collection.get(request, timeout=self.__timeout)
        return response.aoi_info

    async def list(self, **kwargs):
        """

        :param kwargs:
            - min_created_on: Datetime
            - max_created_on: Datetime
            - search_text: str
            - pagination: Pagination
        :return:
        """
        fragments = []
        if 'pagination' not in kwargs.keys():
            fragments.append(AOIVersionListRequest(pagination=Pagination(
                page_token="1",
                page_size=1000,
                next_page_token="2"
            )))
        for key in kwargs.keys():
            if key == 'search_text':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                fragments.append(AOIVersionListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                fragments.append(AOIVersionListRequest(max_created_on=max_created_on))
            if key == 'pagination':
                fragments.append(AOIVersionListRequest(search_text=kwargs[key]))
        request = AOIVersionListRequest()
        for fragment in fragments:
            request.MergeFrom(fragment)
        response = await self.__client.api.aoi_version.list(request)
        return response

    async def add(self, id: str, aoi_version_ids: List):
        """
        Cannot add to a "locked" collection.
        :param id: The AOI Collection id to add aoi versions to.
        :param aoi_version_ids: The version IDs of to be added to the aoi collection
        :return: Empty
        """
        request = AOICollectionAddRequest(
            id=id,
            aoi_version_ids=aoi_version_ids
        )
        await self.__client.api.aoi_collection.add(request, timeout=self.__timeout)

    async def remove(self, aoi_collection_id: str, aoi_version_ids: List):
        """
        Cannot remove from a "locked" collection.
        :param aoi_collection_id:
        :param aoi_version_ids:
        :return:
        """
        request = AOICollectionRemoveRequest(
            id=aoi_collection_id,
            aoi_version_ids=aoi_version_ids
        )
        await self.__client.api.aoi_collection.remove(request, timeout=self.__timeout)

    async def delete(self, aoi_collection_ids: List):
        pass

    async def clone(self, id: str, name: str) -> str:
        """
        Description
        This will let you clone an entire AOI collection.

        :param id: The aoi collection id to clone
        :param name: The new name for the cloned cloned collection
        :return: id: str
        """
        request = AOICollectionCloneRequest(
            id=id,
            name=name
        )
        response = await self.__client.api.aoi_collection.cone(request, timeout=self.__timeout)
        return response.aoi_collection_id


class AOIInputBuilder:
    @staticmethod
    def build(**kwargs) -> AOIInput:
        aoi_input = AOIInput()
        if 'aoi_id' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(aoi_id=kwargs['aoi_id']))
        if 'geom_wkt' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(geom_wkt=kwargs['geom_wkt']))
        if 'name' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(name=kwargs['name']))
        if 'category' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(category=kwargs['category']))
        if 'type' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(type=kwargs['type']))
        if 'tags' in kwargs.keys():
            aoi_input.MergeFrom(AOIInput(tags=kwargs['tags']))
        if 'attributes' in kwargs.keys():
            attributes = Struct()
            attributes.update(kwargs['attributes'])
            aoi_input.MergeFrom(AOIInput(attributes=attributes))

        return aoi_input
