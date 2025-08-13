from datetime import datetime
from typing import List

from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.algorithm_computation_pb2 import AlgorithmComputationGetRequest, \
    AlgorithmComputationCreateRequest, AlgorithmComputationRunRequest, AlgorithmComputation
from terrascope_api.models.algorithm_config_pb2 import AlgorithmConfig as AlgorithmConfig, \
    AlgorithmConfigGetRequest, AlgorithmConfigDeleteRequest, AlgorithmConfigCreateRequest, AlgorithmConfigUpdateRequest, \
    AlgorithmConfigDeprecateRequest, AlgorithmConfigDeactivateRequest, AlgorithmConfigListRequest
from terrascope_api.models.algorithm_pb2 import Algorithm, AlgorithmGetRequest, \
    AlgorithmUpdateRequest, AlgorithmCreateRequest, AlgorithmListRequest
from terrascope_api.models.algorithm_version_pb2 import AlgorithmVersion as AlgorithmVersion, \
    AlgorithmVersionGetRequest, \
    AlgorithmVersionCreateRequest, AlgorithmVersionListRequest, AlgorithmVersionDeprecateRequest, \
    AlgorithmVersionDeactivateRequest
from terrascope_api.models.common_models_pb2 import Pagination

from terrascope.sdk.builder.algorithm import AlgorithmManifest, AlgorithmConfiguration
from terrascope.sdk.tools.sdk_support import SDKSupport


class APIAlgorithm:

    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, name: str, display_name: str, author: str) -> Algorithm:
        """
        Description:
        Create a top level algorithm object. This object is lightweight and is used to connect all versions of an
        algorithm together. Once an algo has been created, an algo_version must be created using a manifest.
        Next an algo_config may be created to specify a particular configuration of an algorithm version, which can
        be used in an algo_computation.

        :return Algorithm
        """
        request = AlgorithmCreateRequest(
            name=name,
            display_name=display_name,
            author=author
        )
        response = await self.__client.api.algorithm.create(request, timeout=self.__timeout)
        return response.algorithm

    async def update(self, algorithms: List):
        """
        Update the mutable fields of a top level algorithm. This should be done rarely and with caution as it will
        affect all algorithm_versions, and algorithm_configs associated with this algorithm.

        :param algorithms: List[terrascope_api.models.algorithm_pb2.Algorithm]
        :return: EmptyResponse
        """

        request = AlgorithmUpdateRequest(
            algorithms=algorithms
        )
        await self.__client.api.algorithm.update(request, timeout=self.__timeout)

    async def get(self, algorithm_ids: List, pagination: Pagination = None) -> List[Algorithm]:
        """
        Retrieve the metadata of a particular algorithm.

        :param pagination:
        :param algorithm_ids:
        :return: List[Algorithm]
        """
        fetch_all = False
        if pagination is None:
            pagination = Pagination(
                page_size=100
            )
            fetch_all = True
        request = AlgorithmGetRequest(
            ids=algorithm_ids,
            pagination=pagination
        )

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.algorithm.get,
                                                                    timeout=self.__timeout)
        else:
            responses = [await self.__client.api.algorithm.get(request)]
        algorithms = []
        for response in responses:
            algorithms.extend(response.algorithms)
        return algorithms

    async def list(self, **kwargs) -> List[Algorithm]:
        """
        Retrieve the metadata for all algos that this user has access to and that match the provided search filters,
        if any.
        :param kwargs:
            -Optional Params
            - search_text: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - pagination: Pagination
        :return: List[Algorithm]
        """
        parameters = ['search_text', 'min_created_on', 'max_created_on', 'pagination', 'raw_response']
        for key in kwargs.keys():
            assert key in parameters

        message_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            message_fragments.append((AlgorithmListRequest(pagination=Pagination(
                page_size=1000
            ))))
            fetch_all = True

        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False

        for key in kwargs.keys():
            if key == 'search_text':
                message_fragments.append(AlgorithmListRequest(search_text=kwargs[key]))
            if key == 'min_created_on':
                assert isinstance(kwargs[key], datetime)
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                assert isinstance(kwargs[key], datetime)
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmListRequest(max_created_on=max_created_on))
            if key == 'pagination':
                message_fragments.append(AlgorithmListRequest(pagination=kwargs[key]))

        request = AlgorithmListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.algorithm.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                return responses
            else:
                algorithms = []
                for response in responses:
                    algorithms.extend(response.algorithms)
                return algorithms
        else:
            response = await self.__client.api.algorithm.list(request, timeout=self.__timeout)
            if kwargs['raw_response']:
                return response
            else:
                return response.algorithms


