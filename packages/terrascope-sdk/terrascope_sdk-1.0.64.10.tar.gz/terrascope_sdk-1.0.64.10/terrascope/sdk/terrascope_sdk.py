import os
import warnings
from dataclasses import dataclass

from terrascope_api import TerrascopeAsyncClient

from terrascope.sdk.api.algorithm import APIAlgorithm, APIAlgorithmVersion, APIAlgorithmConfig, APIAlgorithmComputation
from terrascope.sdk.api.analysis import APIAnalysis, APIAnalysisVersion, APIAnalysisConfig, APIAnalysisComputation
from terrascope.sdk.api.aoi import APIAOI, APIAOITransaction, APIAOIVersion, APIAOICollection
from terrascope.sdk.api.credit import APICredit
from terrascope.sdk.api.data import APIDataSource, APIDataType
from terrascope.sdk.api.permission import APIPermission
from terrascope.sdk.api.result import APIResult
from terrascope.sdk.api.toi import APIToi
from terrascope.sdk.api.user import APIUser
from terrascope.sdk.api.visualization import APIVisualization
from terrascope.sdk.api.order import APIOrder
from terrascope.sdk.api.tasking_order import APITaskingOrder
from terrascope.sdk.api.filter import APIFilter, APIProjectFilter


@dataclass
class TerraScopeSDK:
    """
    https://docs.terrascope.orbitalinsight.com/docs
    """
    algorithm: APIAlgorithm
    algorithm_version: APIAlgorithmVersion
    algorithm_config: APIAlgorithmConfig
    algorithm_computation: APIAlgorithmComputation

    analysis: APIAnalysis
    analysis_version: APIAnalysisVersion
    analysis_config: APIAnalysisConfig
    analysis_computation: APIAnalysisComputation

    aoi: APIAOI
    aoi_transaction: APIAOITransaction
    aoi_version: APIAOIVersion
    aoi_collection: APIAOICollection

    toi: APIToi

    credit: APICredit

    data_source: APIDataSource
    data_type: APIDataType

    permission: APIPermission

    result: APIResult

    visualization: APIVisualization

    user: APIUser

    order: APIOrder

    tasking_order: APITaskingOrder

    filter: APIFilter

    project_filter: APIProjectFilter

    client: TerrascopeAsyncClient

    def __init__(self, client: TerrascopeAsyncClient = None, timeout: int = None):
        if timeout is None:
            timeout = int(os.getenv('TERRASCOPE_TIMEOUT', default='60'))
        if client is None:
            client = self.create_client()

        # Set Up Algo APIs
        self.algorithm = APIAlgorithm(client=client, timeout=timeout)
        self.algorithm_version = APIAlgorithmVersion(client=client, timeout=timeout)
        self.algorithm_config = APIAlgorithmConfig(client=client, timeout=timeout)
        self.algorithm_computation = APIAlgorithmComputation(client=client, timeout=timeout)

        # Set Up Analysis APIs
        self.analysis = APIAnalysis(client=client, timeout=timeout)
        self.analysis_version = APIAnalysisVersion(client=client, timeout=timeout)
        self.analysis_config = APIAnalysisConfig(client=client, timeout=timeout)
        self.analysis_computation = APIAnalysisComputation(client=client, timeout=timeout)

        # Set Up AOI APIs
        self.aoi = APIAOI(client=client, timeout=timeout)
        self.aoi_transaction = APIAOITransaction(client=client, timeout=timeout)
        self.aoi_version = APIAOIVersion(client=client, timeout=timeout)
        self.aoi_collection = APIAOICollection(client=client, timeout=timeout)

        # Set Up AOI APIs
        self.toi = APIToi(client=client, timeout=timeout)

        # Set Up APICredit APIs
        self.credit = APICredit(client=client, timeout=timeout)

        # Set Up Data APIs
        self.data_type = APIDataType(client=client, timeout=timeout)
        self.data_source = APIDataSource(client=client, timeout=timeout)

        # Set Up Permission APIs
        self.permission = APIPermission(client=client, timeout=timeout)

        # Set Up APIResult APIs
        self.result = APIResult(client=client, timeout=timeout)

        # Set Up Visualization APIs
        self.visualization = APIVisualization(client=client, timeout=timeout)

        # Set Up User APIs
        self.user = APIUser(client=client, timeout=timeout)

        # set up order APIs
        self.order = APIOrder(client=client, timeout=timeout)

        # Set Up Tasking Order APIs
        self.tasking_order = APITaskingOrder(client=client, timeout=timeout)

        # Set Up Filter APIs
        self.filter = APIFilter(client=client, timeout=timeout)
        self.project_filter = APIProjectFilter(client=client, timeout=timeout)

    @staticmethod
    def create_client(terrascope_host: str = None, terrascope_api_token: str = None) -> TerrascopeAsyncClient:
        """
        Description:

        Sets up the client / session once for the instance of the builder.
        All subsequent calls to this builder will use this client (session) to complete events.

        envs:
        OI_PAPI_HOST: url for terrascope env
        USER_TOKEN: your api key

        :return: TerrascopeAsyncClient object and sets the internal self to the client. Will likely not need client outside
        this classes scope.
        """

        if not terrascope_host:
            assert os.environ['TERRASCOPE_API_HOST'] is not None
            terrascope_host = os.environ['TERRASCOPE_API_HOST']

        if 'TERRASCOPE_PORT' in os.environ:
            warnings.warn("Please set TERRASCOPE_API_PORT. TERRASCOPE_PORT is deprecated")

        if 'TERRASCOPE_API_PORT' not in os.environ:
            warnings.warn("TERRASCOPE_API_PORT is mandatory. Using 443 as default port.")

        terrascope_port_str = os.getenv('TERRASCOPE_API_PORT', default='443')
        terrascope_port = int(terrascope_port_str)

        if not terrascope_api_token:
            assert os.environ['TERRASCOPE_API_TOKEN'] is not None
            terrascope_api_token = os.getenv('TERRASCOPE_API_TOKEN')

        secure_string = os.getenv('TERRASCOPE_SECURE', default='True')
        secure = True if secure_string in ['True', 'true', 'Yes', 'yes', '1'] else False

        client = TerrascopeAsyncClient(terrascope_host, terrascope_port, api_token=terrascope_api_token,
                                       secure=secure)

        return client
