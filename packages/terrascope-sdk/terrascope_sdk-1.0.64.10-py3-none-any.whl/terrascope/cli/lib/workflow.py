import logging
import os
import re
import uuid
from datetime import datetime
import shapely.wkt as shp_wkt
import pandas as pd
from google.protobuf.timestamp_pb2 import Timestamp

import terrascope.cli.lib.utils as tsu
from terrascope.sdk.builder.algorithm import AlgorithmManifest, AlgorithmConfiguration
from terrascope.sdk.builder.toi import TOIBuilder, TOIRuleBuilder, Frequency
from terrascope.sdk.terrascope_sdk import TerraScopeSDK
from terrascope.sdk.builder.analysis import AnalysisManifest, AnalysisConfiguration
from terrascope_api.models.permission_pb2 import Permission
from terrascope_api.models.resource_pb2 import Resource
from terrascope_api import TerrascopeAsyncClient
from typing import List


VALUE_PRICE_DEFAULT = 0.01
EXECUTION_PRICE_DEFAULT = 0.01


############################################################################
# Init
############################################################################
def check_environment_complete(raise_on_failure=False, print_missing=True, verbose=False, requires_admin=False):
    """
    Check that the required environment parameters are present.

    This function checks whether the required environment parameters are present
    and meets the specified conditions.

    Args:
        raise_on_failure (bool, optional): If True, raise an exception if any required parameter is missing.
            Defaults to False.
        print_missing (bool, optional): If True, print the names of missing parameters to the console.
            Defaults to True.

    Returns:
        bool: True if all required parameters are present; False otherwise.

    Raises:
        EnvironmentError: Raised if raise_on_failure is True and any required parameter is missing.
    """

    missing = set()
    required_environment = ['TERRASCOPE_API_HOST', 'TERRASCOPE_API_TOKEN', 'TERRASCOPE_AUTHOR']
    if requires_admin:
        required_environment.append('TERRASCOPE_API_ADMIN_TOKEN')
    var_list = []
    for var in required_environment:
        value = os.getenv(var, None)
        var_list.append([var, value])
        if value is None:
            missing.add(var)
    df = pd.DataFrame(var_list, columns=['Variable', 'Value'])
    if verbose:
        print('')
        print(df)
        print('')

    if missing:
        msg = "The following required environment variables are missing:\n"
        for var in sorted(missing):
            msg += f"--> {var}"

        if print_missing:
            print(msg)
            print('')

        if raise_on_failure:
            raise EnvironmentError(f"Missing environment variables. [{','.join(missing)}]")

    return len(missing) == 0


############################################################################
# Manifest
############################################################################
def check_manifest_complete(manifest_dict, print_message=False):
    """
    Check if the provided manifest dictionary is complete.

    This function examines the given manifest dictionary to ensure that it contains
    all the required fields for proper functionality.

    Args:
        manifest_dict (dict): The dictionary representing the manifest.
            This dictionary should contain specific fields for proper validation.
        print_message (bool, optional): Whether to print a message about the completion status.
            Defaults to False.

    Returns:
        bool: True if the manifest is complete, False otherwise.
    """

    # This whole thing is ugly ... do this more nicely!

    required = {
        'container_parameters': ['image', 'command'],
        'metadata': ['description', ],
        'interface': ['interface_type'],
        'inputs': [['data_type_name']],
        'outputs': [['data_type_name']],
    }

    out_str = ''
    for param, subparams in required.items():
        if param not in manifest_dict:
            out_str += f'--> {param:40s} MISSING\n'
        else:
            out_str += f'--> {param:40s} OK\n'
            for subparam in subparams:
                # junky hack for inputs.data_type_name
                manifest_check_field = manifest_dict[param]
                if isinstance(subparam, list):
                    subparam = subparam[0]
                    manifest_check_field = manifest_check_field[0]

                if subparam not in manifest_check_field:
                    out_str += f'--> {param+"."+subparam:40s} MISSING\n'
                else:
                    out_str += f'--> {param+"."+subparam:40s} OK\n'
    if 'MISSING' in out_str:
        if print_message:
            print(out_str)
        return False
    return True


def update_manifest_docker_hash(manifest, docker_version_hash=None):
    """Update the Docker version hash in the given manifest dictionary.

    This function allows updating the Docker version hash in the provided manifest
    dictionary. If a new Docker version hash is provided, it will be assigned to
    the 'docker_hash' field in the manifest.

    Args:
        manifest (dict): The dictionary representing the manifest.
            This dictionary is expected to have a container_parameters.image field for updating.
        docker_version_hash (str, optional): The new Docker version hash to assign.
            If not provided, the 'docker_hash' field in the manifest will be cleared.

    Returns:
        image (str): The full image name of the docker image.

    Raises: RuntimeError: Raised if the input docker version hash is
        not present in the manifest, and is not provided as an input
        argument 'docker_version_hash'.
    """

    # replace the docker version hash in the manifest, if one is provided
    params = manifest['container_parameters']
    if docker_version_hash:
        image = params['image']
        image = image.rstrip(":.*") + f":{docker_version_hash}"
        params['image'] = image
    else:
        if ':' not in params['image']:
            raise RuntimeError('Missing docker hash. Not in manifest->container_parameters.image, and none provided')

    return params['image']


def create_algorithm_manifest(manifest_dict):
    """Create an algorithm Manifest object from a dictionary.

    Args:
        manifest_dict (dict): The dictionary representing the manifest.

    Returns:
        manifest (AlgorithmManifest): The manifest object.
    """

    if not check_manifest_complete(manifest_dict, print_message=True):
        raise RuntimeError("Manifest missing required parameters")

    container_parameters = manifest_dict['container_parameters']
    resource_request = container_parameters['resource_request']
    metadata = manifest_dict['metadata']
    interface = manifest_dict['interface']
    inputs = manifest_dict['inputs']
    outputs = manifest_dict['outputs']
    parallelizations = manifest_dict['parallelization']

    manifest = AlgorithmManifest()

    # metadata
    manifest.metadata_required(description=metadata['description'])
    manifest.metadata_tags(metadata['tags'])

    # container parameters
    manifest.container_parameters_required(image=container_parameters['image'],
                                           command=container_parameters['command'])
    manifest.container_parameters_resource_request(**resource_request)

    # interface
    manifest.interface_required(interface_type=interface['interface_type'])

    # inputs/outputs
    for inp in inputs:
        data_type_name = inp['data_type_name']
        data_type_params = {k: v for k, v in inp.items() if k != 'data_type_name'}
        manifest.inputs_add_data_type(data_type_name=data_type_name, **data_type_params)

    for output in outputs:
        manifest.outputs_add_data_type(**output)

    for parallelization in parallelizations:
        manifest.parallelization_add_configuration(parallelization)

    # manifest.grouping_frequency()

    # parameters
    algorithm_parameters = manifest_dict.get('parameters', [])
    for parameter in algorithm_parameters:
        manifest.parameter_add(**parameter)

    return manifest


