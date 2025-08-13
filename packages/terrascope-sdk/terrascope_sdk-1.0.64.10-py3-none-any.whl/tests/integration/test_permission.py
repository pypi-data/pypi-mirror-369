import uuid

import pytest
from terrascope_api.models.permission_pb2 import Permission
from terrascope_api.models.resource_pb2 import Resource

from terrascope.sdk.builder.algorithm import AlgorithmManifest, AlgorithmConfiguration, DataType, InterfaceType
from terrascope.sdk.builder.analysis import AnalysisManifest
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestPermission:

    def __init__(self):
        self.generate_resources()

    async def generate_resources(self):
        sdk = TerraScopeSDK()

        # Algorithm
        algo_hash = str(uuid.uuid4()).split("-")[0]
        algorithm = await sdk.algorithm.create(name="test-algo-permission-{}".format(algo_hash),
                                               author="test@orbitalinsight.com",
                                               display_name="Permission Test")
        algorithm_id = algorithm.id
        self.algorithm_id = algorithm_id
        print('algo id:', algorithm_id)

        # Algorithm Version (not shareable, to feed to config)
        manifest = AlgorithmManifest()
        manifest.metadata_required(description="test-manifest", version="0.0.1")
        manifest.interface_required(interface_type=InterfaceType.NO_OP_WORKER.value)
        manifest.inputs_add_data_type(DataType.DEVICE_VISITS.value)
        manifest.outputs_add_data_type(data_type_name=DataType.DEVICE_TRACKS.value,
                                       observation_value_columns=["device_tracks"])
        manifest.container_parameters_required(image="", command=[])
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm_id, algorithm_manifest=manifest)
        print('algo version id:', algorithm_version.id)

        # Algorithm Config
        configuration = AlgorithmConfiguration()
        configuration.add_data_source(data_type=DataType.DEVICE_VISITS.value)
        algo_config = await sdk.algorithm_config.create(
            algorithm_version_id=algorithm_version.id,
            name="Permission Test Config",
            description="Permission Test Config",
            algorithm_config=configuration)
        algo_config_id = algo_config.id
        self.algo_config_id = algo_config_id
        print('algo config id:', algo_config_id)

        # Analysis
        analysis_hash = str(uuid.uuid4()).split("-")[0]
        analysis = await sdk.analysis.create(name="test-algo-permission-{}".format(analysis_hash),
                                             author="test@orbitalinsight.com")
        analysis_id = analysis.id
        self.analysis_id = analysis_id
        print('analysis id:', analysis_id)

        # Analysis Version
        analysis_manifest = AnalysisManifest()
        analysis_manifest.metadata(description="Permission Test Analysis Version",
                                   version="0.0.1", tags=['permission'])
        analysis_manifest.add_node(name="test-node", algorithm_version_id=algorithm_version.id)
        analysis_version = await sdk.analysis_version.create(analysis_id=analysis_id,
                                                             analysis_manifest=analysis_manifest)
        analysis_version_id = analysis_version.id
        print('analysis version id:', analysis_version_id)

        # # Analysis Config - breaking for some reason
        # confg = AnalysisConfiguration(analysis_version_id=analysis_version_id)
        # config.add_config_node(name="test-node", algorithm_config_id=algo_config_id)
        # analysis_config = await sdk.analysis_config.create(
        #     analysis_version_id=analysis_version_id,
        #     algorithm_config_nodes=config.get(),
        #     name="Permission Test Analysis Config",
        #     description="Permission Test Analysis Config")
        # analysis_config_id = analysis_config.id
        # self.analysis_config_id = analysis_config_id
        # print('analysis config id:', analysis_config_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource, permission_type", [
        (Resource.Type.ALGORITHM, Permission.Type.READ),
        (Resource.Type.ALGORITHM, Permission.Type.WRITE),
        (Resource.Type.ALGORITHM_CONFIG, Permission.Type.READ),
        (Resource.Type.ALGORITHM_CONFIG, Permission.Type.WRITE),
        (Resource.Type.ANALYSIS, Permission.Type.READ),
        (Resource.Type.ANALYSIS, Permission.Type.WRITE),
        # (Resource.Type.ANALYSIS_CONFIG, "read"),
        # (Resource.Type.ANALYSIS_CONFIG, "write"),
    ]
                             )
    async def test_create(self, resource_type: Resource.Type, permission_type: Permission.Type):
        sdk = TerraScopeSDK()
        if resource_type == Resource.Type.ALGORITHM:
            resource_id = self.algorithm_id
        elif resource_type == Resource.Type.ALGORITHM_CONFIG:
            resource_id = self.algo_config_id
        elif resource_type == Resource.Type.ANALYSIS:
            resource_id = self.analysis_id
        elif resource_type == Resource.Type.ANALYSIS_CONFIG:
            pass
        elif resource_type == Resource.Type.ALGORITHM_COMPUTATION:
            pass
        elif resource_type == Resource.Type.ANALYSIS_COMPUTATION:
            pass
        elif resource_type == Resource.Type.RESULT:
            pass
        elif resource_type == Resource.Type.TOI:
            pass
        elif resource_type == Resource.Type.AOI_COLLECTION:
            pass

        response = sdk.permission.create(resource_ids=[resource_id], resource_type=resource_type,
                                         permission_type=permission_type, user_emails=["test_user1@oi.com"],
                                         public=False, public_confirm=False)

        assert response is not None
        assert 200 <= response.status_code < 300
