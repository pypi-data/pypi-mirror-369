from typing import List

from google.protobuf.timestamp_pb2 import Timestamp
from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.analysis_computation_pb2 import (
    AnalysisComputationCreateRequest, AnalysisComputationRunRequest, AnalysisComputation, AnalysisComputationGetRequest,
    AnalysisComputationListRequest
)
from terrascope_api.models.analysis_config_pb2 import (
    AnalysisConfigCreateRequest, AnalysisConfigGetRequest, AnalysisConfigListRequest, AnalysisConfigDeactivateRequest,
    AnalysisConfig
)
from terrascope_api.models.analysis_pb2 import (
    Analysis, AnalysisCreateRequest, AnalysisGetRequest, AnalysisListRequest
)
from terrascope_api.models.analysis_version_pb2 import (
    AnalysisVersionListRequest, AnalysisVersionGetRequest, AnalysisVersionCreateRequest, AnalysisVersion
)
from terrascope_api.models.common_models_pb2 import Pagination

from terrascope.sdk.builder.analysis import AnalysisManifest, AnalysisConfiguration
from terrascope.sdk.tools.sdk_support import SDKSupport


class APIAnalysis:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, name: str, author: str) -> Analysis:
        """
        Create a top level analysis object. This object is lightweight and is used to connect all versions of an
        analysis together. Once an analysis has been created, an analysis_version must be created using a manifest.
        Next an analysis_config may be created to specify a particular configuration of an analysis version,
        which can be used in an analysis_computation.
        :param name:
        :param author:
        :return: Analysis
        """

        request = AnalysisCreateRequest(
            name=name,
            author=author
        )
        response = await self.__client.api.analysis.create(request, timeout=self.__timeout)

        return response.analysis

    async def update(self, analysis_id: str, name: str = None, author: str = None):
        """
        Update the mutable fields of a top level analysis. This should be done rarely and with caution as it will
        affect all analysis_versions, and analysis_configs associated with this analysis.
        :return:
        """
        pass

    async def get(self, ids: List, pagination: Pagination = None) -> List[Analysis]:
        """
        Retrieve the metadata of a set of analyses.

        :param pagination:
        :param ids: List of analysis ids to get the metadata for.
        :return: List[Analysis]
        """
        if pagination is None:
            Pagination(
                page_size=1000,
            )
        request = AnalysisGetRequest(
            ids=ids,
            pagination=pagination
        )
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.analysis.get,
                                                                timeout=self.__timeout)
        analyses = []
        for response in responses:
            analyses.extend(response.analyses)
        return analyses

    async def list(self, **kwargs) -> List[Analysis]:
        """
        Retrieve the metadata for all analyses that this user has access to and that match the provided search filters,
        if any.

        Empty Arg list will list all available Analyses.

        :param kwargs
            - search_text: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - pagination: Pagination
        :return: List[Analysis]
        """
        request_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            request_fragments.append((AnalysisListRequest(pagination=Pagination(
                page_size=200
            ))))
            fetch_all = True

        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False

        for key in kwargs.keys():
            if key == 'search_text':
                assert isinstance(kwargs[key], str)
                request_fragments.append(AnalysisListRequest(search_text=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisListRequest(min_created_on=max_created_on))
            if key == 'pagination':
                request_fragments.append(AnalysisListRequest(pagination=kwargs[key]))

        request = AnalysisListRequest()
        for param in request_fragments:
            request.MergeFrom(param)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.analysis.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                return responses
            else:
                analyses = []
                for response in responses:
                    analyses.extend(response.analyses)

                return analyses
        else:
            response = await self.__client.api.analysis.list(request, timeout=self.__timeout)

            if kwargs['raw_response']:
                return response
            else:
                return response.analyses


class APIAnalysisVersion:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, analysis_id: str, analysis_manifest: AnalysisManifest) -> AnalysisVersion:
        """
        Given a top level analysis, create a new version. Once an analysis version has been created, it is immutable. Any changes require a new version to be
        created. The purpose of this is to either upgrade the structure of the Analysis DAG OR update the versions of
        the algorithms assigned to the Analysis.

        :return: AnalysisVersion
        """
        request = AnalysisVersionCreateRequest(
            analysis_id=analysis_id,
            analysis_manifest=analysis_manifest.get()
        )
        response = await self.__client.api.analysis_version.create(request, timeout=self.__timeout)
        return response.analysis_version

    async def get(self, ids: List,
                  include_manifest: bool = False,
                  include_algorithm_details: bool = False,
                  pagination: Pagination = None) -> List[AnalysisVersion]:
        """
        Get the details for a specific analysis_version. By default it does not include the analysis_manifest.
        Setting include_manifest to true, will also include the manifest in the response for each
        requested analysis_version.

        :param: pagination

        :return: List[AnalysisVersion]
        """
        if pagination is None:
            pagination = Pagination(
                page_size=1000
            )
        request = AnalysisVersionGetRequest(
            ids=ids,
            include_manifest=include_manifest,
            include_algorithm_details=include_algorithm_details,
            pagination=pagination
        )
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.analysis_version.get,
                                                                timeout=self.__timeout)
        analysis_versions = []
        for response in responses:
            analysis_versions.extend(response.analysis_versions)
        return analysis_versions

    async def list(self, **kwargs) -> List[AnalysisVersion]:
        """
        List all the analysis versions that the user has access to. Search text will be applied to the entire manifest
        returning all analysis_versions whose manifest contains the search text. Tags will be matched exactly with the
        tags on the manifest. By default, this method only returns the semantically latest version of each analysis that
        has not been deprecated, It does not include manifests in the response. If include_all_versions is set to true,
        all prior versions of an analysis including deprecated analysis versions will be returned, as well. If
        include_manifest is set to true, the corresponding manifest of each analysis_version will also be returned.

        :param kwargs:
            - analysis_id: str
            - search_text: str
            - tag: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - include_all_versions: bool
            - pagination: Pagination
        :return: List[AnalysisVersion]
        """

        assert kwargs.keys() is not None

        request_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            request_fragments.append((AnalysisVersionListRequest(pagination=Pagination(
                page_size=1000
            ))))
            fetch_all = True

        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False

        if 'include_manifest' in kwargs.keys():
            request_fragments.append(AnalysisVersionListRequest(include_manifest=True))

        if 'include_all_versions' in kwargs.keys():
            request_fragments.append(AnalysisVersionListRequest(include_all_versions=True))

        for key in kwargs.keys():
            if key == 'analysis_id':
                request_fragments.append(AnalysisVersionListRequest(analysis_id=kwargs[key]))
            if key == 'search_text':
                request_fragments.append(AnalysisVersionListRequest(search_text=kwargs[key]))
            if key == 'tag':
                request_fragments.append(AnalysisVersionListRequest(tag=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisVersionListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisVersionListRequest(max_created_on=max_created_on))
            if key == 'include_all_versions':
                request_fragments.append(AnalysisVersionListRequest(include_all_versions=kwargs[key]))
            if key == 'pagination':
                request_fragments.append(AnalysisVersionListRequest(pagination=kwargs[key]))

        request = AnalysisVersionListRequest()
        for request_fragment in request_fragments:
            request.MergeFrom(request_fragment)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.analysis_version.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                return responses
            else:
                analysis_versions = []
                for response in responses:
                    analysis_versions.extend(response.analysis_versions)
                return analysis_versions
        else:
            response = await self.__client.api.analysis_version.list(request, timeout=self.__timeout)

            if kwargs['raw_response']:
                return response
            else:
                return response.analysis_versions

    async def deprecate(self, analysis_version_ids: List):
        """
        Deprecate the specific version of this analysis. Deprecated analysiss can still be searched for, metadata can
        be retrieved, and can still be used to create new analysis_configs which can be used as part of
        analysis_computations, but they are no longer actively supported. All analysis_configs created from this
        analysis_version are also deprecated, but can still be used in new analysis_computations.
        :param analysis_version_ids:
        :return:
        """
        pass

    async def deactivate(self, analysis_version_ids: List):
        """
        Deactivate the specific version of this analysis. Metadata for deactivated analyses can still be retrieved
        directly, but they will no longer show up in search results from the list endpoint.Deactivated
        analysis_versions cannot be used to create new analysis_configs. All analysis_configs created from this
        analysis_version are also deactivated and can no longer be used to create new analysis_computations.
        Existing computations that are already using analysis_configs created from this analysis_version
        will still continue to run.
        :param analysis_version_ids:
        :return:
        """
        pass


class APIAnalysisConfig:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, analysis_version_id: str,
                     name: str,
                     description: str,
                     algorithm_config_nodes: List) -> AnalysisConfig:
        """
        Creates a configuration of the specified analysis version, including concrete values for all of the analysis
        parameters. This configuration is stored in the system and the analysis_config is returned to the user.

        :param analysis_version_id:
        :param name
        :param description:
        :param algorithm_config_nodes:

        :return: AnalysisConfig
        """
        request = AnalysisConfigCreateRequest(
            analysis_version_id=analysis_version_id,
            name=name,
            description=description,
            algorithm_config_nodes=algorithm_config_nodes
        )
        response = await self.__client.api.analysis_config.create(request, timeout=self.__timeout)

        return response.analysis_config

    async def update(self, analysis_config_id: str, analysis_config: AnalysisConfiguration):
        """
        Update details of an analysis_config, so long as it has not been locked. Once the analysis_config is used in a
        computation, it is permanently locked and the specific parameter values can no longer be updated.
        :param analysis_config_id:
        :param analysis_config:
        :return:
        """
        pass

    async def get(self, ids: List,
                  include_algorithm_details: bool = False,
                  pagination: Pagination = None) -> List[AnalysisConfig]:
        """
        Retrieve the metadata of a particular analysis configuration.

        :return: List[AnalysisConfig]
        """
        if pagination is None:
            pagination = Pagination(
                page_size=1000
            )
        request = AnalysisConfigGetRequest(
            ids=ids,
            include_algorithm_details=include_algorithm_details,
            pagination=pagination
        )

        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.analysis_config.get,
                                                                timeout=self.__timeout)
        analysis_configs = []
        for response in responses:
            analysis_configs.extend(response.analysis_configs)

        return analysis_configs

    async def list(self, **kwargs) -> List[AnalysisConfig]:
        """
        Retrieve the metadata for all analysis configurations that this user has access to and that match the provided
        search filters. By default, deactivated analysis_configs are not returned. Setting include_deactivated to true
        will also return any analysis_configs that had been deactivated.

        :param kwargs:
            - analysis_id: str
            - analysis_version_id: str
            - subject_id: str
            - search_text: str
            - tag: str
            - min_created_on: Datetime
            - max_created_on: Datetime
            - include_algorithm_details: bool
            - include_all_versions: bool
            - pagination: Pagination

        :return: List[AnalysisConfig]
        """
        assert kwargs.keys() is not None

        request_fragments = []
        fetch_all = False
        if 'pagination' not in kwargs.keys():
            request_fragments.append(AnalysisConfigListRequest(pagination=Pagination(
                page_size=1000
            )))
            fetch_all = True

        if 'raw_response' not in kwargs.keys():
            kwargs['raw_response'] = False

        for key in kwargs.keys():
            if key == 'analysis_id':
                request_fragments.append(AnalysisConfigListRequest(analysis_id=kwargs[key]))
            if key == 'analysis_version_id':
                request_fragments.append(AnalysisConfigListRequest(analysis_version_id=kwargs[key]))
            if key == 'subject_id':
                request_fragments.append(AnalysisConfigListRequest(subject_id=kwargs[key]))
            if key == 'search_text':
                request_fragments.append(AnalysisConfigListRequest(search_text=kwargs[key]))
            if key == 'tag':
                request_fragments.append(AnalysisConfigListRequest(tag=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisConfigListRequest(min_created_on=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                request_fragments.append(AnalysisConfigListRequest(max_created_on=max_created_on))
            if key == 'pagination':
                request_fragments.append(AnalysisConfigListRequest(pagination=kwargs[key]))

        if 'include_deactivated' in kwargs.keys():
            request_fragments.append(AnalysisConfigListRequest(include_deactivated=kwargs['include_deactivated']))
        else:
            request_fragments.append(AnalysisConfigListRequest(include_deactivated=False))

        # uncomment this when include_all_versions is available
        # if 'include_all_versions' in kwargs.keys():
        #    request_fragments.append(AnalysisConfigListRequest(include_all_versions=kwargs['include_all_versions']))
        # else:
        #    request_fragments.append(AnalysisConfigListRequest(include_all_versions=False))

        request = AnalysisConfigListRequest()
        for request_fragment in request_fragments:
            request.MergeFrom(request_fragment)

        if fetch_all:
            sdk_support = SDKSupport()
            responses = await sdk_support.get_all_paginated_objects(request,
                                                                    api_function=self.__client.api.analysis_config.list,
                                                                    timeout=self.__timeout)
            if kwargs['raw_response']:
                return responses
            else:
                analysis_configs = []
                for response in responses:
                    analysis_configs.extend(response.analysis_configs)
                return analysis_configs
        else:
            response = await self.__client.api.analysis_config.list(request)

            if kwargs['raw_response']:
                return response
            else:
                return response.analysis_configs

    async def deprecate(self, analysis_config_ids: List):
        """
        Deprecate the specific configuration of an analysis_version. Deprecated analysis_configs can still be searched
        for, metadata can be retrieved, and can still be used in new analysis_computations, but they are no longer
        actively supported.
        :param analysis_config_ids:
        :return:
        """
        pass

    async def deactivate(self, analysis_config_ids: List[str]):
        """
        Deactivate the specific configuration of an analysis_version. Deactivated analysis_configs will no longer
        show up in searches, but metadata can still be retrieved for deactivated analysis_configs via the get endpoint.
        Deactivated analysis_configs cannot be used in any new analysis_computations, but existing analysis_computations
         will continue to function properly.
        :param analysis_config_ids:
        :return:
        """
        analysis_config_deactivate_request = AnalysisConfigDeactivateRequest(
            ids=analysis_config_ids
        )
        analysis_config_deactivate_response = await self.__client.api.analysis_config.deactivate(
            analysis_config_deactivate_request, timeout=self.__timeout)

        return analysis_config_deactivate_response

    async def delete(self, analysis_config_ids: List):
        """
        Delete the specified analysis_config, if and only if it has not been used to create an analysis_computation.
        Once an analysis_config has been used to create an analysis_computation it can never be deleted.
        The user must have permission to access the specified analysis.
        :param analysis_config_ids:
        :return:
        """
        pass


class APIAnalysisComputation:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, analysis_config_id: str,
                     aoi_collection_id: str,
                     toi_id: str) -> AnalysisComputation:
        """
        Create the runnable component in the system, by specifiying the ANALYSIS to be run, the set of AOIs to be
        run on, and the TOI to specify the recurrence. The analysis_computation_id is returned so that it can be run.
        Note that until an analysis_computation has been run, its underlying .resources are NOT locked and therefore can
        be changed.
        :param analysis_config_id:
        :param aoi_collection_id:
        :param toi_id:
        :return: AnalysisComputation object
        """

        request = AnalysisComputationCreateRequest(
            analysis_config_id=analysis_config_id,
            toi_id=toi_id,
            aoi_collection_id=aoi_collection_id
        )
        response = await self.__client.api.analysis_computation.create(request, timeout=self.__timeout)
        return response.analysis_computation

    async def run(self, analysis_computation_ids: List):
        """
        The first time this endpoint is called, the system initiates the running of the provided
        analysis_computation_id. This causes credits to be place in pending status and eventually consumed when the
        computation completes. Credits are consumed as each result is produced. Once an analysis has been run, all of
        its underlying constituent parts are considered locked and cannot be modified.

        :param analysis_computation_ids:
        :return: AnalysisSubmitResponse
        """

        request = AnalysisComputationRunRequest(
            ids=analysis_computation_ids
        )
        await self.__client.api.analysis_computation.run(request, timeout=self.__timeout)

    async def get(self, ids: List, pagination: Pagination = None) -> List[AnalysisComputation]:
        """
        Retrieves the details of the provided analysis_computation including its current state and its progress.

        **NOT_STARTED**: Analysis computations that have been created but not yet passed into the "run" endpoint.
        **IN_PROGRESS**: Analysis computations that have been "run" but are not yet complete.
        **COMPLETE**: Once an analysis computation has run on all AOIs and for all TOIs and ALGOs and all
        results are either complete or failed.

        :return: List[AnalysisComputation]
        """
        if pagination is None:
            pagination = Pagination(
                page_size=1000
            )

        request = AnalysisComputationGetRequest(
            ids=ids,
            pagination=pagination
        )
        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(request,
                                                                api_function=self.__client.api.analysis_computation.get,
                                                                timeout=self.__timeout)
        analysis_computations = []
        for response in responses:
            analysis_computations.extend(response.analysis_computations)

        return analysis_computations

    async def update(self, analysis_computation_id: str, **kwargs):
        """
        Update an analysis computation's aoi, toi, algorithm config id. The analysis computation must be unlocked.
        :param analysis_computation_id:
        :param kwargs:
            - analysis_config_id: str
            - id: str,
            - toi_id: str
        :return:
        """
        pass

    async def list(self, **kwargs) -> List[AnalysisComputation]:
        """
        "Lists the details for all analysis_computations that the requester has access to including
        their current state and their progress.

        **NOT_STARTED**: Analysis computations that have been created but not yet passed into the ""run"" endpoint.
        **IN_PROGRESS**: Analysis computations that have been ""run"" but are not yet complete.
        **COMPLETE**: Once an analysis computation has run on all AOIs and for all TOIs and ALGOs
            and all results are either complete or failed."
        :param kwargs:
            - state: state_enum,
            - status: status_enum,
            - max_created_on: Datetime,
            - min_created_on: Datetime,
            - analysis_config_id: str,
            - toi_id: str,
            - id: str,
            - analysis_id: str,
            - pagination: str
        :return: List[AnalysisComputation]
        """
        fragments = []
        if 'pagination' not in kwargs.keys():
            fragments.append(AnalysisComputationListRequest(pagination=Pagination(
                page_size=1000
            )))

        for key in kwargs.keys():
            if key == 'state':
                fragments.append(AnalysisComputationListRequest(state=kwargs[key]))
            if key == 'status':
                fragments.append(AnalysisComputationListRequest(status=kwargs[key]))
            if key == 'min_created_on':
                min_created_on = Timestamp()
                min_created_on.FromDatetime(kwargs[key])
                fragments.append(AnalysisComputationListRequest(submitted_min=min_created_on))
            if key == 'max_created_on':
                max_created_on = Timestamp()
                max_created_on.FromDatetime(kwargs[key])
                fragments.append(AnalysisComputationListRequest(submitted_max=max_created_on))
            if key == 'analysis_config_id':
                fragments.append(AnalysisComputationListRequest(analysis_config_id=kwargs[key]))
            if key == 'toi_id':
                fragments.append(AnalysisComputationListRequest(toi_id=kwargs[key]))
            if key == 'id':
                fragments.append(AnalysisComputationListRequest(aoi_collection_id=kwargs[key]))
            if key == 'analysis_id':
                fragments.append(AnalysisComputationListRequest(analysis_id=kwargs[key]))
            if key == 'pagination':
                fragments.append(AnalysisComputationListRequest(search_text=kwargs[key]))

        request = AnalysisComputationListRequest()
        for param in fragments:
            request.MergeFrom(param)

        sdk_support = SDKSupport()
        responses = await sdk_support.get_all_paginated_objects(
            request,
            api_function=self.__client.api.analysis_computation.list,
            timeout=self.__timeout)

        analysis_computations = []
        for response in responses:
            analysis_computations.extend(response.analysis_computations)

        return analysis_computations

    async def delete(self, analysis_computation_ids: List):
        """
        Deletes the specified analysis_computation, provided that it has not already been run. This is a permanent
        action. Must be the user that created the analysis_computation.
        :param analysis_computation_ids:
        :return:
        """
        pass

    async def pause(self, analysis_computation_ids: List):
        """
        Update the analysis_computation to move out of the *IN_PROGRESS* state. This will ensure that it no longer runs,
        until it is resumed. Whatever is currently running, will still complete.
        :param analysis_computation_ids:
        :return:
        """
        pass

    async def resume(self, analysis_computation_ids: List):
        """
        Update the analysis_computation to move back into the IN_PROGRESS state, and will again be set to run.
        :param analysis_computation_ids:
        :return:
        """
        pass

    async def history(self, analysis_computation_id: str):
        """
        Returns the history of the analysis computation including the status of all previous executions.
        :param analysis_computation_id:
        :return:
        """
        pass
