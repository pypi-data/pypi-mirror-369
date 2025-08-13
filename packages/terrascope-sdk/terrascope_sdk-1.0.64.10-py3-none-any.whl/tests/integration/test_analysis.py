import time
import uuid
import pytest
from datetime import datetime
from typing import List, Tuple

from terrascope_api.models.common_models_pb2 import Pagination
from terrascope.sdk.api.aoi import AOIInputBuilder
from terrascope.sdk.builder.toi import TOIRuleBuilder, TOIBuilder, Frequency
from terrascope.sdk.builder.algorithm import (
    AlgorithmManifest, InterfaceType, DataType, DataSource, AlgorithmConfiguration
)
from terrascope.sdk.builder.analysis import AnalysisManifest, AnalysisConfiguration
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


async def algorithm_create():
    sdk = TerraScopeSDK()
    algo_name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
    algo_display_name = "Device Visits SDK Integration"
    algo_author = "terrascope.sdk.integration@orbitalinsight.com"

    algorithm = await sdk.algorithm.create(name=algo_name,
                                           display_name=algo_display_name,
                                           author=algo_author)
    assert algorithm.id is not None
    assert algorithm.name == algo_name
    assert algorithm.display_name == algo_display_name
    assert algorithm.author == algo_author
    return algorithm


async def algorithm_version_create(algorithm_id: str):
    sdk = TerraScopeSDK()
    manifest = AlgorithmManifest()
    manifest.metadata_required(
        description="Testing algo manifest builder",
    )
    manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
    manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                  min_count=1,
                                  max_count=2)

    manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                           command=["python",
                                                    "/orbital/base/algorithms/"
                                                    "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
    manifest.outputs_add_data_type(data_type_name="device_visits",
                                   observation_value_columns=["unique_device_count"])

    algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm_id,
                                                           algorithm_manifest=manifest)
    assert algorithm_version.id is not None
    return algorithm_version


async def algorithm_config_create(algorithm_version_id: str):
    sdk = TerraScopeSDK()
    algorithm_config_build = AlgorithmConfiguration()
    algorithm_config_build.add_data_source(data_type=DataType.PINGS.value, data_source=DataSource.WEJO)
    algorithm_config = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version_id,
                                                         algorithm_config=algorithm_config_build,
                                                         name="test_config-{}".format(uuid.uuid4()),
                                                         description="sdk test config")
    return algorithm_config


async def analysis_create(name, author):
    sdk = TerraScopeSDK()
    analysis = await sdk.analysis.create(name=name,
                                         author=author)
    assert analysis.id is not None
    assert analysis.name == name
    assert analysis.author == author
    return analysis


async def analysis_version_create(analysis_id: str, algorithm_version_ids: List[str],
                                  node_edges: List[Tuple[int, int]]):
    sdk = TerraScopeSDK()
    manifest = AnalysisManifest()
    description = "Test description for the greatest manifest in the world."
    manifest.metadata(description=description, tags=["sdk-test", "cap-sdk"])
    for algorithm_version_id in algorithm_version_ids:
        manifest.add_node(name=f"fake_name_{str(uuid.uuid4())}",
                          algorithm_version_id=algorithm_version_id)
    for source_node, dest_node in node_edges:
        manifest.add_node_edge(source_node, dest_node)

    analysis_version = await sdk.analysis_version.create(analysis_id=analysis_id, analysis_manifest=manifest)
    assert analysis_version.id is not None
    return analysis_version, manifest


async def analysis_config_create(analysis_version_id, algorithm_config_id, manifest):
    sdk = TerraScopeSDK()
    config = AnalysisConfiguration(analysis_version_id)
    config.add_config_node(name=manifest.get().algorithm_nodes[0].name,
                           algorithm_config_id=algorithm_config_id)
    analysis_config = await sdk.analysis_config.create(analysis_version_id=analysis_version_id,
                                                       name="analysis_config_test_create_{}".format(uuid.uuid4()),
                                                       description="Integration test for analysis_config.create",
                                                       algorithm_config_nodes=config.get())
    assert analysis_config.id is not None
    return analysis_config


