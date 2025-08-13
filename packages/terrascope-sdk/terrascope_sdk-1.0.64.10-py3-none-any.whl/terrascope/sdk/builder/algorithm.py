import logging
from enum import Enum
from typing import List, Dict

from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct

from terrascope.sdk.builder.toi import Frequency


class DataType(Enum):
    PINGS = "pings"
    DEVICE_TRACKS = "device_tracks"
    DEVICE_VISITS = "device_visits"
    OPTICAL_IMAGERY = "optical_imagery"
    OBJECT_DETECTION = "object_detection"
    MULTICLASS_OBJECT_DETECTION = "multiclass_object_detection"
    SPOT_MOSAIC = "spot_mosaic"
    PSSCENE = "psscene"
    SKYSAT = "skysat"
    POPULATION = "population"
    PROXIMITY_ZONE_UDC = "proximity_zone_udc"
    HEURISTIC_JUMPS = "heuristic_jumps"
    NAVIGATIONAL_QUALITY_INDICATORS = "navigational_quality_indicators"
    GNSS_CLUSTERS = "gnss_clusters"
    CROP_CIRCLES = "crop_circles"
    TRACEABILITY_CLUSTERS = "traceability_clusters"
    TRACEABILITY_HEATMAP = "traceability_heatmap"
    UDC_HEATMAP = "unique_device_count_heatmap"
    UDC = "unique_device_count"
    AIRBUS_PLEIADES = "airbus_pleiades"
    PLANET_PSSCENE4BAND = "planet_PSScene4Band"


class DataSource(Enum):
    # Ping Sources
    GEOLOCATION = "geolocation_pings"
    SAFEGRAPH = "safegraph_pings"
    XMODE = "xmode_pings"
    CUEBIQ = "cuebiq_pings"
    BLOGWATCHER = "blogwatcher_pings"
    SPIRE = "spire_pings"
    SPIRE_NMEA = "spire-nmea_pings"
    CUEBIQ_WORKBENCH = "cuebiq-workbench_pings"
    WEJO = "wejo_pings"
    HAWKEYE360 = "hawkeye360_pings"
    OTONOMO = "otonomo_pings"
    ADSBX = "adsbx_pings"
    EXACTEARTH = "exact-earth_pings"
    EXACTEARTH_NMEA = "exact-earth_nmea-pings"

    # Imagery Sources
    IMAGERY = "imagery_imagery"
    PLANET_REORTHOTILE = "planet_REOrthoTile"
    PLANET_PSORTHOTILE = "planet_OSOrthoTile"
    PLANET_PSSCENE4BAND = "planet_PSScene4Band"
    # PLANET_PSSCENE4BAND = "PL-PSScene4Band"
    PLANET_SKYSATSCENE = "planet_SkySatScene"
    PLANET_SKYSATCOLLECT = "planet_SkySatCollect"
    AIRBUS_SPOT7 = "airbus_SPOT7"
    AIRBUS_PHR1A = "airbus_PHR1A"
    AIRBUS_PHR1B = "airbus_PHR1B"
    AIRBUS_PLEIADES = "airbus_pleiades"
    MAXAR_WORLDVIEW_2 = "maxar_Worldview_02"
    AIRBUS_SPOT = "airbus_SPOT"


class ReleaseStatus(Enum):
    DEV = "DEV"
    QA = "QA"
    STAGE = "STAGE"
    PROD = "PROD"


class InterfaceType(Enum):
    SYNCHRONOUS_TASK_HTTP_WORKER = "SYNCHRONOUS_TASK_HTTP_WORKER"
    FILESYSTEM_TASK_WORKER = "FILESYSTEM_TASK_WORKER"
    NO_OP_WORKER = "NO_OP_WORKER"


class ParallelType(Enum):
    AOI = "AOI"
    TIME_RANGE = "TIME_RANGE"


class PermissionType(Enum):
    ALLOWED = 'Allowed'
    DISALLOWED = 'Disallowed'