def create_analysis_manifest(
        name: str,
        algorithm_version_id: str,
        description: str,
        tags: List,
):
    """
    Create an analysis manifest for a specific algorithm version.

    This function creates an analysis manifest based on the provided information
    about the analysis, algorithm version, and associated details.

    Args:
        name (str): The name of the analysis.
        algorithm_version_id (str): The ID of the algorithm version used for the analysis.
        description (str): A description of the analysis.
        tags (List[str]): A list of tags associated with the analysis.

    Returns:
        manifest (AnalysisManifest): The analysis manifest containing provided information.
    """

    manifest = AnalysisManifest()
    manifest.metadata(description=description, tags=tags)
    manifest.add_node(name, algorithm_version_id)

    return manifest


############################################################################
#  Algorithm
############################################################################
async def get_algorithms(algorithm_ids: List = None):
    """Retrieve information about an algorithm by name.

    This asynchronous function retrieves information about an algorithm.

    Args:
        algorithm_ids (List): The IDs of the algorithms to retrieve.

    Returns:
        List[Algorithm]: A list of Algorithm objects.
    """

    algorithms = []
    sdk = TerraScopeSDK()
    if algorithm_ids is not None:
        algorithms += await sdk.algorithm.get(algorithm_ids=algorithm_ids)
    return algorithms


async def list_algorithms(algorithm_name: str = None):
    """Retrieve information about an algorithm by name.

    This asynchronous function retrieves information about an algorithm, optionally
    filtered by the specified algorithm name.

    Args:
        algorithm_name (str, optional): The name of the algorithm to filter results.
            If provided, only information about the specified algorithm will be retrieved.

    Returns:
        List[Algorithm]: A list of Algorithm objects.
    """

    kwargs = {}
    sdk = TerraScopeSDK()
    if algorithm_name is not None:
        kwargs['search_text'] = algorithm_name
    algorithms = await sdk.algorithm.list(**kwargs)
    return algorithms


async def get_algorithm_versions(algorithm_id: str = None, algorithm_version_id: str = None):
    """
    Retrieve algorithm versions for a specified algorithm_id.

    This asynchronous function retrieves algorithm_versions of a specific algorithm,
    based on its algorithm ID.

    Args:
        algorithm_id (str): The ID of the algorithm for which to retrieve version information.

    Returns:
        List[AlgorithmVersion]: A list of algorithm versions.
    """

    algorithm_versions = []
    sdk = TerraScopeSDK()
    if algorithm_id:
        algorithm_versions += await sdk.algorithm_version.list(algorithm_id=algorithm_id)
    if algorithm_version_id:
        algorithm_versions += await sdk.algorithm_version.get(algorithm_version_ids=[algorithm_version_id])

    return algorithm_versions


async def get_current_algorithm_version(algorithm_id: str):
    """Get the next algorithm version
    """

    algo_versions = await get_algorithm_versions(algorithm_id=algorithm_id)
    if algo_versions:
        data = []
        for algo_version in algo_versions:
            algo_version_dict = tsu.protobuf_to_dict(algo_version)
            data.append(algo_version_dict)

        df = pd.DataFrame(data=data)
        current_version = df['version'].max()
    else:
        current_version = None
    return current_version


async def create_algorithm(name: str, author: str, display_name: str):
    """
    Create a new algorithm.

    This asynchronous function creates a new algorithm with the provided information,
    including the algorithm's name, author, and display name.

    Args:
        name (str): The internal name of the algorithm.
        author (str): The author's name or identifier.
        display_name (str): The display name of the algorithm.

    Returns:
        id(str):  The algorithm ID for the newly created algorithm,
    """
    sdk = TerraScopeSDK()
    algorithm = await sdk.algorithm.create(name=name, author=author,
                                           display_name=display_name)
    logging.info("\"algorithm_id\": \"{}\"".format(algorithm.id))
    return algorithm.id


async def create_algorithm_version(
        algorithm_id: str,
        manifest,
):
    """
    Create a new algorithm version for a specified algorithm_id.

    This asynchronous function creates a new version for an existing algorithm
    with the provided algorithm ID and manifest.

    Args:
        algorithm_id (str): The ID of the algorithm for which to create a new version.
        manifest (AlgorithmManifest): The manifest containing details.

    Returns:
        algorithm_version_id (str): The algorithm_version_id of the newly created algorithm version.
    """

    sdk = TerraScopeSDK()
    algorithm_version = await sdk.algorithm_version.create(algorithm_id=algorithm_id,
                                                           algorithm_manifest=manifest)

    logging.info("\"algorithm_version_id\": \"{}\"".format(algorithm_version.id))
    logging.info("algorithm_sem-version: {}".format(algorithm_version.version))
    return algorithm_version


async def deactivate_algorithm_versions(
        algorithm_version_ids: List[str],
):
    """
    """
    oi_papi_host = os.environ["TERRASCOPE_API_HOST"]
    oi_papi_port_string = os.getenv("TERRASCOPE_API_PORT", default="443")
    oi_papi_port = int(oi_papi_port_string)
    secure_string = os.getenv("TERRASCOPE_API_SECURE", default="True")
    secure = True if secure_string in ["True", "true", "Yes", "yes", "1"] else False
    # admin_api_token = os.environ["TERRASCOPE_API_ADMIN_TOKEN"]

    client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure)
    # admin_client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure, api_token=admin_api_token)

    deactivate_algorithm_versions_request = client.models.algorithm_version_pb2.AlgorithmVersionDeactivateRequest(
        ids=algorithm_version_ids
    )
    deactivate_algo_versions_response = await client.api.algorithm_version.deactivate(
        deactivate_algorithm_versions_request
    )

    return deactivate_algo_versions_response.status_code


async def update_algorithm(
        algorithm_id: str,
        manifest,
        value_price=VALUE_PRICE_DEFAULT,
        execution_price=EXECUTION_PRICE_DEFAULT,
        visualizer_config_names=None,
):
    """
    Update an existing algorithm's information.

    This asynchronous function updates the information of an existing algorithm
    with the provided algorithm ID and manifest. It also allows updating the value
    and execution prices, with default values if not provided.

    Args:
        algorithm_id (str): The ID of the algorithm to update.
        manifest (dict): The updated manifest dictionary with new information.
        value_price (float, optional): The new value price for the algorithm.
            Defaults to VALUE_PRICE_DEFAULT if not provided.
        execution_price (float, optional): The new execution price for the algorithm.
            Defaults to EXECUTION_PRICE_DEFAULT if not provided.
        visualizer_config_names (List, optional): Names of visualizations for this algorithm.

    Returns:
        algorithm_version_id (str): The algorithm_version_id for the algorithm.
    """
    algorithm_version = await create_algorithm_version(algorithm_id, manifest)
    await set_credit(algorithm_version_id=algorithm_version.id,
                     value_price=value_price,
                     execution_price=execution_price)

    visualizer_config_ids = []
    if visualizer_config_names:
        visualizer_config_ids = await create_visualizer_config_algo_version(visualizer_config_names,
                                                                            algorithm_version.id)

    logging.info("\"algorithm_version_id\": \"{}\"".format(algorithm_version.id))
    logging.info("algorithm_sem-version: {}".format(algorithm_version.version))
    logging.info("visualizer_config_names: {}".format(visualizer_config_names))
    logging.info("visualizer_config_ids: {}".format(visualizer_config_ids))
    return algorithm_version.id


