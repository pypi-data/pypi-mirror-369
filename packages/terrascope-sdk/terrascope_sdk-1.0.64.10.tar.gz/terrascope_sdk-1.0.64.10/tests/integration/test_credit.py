import logging
import uuid
from datetime import datetime

import pytest

from terrascope.sdk.builder.toi import TOIBuilder, TOIRuleBuilder, Frequency
from terrascope.sdk.builder.algorithm import (
    AlgorithmManifest, InterfaceType, DataType, AlgorithmConfiguration, DataSource
)
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestCredit:
    @pytest.mark.asyncio
    async def test_estimate(self):
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
        manifest.metadata_required(description="Testing algo manifest builder", version="0.0.1")
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

        await sdk.credit.set_algorithm(algorithm_version_id=device_visit_algorithm_version.id,
                                       algorithm_execution_price=0.01,
                                       algorithm_value_price=0.01)

        config = AlgorithmConfiguration()
        config.add_data_source(data_type=DataType.PINGS.value, data_source=DataSource.WEJO)

        device_visit_algorithm_config = await sdk.algorithm_config.create(
            algorithm_version_id=device_visit_algorithm_version.id,
            name="device_visit_test_{}".format(uuid.uuid4()), description="a description", algorithm_config=config)

        algorithm_computation = await sdk.algorithm_computation.create(
            aoi_collection_id=aoi_collection.id,
            toi_id=toi.id,
            algorithm_config_id=device_visit_algorithm_config.id)

        credit_estimate = await sdk.credit.estimate(algorithm_computation_id=algorithm_computation.id)
        logging.info("credit estimate: {}".format(credit_estimate))
        assert credit_estimate is not None

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize("credit_estimate_count", [
    #     1,
    #     10,
    #     25,
    #     45
    # ])
    # async def test_add(self):
    #     sdk = TerraScopeSDK()
    #     credit_source_id = ''
    #     amount = 0
    #     reason = ''
    #
    #     await sdk.credit.add(credit_source_id=credit_source_id, amount=amount, reason=reason)
    #     # there is no response --- oi.papi.EmptyResponse
    #
    #     # TODO: call test_summary before and after credit
    #     # has been added and verify the difference equals
    #     # credit value
    #
    # async def test_remove(self):
    #     sdk = TerraScopeSDK()
    #     credit_source_id = ''
    #     amount = 0
    #     reason = ''
    #
    #     await sdk.credit.remove(credit_source_id=credit_source_id, amount=amount, reason=reason)
    #     # there is no response --- oi.papi.EmptyResponse
    #
    #     # TODO: call test_summary before and after
    #     # verify difference equal credit value removed
    #
    # async def test_refund(self):
    #     sdk = TerraScopeSDK()
    #     credit_source_id = ''
    #     amount = 0
    #     reason = ''
    #
    #     await sdk.credit.refund(credit_source_id=credit_source_id, amount=amount, reason=reason)
    #     # there is no response --- oi.papi.EmptyResponse
    #
    #     # TODO: check everything is good
    #
    # async def test_summary(self):
    #     sdk = TerraScopeSDK()
    #     # TODO : fill in credit_source_id
    #     credit_source_id = ''
    #
    #     credit = await sdk.credit.summary(credit_source_id=credit_source_id)
    #
    #     assert credit.credit_source_id == credit_source_id
    #     assert credit.credit_available is not None
    #     assert credit.credit_reserved is not None
    #     assert credit.credit_used is not None
    #
    # async def test_transactions(self):
    #     sdk = TerraScopeSDK()
    #
    #     # TODO need to fill in fields below
    #     # pagination is object oi.papi.Pagination
    #     # https://sphinx.core3.orbitalinsight.io/oi_papi/latest/api-docs/creditApi.html#oi.papi.Pagination
    #     pagination = ''
    #     credit_source_id = ''
    #     # transaction type is TransactionType
    #     # https://sphinx.core3.orbitalinsight.io/oi_papi/latest/api-docs/creditApi.html#oi.papi.credit.TransactionType
    #     transaction_type = ''
    #     # google.protobuf.Timestamp
    #     start_date = ''
    #     # google.protobuf.Timestamp
    #     end_date = ''
    #     algorithm_computation_id = ''
    #
    #     credit = await sdk.credit.transactions(pagination=pagination, credit_source_id=credit_source_id,
    #                                            transaction_type=transaction_type,
    #                                            start_date=start_date, end_date=end_date,
    #                                            algorithm_computation_id=algorithm_computation_id)
    #
    #     # TODO : figure out how to handle paginated responses
    #     # Response fields in Transaction object are:
    #     assert id === ''
    #     assert credit_source_id = ''
    #     assert user_id == ''
    #     assert transaction_type == ''
    #     assert amount == 0
    #     assert reason == ''
    #     assert transaction_ts == ''
    #     assert credit_available == 0
    #     assert credit_reserved == 0
    #     assert credit_used == 0
    #     assert algorithm_computation_id == ''
    #
    # async def test_set_algorithm(self):
    #     sdk = TerraScopeSDK()
    #
    #     algorithm_version_id = ''
    #     algorithm_execution_price = 0
    #     algorithm_value_price = 0
    #
    #     await sdk.credit.set_algorithm(algorithm_version_id=algorithm_version_id,
    #                                    algorithm_execution_price=algorithm_execution_price,
    #                                    algorithm_value_price=algorithm_value_price)
    #     # there is no response --- oi.papi.EmptyResponse
    #     # TODO: Check that algorithm was properly set
    #
    # async def test_set_data_source(self):
    #     sdk = TerraScopeSDK()
    #     data_source_id = ''
    #     data_source_price = 0
    #
    #     await sdk.credit.set_data_source(data_source_id=data_source_id, data_source_price=data_source_price)
    #     # there is no response --- oi.papi.EmptyResponse
    #     # TODO: Check that data source was properly set