class AlgorithmManifest:
    """
    This is a basic builder to help build a factories in a safe way instead of managing json configuration
    files. This includes all the methods to incrementally build out an algorithm manifest proto struct that can be
    used for an algorithm.

    REQUIRED Methods:
    The following methods have to be run in sequence. I don't have a better way to do this yet so for now we will just
    call these methods. Each time a new algorithm manifest is need use the following sequence.
    - metadata_required()
    - interface_required()
    - inputs_add_data_type(): can call this more than once, need AT LEAST 1
    - container_parameters_required()
    - outputs_add_data_type(): can call more than once, need AT LEAST 1

    """

    def __init__(self):
        self.__metadata = {
            "metadata": {}
        }
        self.__interface = {
            "interface": {}
        }
        self.__inputs = []
        self.container_parameters = {
            "container_parameters": {}
        }
        self.__parameters = {
            "parameters": []
        }
        self.__grouping = {
            "grouping": {}
        }
        self.__parallelization = {
            "parallelization": []
        }
        self.__restrictions = {
            "restrictions": {}
        }
        self.__outputs = []
        self.__performance_metrics = {
            "performance_metrics": {}
        }
        self.__manifest_version = {
            "manifest_version": "0.1.0"
        }
        self.__required = {
            "metadata": {
                "description": False,
            },
            "interface": {
                "interface_type": False
            },
            "inputs": False,
            "container_parameters": {
                "image": False,
                "command": False
            },
            "outputs": False,
            "manifest_version": True,
        }

    # Metadata
    def metadata_required(self, description: str):
        self.metadata_description(description=description)

    def manifest_version(self, manifest_version: str):
        self.__manifest_version['manifest_version'] = manifest_version
        self.__required['manifest_version'] = True

    def metadata_description(self, description: str):
        self.__metadata['metadata']['description'] = description
        self.__required['metadata']['description'] = True

    def metadata_indicator(self, indicator: str):
        self.__metadata['metadata']['indicator'] = indicator

    def metadata_tags(self, tags: List):
        self.__metadata['metadata']['tags'] = tags

    # Interface
    def interface_required(self, interface_type: str):
        self.interface_interface_type(interface_type=interface_type)

    def interface_interface_type(self, interface_type: str):
        self.__interface['interface']["interface_type"] = interface_type
        self.__required['interface']['interface_type'] = True

    def interface_adapter(self, adapter: str):
        self.__interface['interface']['adapter'] = adapter

    # Inputs
    def inputs_add_data_type(self, data_type_name: str, **kwargs):
        """
        [REQUIRED]

        Adds data types this algorithm is allowed to have as inputs.

        :param data_type_name:
        :param kwargs:
        :return:
        """
        entry = {
            "data_type_name": data_type_name
        }
        for key in ['min_count', 'max_count', 'parameters', 'bands', 'data_source_ids']:
            if key in kwargs.keys():
                entry[key] = kwargs[key]

        self.__inputs.append(entry.copy())
        self.__required['inputs'] = True

    # Container Parameters
    def container_parameters_required(self, image: str, command: List):
        self.container_parameters_image(image=image)
        self.container_parameters_command(command=command)

    def container_parameters_image(self, image: str):
        self.container_parameters['container_parameters']['image'] = image
        self.__required['container_parameters']['image'] = True

    def container_parameters_command(self, command: List):
        self.container_parameters['container_parameters']['command'] = command
        self.__required['container_parameters']['command'] = True

    def container_parameters_resource_request(self, **kwargs):
        if 'resource_request' not in self.container_parameters['container_parameters'].keys():
            self.container_parameters['container_parameters']['resource_request'] = {}

        for resource_request_key in ['gpu', 'memory_gb', 'cpu_millicore', 'max_input_gb']:
            if resource_request_key in kwargs.keys():
                self.container_parameters['container_parameters']['resource_request'][resource_request_key] = kwargs[resource_request_key]

    # Parameters
    def parameter_add(self, **kwargs):
        assert 'description' in kwargs.keys()
        entry = {}
        if 'name' in kwargs.keys():
            entry['name'] = kwargs['name']
        if 'type' in kwargs.keys():
            entry['type'] = kwargs['type']
        if 'unit' in kwargs.keys():
            entry['unit'] = kwargs['unit']
        if 'description' in kwargs.keys():
            entry['description'] = kwargs['description']
        if 'min' in kwargs.keys():
            entry['min'] = kwargs['min']
        if 'max' in kwargs.keys():
            entry['max'] = kwargs['max']
        if 'allowed_values' in kwargs.keys():
            entry['allowed_values'] = kwargs['allowed_values']
        if 'default' in kwargs.keys():
            entry['default'] = kwargs['default']

        self.__parameters['parameters'].append(entry.copy())

    # Grouping
    def grouping_frequency(self, frequency: str, value: int):
        assert isinstance(value, int)
        assert isinstance(frequency, str)
        self.__grouping['grouping']['frequency'] = frequency
        self.__grouping['grouping']['value'] = value

    # Parallelization
    def parallelization_add_configuration(self, config: Dict):
        self.__parallelization['parallelization'].append(config)

    # Restrictions
    def restriction_spatial(self, permission_type: PermissionType,
                            overridable: bool,
                            geometry):
        self.__restrictions['spatial_restriction']['permission_type'] = permission_type
        self.__restrictions['spatial_restriction']['overridable'] = overridable
        self.__restrictions['spatial_restriction']['geometry'] = geometry

    def restriction_temporal_restriction(self, tois: List):
        self.__restrictions['temporal_restriction'] = tois

    def restriction_size(self):
        # TODO
        pass

    def outputs_add_data_type(self, data_type_name: str, **kwargs):
        """
        Adds data types this algorithm is allowed to have as outputs.
        """
        entry = {
            "data_type_name": data_type_name
        }
        if 'observation_value_columns' in kwargs.keys():
            entry['observation_value_columns'] = kwargs['observation_value_columns']
        if 'sample_result' in kwargs.keys():
            entry['sample_result'] = kwargs['sample_result']
        if 'classes' in kwargs.keys():
            entry['classes'] = kwargs['classes']
        if 'output_geometry' in kwargs.keys():
            entry['output_geometry'] = kwargs['output_geometry']
        if 'skip_export' in kwargs.keys():
            entry['skip_export'] = kwargs['skip_export']

        self.__outputs.append(entry.copy())
        self.__required['outputs'] = True

    # Performance Metrics

    def get(self) -> Struct:
        """
        Description:

        Once your manifest is built, use this method to pass the manifest into your TerraScope API Calls.
        This will construct the proper format for that, and check that all the required fields are present.

        :return: An Algorithm Manifest
        """
        manifest = Struct()
        manifest.update(self.__metadata)
        manifest.update(self.__interface)
        manifest.update({"inputs": self.__inputs})
        manifest.update(self.container_parameters)
        manifest.update({"outputs": self.__outputs})
        manifest.update(self.__manifest_version)

        if len(self.__performance_metrics) > 0:
            manifest.update(self.__parameters)
        if len(self.__grouping.keys()) > 0:
            manifest.update(self.__grouping)
        if self.__parallelization['parallelization']:
            manifest.update(self.__parallelization)
        if len(self.__restrictions.keys()) > 0:
            manifest.update(self.__restrictions)
        if len(self.__performance_metrics.keys()) > 0:
            manifest.update(self.__performance_metrics)

        for outer_key in self.__required.keys():
            if isinstance(outer_key, Dict):
                for inner_key in outer_key.keys():
                    if not self.__required[outer_key][inner_key]:
                        logging.info("[{} : {}] - was not set, and is required.".format(outer_key, inner_key))
                        assert self.__required[outer_key][inner_key]
            else:
                if not self.__required[outer_key]:
                    logging.info("[{}] - was not set, and is required.".format(outer_key))
                    assert self.__required[outer_key]

        return manifest


