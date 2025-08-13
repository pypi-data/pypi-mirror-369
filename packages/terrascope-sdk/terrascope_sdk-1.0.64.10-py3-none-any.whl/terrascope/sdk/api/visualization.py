from enum import Enum
from typing import List

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.visualization_pb2 import (
    VisualizationGetRequest, Visualization, VisualizerConfigAlgoVersionCreateRequest, VisualizerConfigAlgoVersionCreateResponse,
    VisualizerConfigAlgoConfigCreateResponse, VisualizerConfigAlgoConfigCreateRequest
)


class VisualizationConfigType(Enum):
    UNKNOWN_TYPE = 0
    STANDARD = 1
    SPATIAL = 2
    TEMPORAL = 3


class APIVisualization:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def get(self, result_observation_ids: List) -> List[Visualization]:
        """

        :param result_observation_ids:
        :return: List[Visualization]
        """
        request = VisualizationGetRequest(
            result_observation_ids=result_observation_ids
        )
        response = await self.__client.api.visualization.get(request)
        return response.visualizations

    async def create_visualizer_config_algo_version(self, visualizer_config_id: str,
                                            algorithm_version_id: str) -> VisualizerConfigAlgoVersionCreateResponse:
        request = VisualizerConfigAlgoVersionCreateRequest(
            visualizer_config_id=visualizer_config_id,
            algorithm_version_id=algorithm_version_id
        )
        response = await self.__client.api.visualization.create_config_algo_version(request)
        return response

    async def create_visualizer_config_algo_config(self, visualizer_config_id: str,
                                                   algorithm_config_id: str) -> VisualizerConfigAlgoConfigCreateResponse:
        request = VisualizerConfigAlgoConfigCreateRequest(
            visualizer_config_id=visualizer_config_id,
            algorithm_config_id=algorithm_config_id
        )
        response = await self.__client.api.visualization.create_config_algo_config(request)
        return response