class APIAlgorithmVersion:

    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, algorithm_id: str, algorithm_manifest: AlgorithmManifest) -> AlgorithmVersion:
        """
        Given a top level algorithm, create a new version. Once an algorithm version has been created, it is immutable. Any changes require a new
        version to be created. Any semantically correct version supplied as part of the algorithm_manifest will be
        considered value and assigned to this algorithm_version. New versions will be required to be semantically
        greater than this version.

        Parameters
        :param algorithm_id:
        :param algorithm_manifest:
        :return: AlgorithmVersion
        """
        request = AlgorithmVersionCreateRequest(
            algorithm_id=algorithm_id,
            manifest_struct=algorithm_manifest.get()
        )
        response = await self.__client.api.algorithm_version.create(request, timeout=self.__timeout)
        return response.algorithm_version

    async def get(self, algorithm_version_ids: List, pagination: Pagination = None) -> List[AlgorithmVersion]:
        """
        Description:

        Get the details for a specific algorithm_version. By default it does not include the algorithm_manifest.
        Setting include_manifest to true, will also include the manifest in the response for each requested
        algorithm_version.

        :param pagination:
        :param algorithm_version_ids: The algorithm version ids to use to look up the sem versions associated
               with those algos
        :return: List[AlgorithmVersion]
        """
        if pagination is None:
            pagination = Pagination(
                page_size=1000
            )
        request = AlgorithmVersionGetRequest(
            ids=algorithm_version_ids,
            pagination=pagination
        )
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.algorithm_version.get,
                                                                timeout=self.__timeout)
        algorithm_versions = []
        for response in responses:
            algorithm_versions.extend(response.algorithm_versions)
        return algorithm_versions

    async def list(self, **kwargs) -> List[AlgorithmVersion]:
        """
        List all the algorithm versions that the user has access to.

        **Search text** will be applied to the entire manifest returning all algorithm_versions
        whose manifest contains the search text.

        **Tags** will be matched exactly with the
        tags on the manifest.

        If **include_all_versions** is set to true, all prior versions of an algorithm including deprecated
        algorithm versions will be returned, as well. If include_manifest is set to true, the corresponding manifest
        of each algorithm_version will also be returned.

        By **default**, this method only returns the semantically latest version of each algorithm that has not been
        deprecated, It does not include manifests in the response.

        :param kwargs
            - algorithm_id: str
            - search_text: str
            - tag: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - include_all_versions: bool

        :return: List[AlgorithmVersion]
        """

        message_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            message_fragments.append((AlgorithmVersionListRequest(pagination=Pagination(
                page_size=1000
            ))))
            fetch_all = True

        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False


        for key in kwargs.keys():
            if key == 'algorithm_id':
                message_fragments.append(AlgorithmVersionListRequest(algorithm_id=kwargs[key]))
            if key == 'search_text':
                message_fragments.append(AlgorithmVersionListRequest(search_text=kwargs[key]))
            if key == 'min_created_on':
                assert isinstance(kwargs[key], datetime)
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmVersionListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                assert isinstance(kwargs[key], datetime)
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmVersionListRequest(max_created_on=max_created_on))
            if key == 'include_all_versions':
                message_fragments.append(AlgorithmVersionListRequest(include_all_versions=kwargs[key]))
            if key == 'tag':
                message_fragments.append(AlgorithmVersionListRequest(tag=kwargs[key]))
            if key == 'pagination':
                message_fragments.append(AlgorithmVersionListRequest(pagination=kwargs[key]))

        request = AlgorithmVersionListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)
        MessageToDict(request)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.algorithm_version.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                return responses
            else:
                algorithm_versions = []
                for response in responses:
                    algorithm_versions.extend(response.algorithm_versions)
                return algorithm_versions
        else:
            response = await self.__client.api.algorithm_version.list(request, timeout=self.__timeout)
            if kwargs['raw_response']:
                return response
            else:
                return response.algorithm_versions

    async def deprecate(self, ids: List):
        """
        Deprecate the specific version of this algorithm. Deprecated algorithms can still be searched for, metadata can
        be retrieved, and can still be used to create new algorithm_configs which can be used as part of
        algorithm_computations, but they are no longer actively supported. All algorithm_configs created from this
        algorithm_version are also deprecated, but can still be used in new algorithm_computations.

        :param ids: List[str]
        :return: EmptyResponse
        """
        request = AlgorithmVersionDeprecateRequest(
            ids=ids
        )
        await self.__client.api.algorithm_version.deprecate(request, timeout=self.__timeout)

    async def deactivate(self, algorithm_version_ids: List):
        """
        Deactivate the specific version of this algorithm. Metadata for deactivated algorithms can still be retrieved
        directly, but they will no longer show up in search results from the list endpoint.Deactivated
        algorithm_versions cannot be used to create new algorithm_configs. All algorithm_configs created from this
        algorithm_version are also deactivated and can no longer be used to create new algorithm_computations.
        Existing computations that are already using algorithm_configs created from this algorithm_version will still
        continue to run.

        :param algorithm_version_ids:
        :return:
        """
        request = AlgorithmVersionDeactivateRequest(
            ids=algorithm_version_ids
        )
        await self.__client.api.algorithm_version.deactivate(request, timeout=self.__timeout)


