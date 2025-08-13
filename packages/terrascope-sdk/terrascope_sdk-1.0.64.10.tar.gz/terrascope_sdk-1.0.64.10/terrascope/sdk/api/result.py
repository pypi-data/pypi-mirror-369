import os
import re
import boto3
import logging
import tempfile
from zipfile import ZipFile
from typing import Dict, List
from collections import defaultdict
from google.protobuf.timestamp_pb2 import Timestamp

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.common_models_pb2 import Pagination
from terrascope_api.models.result_pb2 import ResultGetRequest, ResultGetResponse, Result


class APIResult:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    @staticmethod
    async def merge_download_files(
        algorithm_computation_id_to_data_type_to_downloaded_paths: Dict[str, Dict[str, List[str]]],
        download_dir: str = None
    ) -> Dict[str, Dict[str, str]]:
        download_dir = os.getcwd() if not download_dir else download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        algorithm_computation_id_to_data_type_to_merged_file = defaultdict(lambda: defaultdict(str))
        for (algorithm_computation_id,
                data_type_to_downloaded_paths) in algorithm_computation_id_to_data_type_to_downloaded_paths.items():
            for data_type, downloaded_paths in data_type_to_downloaded_paths.items():
                merged_file_dir = os.path.join(download_dir, algorithm_computation_id)
                os.makedirs(merged_file_dir, exist_ok=True)
                merged_file = os.path.join(merged_file_dir, f'{data_type}.csv')
                logging.info(f"Merging files for algorithm_computation_id {algorithm_computation_id} "
                             f"and data_type {data_type} to {merged_file}")

                header_written = False
                with open(merged_file, 'w') as output_csv:
                    for idx, downloaded_path in enumerate(downloaded_paths):
                        with tempfile.TemporaryDirectory() as working_dir:
                            interim_path = f'{working_dir}/{idx}'
                            os.mkdir(interim_path)
                            with ZipFile(downloaded_path, 'r') as zip_ref:
                                zip_ref.extractall(interim_path)
                            csv_path = f'{interim_path}/{data_type}.csv'
                            with open(csv_path, 'r') as input_csv:
                                if header_written:
                                    next(input_csv)
                                output_csv.write(input_csv.read())
                                header_written = True
                algorithm_computation_id_to_data_type_to_merged_file[algorithm_computation_id][data_type] = merged_file
        return algorithm_computation_id_to_data_type_to_merged_file

    async def download(
        self, algorithm_computation_ids: List[str] = None, analysis_computation_ids: List[str] = None,
        source_aoi_version: int = None, dest_aoi_version: int = None,  algo_config_class: str = None,
        algo_config_subclass: str = None, created_on: Timestamp = None, observation_start_ts: Timestamp = None,
        max_observation_start_ts: Timestamp = None, data_type: str = None, download_dir: str = None
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        algorithm_computation_ids: [Required] List[str] - Algorithm computation IDs

        :return: Dict[str, Dict[str, List[str]]]: mapping of algorithm_computation_id_to_data_type_to_downloaded_paths
        """
        download_dir = os.getcwd() if not download_dir else download_dir

        result_get_responses = await self.get(
            algorithm_computation_ids=algorithm_computation_ids, analysis_computation_ids=analysis_computation_ids,
            source_aoi_version=source_aoi_version, dest_aoi_version=dest_aoi_version,
            algo_config_class=algo_config_class, algo_config_subclass=algo_config_subclass,
            created_on=created_on, observation_start_ts=observation_start_ts,
            max_observation_start_ts=max_observation_start_ts, include_export_files=True, data_type=data_type
        )

        result_export_credentials = result_get_responses[0].export_credentials
        credentials = result_export_credentials.credentials
        s3 = boto3.client(
            's3',
            aws_access_key_id=credentials.fields['AccessKeyId'].string_value,
            aws_session_token=credentials.fields['SessionToken'].string_value,
            aws_secret_access_key=credentials.fields['SecretAccessKey'].string_value
        )
        pattern = r"https://(.*?)\.s3"
        container_name = re.search(pattern, result_export_credentials.base_url_template).group(1)
        algorithm_computation_id_to_data_type_to_downloaded_paths = defaultdict(lambda: defaultdict(list))

        for result_get_response in result_get_responses:
            for result in result_get_response.results:
                data_type = result.data_type
                algorithm_computation_id = result.algorithm_computation_id
                for observation in result.observations:
                    key_path = observation.export_file.url
                    if not key_path:
                        continue
                    full_download_path = download_dir + os.path.split(key_path)[0]
                    filename = 'results.zip'
                    os.makedirs(full_download_path)
                    downloaded_path = os.path.join(full_download_path, filename)
                    s3.download_file(container_name, key_path[1:], downloaded_path)
                    algorithm_computation_id_to_data_type_to_downloaded_paths[
                        algorithm_computation_id][data_type].append(downloaded_path)

        logging.info(f"Downloaded results for algorithm_computation_ids and data_types: "
                     f"{algorithm_computation_id_to_data_type_to_downloaded_paths}")
        return algorithm_computation_id_to_data_type_to_downloaded_paths

    async def get(
        self, algorithm_computation_ids: List[str] = None, analysis_computation_ids: List[str] = None,
        source_aoi_version: int = None, dest_aoi_version: int = None,  algo_config_class: str = None,
        algo_config_subclass: str = None, created_on: Timestamp = None, observation_start_ts: Timestamp = None,
        max_observation_start_ts: Timestamp = None, include_export_files: bool = None, data_type: str = None
    ) -> List[ResultGetResponse]:
        """
            required: algorithm_computation_ids or analysis_computation_ids
        """
        # Query all GetResultResponses
        result_get_responses = []
        pagination = Pagination(page_size=1000)
        has_next_result = True
        while has_next_result:
            request = ResultGetRequest(
                algorithm_computation_ids=algorithm_computation_ids,
                analysis_computation_ids=analysis_computation_ids,
                source_aoi_version=source_aoi_version,
                dest_aoi_version=dest_aoi_version,
                algo_config_class=algo_config_class,
                algo_config_subclass=algo_config_subclass,
                created_on=created_on,
                observation_start_ts=observation_start_ts,
                max_observation_start_ts=max_observation_start_ts,
                include_export_files=include_export_files,
                data_type=data_type,
                pagination=Pagination(page_token=pagination.next_page_token, page_size=1000)
            )
            result_get_response = await self.__client.api.result.get(request, timeout=self.__timeout)
            result_get_responses.append(result_get_response)
            pagination = result_get_response.pagination
            has_next_result = pagination and pagination.next_page_token
        return result_get_responses
