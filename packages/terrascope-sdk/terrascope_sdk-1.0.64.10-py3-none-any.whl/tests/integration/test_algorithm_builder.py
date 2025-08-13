import pytest

from google.protobuf.json_format import MessageToDict
from terrascope.sdk.builder.algorithm import AlgorithmManifest, InterfaceType, DataType


class TestAlgorithmManifest:
    @pytest.mark.asyncio
    async def test_algorithm_manifest(self):
        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.PINGS.value,
                                      min_count=2)

        manifest.container_parameters_required(image="orbitalinsight/raw_foottraffic:84c76f7f",
                                               command=["python",
                                                        "/orbital/base/algorithms/"
                                                        "raw_foottraffic/src/py/raw_foottraffic/simple_foottraffic.py"])
        manifest.outputs_add_data_type(data_type_name="device_visits",
                                       observation_value_columns=["unique_device_count"])

        manifest_struct = manifest.get()
        print(manifest_struct)

    @pytest.mark.asyncio
    async def test_algorithm_manifest_imagery(self):
        manifest = AlgorithmManifest()
        manifest.metadata_required(description="Testing algo manifest builder for imagery")
        manifest.interface_required(interface_type=InterfaceType.FILESYSTEM_TASK_WORKER.value)
        manifest.inputs_add_data_type(data_type_name=DataType.OPTICAL_IMAGERY.value, parameters={"image_processing_spec": "PL-SkySatCollect"})
        manifest.container_parameters_required(image="orbitalinsight/skysat_ship_detector:1a354abc",
                                               command=["python",
                                                        "/orbital/base/algorithms/skysat_ship/src/py/skysat_ship_detector/simple_inference.py"])
        manifest.outputs_add_data_type(data_type_name="object_detection", observation_value_columns=["count"])

        manifest_json = MessageToDict(manifest.get())
        assert manifest_json["metadata"] == {"description": "Testing algo manifest builder for imagery"}
        assert manifest_json["interface"] == {"interface_type": InterfaceType.FILESYSTEM_TASK_WORKER.value}
        assert manifest_json["inputs"] == [{"data_type_name": DataType.OPTICAL_IMAGERY.value, "parameters": {"image_processing_spec": "PL-SkySatCollect"}}]
        assert manifest_json["container_parameters"]["image"] ==  "orbitalinsight/skysat_ship_detector:1a354abc"
        assert manifest_json["container_parameters"]["command"] == ["python","/orbital/base/algorithms/skysat_ship/src/py/skysat_ship_detector/simple_inference.py"]
        assert manifest_json["outputs"] == {"observation_value_columns": ["count"], "output_data_types": ["object_detection"]}