class APIAlgorithmConfig:

    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self,
                     algorithm_version_id: str,
                     name: str,
                     description: str,
                     algorithm_config: AlgorithmConfiguration) -> AlgorithmConfig:
        """
        Creates a configuration of the specified algorithm version, including concrete values for all of the algorithm
        parameters. This configuration is stored in the system and the algorithm_config is returned to the user.

        :param algorithm_config:
        :param algorithm_version_id:
        :param name:
        :param description:
        :return: AlgorithmConfig
        """
        request = AlgorithmConfigCreateRequest(
            algorithm_version_id=algorithm_version_id,
            name=name,
            description=description,
            params=algorithm_config.get()
        )
        response = await self.__client.api.algorithm_config.create(request, timeout=self.__timeout)
        return response.algorithm_config

    async def update(self, algorithm_config_id: str, algorithm_config: AlgorithmConfiguration):
        """
        Update details of an algorithm_config, so long as it has not been locked. Once the algorithm_config is used
        in a computation, it is permanently locked and the specific parameter values can no longer be updated.

        :param algorithm_config_id:
        :param algorithm_config:
        :return:
        """
        request = AlgorithmConfigUpdateRequest(
            id=algorithm_config_id,
            algorithm_config=algorithm_config.get()
        )
        await self.__client.api.algorithm_config.update(request, timeout=self.__timeout)

    async def get(self, ids: List, pagination: Pagination = None) -> List[AlgorithmConfig]:
        """
        Retrieve the metadata of a particular algorithm configuration.

        :param ids:
        :param pagination:
        :return: List[AlgorithmConfig]
        """
        if pagination is not None:
            pagination = Pagination(
                page_size=1000
            )
        request = AlgorithmConfigGetRequest(
            ids=ids,
            pagination=pagination
        )
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.algorithm_config.get,
                                                                timeout=self.__timeout)
        algorithm_configs = []
        for response in responses:
            algorithm_configs.extend(response.algorithm_configs)
        return algorithm_configs

    async def list(self, **kwargs) -> List[AlgorithmConfig]:
        """
        Retrieve the metadata for all algorithm configurations that this user has access to and that match the provided
        search filters. By default, deactivated algorithm_configs are not returned. Setting include_deactivated to true
        will also return any algorithm_configs that had been deactivated.

        :param kwargs:
            * algorithm_id: str,
            * algorithm_version_id: str,
            * search_text: str,
            * min_created_on: google.protobuf.Timestamp,
            * max_created_on: google.protobuf.Timestamp,
            * include_deactivated: bool,
            * pagination: Pagination

        :return: List[AlgorithmConfig]
        """
        message_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            message_fragments.append(AlgorithmConfigListRequest(
                pagination=Pagination(
                    page_size=1000
                )))
            fetch_all = True
        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False

        if 'include_deactivated' not in kwargs.keys():
            message_fragments.append(AlgorithmConfigListRequest(
                include_deactivated=False
            ))

        for key in kwargs.keys():
            if key == 'search_text':
                message_fragments.append(AlgorithmConfigListRequest(
                    search_text=kwargs[key]
                ))
            if key == 'algorithm_id':
                message_fragments.append(AlgorithmConfigListRequest(
                    algorithm_id=kwargs[key]
                ))
            if key == 'algorithm_version_id':
                message_fragments.append(AlgorithmConfigListRequest(
                    algorithm_version_id=kwargs[key]
                ))
            if key == 'min_created_on':
                assert isinstance(kwargs[key], datetime)
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmListRequest(creation_date_min=min_created_on))
            if key == 'max_created_on':
                assert isinstance(kwargs[key], datetime)
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                message_fragments.append(AlgorithmListRequest(creation_date_max=max_created_on))
            if key == 'include_deactivated':
                message_fragments.append(AlgorithmConfigListRequest(
                    include_deactivated=kwargs[key]
                ))
            if key == 'pagination':
                message_fragments.append(AlgorithmConfigListRequest(
                    pagination=kwargs[key]
                ))
        request = AlgorithmConfigListRequest()
        for fragment in message_fragments:
            request.MergeFrom(fragment)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.algorithm_config.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                algorithm_configs = []
                for response in responses:
                    algorithm_configs.extend(response.algorithm_configs)
                return algorithm_configs
            else:
                return responses
        else:
            response = await self.__client.api.algorithm_config.list(request, timeout=self.__timeout)
            if kwargs['raw_response']:
                return response
            else:
                return response.algorithm_configs

    async def deprecate(self, algorithm_config_ids: List):
        """
        Deprecate the specific configuration of an algorithm_version. Deprecated algorithm_configs can still be
        searched for, metadata can be retrieved, and can still be used in new algorithm_computations, but they are no
        longer actively supported.

        :param algorithm_config_ids:
        :return:
        """
        request = AlgorithmConfigDeprecateRequest(
            ids=algorithm_config_ids
        )
        await self.__client.api.algorithm_config.deprecate(request, timeout=self.__timeout)

    async def deactivate(self, algorithm_config_ids: List):
        """
        Deactivate the specific configuration of an algorithm_version. Deactivated algorithm_configs will no longer
        show up in searches, but metadata can still be retrieved for deactivated algorithm_configs via the get endpoint.
        Deactivated algorithm_configs cannot be used in any new algorithm_computations, but existing
        algorithm_computations will continue to function properly.

        :param algorithm_config_ids:
        :return:
        """
        request = AlgorithmConfigDeactivateRequest(
            ids=algorithm_config_ids
        )
        await self.__client.api.algorithm_config.deactivate(request, timeout=self.__timeout)

    async def delete(self, algorithm_config_ids: List):
        """
        Delete the specified algorithm_config, if and only if it has not been used to create an algorithm_computation.
        Once an algorithm_config has been used to create an algorithm_computation it can never be deleted.
        The user must have permission to access the specified algorithm.

        :param algorithm_config_ids:
        :return: EmptyResponse
        """
        request = AlgorithmConfigDeleteRequest(
            ids=algorithm_config_ids
        )
        await self.__client.api.algorithm_config.delete(request, timeout=self.__timeout)


