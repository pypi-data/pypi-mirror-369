from google.protobuf.timestamp_pb2 import Timestamp
from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.common_models_pb2 import Pagination
from terrascope_api.models.credit_pb2 import Credit as PapiCredit, CreditEstimateRequest, CreditTransactionsResponse
from terrascope_api.models.credit_pb2 import CreditAddRequest, CreditRemoveRequest, CreditRefundRequest, \
    CreditAlgorithmMultiplierSetRequest, CreditDataSourceMultiplierSetRequest, CreditSummaryRequest, \
    CreditTransactionsRequest, Transaction


class APICredit:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def estimate(self, algorithm_computation_id: str) -> float:
        """
        Description:
        Returns an estimate of the credits required to compute results for the specified algorithm.
        Estimates the full cost, including open orders based on the ending date of the specified TOI.

        :return: APICredit Estimate : float
        """
        request = CreditEstimateRequest(
            algorithm_computation_id=algorithm_computation_id
        )
        response = await self.__client.api.credit.estimate(request, timeout=self.__timeout)
        return response.credit_estimate

    async def add(self, credit_source_id: str, amount: float, reason: str):
        """
        Description
        Add credits to the specified credit_source.

        :param credit_source_id: str
        :param amount: float
        :param reason: str
        :return: No Return
        """
        request = CreditAddRequest(
            credit_source_id=credit_source_id,
            amount=amount,
            reason=reason
        )
        await self.__client.api.credit.add(request, timeout=self.__timeout)

    async def remove(self, credit_source_id: str, amount: float, reason: str):
        """
        Description
        Removes credits to the specified credit_source.

        :param credit_source_id: str
        :param amount: float
        :param reason: str
        :return: No Return
        """
        request = CreditRemoveRequest(
            credit_source_id=credit_source_id,
            amount=amount,
            reason=reason
        )
        await self.__client.api.credit.remove(request, timeout=self.__timeout)

    async def refund(self, credit_source_id: str, amount: float, reason: str):
        """
        Description

        Refund credits to a user collection

        :param credit_source_id: str
        :param amount: float
        :param reason: str
        :return:
        """
        request = CreditRefundRequest(
            credit_source_id=credit_source_id,
            amount=amount,
            reason=reason
        )
        await self.__client.api.credit.refund(request, timeout=self.__timeout)

    async def summary(self, credit_source_id: str) -> PapiCredit:
        """
        Retrieves the credit summary for the specified user's department. As credits are associated with a department,
        all users of a department see the same credit summary. Currently, this can only be done at
        the department level.

        Available - Credits that can be used for future Analyses and Computations
        Reserved - Credits on hold for running Analyses and Computations
        Used - Credits used by past Analyses and Computations

        :param credit_source_id: str
        :return: APICredit
        """
        request = CreditSummaryRequest(
            credit_source_id=credit_source_id
        )
        response = await self.__client.api.credit.summary(request, timeout=self.__timeout)
        return response.credit

    async def transactions(self,
                           credit_source_id,
                           transaction_type: Transaction.TransactionType,
                           start_date: Timestamp,
                           end_date: Timestamp,
                           algorithm_computation_id: str,
                           pagination: Pagination) -> CreditTransactionsResponse:
        """
        Description

        Retrieves the detailed view of all transactions associated with a department. Can filter for a time range or
        transaction type. Currently, this can only be done at the department level.

        :param credit_source_id: str
        :param transaction_type: TransactionType
        :param start_date: Timestamp
        :param end_date: Timestamp
        :param algorithm_computation_id: str
        :param pagination: Pagination
        :return:
        """
        request = CreditTransactionsRequest(
            credit_source_id=credit_source_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            algorithm_computation_id=algorithm_computation_id,
            pagination=pagination
        )
        response = await self.__client.api.credit.transactions(request, timeout=self.__timeout)
        return response

    async def set_algorithm(self, algorithm_version_id: str,
                            algorithm_execution_price: float,
                            algorithm_value_price: float):
        """
        Description

        Assign a price to the specified algorithm. Price must be a multiple of $0.001.
        This can only be done by an admin user.

        :param algorithm_version_id: str
        :param algorithm_execution_price: float
        :param algorithm_value_price: float
        :return:
        """
        request = CreditAlgorithmMultiplierSetRequest(
            algorithm_version_id=algorithm_version_id,
            algorithm_execution_price=algorithm_execution_price,
            algorithm_value_price=algorithm_value_price
        )
        await self.__client.api.credit.set_algorithm(request, timeout=self.__timeout)

    async def set_data_source(self, data_source_id: str, data_source_price: float):
        """
        Description

        Assign a price to the specified data_source. Price must be a multiple of $0.001.
        This can only be done by an admin user.

        :param data_source_id: str
        :param data_source_price: float
        :return:
        """
        request = CreditDataSourceMultiplierSetRequest(
            data_source_id=data_source_id,
            data_source_price=data_source_price
        )
        await self.__client.api.credit.set_data_source(request, timeout=self.__timeout)