async def analysis_computation_create(analysis_config_id: str, toi_id: str, aoi_collection_id: str):
    sdk = TerraScopeSDK()
    analysis_computation = await sdk.analysis_computation.create(
        analysis_config_id=analysis_config_id,
        toi_id=toi_id,
        aoi_collection_id=aoi_collection_id)
    assert analysis_computation.id is not None
    return analysis_computation


async def aoi_collection_create(name):
    sdk = TerraScopeSDK()
    aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=name)
    assert aoi_collection.id is not None

    wkt = """POLYGON ((-121.891336 37.345116, -121.882978 37.322622, -121.865618 37.335404, -121.891336 37.345116))
            """
    aoi_builder = AOIInputBuilder()
    aoi = aoi_builder.build(
        geom_wkt=wkt,
        name="aoi-" + name,
        category="industry",
        category_type="LNG",
        tags=["industrial", "LNG", "test"])
    aoi_identifiers = await sdk.aoi.create(aoi_collection_id=aoi_collection.id, aoi_inputs=[aoi])
    assert aoi_identifiers is not None
    return aoi_collection


async def toi_create():
    sdk = TerraScopeSDK()
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
    return toi


class TestAnalysis:
    @pytest.mark.asyncio
    async def test_create(self):
        await analysis_create(name="integration-test-{}".format(datetime.now()), author="terrascope-sdk")

    @pytest.mark.asyncio
    async def test_update(self):
        pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("analysis_id_count", [
        1,
        10,
        25,
        45
    ])
    async def test_get(self, analysis_id_count: int):
        sdk = TerraScopeSDK()
        analysis_ids = []
        for i in range(analysis_id_count):
            analysis = await analysis_create(name="analysis_get_element_{}".format(uuid.uuid4()),
                                             author="terrascope-sdk-pytest")
            analysis_ids.append(analysis.id)
        assert len(analysis_ids) == analysis_id_count
        analyses = await sdk.analysis.get(ids=analysis_ids,
                                          pagination=Pagination(page_size=5))
        assert len(analyses) == analysis_id_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize("analysis_count", [
        10,
        20
    ])
    async def test_list(self, analysis_count):
        sdk = TerraScopeSDK()
        start = datetime.utcnow()
        halfway = None
        search_text = uuid.uuid4()
        for i in range(analysis_count):
            await analysis_create(name="sdk-search-me-{}-{}".format(i, search_text),
                                  author="terrascope-sdk-list-integration")
            if i + 1 == analysis_count / 2:
                time.sleep(10)
                halfway = datetime.utcnow()

        results = await sdk.analysis.list(search_text=str(search_text))
        assert len(results) == analysis_count

        search_results = await sdk.analysis.list(min_created_on=start, max_created_on=halfway)
        assert len(search_results) == analysis_count / 2