class APIAlgorithmComputation:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, algorithm_config_id: str, aoi_collection_id: str, toi_id: str) -> AlgorithmComputation:
        """
        Create the runnable component in the system, by specifiying the algorithm to be run, the set of AOIs to be run
        on, and the TOI to specify the recurrence. The algorithm_computation_id is returned so that it can be run.
        Note that until an algorithm_computation has been run, its underlying .resources are NOT locked and
        therefore can be changed.
        :param algorithm_config_id:
        :param aoi_collection_id:
        :param toi_id:
        :return: algorithm_computation_id
        """
        request = AlgorithmComputationCreateRequest(
            algorithm_config_id=algorithm_config_id,
            aoi_collection_id=aoi_collection_id,
            toi_id=toi_id
        )
        response = await self.__client.api.algorithm_computation.create(request)
        return response.algorithm_computation

    async def run(self, algorithm_computation_ids: List) -> int:
        """
        The first time this endpoint is called, the system initiates the running of the provided
        algorithm_computation_id. This causes credits to be place in pending status and eventually consumed when
        the computation completes. Credits are consumed as each result is produced. Once an algorithm_computation
        has been run, it is considered locked and cannot be changed, as are its constituents.

        :param algorithm_computation_ids:
        :return
        """
        request = AlgorithmComputationRunRequest(
            ids=algorithm_computation_ids
        )
        await self.__client.api.algorithm_computation.run(request)

    async def get(self, computation_ids: list, pagination: Pagination = None) -> List:
        """
        Description:
        This wrapper will get the status of your computations.

        :param pagination:
        :param computation_ids: The list of computations you want to get status for
        :return: List[AlgorithmComputation]
        """

        request = AlgorithmComputationGetRequest(
            ids=computation_ids,
            pagination=pagination)
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.algorithm_computation.get,
                                                                timeout=self.__timeout)
        algorithm_computations = []
        for response in responses:
            algorithm_computations.extend(response.algorithm_computations)
        return algorithm_computations

    async def update(self):
        pass

    async def list(self, **kwargs):
        # message_fragments = []
        # if 'pagination' not in kwargs.keys():
        #     message_fragments.append(AlgorithmComputationListRequest(
        #         pagination=Pagination(
        #             page_size=100
        #         )))
        # if 'include_deactivated' not in kwargs.keys():
        #     message_fragments.append(AlgorithmComputationListRequest(
        #         include_deactivated=False
        #     ))
        #
        # for key in kwargs.keys():
        #     if key == 'search_text':
        #         message_fragments.append(AlgorithmComputationListRequest(
        #             search_text=kwargs[key]
        #         ))
        #     if key == 'algorithm_id':
        #         message_fragments.append(AlgorithmComputationListRequest(
        #             algorithm_id=kwargs[key]
        #         ))
        #     if key == 'algorithm_version_id':
        #         message_fragments.append(AlgorithmComputationListRequest(
        #             algorithm_version_id=kwargs[key]
        #         ))
        #     if key == 'min_created_on':
        #         assert isinstance(kwargs[key], datetime)
        #         min_created_on = Timestamp()
        #         min_created_on.FromDatetime(kwargs[key])
        #         message_fragments.append(AlgorithmComputationListRequest(creation_date_min=min_created_on))
        #     if key == 'max_created_on':
        #         assert isinstance(kwargs[key], datetime)
        #         max_created_on = Timestamp()
        #         max_created_on.FromDatetime(kwargs[key])
        #         message_fragments.append(AlgorithmComputationListRequest(creation_date_max=max_created_on))
        #     if key == 'include_deactivated':
        #         message_fragments.append(AlgorithmComputationListRequest(
        #             include_deactivated=kwargs[key]
        #         ))
        #     if key == 'pagination':
        #         message_fragments.append(AlgorithmComputationListRequest(
        #             pagination=kwargs[key]
        #         ))
        # request = AlgorithmComputationListRequest()
        # for fragment in message_fragments:
        #     request.MergeFrom(fragment)
        #
        # sdk_support = SDKSupport()
        # responses = await sdk_support.get_all_paginated_objects(request,
        #                                                         api_function=self.__client.api.algorithm_computation.list,
        #                                                         timeout=self.__timeout)
        # algorithm_computations = []
        # for response in responses:
        #     algorithm_computations.extend(response.algorithm_computations)
        # return algorithm_computations
        pass

    async def delete(self):
        pass

    async def pause(self):
        pass

    async def resume(self):
        pass

    async def history(self):
        pass