async def new_algorithm(
        name,
        author,
        display_name,
        manifest,
        value_price=VALUE_PRICE_DEFAULT,
        execution_price=EXECUTION_PRICE_DEFAULT,
        visualizer_config_names=None,
):
    """
    Create a new algorithm with initial information.

    This asynchronous function creates a new algorithm with the provided information,
    including the algorithm's name, author, display name, manifest, and optional
    value and execution prices.

    Args:
        name (str): The internal name of the algorithm.
        author (str): The author's name or identifier.
        display_name (str): The display name of the algorithm.
        manifest (AlgorithmManifest): The initial manifest object containing version and details.
        value_price (float, optional): The initial value price for the algorithm.
            Defaults to VALUE_PRICE_DEFAULT if not provided.
        execution_price (float, optional): The initial execution price for the algorithm.
            Defaults to EXECUTION_PRICE_DEFAULT if not provided.
        visualizer_config_names (List, optional): Names of visualizations for this algorithm.

    Returns:
        algorithm_version_id (str): The algorithm_version_id.
    """
    algorithm_id = await create_algorithm(name, author, display_name)
    algorithm_version_id = await update_algorithm(algorithm_id,
                                                  manifest,
                                                  value_price=value_price,
                                                  execution_price=execution_price,
                                                  visualizer_config_names=visualizer_config_names)

    return algorithm_id, algorithm_version_id


async def get_algorithm_configs(algorithm_version_id: str = None, algorithm_config_id: str = None):
    """
    Retrieve algorithm configs for a specific algorithm version.

    This asynchronous function retrieves configuration details for a specific algorithm version
    identified by the provided algorithm version ID.

    Args:
        algorithm_version_id (str): The ID of the algorithm version for which to retrieve associated configs.
        algorithm_config_id (str): The ID of the algorithm config to retrieve.

    Returns:
        list(AlgorithmConfig): A list of AlgorithmConfig objects for the specified algorithm version.
    """

    sdk = TerraScopeSDK()
    algorithm_configs = []
    if algorithm_version_id:
        algorithm_configs += await sdk.algorithm_config.list(algorithm_version_id=algorithm_version_id)
    if algorithm_config_id:
        algorithm_configs += await sdk.algorithm_config.get(ids=[algorithm_config_id])

    return algorithm_configs


async def create_algorithm_config(
        algorithm_version_id: str,
        config_name: str,
        config_desc: str,
        data_source,
        data_type: str,
        data_parameters: dict = None,
        visualizer_config_names: list = None,
        **kwargs,
):
    """
    Create a new algorithm config for a specific algorithm version.

    This asynchronous function creates a new algorithm config for a specific algorithm version
    identified by the provided algorithm version ID. The configuration details include the
    configuration name, description, data source, and optional data type.

    Args:
        algorithm_version_id (str): The ID of the algorithm version to which the config belongs.
        config_name (str): The name of the configuration.
        config_desc (str): A description of the configuration.
        data_source: The data source for the configuration.
        data_type (DataType, optional): The data type associated with the configuration.
        visualizer_config_names (list, optional): Names associated with visualizer configurations.

    Returns:
        algorithm_config_id (str): The ID of the newly created algorithm config.
    """
    sdk = TerraScopeSDK()

    if data_source is not None and data_source.value is not None:
        kwargs['data_source'] = data_source

    # Config
    config = AlgorithmConfiguration()
    config.add_data_source(data_type=data_type,
                           data_parameters=data_parameters, **kwargs)

    algorithm_config = await sdk.algorithm_config.create(
        algorithm_version_id=algorithm_version_id,
        name=config_name + f"_{str(uuid.uuid4())[:8]}",
        description=config_desc,
        algorithm_config=config
    )

    visualizer_config_ids = []
    if visualizer_config_names:
        visualizer_config_ids = await create_visualizer_config_algo_config(visualizer_config_names,
                                                                           algorithm_config.id)
    logging.info("\"algorithm_config_id\": \"{}\"".format(algorithm_config.id))
    logging.info("\"visualizer_config_names\": \"{}\"".format(visualizer_config_names))
    logging.info("\"visualizer_config_ids\": \"{}\"".format(visualizer_config_ids))

    return algorithm_config.id


async def deactivate_algorithm_configs(
        algorithm_config_ids: List[str]
):

    oi_papi_host = os.environ["TERRASCOPE_API_HOST"]
    oi_papi_port_string = os.getenv("TERRASCOPE_API_PORT", default="443")
    oi_papi_port = int(oi_papi_port_string)
    secure_string = os.getenv("TERRASCOPE_API_SECURE", default="True")
    secure = True if secure_string in ["True", "true", "Yes", "yes", "1"] else False
    # admin_api_token = os.environ["TERRASCOPE_API_ADMIN_TOKEN"]

    client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure)
    # admin_client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure, api_token=admin_api_token)

    deactivate_algorithm_configs_request = client.models.algorithm_config_pb2.AlgorithmConfigDeactivateRequest(
        ids=algorithm_config_ids
    )
    deactivate_algorithm_configs_response = await client.api.algorithm_config.deactivate(
        deactivate_algorithm_configs_request
    )
    return deactivate_algorithm_configs_response.status_code


############################################################################
#  Analysis
############################################################################
async def get_analyses(analysis_ids: List):
    """
    Retrieve analyses for specified analysis IDs

    This asynchronous function retrieves analysis objects by ID.

    Args:
        analysis_ids (List): The analysis_ids to retrieve.

    Returns:
        List[Analysis]: A list of Analysis objects.
    """
    sdk = TerraScopeSDK()
    analyses = await sdk.analysis.get(ids=analysis_ids)
    return analyses


async def list_analyses(analysis_name: str = None):
    """
    Retrieve analyses, optionally filtered by name.

    This asynchronous function retrieves analysis objects, optionally
    filtered by the specified analysis name.

    Args:
        analysis_name (str, optional): The name of the analysis to filter results.
            If provided, only information about the specified analysis will be retrieved.

    Returns:
        List[Analysis]: A list of Analysis objects.
    """
    kwargs = {}
    sdk = TerraScopeSDK()
    analyses = await sdk.analysis.list(**kwargs)

    # Do not use 'search_text' in kwargs, as that doesn't allow regular expressions
    # just get everything and use regex here
    if analysis_name:
        analyses_matched = []
        for analysis in analyses:
            match_name = re.search(analysis_name, analysis.name)
            match_auth = re.search(analysis_name, analysis.author)
            match_id = re.search(analysis_name, analysis.id)
            if match_name or match_auth or match_id:
                analyses_matched.append(analysis)
        analyses = analyses_matched

    return analyses


async def get_analysis_versions(analysis_version_id: str = None, analysis_id: str = None):
    """
    Retrieve analysis_versions for a specific analysis_id.

    This asynchronous function retrieves information about versions of a specific analysis
    identified by the provided analysis ID.

    Args:
        analysis_id (str): The ID of the analysis for which to retrieve version information.

    Returns:
        List[AnalysisVersion]: A list of analysis versions.
    """
    sdk = TerraScopeSDK()
    analysis_versions = []
    if analysis_id:
        analysis_versions += await sdk.analysis_version.list(analysis_id=analysis_id,
                                                             include_algorithm_details=True, include_manifest=True)
    if analysis_version_id:
        analysis_versions += await sdk.analysis_version.get(ids=[analysis_version_id],
                                                            include_algorithm_details=True, include_manifest=True)

    return analysis_versions