class TestAnalysisVersion:
    @pytest.mark.asyncio
    async def test_create(self):
        algorithm = await algorithm_create()
        algorithm_version_ids = []
        for i in range(3):
            algorithm_version = await algorithm_version_create(algorithm.id)
            algorithm_version_ids.append(algorithm_version.id)
        analysis = await analysis_create(name="analysis-version-create-test-{}".format(uuid.uuid4()),
                                         author="terrascope-sdk")
        await analysis_version_create(analysis.id, algorithm_version_ids, [(0, 1), (1, 2)])

    @pytest.mark.asyncio
    @pytest.mark.parametrize("analysis_version_id_count", [
        1,
        10,
        25,
        45
    ])
    async def test_get(self, analysis_version_id_count):
        sdk = TerraScopeSDK()
        algorithm = await algorithm_create()
        algorithm_version_ids = []
        for i in range(3):
            algorithm_version = await algorithm_version_create(algorithm.id)
            algorithm_version_ids.append(algorithm_version.id)
        analysis = await analysis_create(name="analysis-version-get-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")
        analysis_version_ids = []
        for i in range(analysis_version_id_count):
            analysis_version, _ = await analysis_version_create(analysis.id, algorithm_version_ids, [(0, 1), (1, 2)])
            analysis_version_ids.append(analysis_version.id)
        assert len(analysis_version_ids) == analysis_version_id_count

        # Algo details should fail since fake algo
        analysis_versions = await sdk.analysis_version.get(ids=analysis_version_ids,
                                                           include_manifest=True,
                                                           pagination=Pagination(page_size=5))

        assert len(analysis_versions) == analysis_version_id_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize("analysis_version_id_count", [
        10,
        20
    ])
    async def test_list(self, analysis_version_id_count: int):
        sdk = TerraScopeSDK()
        algorithm = await algorithm_create()
        algorithm_version_ids = []
        for i in range(3):
            algorithm_version = await algorithm_version_create(algorithm.id)
            algorithm_version_ids.append(algorithm_version.id)
        analysis = await analysis_create(name="analysis-version-list-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")

        min_created_on = datetime.utcnow()
        max_created_on = None
        analysis_version_ids = []
        for i in range(analysis_version_id_count):
            analysis_version, _ = await analysis_version_create(analysis.id, algorithm_version_ids, [(0, 1), (1, 2)])
            if i == (analysis_version_id_count / 2) - 1:
                time.sleep(10)
                max_created_on = datetime.utcnow()

            analysis_version_ids.append(analysis_version.id)

        analysis_versions = await sdk.analysis_version.list(analysis_id=analysis.id, include_all_versions=False)

        assert len(analysis_versions) == 1

        analysis_versions = await sdk.analysis_version.list(analysis_id=analysis.id,
                                                            include_all_versions=True)
        assert len(analysis_versions) == len(analysis_version_ids)
        for version in analysis_versions:
            assert version.analysis_id == analysis.id

        analysis_versions = await sdk.analysis_version.list(min_created_on=min_created_on,
                                                            max_created_on=max_created_on,
                                                            include_all_versions=True)
        assert len(analysis_versions) == analysis_version_id_count / 2

    @pytest.mark.asyncio
    async def test_deprecate(self):
        pass

    @pytest.mark.asyncio
    async def test_deactivate(self):
        pass


class TestAnalysisConfig:
    @pytest.mark.asyncio
    async def test_create(self):
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        analysis = await analysis_create(name="analysis-config-create-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        algorithm_config = await algorithm_config_create(algorithm_version.id)
        await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)

    @pytest.mark.asyncio
    async def test_update(self):
        pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        1,
        10,
        25,
        45
    ])
    async def test_get(self, config_count: int):
        sdk = TerraScopeSDK()
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        analysis = await analysis_create(name="analysis-config-get-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        algorithm_config = await algorithm_config_create(algorithm_version.id)
        analysis_config_ids = []
        for i in range(config_count):
            analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)
            analysis_config_ids.append(analysis_config.id)

        analysis_configs = await sdk.analysis_config.get(ids=analysis_config_ids,
                                                         include_algorithm_details=False,
                                                         pagination=Pagination(page_size=5))

        assert len(analysis_configs) == config_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        1,
        10,
        25
    ])
    async def test_list(self, config_count: int):
        sdk = TerraScopeSDK()
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        analysis = await analysis_create(name="analysis-config-list-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        algorithm_config = await algorithm_config_create(algorithm_version.id)

        analysis_config_ids = []
        for i in range(config_count):
            analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)
            analysis_config_ids.append(analysis_config.id)

        analysis_configs = await sdk.analysis_config.list(analysis_version_id=analysis_version.id)
        assert len(analysis_configs) == config_count

    @pytest.mark.asyncio
    async def test_deprecate(self):
        pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        1,
        10,
        25
    ])
    @pytest.mark.asyncio
    async def test_deactivate(self, config_count: int):
        sdk = TerraScopeSDK()
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        analysis = await analysis_create(name="analysis-config-list-test-{}".format(datetime.now()),
                                         author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        algorithm_config = await algorithm_config_create(algorithm_version.id)

        analysis_config_ids = []
        for i in range(config_count):
            analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)
            analysis_config_ids.append(analysis_config.id)

        # DEACTIVATE ANALYSIS CONFIG
        await sdk.analysis_config.deactivate(analysis_config_ids)

        # Check that List request doesn't return de-activated Analysis Configs unless specified
        analysis_configs = await sdk.analysis_config.list(analysis_version_id=analysis_version.id)
        assert len(analysis_configs) == 0
        analysis_configs = await sdk.analysis_config.list(analysis_version_id=analysis_version.id,
                                                          include_deactivated=True)
        assert len(analysis_configs) == config_count

        # Check that Analysis Configs can still be queried through the get request, but has deactivated flag set
        analysis_configs = await sdk.analysis_config.get(ids=analysis_config_ids, include_algorithm_details=False)
        assert all([analysis_config.is_deactivated for analysis_config in analysis_configs])

    @pytest.mark.asyncio
    async def test_delete(self):
        pass


