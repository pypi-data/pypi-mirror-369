import logging
import time
import uuid
from datetime import datetime
import pytest

from terrascope_api.models.common_models_pb2 import Pagination
from terrascope.sdk.builder.algorithm import (
    AlgorithmManifest, InterfaceType, DataType, AlgorithmConfiguration, DataSource
)
from terrascope.sdk.builder.toi import Frequency
from terrascope.sdk.builder.toi import TOIBuilder, TOIRuleBuilder
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestAlgorithm:
    @pytest.mark.asyncio
    async def test_create(self):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

    @pytest.mark.asyncio
    @pytest.mark.parametrize("new_name, new_display_name, new_author", [
        ("RegularTestAlgorithm".format(uuid.uuid4()), "Regular Test Algorithm", "bang.test@bangtest.com")

    ])
    async def test_update(self,
                          new_name: str,
                          new_display_name: str,
                          new_author: str):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm_model = await sdk.algorithm.create(name=name,
                                                     display_name=display_name,
                                                     author=author)
        assert algorithm_model.id is not None
        assert algorithm_model.name == name
        assert algorithm_model.display_name == display_name
        assert algorithm_model.author == author

        algorithm_model.display_name = new_display_name
        algorithm_model.author = new_author
        algorithms = [algorithm_model]
        await sdk.algorithm.update(algorithms=algorithms)
        algorithm_new_models = await sdk.algorithm.get([algorithm_model.id])
        assert len(algorithm_new_models) == 1
        algorithm_new_model = algorithm_new_models[0]
        assert algorithm_new_model.display_name == new_display_name
        assert algorithm_new_model.author == new_author

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_count", [
        1,
        10
    ])
    async def test_get(self, algorithm_count):
        sdk = TerraScopeSDK()

        display_name = "Test Get SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm_ids = []

        for i in range(algorithm_count):
            name = "sdk-integration-test-algorithm-get-{}".format(uuid.uuid4())
            algorithm_model = await sdk.algorithm.create(name=name,
                                                         display_name=display_name,
                                                         author=author)
            algorithm_ids.append(algorithm_model.id)

        algorithms = await sdk.algorithm.get(algorithm_ids, pagination=Pagination(page_size=5))
        for algorithm in algorithms:
            assert algorithm.display_name == display_name
            assert algorithm.author == author

        assert len(algorithm_ids) == len(algorithms)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_count", [
        10,
        20
    ])
    async def test_list(self, algorithm_count):
        sdk = TerraScopeSDK()
        search_key = uuid.uuid4()
        name = str(search_key)
        display_name = "sdk-integration-test-algorithm-get-{}".format(name)
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm_ids = []
        now = datetime.utcnow()
        halfway = None
        for i in range(algorithm_count):
            algorithm_model = await sdk.algorithm.create(name="{}-{}".format(name, i),
                                                         display_name=display_name,
                                                         author=author)
            if i + 1 == int(algorithm_count / 2):
                time.sleep(10)
                halfway = datetime.utcnow()
            algorithm_ids.append(algorithm_model.id)

        # search text
        algorithms = await sdk.algorithm.list(search_text=name)
        assert len(algorithm_ids) == len(algorithms)
        algorithms = await sdk.algorithm.list(min_created_on=now, max_created_on=halfway)
        assert len(algorithms) == algorithm_count / 2