async def get_current_analysis_version(analysis_id: str):
    """Get the current analysis version
    """

    analysis_versions = await get_analysis_versions(analysis_id=analysis_id)
    if analysis_versions:
        data = []
        for analysis_version in analysis_versions:
            analysis_version_dict = tsu.protobuf_to_dict(analysis_version)
            data.append(analysis_version_dict)

        df = pd.DataFrame(data=data)
        current_version = df['analysis_manifest.metadata.version'].max()
    else:
        current_version = None
    return current_version


async def create_analysis(name: str, author: str):
    """
    Create a new analysis.

    This asynchronous function creates a new analysis with the provided name and author.

    Args:
        name (str): The name of the new analysis.
        author (str): The author's name or identifier.

    Returns:
        analysis_id (str):  The ID of the new analysis.
    """
    sdk = TerraScopeSDK()
    analysis = await sdk.analysis.create(name=name, author=author)

    logging.info("\"analysis_id\": \"{}\"".format(analysis.id))
    return analysis.id


async def create_analysis_version(analysis_id: str, manifest):
    """
    Create a new analysis version for an existing analysis.

    This asynchronous function creates a new analysis version for an existing analysis
    identified by the provided analysis ID. The new version is defined by the
    provided manifest.

    Args:
        analysis_id (str): The ID of the analysis for which to create a new version.
        manifest (dict): The manifest dictionary containing version and details.

    Returns:
        analysis_version_id (str): The newly created analysis version ID.
    """
    sdk = TerraScopeSDK()
    analysis_version = await sdk.analysis_version.create(analysis_id=analysis_id,
                                                         analysis_manifest=manifest)

    return analysis_version.id


async def update_analysis(
        analysis_id: str,
        manifest,
        value_price=VALUE_PRICE_DEFAULT,
        execution_price=EXECUTION_PRICE_DEFAULT
):
    """
    Update an existing analysis's information.

    This asynchronous function updates the information of an existing analysis
    identified by the provided analysis ID. It also allows updating the value
    and execution prices, with default values if not provided.

    Args:
        analysis_id (str): The ID of the analysis to update.
        manifest (dict): The updated manifest dictionary with new information.
        value_price (float, optional): The new value price for the analysis.
            Defaults to VALUE_PRICE_DEFAULT if not provided.
        execution_price (float, optional): The new execution price for the analysis.
            Defaults to EXECUTION_PRICE_DEFAULT if not provided.

    Returns:
        analysis_version_id (str):  The analysis_version_id of the updated analysis.
    """

    analysis_version = await create_analysis_version(analysis_id, manifest)
    await set_credit(analysis_version_id=analysis_version.id,
                     value_price=value_price,
                     execution_price=execution_price)
    logging.info("\"analysis_version_id\": \"{}\"".format(analysis_version.id))
    logging.info("analysis_sem-version: {}".format(analysis_version.version))
    return analysis_version.id


async def new_analysis(
        name,
        author,
        display_name,
        manifest,
        value_price=VALUE_PRICE_DEFAULT,
        execution_price=EXECUTION_PRICE_DEFAULT
):
    """
    Create a new analysis with initial information.

    This asynchronous function creates a new analysis with the provided information,
    including the analysis's name, author, display name, manifest, and optional
    value and execution prices.

    Args:
        name (str): The internal name of the analysis.
        author (str): The author's name or identifier.
        display_name (str): The display name of the analysis.
        manifest (Manifest): The initial manifest containing version and details.
        value_price (float, optional): The initial value price for the analysis.
            Defaults to VALUE_PRICE_DEFAULT if not provided.
        execution_price (float, optional): The initial execution price for the analysis.
            Defaults to EXECUTION_PRICE_DEFAULT if not provided.

    Returns:
        analysis_version_id (str): The Analysis Version ID of the newly created analysis,
    """

    analysis_id = await create_analysis(name, author, display_name)
    analysis_version_id = await update_analysis(analysis_id,
                                                manifest,
                                                value_price=value_price,
                                                execution_price=execution_price)

    return analysis_version_id


async def get_analysis_configs(analysis_config_id: str = None, analysis_version_id: str = None):
    """
    Retrieve analysis configs for a specific analysis version.

    This asynchronous function retrieves analysis config details for a specific analysis version
    identified by the provided analysis version ID.

    Args:
        analysis_version_id (str): The ID of the analysis version for which to retrieve configurations.

    Returns:
        list(AnalysisConfig): A list of analysis configs for the specified analysis version ID.
    """

    sdk = TerraScopeSDK()
    analysis_configs = []
    if analysis_config_id:
        analysis_configs += await sdk.analysis_config.get(ids=[analysis_config_id])
    if analysis_version_id:
        analysis_configs += await sdk.analysis_config.list(analysis_version_id=analysis_version_id,
                                                           include_deactivated=True)

    return analysis_configs


async def list_analysis_configs(analysis_config_name: str = None):
    """
    Retrieve analysis configs for a analysis by name / regex

    Args:
        analysis_version_name (str): The name or regex of the analysis config for which to retrieve configurations.

    Returns:
        list(AnalysisConfig): A list of analysis configs for the specified analysis version ID.
    """

    sdk = TerraScopeSDK()
    analysis_configs = []
    analysis_configs += await sdk.analysis_config.list(search_text=analysis_config_name)

    return analysis_configs


async def create_analysis_config(
        analysis_version_id: str,
        algorithm_config_id: str,
        analysis_config_name: str,
        analysis_config_desc: str,
):
    """
    Create a new analysis config for a specific analysis version.

    This asynchronous function creates a new analysis config for a specific analysis version,
    identified by the provided analysis version ID. The configuration details include the
    analysis configuration name, description, associated algorithm configuration ID, and name.

    Args:
        analysis_version_id (str): The ID of the analysis version to which the configuration belongs.
        algorithm_config_id (str): The ID of the associated algorithm configuration.
        analyais_config_name (str): The name of the associated analysis configuration.
        analysis_config_desc (str): A description of the analysis configuration.

    Returns:
        analysis_config_id (str): analysis config Id for the newly created analysis config.
    """

    sdk = TerraScopeSDK()

    analysis = await sdk.analysis_version.get(ids=[analysis_version_id],
                                              include_algorithm_details=True, include_manifest=True)
    node_name = analysis[0].analysis_manifest.algorithm_nodes[0].name

    # Config
    config = AnalysisConfiguration(analysis_version_id=analysis_version_id)
    config.add_config_node(
        name=node_name,
        algorithm_config_id=algorithm_config_id,
    )

    analysis_config = await sdk.analysis_config.create(
        analysis_version_id=analysis_version_id,
        algorithm_config_nodes=config.get(),
        name=analysis_config_name,
        description=analysis_config_desc,
    )

    logging.info("\"analysis_config_id\": \"{}\"".format(analysis_config.id))

    return analysis_config.id