class TestAnalysisComputation:
    @pytest.mark.asyncio
    async def test_create(self):
        # SETUP ALGORITHM
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        algorithm_config = await algorithm_config_create(algorithm_version.id)

        # SETUP ANALYSIS
        name = "analysis-computation-create-test-{}".format(datetime.now())
        analysis = await analysis_create(name=name, author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)

        # SETUP AOI
        aoi_collection = await aoi_collection_create(name)

        # SETUP TOI
        toi = await toi_create()

        # SETUP ANALYSIS COMPUTATION
        await analysis_computation_create(analysis_config.id, toi.id, aoi_collection.id)

    @pytest.mark.asyncio
    async def test_run(self):
        sdk = TerraScopeSDK()
        # SETUP ALGORITHM
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        algorithm_config = await algorithm_config_create(algorithm_version.id)

        # SETUP ANALYSIS
        name = "analysis-computation-run-test-{}".format(datetime.now())
        analysis = await analysis_create(name=name, author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)

        # SETUP AOI
        aoi_collection = await aoi_collection_create(name)

        # SETUP TOI
        toi = await toi_create()

        # SETUP ANALYSIS COMPUTATION
        analysis_computation = await analysis_computation_create(analysis_config.id, toi.id, aoi_collection.id)

        # RUN ANALYSIS COMPUTATION
        await sdk.analysis_computation.run([analysis_computation.id])

    @pytest.mark.asyncio
    async def test_get(self):
        sdk = TerraScopeSDK()
        # SETUP ALGORITHM
        algorithm = await algorithm_create()
        algorithm_version = await algorithm_version_create(algorithm.id)
        algorithm_config = await algorithm_config_create(algorithm_version.id)

        # SETUP ANALYSIS
        name = "analysis-computation-get-test-{}".format(datetime.now())
        analysis = await analysis_create(name=name, author="terrascope-sdk")
        analysis_version, manifest = await analysis_version_create(analysis.id, [algorithm_version.id], [])
        analysis_config = await analysis_config_create(analysis_version.id, algorithm_config.id, manifest)

        # SETUP AOI
        aoi_collection = await aoi_collection_create(name)

        # SETUP TOI
        toi = await toi_create()

        # SETUP ANALYSIS COMPUTATION
        analysis_computation = await analysis_computation_create(analysis_config.id, toi.id, aoi_collection.id)

        # GET ANALYSIS COMPUTATION
        analysis_computation = await sdk.analysis_computation.get([analysis_computation.id])
        assert analysis_computation is not None

    @pytest.mark.asyncio
    async def test_list(self):
        pass