class TestAlgorithmVersion:
    @pytest.mark.asyncio
    async def test_create(self):
        sdk = TerraScopeSDK()
        algo_1_name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        algo_1_display_name = "Device Visits SDK Integration"
        algo_1_author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=algo_1_name,
                                               display_name=algo_1_display_name,
                                               author=algo_1_author)
        assert algorithm.id is not None
        assert algorithm.name == algo_1_name
        assert algorithm.display_name == algo_1_display_name
        assert algorithm.author == algo_1_author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=2,
                                      max_count=2)

        manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                               command=["python",
                                                        "/orbital/base/algorithms/"
                                                        "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("version_count", [
        1,
        10,
        20,
        45
    ])
    async def test_get(self, version_count: int):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        algorithm_version_ids = []
        for i in range(version_count):
            manifest = AlgorithmManifest()
            manifest.metadata_required(description="Testing algo manifest builder")
            manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
            manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                          min_count=2,
                                          max_count=2)

            manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                                   command=["python",
                                                            "/orbital/base/algorithms/"
                                                            "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
            manifest.outputs_add_data_type(data_type_name="device_visits",
                                           observation_value_columns=["unique_device_count"])

            algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                                   algorithm_manifest=manifest)

            assert algorithm_version.id is not None
            algorithm_version_ids.append(algorithm_version.id)
        algorithm_versions = await sdk.algorithm_version.get(algorithm_version_ids=algorithm_version_ids,
                                                             pagination=Pagination(page_size=5))
        assert len(algorithm_versions) == version_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize("version_count", [
        10,
        20
    ])
    async def test_list(self, version_count):
        sdk = TerraScopeSDK()
        unique = uuid.uuid4()
        name = "device-visits-sdk-integration-test-{}".format(unique)
        display_name = str(unique)
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author
        tag_search_key = str(uuid.uuid4())
        algorithm_version_ids = []
        now = datetime.utcnow()
        halfway = None
        for i in range(version_count):
            manifest = AlgorithmManifest()
            manifest.metadata_required(
                description="Testing algo manifest builder")
            manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
            manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                          min_count=2,
                                          max_count=2)

            manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                                   command=["python",
                                                            "/orbital/base/algorithms/"
                                                            "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
            manifest.outputs_add_data_type(data_type_name="device_visits",
                                           observation_value_columns=["unique_device_count"])
            manifest.metadata_tags([tag_search_key])

            algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                                   algorithm_manifest=manifest)
            if i + 1 == version_count / 2:
                halfway = datetime.utcnow()
            assert algorithm_version.id is not None
            algorithm_version_ids.append(algorithm_version.id)

        algorithm_versions = await sdk.algorithm_version.list(algorithm_id=algorithm.id,
                                                              include_all_versions=True)
        assert len(algorithm_versions) == len(algorithm_version_ids)

        algorithm_versions = await sdk.algorithm_version.list(tag=tag_search_key, include_all_versions=True)
        assert len(algorithm_versions) == version_count
        algorithm_versions = await sdk.algorithm_version.list(min_created_on=now,
                                                              max_created_on=halfway, include_all_versions=True)
        assert len(algorithm_versions) == version_count / 2

    @pytest.mark.asyncio
    async def test_deprecate(self):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=2,
                                      max_count=2)

        manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                               command=["python",
                                                        "/orbital/base/algorithms/"
                                                        "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        await sdk.algorithm_version.deprecate([algorithm_version.id])
        algorithm_versions = await sdk.algorithm_version.get([algorithm_version.id])
        assert algorithm_versions[0].is_deprecated

    @pytest.mark.asyncio
    async def test_deactivate(self):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=2,
                                      max_count=2)

        manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                               command=["python",
                                                        "/orbital/base/algorithms/"
                                                        "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        await sdk.algorithm_version.deactivate([algorithm_version.id])
        algorithm_versions = await sdk.algorithm_version.get([algorithm_version.id])
        assert algorithm_versions[0].is_deactivated


class TestAlgorithmConfig:

    @pytest.mark.asyncio
    async def test_create(self):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)
        manifest.grouping_frequency("DAILY", 1)
        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None

        configuration = AlgorithmConfiguration()
        configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)
        configuration.grouping_frequency(Frequency.WEEKLY, 1)
        algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                    name="device_visit_sdk_test_config",
                                                                    description="A test configuration.",
                                                                    algorithm_config=configuration)

        assert algorithm_configuration.id is not None

    @pytest.mark.asyncio
    async def test_update(self):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)
        manifest.grouping_frequency("DAILY", 1)
        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None

        configuration = AlgorithmConfiguration()
        configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)
        configuration.grouping_frequency(Frequency.WEEKLY, 1)
        algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                    name="device_visit_sdk_test_config",
                                                                    description="A test configuration.",
                                                                    algorithm_config=configuration)
        assert algorithm_configuration.id is not None

        configuration.grouping_frequency(Frequency.DAILY, 2)

        await sdk.algorithm_config.update(algorithm_config_id=algorithm_configuration.id,
                                          algorithm_config=configuration)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        1,
        10
    ])
    async def test_get(self, config_count):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)

        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        config_ids = []
        for i in range(config_count):
            configuration = AlgorithmConfiguration()
            configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)

            algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                        name="device_visit_sdk_test_config",
                                                                        description="A test configuration.",
                                                                        algorithm_config=configuration)

            assert algorithm_configuration.id is not None
            config_ids.append(algorithm_configuration.id)

        configurations = await sdk.algorithm_config.get(config_ids, pagination=Pagination(page_size=5))
        assert len(config_ids) == config_count == len(configurations)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        10,
        20
    ])
    async def test_list(self, config_count: int):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)

        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        config_ids = []
        search_me = str(uuid.uuid4())
        for i in range(config_count):
            configuration = AlgorithmConfiguration()
            configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)

            algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                        name="device_visit_sdk_test_config",
                                                                        description=search_me,
                                                                        algorithm_config=configuration)

            assert algorithm_configuration.id is not None
            config_ids.append(algorithm_configuration.id)

        configurations = await sdk.algorithm_config.list()
        assert len(configurations) > 0
        configurations = await sdk.algorithm_config.list(algorithm_version_id=algorithm_version.id,
                                                         include_all_versions=True)
        assert len(config_ids) == config_count == len(configurations)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        10
    ])
    async def test_deprecate(self, config_count):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)

        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        config_ids = []
        search_me = str(uuid.uuid4())
        for i in range(config_count):
            configuration = AlgorithmConfiguration()
            configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)

            algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                        name="device_visit_sdk_test_config",
                                                                        description=search_me,
                                                                        algorithm_config=configuration)

            assert algorithm_configuration.id is not None
            config_ids.append(algorithm_configuration.id)

        await sdk.algorithm_config.deprecate(algorithm_config_ids=config_ids)
        configurations = await sdk.algorithm_config.get(ids=config_ids)
        for config in configurations:
            assert config.is_deprecated

    @pytest.mark.asyncio
    @pytest.mark.parametrize("config_count", [
        10
    ])
    async def test_deactivate(self, config_count):
        sdk = TerraScopeSDK()
        name = "device-visits-sdk-integration-test-{}".format(uuid.uuid4())
        display_name = "Device Visits SDK Integration"
        author = "terrascope.sdk.integration@orbitalinsight.com"

        algorithm = await sdk.algorithm.create(name=name,
                                               display_name=display_name,
                                               author=author)
        assert algorithm.id is not None
        assert algorithm.name == name
        assert algorithm.display_name == display_name
        assert algorithm.author == author

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=1,
                                      max_count=1)

        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")

        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm.id,
                                                               algorithm_manifest=manifest)

        assert algorithm_version.id is not None
        config_ids = []
        search_me = str(uuid.uuid4())
        for i in range(config_count):
            configuration = AlgorithmConfiguration()
            configuration.add_data_source(DataType.PINGS.value, DataSource.WEJO)

            algorithm_configuration = await sdk.algorithm_config.create(algorithm_version_id=algorithm_version.id,
                                                                        name="device_visit_sdk_test_config",
                                                                        description=search_me,
                                                                        algorithm_config=configuration)

            assert algorithm_configuration.id is not None
            config_ids.append(algorithm_configuration.id)

        await sdk.algorithm_config.deactivate(algorithm_config_ids=config_ids)
        configurations = await sdk.algorithm_config.get(ids=config_ids)
        for config in configurations:
            assert config.is_deactivated

    @pytest.mark.asyncio
    async def test_delete(self):
        pass