async def deactivate_analysis_configs(
        analysis_config_ids: List[str]
):

    oi_papi_host = os.environ["TERRASCOPE_API_HOST"]
    oi_papi_port_string = os.getenv("TERRASCOPE_API_PORT", default="443")
    oi_papi_port = int(oi_papi_port_string)
    secure_string = os.getenv("TERRASCOPE_API_SECURE", default="True")
    secure = True if secure_string in ["True", "true", "Yes", "yes", "1"] else False
    # admin_api_token = os.environ["TERRASCOPE_API_ADMIN_TOKEN"]

    client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure)
    # admin_client = TerrascopeAsyncClient(oi_papi_host, oi_papi_port, secure=secure, api_token=admin_api_token)

    deactivate_analysis_configs_request = client.models.analysis_config_pb2.AnalysisConfigDeactivateRequest(
        ids=analysis_config_ids
    )
    deactivate_analysis_configs_response = await client.api.analysis_config.deactivate(
        deactivate_analysis_configs_request
    )
    return deactivate_analysis_configs_response.status_code


############################################################################
# Price
############################################################################
async def get_credit(credit_source_id: str):
    """
    Retrieve the credit information for a specific credit source.

    This asynchronous function retrieves the price information associated with a specific
    credit source identified by the provided credit source ID.

    Args:
        credit_source_id (str): The ID of the credit source for which to retrieve price information.

    Returns:
        summary: A credit summary for the specified credit source.
    """
    sdk = TerraScopeSDK()
    summary = await sdk.credit.summary(credit_source_id)
    return summary


async def set_credit(
        algorithm_version_id: str,
        value_price=VALUE_PRICE_DEFAULT,
        execution_price=EXECUTION_PRICE_DEFAULT
):
    """
    Set the credit information for a specific algorithm version.

    This asynchronous function sets the price information for a specific algorithm version
    identified by the provided algorithm version ID. It allows setting both the value price
    and the execution price, with default values if not provided.

    In order this to work, the user must also have the following in their environment.

    export TERRASCOPE_API_ADMIN_TOKEN=<admin_token>

    Args:
        algorithm_version_id (str): The ID of the algorithm version for which to set the price information.
        value_price (float, optional): The new value price for the algorithm version.
            Defaults to VALUE_PRICE_DEFAULT if not provided.
        execution_price (float, optional): The new execution price for the algorithm version.
            Defaults to EXECUTION_PRICE_DEFAULT if not provided.

    Returns:
        None

    """

    terrascope_host = os.environ['TERRASCOPE_API_HOST']
    terrascope_api_admin_token = os.getenv('TERRASCOPE_API_ADMIN_TOKEN')
    assert terrascope_api_admin_token is not None
    client = TerraScopeSDK().create_client(terrascope_host=terrascope_host,
                                           terrascope_api_token=terrascope_api_admin_token)
    sdk = TerraScopeSDK(client=client)
    await sdk.credit.set_algorithm(algorithm_version_id=algorithm_version_id,
                                   algorithm_value_price=value_price,
                                   algorithm_execution_price=execution_price)


############################################################################
# TOI
############################################################################
async def create_toi(
        start: str,
        end: str,
        date_format: str = "%Y-%m-%dT%H:%M:%SZ",
        frequency=Frequency.DAILY,
):
    """
    Create a new time of interest (TOI) object.

    This asynchronous function creates a new time of interest (TOI) object based on the provided
    start and end times, along with optional parameters for date format and frequency.

    Args:
        start (str): The start time of the time of interest (TOI) in the specified date format.
        end (str): The end time of the time of interest (TOI) in the specified date format.
        date_format (str, optional): The date format of the start and end times.
            Defaults to "%Y-%m-%dT%H:%M:%SZ" if not provided.
        frequency (Frequency, optional): The frequency of the time of interest (TOI).
            Defaults to Frequency.DAILY if not provided.

    Returns:
        toi_id (str): The toi_id of the newly created time of interest (TOI) object,
    """
    sdk = TerraScopeSDK()

    toi_configuration = TOIBuilder()
    toi_configuration.build_toi(start=datetime.strptime(start, date_format),
                                finish=datetime.strptime(end, date_format))
    toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(
        frequency=Frequency.DAILY,
        interval=1))
    toi = await sdk.toi.create(toi_configuration.get())
    logging.info("\"toi_id\": \"{}\"".format(toi.id))
    return toi.id


async def get_tois(toi_ids: List):
    """
    Retrieve information about multiple time of interest (TOI) objects.

    This asynchronous function retrieves information about multiple time of interest (TOI) objects
    identified by the provided list of TOI IDs.

    Args:
        toi_ids (List): A list of TOI IDs for which to retrieve information.

    Returns:
        List[Toi]: A list of Toi objects for the requested TOIs.
    """
    sdk = TerraScopeSDK()
    if toi_ids:
        tois = await sdk.toi.get(ids=toi_ids)
    else:
        tois = await sdk.toi.list()
    return tois


async def delete_tois(toi_ids: List):
    """
    Delete multiple time of interest (TOI) objects.

    This asynchronous function deletes multiple time of interest (TOI) objects identified by
    the provided list of TOI IDs.

    Args:
        toi_ids (List): A list of TOI IDs for the TOIs to be deleted.

    Returns:
        None
    """
    sdk = TerraScopeSDK()
    await sdk.toi.delete(ids=toi_ids)


############################################################################
# AOI
############################################################################
async def upload_aoi(aoi_collection_id, file_path):
    """
    Upload an area of interest (AOI) file to a collection.

    This asynchronous function uploads an area of interest (AOI) file specified by the provided
    file path to the given AOI collection identified by its ID.  Only geojson is currently supported.

    Args:
        aoi_collection_id (str): The ID of the AOI collection to which the file will be uploaded.
        file_path (str): The file path to the area of interest (AOI) file to be uploaded.
                         Only geojson is currently supported.

    Returns:
        response: What is this?
    """

    sdk = TerraScopeSDK()
    response = await sdk.aoi.upload(aoi_collection_id=aoi_collection_id,
                                    file_path=file_path)
    return response


async def create_aoi_collection(file_path: str):
    """
    Create a new area of interest (AOI) collection using a file.

    This asynchronous function creates a new area of interest (AOI) collection based on the
    data in the file specified by the provided file path.  Only geojson is currently supported.

    Args:
        file_path (str): The file path to the data file used to create the AOI collection.
                         Only geojson is currently supported.

    Returns:
        aoi_collection_id (str):  The ID of the newly created aoi collection.
    """

    sdk = TerraScopeSDK()
    aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4())[:8])
    await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                         file_path=file_path)
    logging.info("\"aoi_collection_id\": \"{}\"".format(aoi_collection.id))
    return aoi_collection.id


async def get_aoi_collection(aoi_collection_id: str):
    """
    Retrieve information about an area of interest (AOI) collection.

    This asynchronous function retrieves information about an area of interest (AOI) collection
    identified by the provided AOI collection ID.

    Args:
        aoi_collection_id (str): An AOI collection ID for which to retrieve information.

    Returns:
        aoi_collection: The requested AOI collection.

    """
    sdk = TerraScopeSDK()
    if aoi_collection_id is not None:
        aoi_collections = [await sdk.aoi_collection.get(aoi_collection_id)]
    else:
        aoi_collections = await sdk.aoi_collection.list()
    return aoi_collections


