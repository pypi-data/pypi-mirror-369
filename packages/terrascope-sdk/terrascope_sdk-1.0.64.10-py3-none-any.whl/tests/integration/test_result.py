import uuid
import pytest
import os.path
import logging
from datetime import datetime

from terrascope.sdk.builder.toi import TOIBuilder, TOIRuleBuilder, Frequency
from terrascope.sdk.builder.algorithm import (
    AlgorithmManifest, AlgorithmConfiguration, InterfaceType, DataType, DataSource
)
from terrascope.sdk.builder.analysis import AnalysisManifest, AnalysisConfiguration
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestResult:

    @pytest.mark.asyncio
    # @pytest.mark.parametrize()
    async def test_result_get_export(self):
        # SETUP ALGORITHM
        sdk = TerraScopeSDK()
        algorithm_name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        algorithm_display_name = "Device Visits SDK Integration"
        algorithm_author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=algorithm_name,
                                               display_name=algorithm_display_name,
                                               author=algorithm_author)
        assert algorithm.id is not None
        assert algorithm.name == algorithm_name
        assert algorithm.display_name == algorithm_display_name
        assert algorithm.author == algorithm_author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value)

        manifest.container_parameters_required(image="orbitalinsight/device_visits:1d77d321",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits", observation_value_columns=["device_visits"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        await sdk.credit.set_algorithm(algorithm_version_id=algorithm_version.id,
                                       algorithm_execution_price=1.0,
                                       algorithm_value_price=0.0)

        configuration = AlgorithmConfiguration()
        configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)

        algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                    name="device_visit_sdk_test_config",
                                                                    description="A test configuration.",
                                                                    algorithm_config=configuration)
        # AOI Setup
        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))
        assert aoi_collection.id is not None
        await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                             file_path="../resources/aois/geojson/us-amz-distro-centers.geojson")
        # TOI Setup
        datetime_format = '%Y-%m-%dT%H:%M:%SZ'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime("2019-01-05T01:00:00Z", datetime_format),
                                    finish=datetime.strptime("2019-01-06T01:00:00Z", datetime_format))
        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(
            frequency=Frequency.DAILY,
            interval=1
        ))
        toi = await sdk.toi.create(toi_configuration.get())
        assert toi.id is not None

        # Analysis Setup
        name = "analysis-config-create-test-{}".format(uuid.uuid4())
        author = "terrascope-sdk"
        analysis = await sdk.analysis.create(name=name,
                                             author=author)
        assert analysis.id is not None
        assert analysis.name == name
        assert analysis.author == author

        manifest = AnalysisManifest()
        description = "Test description for the greatest manifest in the world."
        version = "0.0.1"
        manifest.metadata(description=description,
                          version=version,
                          tags=["device-visits", "result-test"])
        manifest.add_node(name="device-visits",
                          algorithm_version_id=algorithm_version.id)
        analysis_version = await sdk.analysis_version.create(analysis_id=analysis.id,
                                                             analysis_manifest=manifest)

        config = AnalysisConfiguration(analysis_version.id)
        config.add_config_node(name=manifest.get().algorithm_nodes[0].name,
                               algorithm_config_id=algorithm_configuration.id)
        analysis_config = await sdk.analysis_config.create(analysis_version_id=analysis_version.id,
                                                           name="Results Analysis - Device Visits-{}".format(str(uuid.uuid4()).split("-")[0]),
                                                           description="Integration test for analysis_config.create",
                                                           algorithm_config_nodes=config.get())

        assert analysis_config.id is not None

        analysis_computation = await sdk.analysis_computation.create(analysis_config_id=analysis_config.id,
                                                                     toi_id=toi.id,
                                                                     aoi_collection_id=aoi_collection.id)

        logging.info(analysis_computation)
        assert analysis_computation.id is not None
        await sdk.analysis_computation.run(analysis_computation_ids=[analysis_computation.id])

        algorithm_computation_id = analysis_computation.computation_nodes[0].computation_id
        source_aoi_version = 10  # How to get this?
        await sdk.result.wait_and_download(algorithm_computation_ids=[algorithm_computation_id],
                                           output="../output/test-result-wejo-amzdst-{}.zip".format(
                                               algorithm_computation_id),
                                           source_aoi_version=source_aoi_version)

        assert os.path.isfile("../output/test-result-wejo-amzdst-{}.zip".format(algorithm_computation_id))

    @pytest.mark.asyncio
    async def test_result_export(self):
        sdk = TerraScopeSDK()
        # algorithm_computation_id for prod env
        algorithm_computation_id = '5ce2d9b4-170f-42ad-9c18-21398e45c72b'
        source_aoi_version = 36091042
        file_paths = await sdk.result.export(algorithm_computation_id, source_aoi_version)
        for file_path in file_paths:
            assert os.path.exists(file_path)