class TestAlgorithmComputation:

    @pytest.mark.asyncio
    async def test_create(self):
        sdk = TerraScopeSDK()

        date_format = "%Y-%m-%dT%H:%M:%SZ"
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime("2019-01-05T01:00:00Z", date_format),
                                    finish=datetime.strptime("2019-01-06T01:00:00Z", date_format))
        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(
            frequency=Frequency.DAILY,
            interval=1))
        toi = await sdk.toi.create(toi_configuration.get())

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))
        await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                             file_path="../resources/aois/geojson/basic_factory_phillips_66.geojson")

        device_visit_algorithm = await sdk.algorithm.create(name="device-visits-{}".format(uuid.uuid4()),
                                                            author="sdk@orbitalinsight.com",
                                                            display_name="Device Visits")

        logging.info(device_visit_algorithm.id)
        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value)
        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])
        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        device_visit_algorithm_version = await sdk.algorithm_version.create(algorithm_id=device_visit_algorithm.id,
                                                                            algorithm_manifest=manifest)

        config = AlgorithmConfiguration()
        config.add_data_source(data_type=DataType.PINGS.value, data_source=DataSource.WEJO)

        device_visit_algorithm_config = await sdk.algorithm_config.create(
            algorithm_version_id=device_visit_algorithm_version.id,
            name="device_visit_test_{}".format(uuid.uuid4()), description="a description", algorithm_config=config)

        algorithm_computation = await sdk.algorithm_computation.create(
            aoi_collection_id=aoi_collection.id,
            toi_id=toi.id,
            algorithm_config_id=device_visit_algorithm_config.id)

        assert algorithm_computation.id is not None

        algorithm_computation = await sdk.algorithm_computation.get([algorithm_computation.id])
        print(algorithm_computation)
        # status = ""
        # while status != "COMPLETED":
        #     pass

    @pytest.mark.asyncio
    async def test_run(self):
        sdk = TerraScopeSDK()

        datetime_format = "%Y-%m-%dT%H:%M:%SZ"
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime("2019-01-05T01:00:00Z", datetime_format),
                                    finish=datetime.strptime("2019-01-06T01:00:00Z", datetime_format))
        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(
            frequency=Frequency.DAILY,
            interval=1
        ))
        toi = await sdk.toi.create(toi_configuration.get())

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))
        await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                             file_path="../resources/aois/geojson/basic_factory_phillips_66.geojson")

        device_visit_algorithm = await sdk.algorithm.create(name="device-visits-{}".format(uuid.uuid4()),
                                                            author="sdk@orbitalinsight.com",
                                                            display_name="Device Visits")

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest factory")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value)
        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])
        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        device_visit_algorithm_version = await sdk.algorithm_version.create(algorithm_id=device_visit_algorithm.id,
                                                                            algorithm_manifest=manifest)

        config = AlgorithmConfiguration()
        config.add_data_source(data_type=DataType.PINGS.value, data_source=DataSource.WEJO)

        device_visit_algorithm_config = await sdk.algorithm_config.create(
            algorithm_version_id=device_visit_algorithm_version.id,
            name="device_visit_test_{}".format(uuid.uuid4()), description="a description", algorithm_config=config)

        algorithm_computation = await sdk.algorithm_computation.create(
            aoi_collection_id=aoi_collection.id,
            toi_id=toi.id,
            algorithm_config_id=device_visit_algorithm_config.id)

        assert algorithm_computation.id is not None

        # RUN ALGORITHM COMPUTATION
        await sdk.algorithm_computation.run([algorithm_computation.id])

    @pytest.mark.asyncio
    async def test_get(self):
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

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))
        await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                             file_path="../resources/aois/geojson/basic_factory_phillips_66.geojson")

        device_visit_algorithm = await sdk.algorithm.create(name="device-visits-{}".format(uuid.uuid4()),
                                                            author="sdk@orbitalinsight.com",
                                                            display_name="Device Visits")

        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest factory")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value)
        manifest.container_parameters_required(image="orbitalinsight/device_visits:5a579e59",
                                               command=["python",
                                                        "/orbital/base/algorithms/device_visits/src/py/"
                                                        "device_visits/device_visits.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])
        manifest.parameter_add(name="look_back_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.parameter_add(name="look_forward_time", type="integer", default=3600,
                               description="how far to look back")
        manifest.container_parameters_resource_request(memory_gb=5, cpu_millicore=200)
        device_visit_algorithm_version = await sdk.algorithm_version.create(algorithm_id=device_visit_algorithm.id,
                                                                            algorithm_manifest=manifest)

        config = AlgorithmConfiguration()
        config.add_data_source(data_type=DataType.PINGS.value, data_source=DataSource.WEJO)

        device_visit_algorithm_config = await sdk.algorithm_config.create(
            algorithm_version_id=device_visit_algorithm_version.id,
            name="device_visit_test_{}".format(uuid.uuid4()), description="a description", algorithm_config=config)

        algorithm_computation = await sdk.algorithm_computation.create(
            aoi_collection_id=aoi_collection.id,
            toi_id=toi.id,
            algorithm_config_id=device_visit_algorithm_config.id)

        assert algorithm_computation.id is not None

        # RUN ALGORITHM COMPUTATION
        await sdk.algorithm_computation.run([algorithm_computation.id])

        algorithm_computation = await sdk.algorithm_computation.get([algorithm_computation.id])
        assert algorithm_computation is not None