async def list_aoi_collections():
    """
    Retrieve information about all area of interest (AOI) collections.

    This asynchronous function retrieves information about area of interest (AOI) collections

    Returns:
        aoi_collections: The requested AOI collection.

    """
    sdk = TerraScopeSDK()
    aoi_collections = await sdk.aoi_collection.list()
    return aoi_collections


async def delete_aois(aoi_ids: List):
    """
    Delete multiple area of interest (TOI) objects.

    This asynchronous function deletes multiple area of interest (TOI) objects identified by
    the provided list of AOI IDs.

    Args:
        aoi_ids (List): A list of AOI IDs for the AOIs to be deleted.

    Returns:
        None
    """
    sdk = TerraScopeSDK()
    await sdk.aoi.delete(aoi_collection_ids=aoi_ids)


############################################################################
# Algorithm Computation
############################################################################
async def create_algorithm_computation(
        algorithm_config_id: str,
        toi_id: str,
        aoi_collection_id: str
):
    """
    Create a new algorithm computation using provided algorithm_config_id, TOI, and AOI collection.

    This asynchronous function creates a new algorithm computation using the provided algorithm configuration,
    time of interest (TOI) ID, and area of interest (AOI) collection ID.

    Args:
        algorithm_config_id (str): The ID of the algorithm configuration to be used in the computation.
        toi_id (str): The ID of the time of interest (TOI) to be used in the computation.
        aoi_collection_id (str): The ID of the area of interest (AOI) collection to be used in the computation.

    Returns:
        algorithm_computation_id (str):  The ID of the newly created algorithm computation.
    """
    sdk = TerraScopeSDK()

    algorithm_computation = await sdk.algorithm_computation.create(
        aoi_collection_id=aoi_collection_id,
        toi_id=toi_id,
        algorithm_config_id=algorithm_config_id
    )

    logging.info("\"algorithm_computation_id\": \"{}\"".format(algorithm_computation))
    return algorithm_computation.id


async def get_algorithm_computation_info(algorithm_computation_ids: List, verbose=False):
    """
    Retrieve information about multiple algorithm computations.

    This asynchronous function retrieves information about multiple algorithm computations identified by
    the provided list of algorithm computation IDs. The verbosity parameter can be used to control
    the level of detail in the returned information.

    Args:
        algorithm_computation_ids (List): A list of algorithm computation IDs for which to retrieve information.
        verbose (bool, optional): If True, detailed information will be printed.
            Defaults to False.

    Returns:
        List[computation]: A list of the requested algorithm computations.
    """
    sdk = TerraScopeSDK()
    algorithm_computations = await sdk.algorithm_computation.get(computation_ids=algorithm_computation_ids)

    for algorithm_computation in algorithm_computations:
        if verbose:
            print("Algorithm Computation: ")
            logging.info(algorithm_computation)
        algorithm_config = await sdk.algorithm_config.get(ids=[algorithm_computation.algo_config_id])
        if verbose:
            print("Algorithm Config: ")
            logging.info(algorithm_config)

    return algorithm_computations


async def run_algorithm_computations(algorithm_computation_ids: List):
    """
    Run algorithm computations for a list of algorithm computation IDs.

    This asynchronous function initiates the execution of algorithm computations for the
    provided list of algorithm computation IDs. The computations will be run asynchronously.

    Args:
        algorithm_computation_ids (List): A list of algorithm computation IDs to run.

    Returns:
        None
    """
    sdk = TerraScopeSDK()
    await sdk.algorithm_computation.run(algorithm_computation_ids=algorithm_computation_ids)

    return None


async def download_algorithm_computation_results(
    algorithm_computation_ids: List[str] = None, analysis_computation_ids: List[str] = None,
    source_aoi_version: int = None, observation_start_ts: str = None, max_observation_start_ts: str = None,
    download_dir: str = None
):
    """
    Download results from a completed algorithm computation.

    This asynchronous function downloads the results from a completed algorithm computation
    identified by the provided algorithm computation ID. The results will be saved to the specified
    file path, with a default name of "test.zip" if not provided.

    Args:
        algorithm_computation_ids (List[str]): The IDs of the completed algorithm computations.
        analysis_computation_ids (List[str]): The IDs of the completed analysis computations

    Returns:
        Dict[str, Dict[str, str]: mapping of algorithm_computation_id_to_data_type_to_merged_file
    """
    sdk = TerraScopeSDK()
    min_observation_start_timestamp = None
    if observation_start_ts:
        min_observation_start_dt = datetime.strptime(observation_start_ts, '%Y-%m-%d')
        min_observation_start_timestamp = Timestamp()
        min_observation_start_timestamp.FromDatetime(min_observation_start_dt)
    max_observation_start_timestamp = None
    if max_observation_start_ts:
        max_observation_start_dt = datetime.strptime(max_observation_start_ts, '%Y-%m-%d')
        max_observation_start_timestamp = Timestamp()
        max_observation_start_timestamp.FromDatetime(max_observation_start_dt)

    algorithm_computation_id_to_data_type_to_downloaded_paths = await sdk.result.download(
        algorithm_computation_ids=algorithm_computation_ids, analysis_computation_ids=analysis_computation_ids,
        source_aoi_version=source_aoi_version, observation_start_ts=min_observation_start_timestamp,
        max_observation_start_ts=max_observation_start_timestamp, download_dir=download_dir
    )
    algorithm_computation_id_to_data_type_to_merged_file = await sdk.result.merge_download_files(
        algorithm_computation_id_to_data_type_to_downloaded_paths, download_dir
    )
    return algorithm_computation_id_to_data_type_to_merged_file


############################################################################
# Analysis Computation
############################################################################
async def create_analysis_computation(
        analysis_config_id: str,
        toi_id: str,
        aoi_collection_id: str
):
    """
    Create a new analysis computation using provided analysis config, TOI, and AOI collection.

    This asynchronous function creates a new analysis computation using the provided analysis configuration,
    time of interest (TOI) ID, and area of interest (AOI) collection ID.

    Args:
        analysis_config_id (str): The ID of the analysis configuration to be used in the computation.
        toi_id (str): The ID of the time of interest (TOI) to be used in the computation.
        aoi_collection_id (str): The ID of the area of interest (AOI) collection to be used in the computation.

    Returns:
        analysis_computation_id (str):  The analysis_computation_id of the newly created analysis computation.
    """
    sdk = TerraScopeSDK()

    analysis_computation = await sdk.analysis_computation.create(
        aoi_collection_id=aoi_collection_id,
        toi_id=toi_id,
        analysis_config_id=analysis_config_id
    )

    logging.info("\"analysis_computation_id\": \"{}\"".format(analysis_computation))
    return analysis_computation.id


async def get_analysis_computation_info(
        min_created_on=None,
        max_created_on=None,
        verbose=False,
        search_text=None,
):
    """
    Retrieve information about multiple analysis computations.

    This asynchronous function retrieves information about multiple analysis computations.
    The verbosity parameter can be used to control the level of detail in the returned information.

    Args:
        verbose (bool, optional): If True, detailed information will be included in the results.
            Defaults to False.

    Returns:
        min_created_on (date): Minimum created_on date to query
        max_created_on (date): Maximum created_on date to query
        List[Computations]: A list of computations.
    """

    kwargs = {}
    enabled = False  # date specs are currently not working in sdk.
    if min_created_on and enabled:
        kwargs['min_created_on'] = min_created_on
    if max_created_on and enabled:
        kwargs['max_created_on'] = max_created_on
    if search_text:
        kwargs['search_text'] = search_text

    sdk = TerraScopeSDK()
    computations = await sdk.analysis_computation.list(**kwargs)

    for computation in computations:
        if verbose:
            print("Analysis Computation: ")
            logging.info(computation)

    return computations