class AlgorithmConfiguration:

    def __init__(self):
        """
        This is an Algorithm Configuration Factory. The purpose is to simplify building an algo configuration struct.
        When creating an algorithm config, specifying a data source is required. Optionally, you may also specify
        modifications to algorithm parameters that were set in the algorithm manifest.

        Defaults:
            - Grouping Frequency: DAILY, 1
        """
        self.__required = {
            "data_sources": False,
            "grouping": False
        }
        self.__algorithm_parameters = {
            "parameters": {}
        }
        self.__grouping = {
            "grouping": {}
        }
        self.__data_sources = []
        self.__outputs = []
        # Any additional configuration
        self.__additional_configuration = {}
        # Set Default grouping frequency
        self.grouping_frequency(Frequency.DAILY, 1)

    def add_data_source(self, data_type: str, **kwargs):

        data_source = kwargs.pop('data_source', None)
        data_sources = kwargs.pop('data_sources', [])
        if data_source and data_sources:
            logging.error("Only specify either data_source or data_sources for add_data_source.")
            return
        if data_source is not None:
            data_sources.append(data_source)

        for source in self.__data_sources:
            # Check if Data Type and Data Source combination Exists
            if source['data_type_name'] == data_type:
                for source_id in source['data_source_ids']:
                    for data_source in data_sources:
                        if source_id == data_source.value:
                            logging.info("data source [{}] already registered.".format(data_source))
                            return

        data_parameters = kwargs.pop('data_parameters', None)
        new_data_source = {
            "data_type_name": data_type,
            "data_source_ids": [data_source.value for data_source in data_sources]
        }
        new_data_source.update(kwargs)
        if data_parameters is not None:
            new_data_source.update({
                "parameters": data_parameters
            })
        self.__data_sources.append(new_data_source)

        self.__required['data_sources'] = True

    def update_output_data_type(self, data_type: str, skip_export: bool = False,
                                observation_value_columns: List[str] = None, data_transfer_params: Dict = None):
        data_type_updated = False
        observation_value_columns = observation_value_columns if observation_value_columns else []
        data_transfer_params = data_transfer_params if data_transfer_params else {}
        for source in self.__outputs:
            if source['data_type_name'] == data_type:
                data_type_updated = True
                source['skip_export'] = skip_export
                source['observation_value_columns'] = observation_value_columns
                source['data_transfer'] = data_transfer_params

        if not data_type_updated:
            self.__outputs.append({
                'data_type_name': data_type,
                'skip_export': skip_export,
                'observation_value_columns': observation_value_columns,
                'data_transfer': data_transfer_params
            })

    def add_algorithm_parameter(self, key: str, value):
        for param in self.__algorithm_parameters['parameters'].keys():
            if key == param:
                assert key != param

        self.__algorithm_parameters['parameters'][key] = value

    def update_configuration(self, configuration: Dict):
        self.__additional_configuration.update(configuration)

    # Grouping
    def grouping_frequency(self, frequency: Frequency, value: int):
        assert isinstance(frequency, Frequency)
        assert isinstance(value, int)
        self.__grouping['grouping']['frequency'] = Frequency(frequency).name
        self.__grouping['grouping']['value'] = value
        self.__required['grouping'] = True

    def get(self) -> Struct:
        """
        Description:

        Once your manifest is built, use this method to pass the manifest into your TerraScope API Calls.
        This will construct the proper format for that, and check that all the required fields are present.

        :return: An Algorithm Configuration as struct_pb2.Struct
        """

        for key in self.__required.keys():
            if not self.__required[key]:
                logging.info("[{}] - was not set, and is required.".format(key))
                assert self.__required[key]

        algorithm_config = Struct()
        algorithm_config.update({"data_sources": self.__data_sources})
        algorithm_config.update({"outputs": self.__outputs})
        algorithm_config.update(self.__algorithm_parameters)
        algorithm_config.update(self.__grouping)
        algorithm_config.update(self.__additional_configuration)

        MessageToDict(algorithm_config)
        return algorithm_config