async def run_analysis_computations(analysis_computation_ids: List):
    """
    Run analysis computations for a list of analysis computation IDs.

    This asynchronous function initiates the execution of analysis computations for the
    provided list of analysis computation IDs. The computations will be run asynchronously.

    Args:
        analysis_computation_ids (List): A list of analysis computation IDs to run.

    Returns:
        None
    """
    sdk = TerraScopeSDK()
    await sdk.analysis_computation.run(analysis_computation_ids=analysis_computation_ids)

    return None


############################################################################
# Permissions
############################################################################
async def get_permissions(
        analysis_config_id,
):
    """
    Retrieve permissions associated with an analysis configuration.

    This asynchronous function retrieves the permissions associated with a specific analysis configuration
    identified by the provided analysis configuration ID.

    Args:
        analysis_config_id: The ID of the analysis configuration for which to retrieve permissions.

    Returns:
        List[permission]: A list of the permissions associated with
            the specified analysis configuration.
    """
    sdk = TerraScopeSDK()
    permissions = await sdk.permission.get(analysis_config_ids=[analysis_config_id])
    return permissions


async def resource_permission_create(
        resource_ids: List,
        user_emails: List,
        permission_type=Permission.Type.READ,
        resource_type=Resource.Type.ALGORITHM,
        public=False,
        public_confirm=False,
):
    """
    Grant resource permissions for specified users.

    This asynchronous function creates resource permissions for the specified users, granting them
    the specified permission type on the specified resource IDs. The permissions can be associated
    with different resource types, and there's an option to set the permissions as public.

    In order this to work, the user must also have the following in their environment.

    export TERRASCOPE_API_ADMIN_TOKEN=<admin_token>

    Args:
        resource_ids (List): A list of resource IDs for which to grant permissions.
        user_emails (List): A list of user emails to whom the permissions will be granted.
        permission_type (Permission.Type, optional): The type of permission to grant.
            Defaults to Permission.Type.READ.
        resource_type (Resource.Type, optional): The type of resource for which to grant permissions.
            Defaults to Resource.Type.ALGORITHM.
        public (bool, optional): If True, set the permissions as public. Defaults to False.
        public_confirm (bool, optional): If True, confirm setting permissions as public. Defaults to False.

    Returns:
        None
    """

    if 0:
        terrascope_host = os.environ['TERRASCOPE_API_HOST']
        terrascope_api_admin_token = os.getenv('TERRASCOPE_API_ADMIN_TOKEN')
        assert terrascope_api_admin_token is not None
        client = TerraScopeSDK().create_client(terrascope_host=terrascope_host,
                                               terrascope_api_token=terrascope_api_admin_token)
        sdk = TerraScopeSDK(client=client)
    else:
        sdk = TerraScopeSDK()

    resp = await sdk.permission.create(resource_ids=resource_ids,
                                       permission_type=permission_type,
                                       resource_type=resource_type,
                                       user_ids=user_emails,
                                       public=public,
                                       public_confirm=public_confirm)
    logging.info(f"Status code: {resp.status_code}  public={public}")


async def analysis_permission_create(
        analysis_config_id: str,
        user_emails: List,
        permission_type=Permission.Type.READ,
        public=False,
        public_confirm=False,
        chunk_size=10
):
    """
    Grant analysis configuration permissions for specified users.

    This asynchronous function creates analysis configuration permissions for the specified users,
    granting them the specified permission type on the specified analysis configuration. The permissions
    can be set as public, and the chunk size parameter determines how many permissions are created in
    each batch.

    Args:
        analysis_config_id (str): The ID of the analysis configuration for which to grant permissions.
        user_emails (List): A list of user emails to whom the permissions will be granted.
        permission_type (Permission.Type, optional): The type of permission to grant.
            Defaults to Permission.Type.READ.
        public (bool, optional): If True, set the permissions as public. Defaults to False.
        public_confirm (bool, optional): If True, confirm setting permissions as public. Defaults to False.
        chunk_size (int, optional): The number of permissions to create in each batch.
            Defaults to 10.

    Returns:
        None
    """
    # get the algorithm, algorithm_config, analysis, and analysis_config_id
    sdk = TerraScopeSDK()
    ac = await sdk.analysis_config.get([analysis_config_id], include_algorithm_details=True)
    ac = ac[0]
    algorithms = [f.algorithm.id for f in ac.algorithm_configs]
    algorithm_configs = [f.id for f in ac.algorithm_configs]
    analyses = [ac.analysis_version.analysis.id]

    await resource_permission_create(algorithms, user_emails,
                                     permission_type, Resource.Type.ALGORITHM,
                                     public=public, public_confirm=public_confirm)
    await resource_permission_create(analyses, user_emails,
                                     permission_type, Resource.Type.ANALYSIS,
                                     public=public, public_confirm=public_confirm)
    for algo_configs in tsu.chunk_array(algorithm_configs, chunk_size):
        await resource_permission_create(algo_configs, user_emails,
                                         permission_type, Resource.Type.ALGORITHM_CONFIG,
                                         public=public, public_confirm=public_confirm)
    await resource_permission_create([analysis_config_id], user_emails,
                                     permission_type, Resource.Type.ANALYSIS_CONFIG,
                                     public=public, public_confirm=public_confirm)


############################################################################
# Data
############################################################################
async def list_data_sources():
    """
    Get list of supported data sources.

    """
    sdk = TerraScopeSDK()
    data_sources = await sdk.data_source.list()
    return data_sources


async def create_data_type(
        name: str,
        description: str,
        schema: str,
        data_source_ids: List,
        sensor_type: str
):
    """
    Create a new data type.
    """

    sdk = TerraScopeSDK()
    await sdk.data_type.create(
        name=name,
        description=description,
        schema=schema,
        data_source_ids=data_source_ids,
        sensor_type=sensor_type,
    )


async def list_data_types():
    """
    Get list of supported data types.

    """
    sdk = TerraScopeSDK()
    data_types = await sdk.data_type.list()
    return data_types


############################################################################
# Imagery
############################################################################
async def search_imagery(
        geometry_wkt,
        datetime_start,
        datetime_end,
        data_source_id,
        product_spec_name,
        search_service='SCENE'):
    """
    """
    wkb = shp_wkt.loads(geometry_wkt).wkb
    sdk = TerraScopeSDK()
    scenes = await sdk.imagery.search(
        wkb,
        datetime_start,
        datetime_end,
        data_source_id,
        product_spec_name,
        search_service=search_service
    )
    return scenes


############################################################################
# Visualization
############################################################################

def get_visualizer_config_uuid(visualizer_config_name):

    # This will return the same uuid for the same string.
    visualizer_config_id = str(uuid.uuid5(uuid.NAMESPACE_OID, visualizer_config_name))
    return visualizer_config_id


async def create_visualizer_config_algo_version(
        visualizer_config_names: List,
        algorithm_version_id: str
):

    sdk = TerraScopeSDK()

    visualizer_config_ids = []
    for visualizer_config_name in visualizer_config_names:

        visualizer_config_id = get_visualizer_config_uuid(visualizer_config_name)
        await sdk.visualization.create_visualizer_config_algo_version(visualizer_config_id=visualizer_config_id,
                                                                      algorithm_version_id=algorithm_version_id)
        logging.info(f"Set Visualizer Config: {visualizer_config_name} = {visualizer_config_id}")
        visualizer_config_ids.append(visualizer_config_id)

    return visualizer_config_ids


async def create_visualizer_config_algo_config(
        visualizer_config_names: List,
        algorithm_config_id: str
):

    sdk = TerraScopeSDK()

    visualizer_config_ids = []
    for visualizer_config_name in visualizer_config_names:

        visualizer_config_id = get_visualizer_config_uuid(visualizer_config_name)
        await sdk.visualization.create_visualizer_config_algo_config(visualizer_config_id=visualizer_config_id,
                                                                     algorithm_config_id=algorithm_config_id)
        logging.info(f"Set Visualizer Config: {visualizer_config_name} = {visualizer_config_id}")
        visualizer_config_ids.append(visualizer_config_id)

    return visualizer_config_ids


############################################################################
# Multi-function
############################################################################
async def create_algorithm_computation_aoi_toi(
        algorithm_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format="%Y-%m-%d",
        frequency=Frequency.DAILY,
):
    """
    Create an algorithm computation with AOI and TOI from specified parameters.

    This asynchronous function creates an algorithm computation using the provided algorithm configuration,
    start and end dates for the time of interest (TOI), an AOI file path, and optional parameters for date format
    and frequency.

    Args:
        algorithm_config_id: The ID of the algorithm configuration to be used in the computation.
        start_date: The start date of the time of interest (TOI) in the specified date format.
        end_date: The end date of the time of interest (TOI) in the specified date format.
        aoi_file_path: The file path to the area of interest (AOI) file to be used in the computation.
        date_format (str, optional): The date format of the start and end dates. Defaults to "%Y-%m-%d".
        frequency (Frequency, optional): The frequency of the time of interest (TOI). Defaults to Frequency.DAILY.

    Returns:
        algorithm_computation_id (str): The Algorithm computation ID of the newly created algorithm computation.
    """
    sdk = TerraScopeSDK()

    toi_id = await create_toi(
        start=start_date,
        end=end_date,
        date_format=date_format,
        frequency=frequency,
    )
    aoi_collection_id = await create_aoi_collection(file_path=aoi_file_path)

    algorithm_computation = await sdk.algorithm_computation.create(
        aoi_collection_id=aoi_collection_id,
        toi_id=toi_id,
        algorithm_config_id=algorithm_config_id
    )
    logging.info("----------------------\n")
    return algorithm_computation.id


async def create_analysis_computation_aoi_toi(
        analysis_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format="%Y-%m-%d",
        frequency=Frequency.DAILY,
):
    """
    Create an analysis computation with AOI and TOI from specified parameters.

    This asynchronous function creates an analysis computation using the provided analysis configuration,
    start and end dates for the time of interest (TOI), an AOI file path, and optional parameters for date format
    and frequency.

    Args:
        analysis_config_id: The ID of the analysis configuration to be used in the computation.
        start_date: The start date of the time of interest (TOI) in the specified date format.
        end_date: The end date of the time of interest (TOI) in the specified date format.
        aoi_file_path: The file path to the area of interest (AOI) file to be used in the computation.
        date_format (str, optional): The date format of the start and end dates. Defaults to "%Y-%m-%d".
        frequency (Frequency, optional): The frequency of the time of interest (TOI). Defaults to Frequency.DAILY.

    Returns:
        analysis_computation_id (str):  The analysis computation ID of the newly created analysis computation.
    """
    sdk = TerraScopeSDK()

    toi_id = await create_toi(
        start=start_date,
        end=end_date,
        date_format=date_format,
        frequency=frequency,
    )
    aoi_collection_id = await create_aoi_collection(file_path=aoi_file_path)

    analysis_computation = await sdk.analysis_computation.create(
        aoi_collection_id=aoi_collection_id,
        toi_id=toi_id,
        analysis_config_id=analysis_config_id
    )
    logging.info("----------------------\n")
    return analysis_computation.id


async def create_and_run_algorithm_computation(
        algorithm_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format="%Y-%m-%d",
        frequency=Frequency.DAILY,
):
    """
    Create and run an algorithm computation with AOI and TOI from specified parameters.

    This asynchronous function combines the creation and execution of an algorithm computation using
    the provided algorithm configuration, start and end dates for the time of interest (TOI), an AOI file path,
    and optional parameters for date format and frequency.

    Args:
        algorithm_config_id: The ID of the algorithm configuration to be used in the computation.
        start_date: The start date of the time of interest (TOI) in the specified date format.
        end_date: The end date of the time of interest (TOI) in the specified date format.
        aoi_file_path: The file path to the area of interest (AOI) file to be used in the computation.
        date_format (str, optional): The date format of the start and end dates. Defaults to "%Y-%m-%d".
        frequency (Frequency, optional): The frequency of the time of interest (TOI). Defaults to Frequency.DAILY.

    Returns:
        algorithm_computation_id (str):  The algorithm computation ID of the newly created and (hopefully)
                                         running algorithm computation.
    """
    sdk = TerraScopeSDK()

    algorithm_computation_id = await create_algorithm_computation_aoi_toi(
        algorithm_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format=date_format,
        frequency=frequency,
    )

    await sdk.algorithm_computation.run(
        algorithm_computation_ids=[algorithm_computation_id])

    return algorithm_computation_id


async def create_and_run_analysis_computation(
        analysis_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format="%Y-%m-%d",
        frequency=Frequency.DAILY,
):
    """
    Create and run an analysis computation with AOI and TOI from specified parameters.

    This asynchronous function combines the creation and execution of an analysis computation using
    the provided analysis configuration, start and end dates for the time of interest (TOI), an AOI file path,
    and optional parameters for date format and frequency.

    Args:
        analysis_config_id: The ID of the analysis configuration to be used in the computation.
        start_date: The start date of the time of interest (TOI) in the specified date format.
        end_date: The end date of the time of interest (TOI) in the specified date format.
        aoi_file_path: The file path to the area of interest (AOI) file to be used in the computation.
        date_format (str, optional): The date format of the start and end dates. Defaults to "%Y-%m-%d".
        frequency (Frequency, optional): The frequency of the time of interest (TOI). Defaults to Frequency.DAILY.

    Returns:
        analysis_computation_id (str): The analysis computation ID of the newly created and (hopefully)
                                       running analysis computation.
    """
    sdk = TerraScopeSDK()

    analysis_computation_id = await create_analysis_computation_aoi_toi(
        analysis_config_id,
        start_date,
        end_date,
        aoi_file_path,
        date_format=date_format,
        frequency=frequency,
    )

    await sdk.analysis_computation.run(
        analysis_computation_ids=[analysis_computation_id])

    return analysis_computation_id
